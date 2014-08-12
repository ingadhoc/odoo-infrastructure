# -*- coding: utf-8 -*-

from openerp import netsvc
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from fabric.api import env, sudo, reboot


class server(models.Model):
    """"""

    _name = 'infrastructure.server'
    _description = 'server'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _states_ = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('cancel', 'Cancel'),
    ]

    _track = {
        'state': {
            'infrastructure.server_draft':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'infrastructure.server_active':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active',
            'infrastructure.server_cancel':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }

    name = fields.Char(
        string='Name',
        required=True
    )

    ip_address = fields.Char(
        string='IP Address',
        required=True
    )

    ssh_port = fields.Char(
        string='SSH Port',
        required=True
    )

    main_hostname = fields.Char(
        string='Main Hostname',
        required=True
    )

    user_name = fields.Char(
        string='User Name'
    )

    password = fields.Char(
        string='Password'
    )

    holder_id = fields.Many2one(
        'res.partner',
        string='Holder',
        required=True
    )

    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        required=True
    )

    user_id = fields.Many2one(
        'res.partner',
        string='Used By',
        required=True
    )

    software_data = fields.Html(
        string='Software Data'
    )

    hardware_data = fields.Html(
        string='Hardware Data'
    )

    contract_data = fields.Html(
        string='Contract Data'
    )

    note = fields.Html(
        string='Note'
    )

    base_path = fields.Char(
        string='Base path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/opt/odoo'
    )

    color = fields.Integer(
        string='Color Index'
    )

    sources_dir = fields.Char(
        string='Sources Directory',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/opt/odoo/sources'
    )

    service_dir = fields.Char(
        string='Service Directory',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/etc/init.d'
    )

    instance_user_group = fields.Char(
        string='Instance Users Group',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='odoo'
    )

    nginx_log_dir = fields.Char(
        string='Nginx Log Directory',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/var/log/nginx'
    )

    nginx_sites_path = fields.Char(
        string='Nginx Sites Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/etc/nginx/sites-enabled'
    )

    gdrive_account = fields.Char(
        string='Gdrive Account',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    gdrive_passw = fields.Char(
        string='Gdrive Password',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    gdrive_space = fields.Char(
        string='Gdrive Space'
    )

    open_ports = fields.Char(
        string='Open Ports'
    )

    requires_vpn = fields.Boolean(
        string='Requires VPN?'
    )

    state = fields.Selection(
        _states_,
        string="State",
        default='draft'
    )

    server_service_ids = fields.One2many(
        'infrastructure.server_service',
        'server_id',
        string='Services'
    )

    server_repository_ids = fields.One2many(
        'infrastructure.server_repository',
        'server_id',
        string='server_repository_ids'
    )

    hostname_ids = fields.One2many(
        'infrastructure.server_hostname',
        'server_id',
        string='Hostnames'
    )

    change_ids = fields.One2many(
        'infrastructure.server_change',
        'server_id',
        string='Changes'
    )

    environment_ids = fields.One2many(
        'infrastructure.environment',
        'server_id',
        string='Environments',
        context={'from_server': True}
    )

    server_configuration_id = fields.Many2one(
        'infrastructure.server_configuration',
        string='Server Config.',
        required=True
    )

    install_command_ids = fields.One2many(
        'infrastructure.server_configuration_command',
        string='Installation Commands',
        related="server_configuration_id.install_command_ids"
    )

    maint_command_ids = fields.One2many(
        'infrastructure.server_configuration_command',
        string='Maintenance Commands',
        related="server_configuration_id.maint_command_ids"
    )

    environment_count = fields.Integer(
        string='# Environment',
        compute='_get_environments'
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'Server Name must be unique!'),
    ]

    @api.one
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise Warning(_(
                'You cannot delete a server which is not draft or cancelled.'))
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
        env.user = self.user_name
        env.password = self.password
        env.host_string = self.main_hostname
        env.port = self.ssh_port
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
            raise except_orm(
                _('Could Not Restart Service!'),
                _("Check if service is installed!"))

    @api.multi
    def restart_nginx(self):
        self.get_env()
        try:
            sudo('service nginx restart')
        except:
            raise except_orm(
                _('Could Not Restart Service!'),
                _("Check if service is installed!"))


    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.server', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.server', obj_id, cr)
        return True


server()
