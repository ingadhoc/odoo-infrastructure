# -*- coding: utf-8 -*-
from openerp import models, fields, api, SUPERUSER_ID, netsvc, _
from openerp.exceptions import except_orm
import xmlrpclib, socket
from dateutil.relativedelta import relativedelta
from datetime import datetime
from fabric.api import sudo
from fabric.contrib.files import exists, append, sed
from os import path
from erppeek import Client
from openerp.exceptions import Warning
from ast import literal_eval
import os
import base64
import logging
import fabtools
_logger = logging.getLogger(__name__)


class database(models.Model):

    """"""
    # TODO agregar campos calculados
    # Cantidad de usuarios
    # Modulos instalados
    # Ultimo acceso
    _name = 'infrastructure.database'
    _description = 'database'
    _inherit = ['ir.needaction_mixin', 'mail.thread']
    _states_ = [
        ('draft', 'Draft'),
        ('maintenance', 'Maintenance'),
        ('active', 'Active'),
        ('deactivated', 'Deactivated'),
        ('cancel', 'Cancel'),
    ]

    _mail_post_access = 'read'

    _track = {
        'state': {
            'infrastructure.database_draft':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'infrastructure.database_maintenance':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'maintenance',
            'infrastructure.database_active':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active',
            'infrastructure.database_deactivated':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'deactivated',
            'infrastructure.database_cancel':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }

    @api.model
    def _get_base_modules(self):
        base_modules = self.env['infrastructure.base.module'].search([
            ('default_on_new_db', '=', True)])
        return [(6, _, base_modules.ids)]

    database_type_id = fields.Many2one(
        'infrastructure.database_type',
        string='Database Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
        copy=False,
    )
    name = fields.Char(
        string='Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange'
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
        # readonly=True,
        # states={'draft': [('readonly', False)]},
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
    protected_db = fields.Boolean(
        string='Protected DB?',
        related='database_type_id.protect_db',
        store=True,
        readonly=True,
    )
    color = fields.Integer(
        string='Color',
        related='database_type_id.color',
        store=True,
        readonly=True,
    )
    backup_ids = fields.One2many(
        'infrastructure.database.backup',
        'database_id',
        string='Backups',
    )
    module_ids = fields.One2many(
        'infrastructure.database.module',
        'database_id',
        string='Modules',
    )
    base_module_ids = fields.Many2many(
        'infrastructure.base.module',
        'infrastructure_database_ids_base_module_rel',
        'database_id',
        'base_module_id',
        string='Base Modules',
        default=_get_base_modules,
    )
    admin_password = fields.Char(
        string='Admin Password',
        help='When trying to connect to the database first we are going to try by using the instance password and then with thisone.',
        # required=True,
        default='admin',
        readonly=True,
        states={'draft': [('readonly', False)]},
        # deprecated=True,  # we use server admin pass to autheticate now
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
        # readonly=True,
        # states={'draft': [('readonly', False)]},
        copy=False,
    )

    alias_hostname_id = fields.Many2one(
        'infrastructure.server_hostname',
        string='Alias Hostname',
        # readonly=True,
        # states={'draft': [('readonly', False)]},
        copy=False,
    )
    alias_hostname_wildcard = fields.Boolean(
        related='alias_hostname_id.wildcard',
        string='Wildcard?',
        readonly=True,
        copy=False,
    )
    module_count = fields.Integer(
        string='# Modules',
        compute='_get_modules',
    )
    daily_backup = fields.Boolean(
        string='Daily Backups?',
    )
    weekly_backup = fields.Boolean(
        string='Weekly Backups?',
    )
    monthly_backup = fields.Boolean(
        string='Monthly Backups?',
    )
    backups_enable = fields.Boolean(
        'Backups Enable',
        copy=False,
    )
    catchall_enable = fields.Boolean(
        'Catchall Enable',
        copy=False,
    )

    @api.one
    @api.onchange('instance_id')
    def _onchange_instance(self):
        self.partner_id = self.instance_id.environment_id.partner_id

    @api.one
    @api.depends('module_ids')
    def _get_modules(self):
        self.module_count = len(self.module_ids)

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
    @api.depends()
    def get_mailgate_path(self):
        env_rep = self.env['infrastructure.environment_repository'].search([
            ('server_repository_id.repository_id.is_server', '=', True),
            ('environment_id', '=', self.instance_id.environment_id.id)])
        mailgate_path = _('Not base path found for mail module')
        if env_rep.addons_paths:
            for path in literal_eval(env_rep.addons_paths):
                if 'openerp' not in path and 'addons'in path:
                    mailgate_path = os.path.join(
                        path, 'mail/static/scripts/openerp_mailgate.py')
        self.mailgate_path = mailgate_path

    @api.one
    @api.depends()
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
            local_alias = '%s: "| %s  --host=localhost --port=%i -u %i -p %s -d %s' % (
                self.domain_alias, self.mailgate_path,
                self.instance_id.xml_rpc_port,
                SUPERUSER_ID, self.instance_id.admin_pass, self.name)
        return local_alias

    _sql_constraints = [
        ('name_uniq', 'unique(name, server_id)',
            'Database Name Must be Unique per server'),
        ('domain_alias_uniq', 'unique(domain_alias)',
            'Domain Alias Must be Unique'),
    ]

    @api.one
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise Warning(
                _('You cannot delete a database which is not draft \
                    or cancelled.'))
        return super(database, self).unlink()

    @api.onchange('database_type_id')
    def onchange_database_type_id(self):
        if self.database_type_id:
            self.name = self.database_type_id.prefix + '_'
            # TODO send suggested backup data

    @api.one
    @api.onchange('database_type_id', 'issue_date')
    def get_deact_date(self):
        deactivation_date = False
        if self.issue_date and self.database_type_id.auto_deactivation_days:
            deactivation_date = (datetime.strptime(
                self.issue_date, '%Y-%m-%d') + relativedelta(
                days=self.database_type_id.auto_deactivation_days))
        self.deactivation_date = deactivation_date

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
        rpc_db_url = 'http://%s/xmlrpc/%s' % (base_url, service)
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
                # connected to the server and the method doesn't exist which is expected.
                _logger.info("Connected to socket")
                connected = True
                pass
            except socket.error:
                _logger.info("Could not connect to socket")
                pass
            except:
                # Tuve que agregar este porque el error no me era atrapado arriba
                _logger.info("Connecting3")
                pass
        if not connected:
            raise Warning(_("Could not connect to socket '%s'") % (rpc_db_url))
        return sock

    @api.one
    def create_db(self):
        """Funcion que utliza erpeek para crear bds"""
        client = self.get_client(not_database=True)
        client.create_database(
            self.instance_id.admin_pass,
            self.name,
            demo=self.demo_data,
            lang='en_US',
            user_password=self.admin_password or 'admin')
        client = self.get_client()
        self.update_modules_data()
        self.signal_workflow('sgn_to_active')

    @api.one
    def drop_db(self):
        """Funcion que utiliza ws nativos de odoo para eliminar db"""
        sock = self.get_sock()
        try:
            sock.drop(self.instance_id.admin_pass, self.name)
        except:
            # If we get an error we try restarting the service
            try:
                self.instance_id.restart_service()
                # we ask again for sock and try to connect waiting for service start
                sock = self.get_sock(max_attempts=1000)
                sock.drop(self.instance_id.admin_pass, self.name)
            except Exception, e:
                raise Warning(
                    _('Unable to drop Database. If you are working in an \
                    instance with "workers" then you can try \
                    restarting service. This is what we get:\n%s') % (e))
        self.signal_workflow('sgn_cancel')

    @api.one
    def dump_db(self):
        """Funcion que utiliza ws nativos de odoo para hacer backup de bd"""
        raise Warning(_('Not Implemented yet'))
        # TODO arreglar esto para que devuelva el archivo y lo descargue
        sock = self.get_sock()
        try:
            backup_file = open('backup.dump', 'wb')
            backup_file.write(base64.b64decode(
                sock.dump(self.instance_id.admin_pass, self.name)))
            # return sock.dump(self.instance_id.admin_pass, self.name)
            backup_file.close()
        except:
            raise Warning(
                _('Unable to dump Database. If you are working in an \
                    instance with "workers" then you can try \
                    restarting service.'))

    @api.one
    def migrate_db(self):
        """Funcion que utiliza ws nativos de odoo para hacer update de bd"""
        sock = self.get_sock()
        try:
            return sock.migrate_databases(
                self.instance_id.admin_pass, [self.name])
        except:
            raise Warning(
                _('Unable to migrate Database. If you are working in an \
                    instance with "workers" then you can try \
                    restarting service.'))

    @api.one
    def rename_db(self):
        """Funcion que utiliza ws nativos de odoo para hacer update de bd"""
        raise Warning(_('Not Implemented yet'))
        sock = self.get_sock()
        new_name = 'pepito'  # implementar esto
        try:
            return sock.rename(
                self.instance_id.admin_pass, self.name, new_name)
        except:
            raise Warning(
                _('Unable to Rename Database. If you are working in an \
                    instance with "workers" then you can try \
                    restarting service.'))

    @api.one
    def restore_db(self):
        """Funcion que utiliza ws nativos de odoo para hacer update de bd"""
        raise Warning(_('Not Implemented yet'))
        # TODO implementar
        sock = self.get_sock()
        f = file('/home/chosco/back/backup.dump', 'r')
        data_b64 = base64.encodestring(f.read())
        f.close()
        try:
            return sock.restore(
                self.instance_id.admin_pass, self.name, data_b64)
        except:
            raise Warning(
                _('Unable to migrate Database. If you are working in an \
                    instance with "workers" then you can try \
                    restarting service.'))

    @api.one
    def exist_db(self, database_name):
        """Funcion que utiliza ws nativos de odoo"""
        sock = self.get_sock()
        if sock.db_exist():
            return True
        else:
            return False

    @api.multi
    def duplicate_db(self, new_database_name, backups_enable, database_type):
        """Funcion que utiliza ws nativos de odoo para hacer duplicar bd"""
        self.ensure_one()
        sock = self.get_sock()
        client = self.get_client()
        new_db = self.copy({
            'name': new_database_name,
            'backups_enable': backups_enable,
            'issue_date': fields.Date.today(),
            'database_type_id': database_type.id,
            })
        try:
            sock.duplicate_database(
                self.instance_id.admin_pass, self.name, new_database_name)
            client.model('db.database').backups_state(
                new_database_name, backups_enable)
        except:
            # If we get an error we try duplicating restarting service without workers
            try:
                # TODO borrar esto. tratamos solo reiniciando pero da error
                # self.instance_id.restart_service()
                # sock = self.get_sock(max_attempts=100)
                # sock.duplicate_database(
                #     self.instance_id.admin_pass, self.name, new_database_name)
                # client.model('db.database').backups_state(
                #     new_database_name, backups_enable)
                # restart the instance without workers
                instance = self.instance_id
                instance.update_conf_file(force_no_workers=True)
                instance.start_service()
                # we ask again for sock and try to connect waiting for service start
                sock = self.get_sock(max_attempts=1000)
                sock.duplicate_database(
                    self.instance_id.admin_pass, self.name, new_database_name)
                client.model('db.database').backups_state(
                    new_database_name, backups_enable)
                # restart the instance with default config
                instance.update_conf_file()
                instance.start_service()
                # TODo agregar aca releer los modulos y demas en la nueva bd
            except Exception, e:
                raise Warning(
                    _('Unable to duplicate Database. This is what we get:\n%s') % (e))
        new_db.signal_workflow('sgn_to_active')

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
    #         raise Warning(
    #             _('Unable to duplicate Database. This is what we get:\n%s') % (e))
    #     new_db.signal_workflow('sgn_to_active')
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
                raise Warning(
                    _("You can not kill connections if module '%s' is not installed in the database") % (module))

        self_db_id = client.model('ir.model.data').xmlid_to_res_id(
            'database_tools.db_self_database')
        client.model('db.database').drop_con(self_db_id)

# Database connection helper
    @api.multi
    def get_client(self, not_database=False):
        self.ensure_one()
        try:
            if not_database:
                return Client(
                    'http://%s' % (self.instance_id.main_hostname))
        except Exception, e:
            raise except_orm(
                _("Unable to Connect to Database."),
                _('Error: %s') % e
            )
        # First try to connect using instance pass
        try:
            return Client(
                'http://%s' % (self.instance_id.main_hostname),
                db=self.name,
                user='admin',
                password=self.instance_id.admin_pass)
        # then try to connect using database pass
        except:
            try:
                return Client(
                    'http://%s' % (self.instance_id.main_hostname),
                    db=self.name,
                    user='admin',
                    password=self.admin_password)
            except Exception, e:
                raise except_orm(
                    _("Unable to Connect to Database."),
                    _('Error: %s') % e
                )

# Modules management
    @api.one
    def install_base_modules(self):
        client = self.get_client()
        for module in self.base_module_ids:
            client.install(module.name)
        module_names = [x.name for x in self.base_module_ids]
        self.update_modules_data(
            modules_domain=[('name', 'in', module_names)])

    @api.one
    def action_update_modules_data(self):
        self.update_modules_data()

    def update_modules_data(self, modules_domain=None):
        if not modules_domain:
            modules_domain = []
        client = self.get_client()
        fields = [
            'sequence',
            'author',
            'auto_install',
            'installed_version',
            'latest_version',
            'published_version',
            'name',
            'shortdesc',
            'state']

        client.model('ir.module.module').update_list()
        modules_data = client.read(
            'ir.module.module', modules_domain, fields)

        modules_domain.append(('database_id', '=', self.id))
        self.env['infrastructure.database.module'].search(
            modules_domain).unlink()

        vals = {'database_id': self.id}
        for module in modules_data:
            for field in fields:
                vals[field] = module[field]
            self.env['infrastructure.database.module'].create(vals)

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
        fields = [
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
            return mail_server_obj.load(fields, rows)

        except Exception, e:
            raise except_orm(
                _("Unable to Upload SMTP Config."),
                _('Error: %s') % e
            )

    @api.one
    def config_backups(self):
        self.server_id.get_env()
        client = self.get_client()
        modules = ['database_tools']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                raise Warning(
                    _("You can not configure backups if module '%s' is not installed in the database") % (module))

        # Configure backups
        self_db_id = client.model('ir.model.data').xmlid_to_res_id(
            'database_tools.db_self_database')
        vals = {
            'backups_path': os.path.join(
                self.instance_id.environment_id.backups_path, self.name),
            'daily_backup': self.daily_backup,
            'weekly_backup': self.weekly_backup,
            'monthly_backup': self.monthly_backup,
        }
        client.model('db.database').write([self_db_id], vals)

    @api.one
    def config_catchall(self):
        self.server_id.get_env()
        client = self.get_client()
        modules = ['auth_server_admin_passwd_passkey', 'mail']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                raise Warning(
                    _("You can not configure catchall if module '%s' is not installed in the database") % (module))
        if not self.local_alias:
            raise Warning(
                _("You can not configure catchall if Local Alias is not set. Probably this is because Mailgate File was not found"))
        if not exists(self.mailgate_path, use_sudo=True):
            raise Warning(_("Mailgate file was not found on mailgate path '%s' base path found for mail module") % (
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

# WORKFLOW
    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.database', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.database', obj_id, cr)
        return True
