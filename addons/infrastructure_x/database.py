# -*- coding: utf-8 -*-
from openerp import osv, models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
import openerplib
import xmlrpclib
from dateutil.relativedelta import relativedelta
from datetime import datetime
# from fabric.api import local, settings, abort, run, cd, env, sudo
# import os
class database(models.Model):
    """"""
    # TODO agregar campos calculados
    # Cantidad de usuarios
    # Modulos instalados
    # Ultimo acceso
    _inherit = 'infrastructure.database'

    _sql_constraints = [
        ('name_uniq', 'unique(name, server_id)',
            'Database Name Must be Unique per server'),
    ]    
    server_id = fields.Many2one('infrastructure.server', string='Server', related='instance_id.environment_id.server_id', store=True, readonly=True,)
    protected_db = fields.Boolean(string='Protected DB?', related='database_type_id.protect_db', store=True, readonly=True,)
    color = fields.Integer(string='Color', related='database_type_id.color', store=True, readonly=True,)
    deactivation_date = fields.Date(string='Deactivation Date', compute='get_deact_date', store=True, readonly=False,)

    @api.one
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise Warning(_('You cannot delete a database which is not draft or cancelled.'))
        return super(database, self).unlink()
    
    @api.onchange('database_type_id')
    def onchange_database_type_id(self):
        if self.database_type_id:
            self.name = self.database_type_id.prefix + '_'
            self.db_back_up_policy_ids = self.database_type_id.db_back_up_policy_ids

    @api.one
    @api.depends('database_type_id','issue_date')
    def get_deact_date(self):
        deactivation_date = False
        if self.issue_date and self.database_type_id.auto_deactivation_days:
            deactivation_date = (datetime.strptime(self.issue_date, '%Y-%m-%d') + relativedelta(days=self.database_type_id.auto_deactivation_days))
        self.deactivation_date = deactivation_date

    @api.one
    def get_sock(self):
        base_url = self.instance_id.main_hostname # base_url = self.instance_id.environment_id.server_id.main_hostname
        server_port = 80 # server_port = self.instance_id.xml_rpc_port
        rpc_db_url = 'http://%s:%d/xmlrpc/db' % (base_url, server_port)
        return xmlrpclib.ServerProxy(rpc_db_url)

    @api.one
    def create_db(self):
        sock = self.get_sock()[0]
        new_db_name = self.name
        demo = self.demo_data
        user_password = 'admin'
        lang = False # lang = 'en_US'

        try:
            sock.create_database(self.instance_id.admin_pass, new_db_name, demo, lang, user_password)
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
            raise Warning(_('Unable to drop Database. If you are working in an instance with "workers" then you can try restarting service.'))
        self.signal_workflow('sgn_cancel')
        

    @api.one
    def dump_db(self):
        raise Warning(_('Not Implemented yet'))
        # TODO arreglar esto para que devuelva el archivo y lo descargue
        sock = self.get_sock()[0]
        try:
            return sock.dump(self.instance_id.admin_pass, self.name)
        except:
            raise Warning(_('Unable to dump Database. If you are working in an instance with "workers" then you can try restarting service.'))

    @api.one
    def kill_db_connection(self):
        self.server_id.get_env()
        psql_command = "/SELECT pg_terminate_backend(pg_stat_activity.procpid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '" 
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
    #             # if it's a copy of a database, force generation of a new dbuuid
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
            sock.duplicate_database(self.instance_id.admin_pass, self.name, new_database_name)
        except:
            raise Warning(_('Unable to duplicate Database. If you are working in an instance with "workers" then you can try restarting service.'))
        new_db.signal_workflow('sgn_to_active')
        # TODO retornar accion de ventana a la bd creada
    
    @api.one
    def back_up_now_db(self):
        # TODO implementar esto
        raise Warning(_('Not Implemented yet'))

    # def connect_to_openerp(self, cr, uid, inst_id, parameters, context=None):
    #     param = parameters
    #     base_url = param[inst_id]['base_url']
    #     server_port = int(param[inst_id]['server_port'])
    #     admin_name = param[inst_id]['admin_name']
    #     admin_pass = param[inst_id]['admin_pass']
    #     database = param[inst_id]['database']
    #     #domain = database + '.' + param[inst_id]['base_url']
    #     domain = base_url
    #     connection = openerplib.get_connection(hostname=domain, database=database, \
    #         login=admin_name, password=admin_pass, port=server_port)
    #     return connection