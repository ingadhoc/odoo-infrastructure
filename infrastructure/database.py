# -*- coding: utf-8 -*-

from openerp import models, fields, api, netsvc, _
from openerp.exceptions import except_orm
import xmlrpclib
from dateutil.relativedelta import relativedelta
from datetime import datetime
from fabric.api import sudo
from fabric.contrib.files import exists
from os import path


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
        string='Domain Alias'
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
        required=True
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
        readonly=False
    )

    admin_password = fields.Char(
        string='Admin Password',
        required=True,
        default='admin'
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, server_id)',
            'Database Name Must be Unique per server'),
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
        sock = self.get_sock()[0]
        new_db_name = self.name
        demo = self.demo_data
        user_password = 'admin'
        lang = False  # lang = 'en_US'

        try:
            sock.create_database(
                self.instance_id.admin_pass,
                new_db_name,
                demo,
                lang,
                user_password
            )
        except Exception, e:
            raise except_orm(
                _("Unable to create '%s' database") % new_db_name,
                _('Command output: %s') % e
            )
        self.signal_workflow('sgn_to_active')
        return True

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
    def change_admin_pass_db(self):
        pass
        # sock = self.get_sock()[0]
        # try:
            # sock.drop(self.instance_id.admin_pass, self.name)
        # except Exception, e:
            # raise except_orm(_("Unable to backup '%s' database") % e
            # print e
            # raise Warning(
            #     _('Unable to drop Database. If you are working in an \
            #         instance with "workers" then you can try \
            #         restarting service.'))
        # self.signal_workflow('sgn_cancel')

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
    def kill_db_connection(self):
        self.server_id.get_env()
        psql_command = "/SELECT pg_terminate_backend(pg_stat_activity.procpid)\
         FROM pg_stat_activity WHERE pg_stat_activity.datname = '"
        psql_command += self.name + " AND procpid <> pg_backend_pid();"
        sudo('psql -U postgres -c ' + psql_command)

    @api.one
    def upload_mail_server_config(self):
        # TODO implementar esta funcion
        raise Warning(_('Not Implemented yet'))

    @api.one
    def config_catchall(self):
        # TODO implementar esta funcion
        raise Warning(_('Not Implemented yet'))

    @api.one
    def apply_attachment_type(self):
        # TODO implementar esta funcion
        raise Warning(_('Not Implemented yet'))
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
                sudo('mkdir -m a=rwx -p ' + backups_path, user=user, group='odoo')

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

    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.database', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.database', obj_id, cr)
        return True
