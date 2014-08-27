# -*- coding: utf-8 -*-

from openerp import models, fields, api, netsvc, _
import xmlrpclib
from dateutil.relativedelta import relativedelta
from datetime import datetime
from fabric.api import sudo


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
        string='Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
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

    alias_domain = fields.Char(
        string='Alias Domain'
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
        server_port = 80  # server_port = self.instance_id.xml_rpc_port
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
        except:
            raise Warning(_('Unable to create Database.'))
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

    @api.one
    def _cron_bd_backup(self):
        """ backup_policy_ids: Lista de back up policy que se referencia a este cron.
        Para cada back up policy:
            buscar las database_ids: lista de bases de datos con esas politicas de back up
            ejecutar "backup_now_db" pasando el 'backup_policy_id'
        """

    @api.one
    def backup_now_db(self, backup_policy_id=False):
        """
        Construir nombre_backup = '%s - %s - %s' % (backup_policy_prefix or 'manual', backup_name, now)
        Hacer back up con dicho nombre y en el path del environment
        Escribir un registro de "database.backup" con
            name = nombre_backup
            database_id = self.id
            database_id = self.id
            create_date = now
            db_backup_policy_id = backup_policy_id
        """
        # TODO implementar esto
        raise Warning(_('Not Implemented yet'))

    # def connect_to_openerp(self, cr, uid, inst_id, parameters, context=None):
    #     param = parameters
    #     base_url = param[inst_id]['base_url']
    #     server_port = int(param[inst_id]['server_port'])
    #     admin_name = param[inst_id]['admin_name']
    #     admin_pass = param[inst_id]['admin_pass']
    #     database = param[inst_id]['database']
    # domain = database + '.' + param[inst_id]['base_url']
    #     domain = base_url
    #     connection = openerplib.get_connection(hostname=domain, database=database, \
    #         login=admin_name, password=admin_pass, port=server_port)
    #     return connection

    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.database', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.database', obj_id, cr)
        return True

    # @api.one
    # def action_wfk_set_draft(self):

database()
