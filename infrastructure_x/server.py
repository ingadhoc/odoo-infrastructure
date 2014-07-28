# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
# from openerp.osv import osv, fields
from fabric.api import local, settings, abort, run, cd, env, sudo, reboot

class server(models.Model):
    """"""
    
    _inherit = 'infrastructure.server'

    install_command_ids = fields.One2many('infrastructure.server_configuration_command',
        string='Installation Commands', related="server_configuration_id.install_command_ids")

    maint_command_ids = fields.One2many('infrastructure.server_configuration_command',
        string='Maintenance Commands', related="server_configuration_id.maint_command_ids")
    
    environment_count = fields.Integer(string='# Environment', compute='_get_environments',)

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'Server Name must be unique!'),
    ]

    @api.one
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise Warning(_('You cannot delete a server which is not draft or cancelled.'))
        return super(server, self).unlink()

    @api.one
    @api.depends('environment_ids')
    def _get_environments(self):
        self.environment_count = len(self.environment_ids)

    @api.one
    def get_env(self):
        if not self.user_name:    
            raise Warning(_('Not User Defined for the server'))        
        if not self.password:    
            raise Warning(_('Not Password Defined for the server'))        
        env.user=self.user_name
        env.password=self.password
        env.host_string=self.main_hostname
        env.port=self.ssh_port    
        return env

    @api.multi
    def reboot_server(self):
        self.get_env()
        reboot()

    @api.multi
    def restart_postgres(self):
        self.get_env()
        try:
            sudo('service postgres restart')
        except:
            raise except_orm(_('Could Not Restart Service!'), 
                _("Check if service is installed!"))
    @api.multi
    def restart_nginx(self):
        self.get_env()
        try:
            sudo('service nginx restart')
        except:
            raise except_orm(_('Could Not Restart Service!'), 
                _("Check if service is installed!"))
