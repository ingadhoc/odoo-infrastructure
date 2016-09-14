# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, SUPERUSER_ID, _
from openerp.exceptions import except_orm
from openerp.tools.parse_version import parse_version
import xmlrpclib
import operator
import socket
import time
import uuid
from dateutil.relativedelta import relativedelta
from openerp.addons.server_mode.mode import get_mode
from datetime import datetime
from .server import custom_sudo as sudo
from fabric.contrib.files import exists, append, sed
from erppeek import Client
from openerp.exceptions import Warning
import os
import requests
import simplejson
import logging
_logger = logging.getLogger(__name__)
_update_state_vals = [
    ('unknown', 'Unknown'),
    ('init_and_conf_required', 'Init and Config Required'),
    ('update_required', 'Update Required'),
    ('optional_update', 'Optional Update'),
    ('on_to_install', 'On To Install'),
    ('on_to_remove', 'On To Remove'),
    ('on_to_upgrade', 'On To Upgrade'),
    ('unmet_deps', 'Unmet Dependencies'),
    ('not_installable', 'Not Installable Modules'),
    ('installed_uninstallable', 'Installed Uninstallable'),
    ('installed_uncontracted', 'Installed Uncontracted'),
    ('uninstalled_auto_install', 'Uninstalled Auto Install'),
    ('ok', 'Ok'),
]


class database(models.Model):

    """"""
    _name = 'infrastructure.database'
    _description = 'database'
    _inherit = ['ir.needaction_mixin', 'mail.thread']
    _rec_name = 'display_name'
    _states_ = [
        ('draft', 'Draft'),
        ('maintenance', 'Maintenance'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        # ('deactivated', 'Deactivated'),
        ('cancel', 'Cancel'),
    ]
    _mail_post_access = 'read'

    @api.multi
    def message_get_default_recipients(self):
        res = super(database, self).message_get_default_recipients()
        database_email_cc = self._context.get('database_email_cc', False)
        if database_email_cc == 'db_related_contacts':
            for db_id in res.iterkeys():
                db = self.browse(db_id)
                commercial_partner_id = db.partner_id.commercial_partner_id
                related_contacts = self.env['res.partner'].search([
                    ('id', 'child_of', commercial_partner_id.id),
                    ('email', '!=', False)])
                res[db_id]['partner_ids'] = related_contacts.ids
                # we replace partner for all related contacts
                # exclude de partner id
                # ('id', '!=', db.partner_id.id),
                # res[db_id]['email_cc'] = ','.join(
                #     related_contacts.mapped('email'))
        return res

    database_type_id = fields.Many2one(
        # TODO remove this field as it is no more longer needed
        'infrastructure.database_type',
        string='Database Type',
        readonly=True,
        # required=True,
        states={'draft': [('readonly', False)]},
        # track_visibility='onchange',
        copy=False,
    )
    instance_type_id = fields.Many2one(
        # 'infrastructure.database_type',
        string='Instance Type',
        store=True,
        related='instance_id.database_type_id',
    )
    display_name = fields.Char(
        compute='_get_display_name',
        store=True,
    )
    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange'
    )
    color = fields.Integer(
        string='Color Index',
        compute='get_color',
    )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
    )
    demo_data = fields.Boolean(
        string='Demo Data?',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    note = fields.Html(
        string='Note'
    )
    smtp_server_id = fields.Many2one(
        'infrastructure.mailserver',
        string='SMTP Server',
    )
    domain_alias = fields.Char(
        string='Domain Alias',
        compute='get_domain_alias',
    )
    attachment_loc_type = fields.Selection(
        [(u'filesystem', 'filesystem'), (u'database', 'database')],
        string='Attachment Location Type',
        default='filesystem',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    attachment_location = fields.Char(
        string='Attachment Location',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    issue_date = fields.Date(
        string='Issue Data',
        copy=False,
        default=fields.Date.context_today,
    )
    deactivation_date = fields.Date(
        string='Deactivation Date',
        copy=False,
        help='Depending on type it could be onl informative or could be '
        'automatically deactivated on this date',
    )
    drop_date = fields.Date(
        string='Drop Date',
        copy=False,
        help='Depending on type it could be onl informative or could be '
        'automatically dropped on this date',
    )
    advance_type = fields.Selection(
        related='instance_type_id.type',
        # related='database_type_id.type',
        string='Type',
        readonly=True,
        # store=True,
    )
    state = fields.Selection(
        _states_,
        'State',
        default='draft'
    )
    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='Instance',
        ondelete='cascade',
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=True,
    )
    environment_id = fields.Many2one(
        'infrastructure.environment',
        string='Environment',
        related='instance_id.environment_id',
        store=True,
        readonly=True,
    )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        related='instance_id.environment_id.server_id',
        store=True,
        readonly=True,
    )
    main_hostname = fields.Char(
        string='Main Hostname',
        compute='get_main_hostname',
    )
    backup_ids = fields.One2many(
        'infrastructure.database.backup',
        'database_id',
        string='Backups',
        readonly=True,
    )
    # module_ids = fields.One2many(
    #     'infrastructure.database.module',
    #     'database_id',
    #     string='Modules',
    #     )
    user_ids = fields.One2many(
        'infrastructure.database.user',
        'database_id',
        string='Users',
        copy=True,
    )
    admin_password = fields.Char(
        string='Admin Password',
        help='When trying to connect to the database first we are going to '
        'try by using the instance password and then with thisone.',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
    )
    virtual_alias = fields.Char(
        string='Virtual Alias',
        compute='get_aliases',
    )
    local_alias = fields.Char(
        string='Local Alias',
        compute='get_aliases',
    )
    mailgate_path = fields.Char(
        string='Mailgate Path',
        compute='get_mailgate_path',
    )
    alias_prefix = fields.Char(
        'Alias Prefix',
        copy=False,
    )
    alias_hostname_id = fields.Many2one(
        'infrastructure.server_hostname',
        string='Alias Hostname',
        copy=False,
    )
    alias_hostname_wildcard = fields.Boolean(
        related='alias_hostname_id.wildcard',
        string='Wildcard?',
        readonly=True,
        copy=False,
    )
    backups_enable = fields.Boolean(
        'Backups Enable',
        copy=False,
    )
    backup_format = fields.Selection([
        ('zip', 'zip (With Filestore)'),
        ('pg_dump', 'pg_dump (Without Filestore)')],
        'Backup Format',
        default='zip',
        required=True,
        copy=False,
    )
    catchall_enable = fields.Boolean(
        'Catchall Enable',
        copy=False,
    )
    update_state = fields.Selection(
        _update_state_vals,
        'Update Status',
        readonly=True,
    )
    last_overall_check_date = fields.Datetime(
        'Last Overall Check',
        readonly=True,
    )
    instante_state = fields.Selection(
        related='instance_id.odoo_service_state',
        string='Instance Status'
    )
    update_state_detail = fields.Text(
        'Update Status Detail',
        readonly=True,
    )
    base_modules_state = fields.Selection(
        [('ok', 'OK'), ('error', 'Error'), ('unknown', 'Unknown')],
        'Base Modules Status',
        readonly=True,
    )
    base_modules_state_detail = fields.Text(
        'Base Modules Detail',
        readonly=True,
    )
    backups_state = fields.Selection(
        [('ok', 'OK'), ('error', 'Error'), ('unknown', 'Unknown')],
        'Backups Status',
        readonly=True,
    )
    backups_state_detail = fields.Text(
        'Backups Detail',
        readonly=True,
    )
    check_database = fields.Boolean(
        'Check Databse with cron',
        copy=False,
    )
    overall_state = fields.Selection(
        [('ok', 'OK'), ('error', 'Error')],
        'Overall State',
        compute='get_overall_state',
        store=True,
    )

    @api.one
    @api.depends('name', 'instance_type_id.prefix')
    def _get_display_name(self):
        self.display_name = "%s (%s)" % (
            self.name, self.instance_type_id.prefix)

    @api.model
    def cron_check_databases(self):
        # TODO mejorar y solo verificar las que no fueron verificadas en el
        # ultimo intervalo de cron
        if get_mode():
            _logger.info(
                'Check databases cron is disable by server_mode. '
                'If you want to enable it you should remove develop or test '
                'value for server_mode key on openerp server config file')
            return False
        databases = self.with_context(
            do_not_raise=True).search([
                ('check_database', '=', True),
                ('state', '!=', 'inactive'),
            ])
        for db in databases:
            db.refresh_overall_state()
            db._cr.commit()
        return True

    @api.one
    def restart_instance(self):
        self.instance_id.restart_all()

    @api.one
    def refresh_overall_state(self):
        _logger.info('Checking database id: "%s"' % self.id)
        self.refresh_base_modules_state()
        self.refresh_backups_state()
        self.refresh_update_state()
        self.last_overall_check_date = fields.Datetime.now()

    @api.depends(
        'backups_state',
        'base_modules_state',
        'update_state',
        'instante_state'
    )
    def get_overall_state(self):
        overall_state = 'ok'
        if self.backups_state and self.backups_state != 'ok':
            overall_state = 'error'
        elif self.base_modules_state and self.base_modules_state != 'ok':
            overall_state = 'error'
        elif self.update_state and self.update_state not in [
                'ok', 'optional_update']:
            overall_state = 'error'
        elif self.instante_state and self.instante_state != 'ok':
            overall_state = 'error'
        self.overall_state = overall_state

    @api.multi
    def clean_overall_state(self):
        self.write({
            'base_modules_state': False,
            'backups_state': False,
            'update_state': False,
        })

    # TODO mejorar el codigo este de do_not_raise, hacerlo mucho mas siemple
    # se repite lo mismo en tres funciones distintas en distintos momentos
    @api.multi
    def refresh_base_modules_state(self):
        self.ensure_one()
        do_not_raise = self._context.get('do_not_raise', False)
        try:
            client = self.get_client()
        except:
            if do_not_raise:
                self.base_modules_state = 'unknown'
                self.base_modules_state_detail
                return True
            else:
                raise Warning(_('Could not get client'))
        # TODO extend do_not_raise to following warnings
        base_modules_state = 'ok'
        base_modules = self.env[
            'infrastructure.base.module'].search([]).mapped('name')
        installed_modules = client.modules(installed=True)['installed']
        uninstalled_modules = list(
            set(base_modules) - set(installed_modules))
        if uninstalled_modules:
            base_modules_state = 'error'
        self.base_modules_state = base_modules_state
        self.base_modules_state_detail = (
            '*Uninstalled modules: %s\n\n'
            '*Base modules: %s\n\n'
            '*Installed modules: %s\n' % (
                uninstalled_modules, base_modules, installed_modules))

    @api.multi
    def refresh_backups_state(self):
        self.ensure_one()
        do_not_raise = self._context.get('do_not_raise', False)
        if not self.backups_enable:
            self.backups_state = False
            return True
        try:
            client = self.get_client()
        except Exception, e:
            msg = _(
                'Could not get state!\n'
                'This is what we get %s' % e)
            if do_not_raise:
                self.backups_state = 'unknown'
                self.backups_state_detail = msg
                return True
            else:
                raise Warning(msg)
        modules = ['database_tools']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                msg = _(
                    "You can not refresh backups state if module '%s' is not "
                    "installed in the database") % (module)
                if do_not_raise:
                    _logger.warning(msg)
                    self.backups_state = ''
                    self.backups_state_detail = msg
                    return True
                else:
                    raise Warning(msg)
        try:
            backups_state = client.model(
                'db.database').get_overall_backups_state()
        except Exception, e:
            msg = _(
                'Could not get state!\n'
                'This is what we get %s' % e)
            if do_not_raise:
                self.backups_state = 'unknown'
                self.backups_state_detail = msg
                return True
            else:
                raise Warning(msg)
        state = backups_state.get('state', False)
        detail = backups_state.get('detail', False)

        if state not in ['ok', 'error']:
            msg = _(
                'Could not get state! Unknow error, we could not get state '
                'from "%s"' % (backups_state))
            if do_not_raise:
                _logger.warning(msg)
                self.backups_state = ''
                self.backups_state_detail = msg
                return True
            else:
                raise Warning(msg)
        self.backups_state = state
        self.backups_state_detail = detail
        return backups_state

    @api.multi
    def refresh_update_state(self):
        self.ensure_one()
        do_not_raise = self._context.get('do_not_raise', False)
        # we make a try because perhups instances is not up
        try:
            client = self.get_client()
        except Exception, e:
            msg = _(
                'Could not get state!\n'
                'This is what we get %s' % e)
            if do_not_raise:
                self.update_state = 'unknown'
                self.update_state_detail = msg
                return True
            else:
                raise Warning(msg)
        modules = ['database_tools']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                msg = (_(
                    "You can not refresh modules update status if module '%s' "
                    "is not installed in the database") % (module))
                if do_not_raise:
                    _logger.warning(msg)
                    self.update_state = 'unknown'
                    self.update_state_detail = msg
                    return True
                else:
                    raise Warning(msg)
        try:
            update_state = client.model(
                'ir.module.module').get_overall_update_state()
        except Exception, e:
            msg = (_(
                'Could not get state!\n'
                'This is what we get %s' % e))
            if do_not_raise:
                _logger.warning(msg)
                self.update_state = 'unknown'
                self.update_state_detail = msg
                return True
            else:
                raise Warning(msg)
        state = update_state.get('state', False)
        detail = update_state.get('detail', False)
        update_state_keys = [x[0] for x in _update_state_vals]

        if state not in update_state_keys:
            msg = (_(
                'Could not get state! Unknow error, we could not get state '
                'from "%s"' % (update_state)))
            if do_not_raise:
                _logger.warning(msg)
                self.update_state = 'unknown'
                self.update_state_detail = msg
                return True
            else:
                raise Warning(msg)
        self.update_state = state
        self.update_state_detail = detail
        return update_state

    @api.one
    def fix_db(self, uninstall_modules=True):
        """
        Method to be called from wizard or automatic
        """
        client = self.get_client_attempts()

        self.refresh_update_state()
        if self.update_state == 'ok':
            _logger.info('No need to update db %s' % self.name)
            return True

        _logger.info('Fixing db %s' % self.name)
        # TODO puede dar timeout si no responde la bd, en realidad en cualqueir
        # lugar de client, deberiamos ver como gestionarlo
        raise_msg = False
        restart_if_needed = False
        res = client.model('db.configuration').fix_db(
            raise_msg, uninstall_modules, restart_if_needed)
        if res.get('error'):
            raise Warning(res.get('error'))
        self.refresh_update_state()
        return True

    @api.multi
    def reinit_modules(self, modules_names):
        """
        modules_names is a list of modules names to be reinit
        """
        # TODO lo ideal sería hacer un metodo algo mas lindo pero no encontre
        # la manera
        _logger.info('Initializing modules: %s' % modules_names)

        # update module list
        self.update_module_list()

        # remove odoo server
        self.server_id.get_env()
        self.instance_id.remove_odoo_service()

        # prepare and run odoo initializing modules
        init_command = ('%s -i %s -d %s' % (
            self.instance_id.update_cmd,
            ','.join(modules_names),
            self.name)
        )
        _logger.info('Running init modules commmand: %s' % init_command)
        sudo(init_command)

        # run again odoo server
        self.instance_id.run_odoo_service()

        # TODO mejorar esto y ver que el servicio este andando
        time.sleep(10)

    @api.multi
    def install_base_modules(self):
        base_modules = self.env[
            'infrastructure.base.module'].search([]).mapped('name')
        self.install_modules(base_modules)
        self.refresh_base_modules_state()

    @api.multi
    def install_modules(self, modules_names):
        """
        modules_names is a list of modules names to be upgraded
        """
        _logger.info('Installing modules: %s' % modules_names)
        client = self.get_client()
        client.install(*modules_names)

    @api.multi
    def upgrade_modules(self, modules_names):
        """
        modules_names is a list of modules names to be upgraded
        """
        _logger.info('Updating modules: %s' % modules_names)
        client = self.get_client()
        client.upgrade(*modules_names)

    @api.multi
    def update_module_list(self):
        """
        modules_names is a list of modules names to be upgraded
        """
        client = self.get_client()
        client.model('ir.module.module').update_list()

    @api.multi
    def check_module_version(self, module_name, version, operator_string):
        database_ids = []
        version = parse_version(version)
        operators_dic = {
            "=": operator.eq,
            "<": operator.lt,
            '<=': operator.le
        }
        op = operators_dic.get(operator_string)
        if not op:
            raise Warning(_('Operator must be one of: %s') % (
                ', '.join(operators_dic.keys())))
        for database in self:
            client = database.get_client()
            # on odoo is called latest but we call properly "installed"
            installed_version = client.model('ir.module.module').browse(
                ['name = %s' % module_name], limit=1).latest_version
            # it should return a list with one element, if that element is
            # false then module is not installed
            if installed_version and installed_version[0]:
                installed_version = parse_version(installed_version[0])
                if op(installed_version, version):
                    database_ids.append(database.id)
        return self.browse(database_ids)

    @api.one
    @api.depends('state')
    def get_color(self):
        color = 4
        if self.state == 'draft':
            color = 7
        elif self.state == 'cancel':
            color = 1
        elif self.state == 'inactive':
            color = 3
        if self.overall_state != 'ok':
            color = 2
        self.color = color

    @api.onchange('instance_id')
    def _onchange_instance(self):
        instance = self.instance_id
        self.partner_id = instance.environment_id.partner_id
        # self.database_type_id = instance.database_type_id
        main_hostname = instance.main_hostname_id
        if main_hostname:
            self.alias_hostname_id = main_hostname.server_hostname_id
            self.alias_prefix = main_hostname.prefix

    @api.one
    @api.depends(
        'instance_id.main_hostname',
        'instance_id.db_filter.add_bd_name_to_host'
    )
    def get_main_hostname(self):
        main_hostname = self.instance_id.main_hostname
        if self.instance_id.db_filter.add_bd_name_to_host:
            main_hostname = "%s.%s" % (
                self.name,
                self.instance_id.main_hostname_id.name
            )
        self.main_hostname = main_hostname

    @api.one
    @api.depends(
        'alias_prefix', 'alias_hostname_id', 'alias_hostname_id.wildcard')
    def get_domain_alias(self):
        domain_alias = False
        if self.alias_hostname_id:
            domain_alias = ''
            if self.alias_hostname_id.wildcard and self.alias_prefix:
                domain_alias = self.alias_prefix + '.'
            domain_alias += self.alias_hostname_id.name
        self.domain_alias = domain_alias

    @api.one
    @api.depends('instance_id')
    def get_mailgate_path(self):
        """We use this function because perhups in future you need to use one
        or another mailgate file depending odoo version
        """
        mailgate_path = self.server_id.mailgate_file
        self.mailgate_path = mailgate_path

    @api.one
    @api.depends('virtual_alias', 'local_alias', 'instance_id')
    def get_aliases(self):
        virtual_alias = False
        local_alias = False
        self.virtual_alias = virtual_alias
        self.local_alias = local_alias
        if self.domain_alias:
            virtual_alias = "@%s %s@localhost" % (
                self.domain_alias, self.domain_alias)
            local_alias = self.get_local_alias()
        self.virtual_alias = virtual_alias
        self.local_alias = local_alias

    @api.model
    def get_local_alias(self):
        local_alias = False
        if self.mailgate_path:
            local_alias = (
                '%s: "| %s  --host=localhost --port=%i -u %i -p %s -d %s' % (
                    self.domain_alias, self.mailgate_path,
                    self.instance_id.xml_rpc_port,
                    SUPERUSER_ID, self.instance_id.admin_pass, self.name))
        return local_alias

    _sql_constraints = [
        ('name_uniq', 'unique(name, instance_id)',
            'Database Name Must be Unique per instance'),
    ]

    @api.one
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise Warning(_(
                'You cannot delete a database which is not draft or cancelled')
            )
        return super(database, self).unlink()

    # @api.onchange('database_type_id', 'instance_id')
    # def onchange_database_type_id(self):
    @api.onchange('instance_type_id', 'instance_id')
    def onchange_instance_type_id(self):
        # if self.database_type_id and self.instance_id:
        if self.instance_id:
            self.name = ('%s') % (
                # self.instance_type_id.prefix,
                self.instance_id.environment_id.name.replace('-', '_')
            )
            self.demo_data = self.instance_type_id.demo_data
            self.check_database = self.instance_type_id.check_database
            self.backups_enable = self.instance_type_id.backups_enable
            self.admin_password = self.instance_type_id.db_admin_pass or \
                self.instance_id.name

    # @api.onchange('database_type_id', 'issue_date')
    @api.onchange('instance_type_id', 'issue_date')
    def get_deact_date(self):
        deactivation_date = False
        drop_date = False
        if self.issue_date:
            if self.instance_type_id.auto_deactivation_days:
                deactivation_date = (datetime.strptime(
                    self.issue_date, '%Y-%m-%d') + relativedelta(
                    days=self.instance_type_id.auto_deactivation_days))
            if self.instance_type_id.auto_drop_days:
                drop_date = (datetime.strptime(
                    self.issue_date, '%Y-%m-%d') + relativedelta(
                    days=self.instance_type_id.auto_drop_days))
        self.deactivation_date = deactivation_date
        self.drop_date = drop_date

    @api.one
    def show_passwd(self):
        raise except_orm(
            _("Password:"),
            _("%s") % self.admin_password
        )

# DATABASE CRUD

    @api.multi
    def get_sock(self, service='db', max_attempts=5):
        self.ensure_one()
        base_url = self.instance_id.main_hostname
        rpc_db_url = '%s/xmlrpc/%s' % (base_url, service)
        # rpc_db_url = 'http://%s/xmlrpc/%s' % (base_url, service)
        sock = xmlrpclib.ServerProxy(rpc_db_url)

        # try connection
        connected = False
        attempts = 0
        while not connected and attempts < max_attempts:
            attempts += 1
            _logger.info("Connecting, attempt number: %i" % attempts)
            try:
                sock._()   # Call a fictive method.
            except xmlrpclib.Fault:
                # connected to the server and the method doesn't exist which
                # is expected.
                _logger.info("Connected to socket")
                connected = True
                pass
            except socket.error:
                _logger.info("Could not connect to socket")
                pass
            except:
                # Tuve que agregar este porque el error no me era atrapado
                # arriba
                _logger.info("Connecting3")
                pass
        if not connected:
            raise Warning(_("Could not connect to socket '%s'") % (rpc_db_url))
        return sock

    @api.one
    def create_db(self):
        """Funcion que utliza erpeek para crear bds"""
        _logger.info("Creating db '%s'" % (self.name))
        client = self.get_client(not_database=True)
        lang = self.instance_type_id.install_lang_id or 'en_US'
        client.create_database(
            self.instance_id.admin_pass,
            self.name,
            demo=self.demo_data,
            lang=lang,
            user_password=self.admin_password or 'admin')
        self.install_base_modules()
        # config backups
        self.config_backups()
        self.action_activate()

    @api.multi
    def drop_db(self):
        """Funcion que utiliza ws nativos de odoo para eliminar db"""
        self.ensure_one()
        by_pass_protection = self._context.get('by_pass_protection', False)
        if self.advance_type == 'protected' and not by_pass_protection:
            raise Warning(_(
                'You can not drop a database protected, '
                'you can change database type, or drop it manually'))
        _logger.info("Dropping db '%s'" % (self.name))
        sock = self.get_sock()
        try:
            sock.drop(self.instance_id.admin_pass, self.name)
        except:
            # If we get an error we try restarting the service
            try:
                self.instance_id.restart_odoo_service()
                # we ask again for sock and try to connect waiting for service
                # start
                sock = self.get_sock(max_attempts=1000)
                sock.drop(self.instance_id.admin_pass, self.name)
            except Exception, e:
                raise Warning(_(
                    'Unable to drop Database. If you are working in an '
                    'instance with "workers" then you can try '
                    'restarting service. This is what we get:\n%s') % (e))
        self.action_cancel()

    @api.one
    def backup_now(
            self, name=False, keep_till_date=False, backup_format='zip'):
        client = self.get_client()
        try:
            self_db_id = client.model('ir.model.data').xmlid_to_res_id(
                'database_tools.db_self_database')
            bd_result = client.model('db.database').database_backup(
                self_db_id,
                'manual',
                backup_format,
                name,
                keep_till_date,
            )
        except Exception, e:
            raise Warning(_(
                'Could not make backup! This is what we get %s' % e))
        if not bd_result.get('backup_name', False):
            raise Warning(_(
                'Could not make backup! This is what we get %s' % (
                    bd_result.get('error', ''))))
        # TODO log message or do something (do not raise warning because it
        # dont close wizard)
        # else:
            # raise Warning(_(
            # 'Backup %s succesfully created!' % bd_result['backup_name']))

    @api.one
    def migrate_db(self):
        """Funcion que utiliza ws nativos de odoo para hacer update de bd"""
        _logger.info("Migrating db '%s'" % (self.name))
        sock = self.get_sock()
        try:
            return sock.migrate_databases(
                self.instance_id.admin_pass, [self.name])
        except Exception, e:
            raise Warning(_(
                'Unable to migrate Database. If you are working in an '
                'instance with "workers" then you can try '
                'restarting service. This is what we get:\n%s') % (e))

    @api.one
    def rename_db(self, new_name):
        """Funcion que utiliza ws nativos de odoo para hacer update de bd"""
        _logger.info("Rennaming db '%s' to '%s'" % (self.name, new_name))
        sock = self.get_sock()
        try:
            sock.rename(self.instance_id.admin_pass, self.name, new_name)
        except:
            # If we get an error we try restarting the service
            try:
                self.instance_id.restart_odoo_service()
                # we ask again for sock and try to connect waiting for start
                sock = self.get_sock(max_attempts=1000)
                sock.rename(self.instance_id.admin_pass, self.name, new_name)
            except Exception, e:
                raise Warning(_(
                    'Unable to rename Database. If you are working in an '
                    'instance with "workers" then you can try '
                    'restarting service. This is what we get:\n%s') % (e))
        self.name = new_name
        # reconfigure catchall
        if self.catchall_enable:
            self.config_catchall()
        if self.backups_enable:
            self.config_backups()

    @api.one
    def exist_db(self, database_name):
        """Funcion que utiliza ws nativos de odoo"""
        sock = self.get_sock()
        if sock.db_exist():
            return True
        else:
            return False

    @api.model
    def restore(
            self, host, admin_pass, db_name, file_path, file_name,
            backups_enable, remote_server=False, overwrite=False):
        """Used on restore from file"""
        try:
            url = "%s/%s" % (host, 'restore_db')
            headers = {'content-type': 'application/json'}
            data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    'admin_pass': admin_pass,
                    'db_name': db_name,
                    'file_path': file_path,
                    'file_name': file_name,
                    'backups_state': backups_enable,
                    'remote_server': remote_server,
                    'overwrite': overwrite,
                },
            }
            _logger.info(
                'Restoring backup %s, you can also watch target '
                'instance log' % db_name)
            response = requests.post(
                url,
                data=simplejson.dumps(data),
                headers=headers,
                verify=False,
                # TODO fix this, we disable verify because an error we have
                # with certificates aca se explica le error
                # http://docs.python-requests.org/en/latest/community/faq/
                # what-are-hostname-doesn-t-match-errors
            ).json()
            _logger.info('Restored complete, result: %s' % response)
            if response['result'].get('error', False):
                raise Warning(_(
                    'Unable to restore bd %s, you can try restartin target '
                    'instance. This is what we get: \n %s') % (
                    db_name, response['result'].get('error')))
            _logger.info('Back Up %s Restored Succesfully' % db_name)
        except Exception, e:
            raise Warning(_(
                'Unable to restore bd %s, you can try restartin target '
                'instance. This is what we get: \n %s') % (
                db_name, e))
        return True

    @api.multi
    def duplicate_db(self, new_database_name, backups_enable):
        """Funcion que utiliza ws nativos de odoo para hacer duplicar bd"""
        self.ensure_one()
        sock = self.get_sock()
        client = self.get_client()
        new_db = self.copy({
            'name': new_database_name,
            'backups_enable': backups_enable,
            'issue_date': fields.Date.today(),
            # 'database_type_id': database_type.id,
        })
        try:
            sock.duplicate_database(
                self.instance_id.admin_pass, self.name, new_database_name)
        except Exception, e:
            raise Warning(
                _('Unable to duplicate Database. This is what we get:\n%s') % (
                    e))
        client.model('db.database').backups_state(
            new_database_name, backups_enable)
        new_db.action_activate()
        if backups_enable:
            new_db.config_backups()
        # devolvemos la accion de la nueva bd creada
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')
        if not action:
            return False
        res = action.read()[0]
        # res['domain'] = [('id', 'in', databases.ids)]
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'infrastructure.view_infrastructure_database_form')
        res['views'] = [(form_view_id, 'form')]
        res['res_id'] = new_db.id
        return res

    # TODO ver si borramos esta Funcion vieja que usaba el kill de odoo tools
    # @api.one
    # def duplicate_db(self, new_database_name, backups_enable):
    #     """Funcion que utiliza ws nativos de odoo para hacer duplicar bd"""
    #     client = self.get_client()
    #     sock = self.get_sock()
    #     new_db = self.copy({
    #         'name': new_database_name,
    #         'backups_enable': backups_enable
    #         })
    #     self.kill_db_connection()
    #     try:
    #         sock.duplicate_database(
    #             self.instance_id.admin_pass, self.name, new_database_name)
    #         client.model('db.database').backups_state(
    #             new_database_name, backups_enable)
    #     except Exception, e:
    #         raise Warning(_(
    #             'Unable to duplicate Database. This is what we get:\n%s') % (
    #               e))
    #     new_db.action_activate()
    #     # TODO retornar accion de ventana a la bd creada

    @api.multi
    def get_version(self):
        """Funcion que utiliza ws nativos de odoo"""
        sock = self.get_sock('common')
        return sock.version()

    @api.one
    def kill_db_connection(self):
        client = self.get_client()
        self.server_id.get_env()
        modules = ['database_tools']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                raise Warning(_(
                    "You can not kill connections if module '%s' is not "
                    "installed in the database") % (module))

        self_db_id = client.model('ir.model.data').xmlid_to_res_id(
            'database_tools.db_self_database')
        client.model('db.database').drop_con(self_db_id)

# Database connection helper
    @api.multi
    def get_client_attempts(self, not_database=False, attempts=20):
        self.ensure_one()
        _logger.info('Getting client with attempts %s' % attempts)
        # connected = False
        # remaining = 0
        try:
            return self.get_client(not_database)
        except Exception, e:
            if attempts:
                time.sleep(1)
                return self.get_client_attempts(
                    not_database, attempts - 1)
            else:
                raise Warning('asda %s' % e)

    @api.multi
    def get_client(self, not_database=False):
        self.ensure_one()
        try:
            if not_database:
                return Client(self.instance_id.main_hostname)
        except Exception, e:
            raise except_orm(
                _("Unable to Connect to Database."),
                _('Error: %s') % e
            )
        # First try to connect using instance pass
        try:
            return Client(
                self.instance_id.main_hostname,
                db=self.name,
                user='admin',
                password=self.instance_id.admin_pass)
        # then try to connect using database pass
        except:
            try:
                return Client(
                    self.instance_id.main_hostname,
                    # 'http://%s' % (self.instance_id.main_hostname),
                    db=self.name,
                    user='admin',
                    password=self.admin_password)
            except Exception, e:
                raise except_orm(
                    _("Unable to Connect to Database."),
                    _('Error: %s') % e
                )

# Backups management

    @api.one
    def update_backups_data(self):
        client = self.get_client()
        modules = ['database_tools']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                raise Warning(_(
                    "You can not Update Backups Data if module '%s' is not "
                    "installed in the database") % (module))
        self_db_id = client.model('ir.model.data').xmlid_to_res_id(
            'database_tools.db_self_database')
        _logger.info('Updating remote backups data')
        client.model('db.database').update_backups_data(self_db_id)
        _logger.info('Reading Remote Backups Data')
        backups_data = client.read(
            'db.database.backup', [('database_id', '=', self_db_id)])
        imp_fields = [
            'id',
            'database_id/.id',
            'date',
            'name',
            'path',
            'type',
            'keep_till_date',
        ]
        rows = []
        for backup in backups_data:
            row = [
                'db_%i_backup_%i' % (self.id, backup['id']),
                self.id,
                backup['date'],
                backup['name'],
                backup['path'],
                backup['type'],
                backup['keep_till_date'],
            ]
            rows.append(row)
        self.env['infrastructure.database.backup'].load(imp_fields, rows)
        # remove removed backups
        self_backups = [x.name for x in self.backup_ids]
        remote_backups = [x['name'] for x in backups_data]
        removed_backups = list(set(self_backups) - set(remote_backups))
        self.backup_ids.search([('name', 'in', removed_backups)]).unlink()

# Modules management
    @api.multi
    def upload_partners_uuid(self):
        self.ensure_one()
        client = self.get_client()
        # TODO we should update this in other place
        remote_contract = client.model('support.contract')
        talkusID = self.env['ir.config_parameter'].get_param(
            "support.server.talkusID", False)
        talkus_image_url = self.env['ir.config_parameter'].get_param(
            "support.server.talkus_image_url", False)
        remote_contract.write(remote_contract.search([]), {
            'talkusID': talkusID,
            'talkus_image_url': talkus_image_url,
        })
        for user in self.user_ids:
            partner = user.partner_id
            if partner and user.login:
                if not partner.support_uuid:
                    partner.support_uuid = str(uuid.uuid1())
                remote_user_id = client.model('res.users').search(
                    [('login', '=', user.login)], limit=1)
                client.model('res.users').write(remote_user_id, {
                    'remote_partner_uuid': partner.support_uuid})

    @api.multi
    def update_users_data(self):
        self.ensure_one()
        client = self.get_client()
        fields = [
            'name',
            'login',
            'email',
        ]

        _logger.info('Reading users data for db %s' % self.name)
        exp_users_data = client.model('res.users').search_read([], fields)
        update_users = self.env['infrastructure.database.user']
        _logger.info('Loading users data for db %s' % self.name)
        for user_data in exp_users_data:
            # we dont wont or need id
            user_data.pop('id')
            db_user = self.user_ids.search([
                ('login', '=', user_data.get('login')),
                ('database_id', '=', self.id)], limit=1)
            if db_user:
                db_user.write(user_data)
            else:
                user_data['database_id'] = self.id
                db_user = db_user.create(user_data)
            update_users += db_user
        _logger.info('Removing old users data for db %s' % self.name)
        # remove users that has not been updated (they dont exist anymore)
        (self.user_ids - update_users).unlink()
        return True

# MAIL server and catchall configurations
    @api.one
    def upload_mail_server_config(self):
        if not self.smtp_server_id:
            raise Warning(_(
                'You must choose an SMTP server config in order to upload it'))
        rows = [[
            self.smtp_server_id.external_id,
            self.smtp_server_id.name,
            self.smtp_server_id.sequence,
            self.smtp_server_id.smtp_debug,
            self.smtp_server_id.smtp_encryption,
            self.smtp_server_id.smtp_host,
            self.smtp_server_id.smtp_pass,
            self.smtp_server_id.smtp_port,
            self.smtp_server_id.smtp_user,
        ]]
        imp_fields = [
            'id',
            'name',
            'sequence',
            'smtp_debug',
            'smtp_encryption',
            'smtp_host',
            'smtp_pass',
            'smtp_port',
            'smtp_user',
        ]
        client = self.get_client()
        try:
            mail_server_obj = client.model('ir.mail_server')
            return mail_server_obj.load(imp_fields, rows)

        except Exception, e:
            raise except_orm(
                _("Unable to Upload SMTP Config."),
                _('Error: %s') % e
            )

    @api.one
    def change_admin_passwd(self, current_passwd, new_passwd):
        client = self.get_client()
        try:
            user_obj = client.model('res.users')
            return user_obj.change_password(current_passwd, new_passwd)

        except Exception, e:
            raise except_orm(
                _("Unable to change password."),
                _('Error: %s') % e
            )

    @api.one
    def config_backups(self):
        self.server_id.get_env()
        client = self.get_client()
        modules = ['database_tools']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                raise Warning(_(
                    "You can not configure backups if module '%s' is not "
                    "installed in the database") % (module))

        # TODO habriq ue chequear que exista self_db_id
        # Configure backups
        self_db_id = client.model('ir.model.data').xmlid_to_res_id(
            'database_tools.db_self_database')
        if self.backups_enable:
            vals = {
                # we set next backup at a night
                'backup_next_date': datetime.strftime(
                    datetime.today() + relativedelta(days=1),
                    '%Y-%m-%d 05:%M:%S'),
                'backups_path': os.path.join(
                    self.instance_id.backups_path, self.name),
                'syncked_backup_path': os.path.join(
                    self.instance_id.syncked_backup_path, self.name),
                'backup_format': self.backup_format
            }
            client.model('db.database').write([self_db_id], vals)
        client.model('db.database').backups_state(
            self.name, self.backups_enable)

    @api.one
    def config_catchall(self):
        self.server_id.get_env()
        client = self.get_client()

        modules = ['auth_server_admin_passwd_passkey', 'mail']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                raise Warning(_(
                    "You can not configure catchall if module '%s'"
                    " is not installed in the database") % (module))
        if not self.local_alias:
            raise Warning(_(
                "You can not configure catchall if Local Alias is "
                "not set. Probably this is because Mailgate File was not "
                "found"))
        if not exists(self.mailgate_path, use_sudo=True):
            raise Warning(_(
                "Mailgate file was not found on mailgate path '%s' base path "
                "found for mail module") % (
                self.mailgate_path))
        # Configure domain_alias on databas
        client.model('ir.config_parameter').set_param(
            "mail.catchall.domain", self.domain_alias or '')

        # clean and append virtual_alias
        if exists(self.server_id.virtual_alias_path, use_sudo=True):
            sed(
                self.server_id.virtual_alias_path,
                '@%s.*' % self.domain_alias, '', use_sudo=True, backup='.bak')
        append(
            self.server_id.virtual_alias_path,
            self.virtual_alias, use_sudo=True, partial=True)

        # clean and append virtual_alias
        if exists(self.server_id.local_alias_path, use_sudo=True):
            sed(
                self.server_id.local_alias_path,
                '%s.*' % self.domain_alias, '', use_sudo=True, backup='.bak')
        append(
            self.server_id.local_alias_path,
            self.local_alias, use_sudo=True)
        sudo('postmap /etc/postfix/virtual_aliases')
        sudo('newaliases')
        sudo('/etc/init.d/postfix restart')

    @api.multi
    def action_to_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_activate(self):
        self.write({'state': 'active'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_inactive(self):
        self.write({'state': 'inactive'})
