# -*- coding: utf-8 -*-
from openerp import models, fields, api, SUPERUSER_ID, netsvc, _
from openerp.exceptions import except_orm
import xmlrpclib
from dateutil.relativedelta import relativedelta
from datetime import datetime
from fabric.api import sudo
from fabric.contrib.files import exists, append, sed
from os import path
from erppeek import Client
from openerp.exceptions import Warning
from ast import literal_eval
import os


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

    database_type_id = fields.Many2one(
        'infrastructure.database_type',
        string='Database Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange'
    )

    name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange'
    )

    partner_id = fields.Many2one(
        'res.partner',
        string='Partner'
    )

    demo_data = fields.Boolean(
        string='Demo Data?',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    note = fields.Html(
        string='Note'
    )

    color = fields.Integer(
        string='Color Index'
    )

    smtp_server_id = fields.Many2one(
        'infrastructure.mailserver',
        string='SMTP Server'
    )

    domain_alias = fields.Char(
        string='Domain Alias',
        compute='get_domain_alias',
    )

    attachment_loc_type = fields.Selection(
        [(u'filesystem', 'filesystem'), (u'database', 'database')],
        string='Attachment Location Type',
        default='filesystem'
    )

    attachment_location = fields.Char(
        string='Attachment Location'
    )

    issue_date = fields.Date(
        string='Issue Data'
    )

    deactivation_date = fields.Date(
        string='Deactivation Date'
    )

    state = fields.Selection(
        _states_,
        'State',
        default='draft'
    )

    db_backup_policy_ids = fields.Many2many(
        'infrastructure.db_backup_policy',
        'infrastructure_database_ids_db_backup_policy_ids_rel',
        'database_id',
        'db_backup_policy_id',
        string='Suggested Backup Policies'
    )

    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='Instance',
        ondelete='cascade',
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=True
    )

    environment_id = fields.Many2one(
        'infrastructure.environment',
        string='Environment',
        related='instance_id.environment_id',
        store=True,
        readonly=True
    )

    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        related='instance_id.environment_id.server_id',
        store=True,
        readonly=True
    )

    protected_db = fields.Boolean(
        string='Protected DB?',
        related='database_type_id.protect_db',
        store=True,
        readonly=True
    )

    color = fields.Integer(
        string='Color',
        related='database_type_id.color',
        store=True,
        readonly=True
    )

    deactivation_date = fields.Date(
        string='Deactivation Date',
        compute='get_deact_date',
        store=True,
        readonly=False
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

    @api.model
    def _get_base_modules(self):
        base_modules = self.env['infrastructure.base.module'].search([
            ('default_on_new_db', '=', True)])
        return [(6, _, base_modules.ids)]

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
        required=True,
        default='admin',
        deprecated=True,  # we use server admin pass to autheticate now
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
        'Alias Prefix'
    )

    alias_hostname_id = fields.Many2one(
        'infrastructure.server_hostname',
        string='Alias Hostname',
    )

    alias_hostname_wildcard = fields.Boolean(
        related='alias_hostname_id.wildcard',
        string='Wildcard?',
    )

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
            ('environment_id', '=', self.instance_id.environment_id.id)],)
        mailgate_path = _('Not base path found for mail module')
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
                SUPERUSER_ID, self.instance_id.admin_pass, self._cr.dbname)
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
            self.db_backup_policy_ids = self.database_type_id.db_backup_policy_ids

    @api.one
    @api.depends('database_type_id', 'issue_date')
    def get_deact_date(self):
        deactivation_date = False
        if self.issue_date and self.database_type_id.auto_deactivation_days:
            deactivation_date = (datetime.strptime(
                self.issue_date, '%Y-%m-%d') + relativedelta(
                days=self.database_type_id.auto_deactivation_days))
        self.deactivation_date = deactivation_date
# DATABASE CRUD

    @api.one
    def get_sock(self):
        # base_url = self.instance_id.environment_id.server_id.main_hostname
        base_url = self.instance_id.main_hostname
        server_port = 80
        # server_port = self.instance_id.xml_rpc_port
        rpc_db_url = 'http://%s:%d/xmlrpc/db' % (base_url, server_port)
        return xmlrpclib.ServerProxy(rpc_db_url)

    @api.one
    def create_db(self):
        client = self.get_client(not_database=True)
        client.create_database(
            self.instance_id.admin_pass,
            self.name,
            demo=self.demo_data,
            lang='en_US',
            user_password='admin')
        client = self.get_client()
        self.update_modules_data()
        self.signal_workflow('sgn_to_active')

    @api.one
    def drop_db(self):
        sock = self.get_sock()[0]
        try:
            sock.drop(self.instance_id.admin_pass, self.name)
        except:
            raise Warning(
                _('Unable to drop Database. If you are working in an \
                    instance with "workers" then you can try \
                    restarting service.'))
        self.signal_workflow('sgn_cancel')

    @api.one
    def dump_db(self):
        raise Warning(_('Not Implemented yet'))
        # TODO arreglar esto para que devuelva el archivo y lo descargue
        sock = self.get_sock()[0]
        try:
            return sock.dump(self.instance_id.admin_pass, self.name)
        except:
            raise Warning(
                _('Unable to dump Database. If you are working in an \
                    instance with "workers" then you can try \
                    restarting service.'))

    @api.one
    def duplicate_db(self, new_database_name):
        new_db = self.copy({'name': new_database_name})
        sock = self.get_sock()[0]
        try:
            sock.duplicate_database(
                self.instance_id.admin_pass, self.name, new_database_name)
        except:
            raise Warning(
                _('Unable to duplicate Database. If you are working in \
                    an instance with "workers" then you can try \
                    restarting service.'))
        new_db.signal_workflow('sgn_to_active')
        # TODO retornar accion de ventana a la bd creada

    @api.one
    def kill_db_connection(self):
        self.server_id.get_env()
        psql_command = "/SELECT pg_terminate_backend(pg_stat_activity.procpid)\
         FROM pg_stat_activity WHERE pg_stat_activity.datname = '"
        psql_command += self.name + " AND procpid <> pg_backend_pid();"
        sudo('psql -U postgres -c ' + psql_command)

# Database connection helper
    @api.multi
    def get_client(self, not_database=False):
        self.ensure_one()
        try:
            if not_database:
                return Client(
                    'http://%s:%d' % (self.instance_id.main_hostname, 80))
            return Client(
                'http://%s:%d' % (self.instance_id.main_hostname, 80),
                db=self.name,
                user='admin',
                password=self.instance_id.admin_pass)
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
    def config_catchall(self):
        self.server_id.get_env()
        client = self.get_client()
        modules = ['auth_server_admin_passwd_passkey', 'mail']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
            # if module not in client.modules(name=module,
            # installed=True)['installed']:
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
    # TODO implementar cambio de usuario de postgres al duplicar una bd o de manera manual.
    # Al parecer da error por el parametro que se alamcena database.uuid
    # Para eso podemos ver todo el docigo que esta en db.py, sobre todo esta parte:
    #     registry = openerp.modules.registry.RegistryManager.new(db)
    #     with registry.cursor() as cr:
    #         if copy:
    # if it's a copy of a database, force generation of a new dbuuid
    #             registry['ir.config_parameter'].init(cr, force=True)
    #         if filestore_path:
    #             filestore_dest = registry['ir.attachment']._filestore(cr, SUPERUSER_ID)
    #             shutil.move(filestore_path, filestore_dest)

    #         if openerp.tools.config['unaccent']:
    #             try:
    #                 with cr.savepoint():
    #                     cr.execute("CREATE EXTENSION unaccent")
    #             except psycopg2.Error:
    #                 pass

# DATABASE back ups
    def _cron_db_backup(self, cr, uid, policy, context=None):
        """"""
        # Search for the backup policy having 'policy' as backup prefix
        backup_policy_obj = self.pool['infrastructure.db_backup_policy']
        backup_policy_id = backup_policy_obj.search(
            cr, uid, [('backup_prefix', '=', policy)], context=context)[0]

        # Search for databases using that backup policy
        backup_policy = backup_policy_obj.browse(
            cr, uid, backup_policy_id, context=None)
        databases = backup_policy.database_ids

        # Backup each database
        for database in databases:
            database.backup_now(backup_policy_id)

    @api.one
    def action_backup_now(self):
        return self.backup_now()

    @api.one
    def backup_now(self, backup_policy_id=False):
        """"""
        now = datetime.now().strftime('%Y%m%d_%H%M%S')

        if not backup_policy_id:
            policy_name = 'manual'
        else:
            backup_policy = self.env['infrastructure.db_backup_policy'].search(
                [('id', '=', backup_policy_id)])
            policy_name = backup_policy.backup_prefix

        dump_name = '%s_%s_%s.sql' % (policy_name, self.name, now)

        backups_path = self.instance_id.environment_id.backups_path

        dump_file = path.join(backups_path, dump_name)

        cmd = 'pg_dump %s --format=c --compress 9 --file=%s' % (
            self.name,
            dump_file
        )

        values = {
            'database_id': self.id,
            'name': dump_name,
            'create_date': datetime.now(),
            'db_backup_policy_id': backup_policy_id
        }

        try:
            self.server_id.get_env()
            user = self.instance_id.user

            if not exists(backups_path, use_sudo=True):
                sudo(
                    'mkdir -m a=rwx -p ' + backups_path, user=user, group='odoo')

            sudo(cmd, user='postgres')
            self.backup_ids.create(values)
            self.message_post(
                subject=_('Backup Status'),
                body=_('Completed Successfully'),
                type='comment',
                subtype='mt_backup_ok'
            )

        except Exception, e:
            if policy_name == 'manual':
                raise except_orm(
                    _("Unable to backup '%s' database") % self.name,
                    _('Command output: %s') % e
                )
            else:
                self.message_post(
                    subject=_('Backup Status'),
                    body=_('Backup Failed: %s' % e),
                    type='notification',
                    subtype='mt_backup_fail'
                )

        except SystemExit:
            if policy_name == 'manual':
                raise except_orm(
                    _("Unable to backup '%s' database") % self.name,
                    _('Unknown System Error')
                )
            else:
                self.message_post(
                    subject=_('Backup Status'),
                    body=_('Backup Failed: Unknown System Error'),
                    type='notification',
                    subtype='mt_backup_fail'
                )

# WORKFLOW
    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.database', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.database', obj_id, cr)
        return True
