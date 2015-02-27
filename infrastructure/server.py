# -*- coding: utf-8 -*-
from openerp import netsvc
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from fabric.api import env, reboot
# from fabric.api import env, sudo, reboot
# utilizamos nuestro custom sudo que da un warning
# import custom_sudo as sudo
from fabric.contrib.files import append
# For postfix
from fabric.api import *
from fabtools.deb import is_installed, preseed_package, install
from fabtools.require.service import started
import logging
_logger = logging.getLogger(__name__)


def custom_sudo(command, user=False):
    env.warn_only = True
    if user:
        res = sudo(command, user=user)
    else:
        res = sudo(command)
    env.warn_only = False
    if res.failed:
        raise Warning(_(
            "Can not run command:\n%s\nThis is what we get:\n%s") % (
            res.real_command, res.stdout))
    return res


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
        required=True,
    )

    ip_address = fields.Char(
        string='IP Address',
        required=True,
    )

    ssh_port = fields.Char(
        string='SSH Port',
        required=True,
        default=22,
    )

    main_hostname = fields.Char(
        string='Main Hostname',
        required=True,
    )

    user_name = fields.Char(
        string='User Name',
        required=True,
    )

    password = fields.Char(
        string='Password',
        required=True,
    )

    holder_id = fields.Many2one(
        'res.partner',
        string='Holder',
        required=True,
    )

    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        required=True,
    )

    used_by_id = fields.Many2one(
        'res.partner',
        string='Used By',
        required=True,
    )

    database_ids = fields.One2many(
        'infrastructure.database',
        'server_id',
        string='Databases',
    )

    database_count = fields.Integer(
        string='# Databases',
        compute='_get_databases',
    )

    instance_ids = fields.One2many(
        'infrastructure.instance',
        'server_id',
        string='Databases',
    )

    instance_count = fields.Integer(
        string='# Instances',
        compute='_get_instances',
    )

    software_data = fields.Html(
        string='Software Data',
    )

    hardware_data = fields.Html(
        string='Hardware Data',
    )

    contract_data = fields.Html(
        string='Contract Data',
    )

    note = fields.Html(
        string='Note',
    )

    base_path = fields.Char(
        string='Base path',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='/opt/odoo',
    )

    color = fields.Integer(
        string='Color Index',
    )

    sources_path = fields.Char(
        string='Sources Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/opt/odoo/sources',
    )

    service_path = fields.Char(
        string='Service Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/etc/init.d',
    )

    instance_user_group = fields.Char(
        string='Instance Users Group',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='odoo',
    )

    nginx_log_path = fields.Char(
        string='Nginx Log Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/var/log/nginx',
    )

    nginx_sites_path = fields.Char(
        string='Nginx Sites Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/etc/nginx/sites-enabled',
    )

    nginx_sites_path = fields.Char(
        string='Nginx Sites Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/etc/nginx/sites-enabled',
    )

    postgres_superuser = fields.Char(
        string='Postgres Superuser',
        help="Postgres Superuser. You can record and existing one or create a new one with an installation command",
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='odoo',
    )

    postgres_superuser_pass = fields.Char(
        string='Postgres Superuser Pwd',
        help="Postgres Superuser Password. You can record and existing one or create a new one with an installation command",
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    gdrive_account = fields.Char(
        string='Gdrive Account',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    gdrive_passw = fields.Char(
        string='Gdrive Password',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    gdrive_space = fields.Char(
        string='Gdrive Space',
    )

    open_ports = fields.Char(
        string='Open Ports',
    )

    requires_vpn = fields.Boolean(
        string='Requires VPN?',
    )

    state = fields.Selection(
        _states_,
        string="State",
        default='draft',
    )

    server_service_ids = fields.One2many(
        'infrastructure.server_service',
        'server_id',
        string='Services',
    )

    server_repository_ids = fields.One2many(
        'infrastructure.server_repository',
        'server_id',
        string='server_repository_ids',
    )

    hostname_ids = fields.One2many(
        'infrastructure.server_hostname',
        'server_id',
        string='Hostnames',
    )

    change_ids = fields.One2many(
        'infrastructure.server_change',
        'server_id',
        string='Changes',
    )

    environment_ids = fields.One2many(
        'infrastructure.environment',
        'server_id',
        string='Environments',
        context={'from_server': True},
    )

    server_configuration_id = fields.Many2one(
        'infrastructure.server_configuration',
        string='Server Config.',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    install_command_ids = fields.One2many(
        'infrastructure.server_configuration_command',
        string='Installation Commands',
        related="server_configuration_id.install_command_ids",
    )

    maint_command_ids = fields.One2many(
        'infrastructure.server_configuration_command',
        string='Maintenance Commands',
        related="server_configuration_id.maint_command_ids",
    )

    environment_count = fields.Integer(
        string='# Environment',
        compute='_get_environments',
    )

    local_alias_path = fields.Char(
        string='Local Aliases Path',
        help='Local Alias Path For Catch All Configuration',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='/etc/aliases',
    )

    virtual_alias_path = fields.Char(
        string='Virtual Aliases Path',
        readonly=True,
        required=True,
        help='Virtual Alias Path For Postfix Catch All Configuration',
        states={'draft': [('readonly', False)]},
        default='/etc/postfix/virtual_aliases',
    )

    virtual_domains_regex_path = fields.Char(
        string='Virtual Domain Regex Path',
        readonly=True,
        required=True,
        help='Virtual Domain Regex Path For Postfix Catch All Configuration',
        states={'draft': [('readonly', False)]},
        default='/etc/postfix/virtual_domains_regex',
    )

    postfix_hostname = fields.Char(
        string='Postfix Hostname',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name)',
            'Server Name must be unique!'),
    ]

    @api.one
    @api.onchange('main_hostname')
    def change_main_hostname(self):
        if not self.postfix_hostname:
            self.postfix_hostname = self.main_hostname

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
    @api.depends('database_ids')
    def _get_databases(self):
        self.database_count = len(self.database_ids)

    @api.one
    @api.depends('instance_ids')
    def _get_instances(self):
        self.instance_count = len(self.instance_ids)

    @api.one
    def get_env(self):
        if not self.user_name:
            raise Warning(_('Not User Defined for the server'))
        if not self.password:
            raise Warning(_('Not Password Defined for the server'))
        env.user = self.user_name
        # env.warn_only = True
        # env.warn_only = False
        env.password = self.password
        env.host_string = self.main_hostname
        env.port = self.ssh_port
        return env

    @api.one
    def show_passwd(self):
        raise except_orm(
            _("Password for user '%s':") % self.user_name,
            _("%s") % self.password
        )

    @api.one
    def show_pg_passwd(self):
        raise except_orm(
            _("Password for pg user '%s':") % self.postgres_superuser,
            _("%s") % self.postgres_superuser_pass
        )

    @api.multi
    def reboot_server(self):
        self.get_env()
        reboot()

    @api.multi
    def restart_postgres(self):
        self.get_env()
        try:
            custom_sudo('service postgres restart')
        except:
            raise except_orm(
                _('Could Not Restart Service!'),
                _("Check if service is installed!"))

    @api.multi
    def restart_nginx(self):
        _logger.info("Restarting nginx")
        self.get_env()
        try:
            custom_sudo('service nginx restart')
        except:
            raise except_orm(
                _('Could Not Restart Service!'),
                _("Check if service is installed!"))

    @api.multi
    def reload_nginx(self):
        _logger.info("Reloading nginx")
        self.get_env()
        try:
            custom_sudo('nginx -s reload')
        except:
            raise except_orm(
                _('Could Not Reload Service!'),
                _("Check if service is installed!"))

    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.server', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.server', obj_id, cr)
        return True

    @api.one
    def add_to_virtual_domains(self):
        self.get_env()
        # TODO remove this
        # booelan values as unaccent
        # if exists(self.virtual_domains_regex_path, use_sudo=True):
        #     sudo('rm ' + self.virtual_domains_regex_path)
        for domain in self.hostname_ids:
            append(
                self.virtual_domains_regex_path,
                domain.domain_regex,
                use_sudo=True,)

# Install POSTFIX (TODO tal vez llevar a server service o hacer de otra manera)
    @api.one
    def install_postfix(self):
    # def install_postfix(mailname):
        """
        Require a Postfix email server.

        This makes sure that Postfix is installed and started.

        ::

            from fabtools import require

            # Handle incoming email for our domain
            require.postfix.server('example.com')

        """
        self.get_env()
        # Ensure the package is installed
        if not is_installed('postfix'):
            print 'self.postfix_hostname', self.postfix_hostname
            preseed_package('postfix', {
                'postfix/main_mailer_type': ('select', 'Internet Site'),
                'postfix/mailname': ('string', self.postfix_hostname),
                'postfix/destinations': (
                    'string', '%s, localhost.localdomain, localhost ' % (
                        self.postfix_hostname),)
            })
            install('postfix')

        # Ensure the service is started
        started('postfix')

    @api.multi
    def action_view_environments(self):
        '''
        This function returns an action that display a form or tree view
        '''
        environments = self.environment_ids.search(
            [('server_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_environment_environments')

        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('id', 'in', environments.ids)]
        if len(self) == 1:
            res['context'] = {'default_server_id': self.id}
        if not len(environments.ids) > 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_environment_form')
            res['views'] = [(form_view_id, 'form')]
            # if 1 then we send res_id, if 0 open a new form view
            res['res_id'] = environments and environments.ids[0] or False
        return res

    @api.multi
    def action_view_instances(self):
        '''
        This function returns an action that display a form or tree view
        '''
        instances = self.instance_ids.search(
            [('server_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_instance_instances')

        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('id', 'in', instances.ids)]
        if len(self) == 1:
            res['context'] = {'default_server_id': self.id}
        if not len(instances.ids) > 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_instance_form')
            res['views'] = [(form_view_id, 'form')]
            # if 1 then we send res_id, if 0 open a new form view
            res['res_id'] = instances and instances.ids[0] or False
        return res

    @api.multi
    def action_view_databases(self):
        '''
        This function returns an action that display a form or tree view
        '''
        databases = self.database_ids.search(
            [('server_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')

        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('id', 'in', databases.ids)]
        if len(self) == 1:
            res['context'] = {'default_server_id': self.id}
        if not len(databases.ids) > 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_database_form')
            res['views'] = [(form_view_id, 'form')]
            # if 1 then we send res_id, if 0 open a new form view
            res['res_id'] = databases and databases.ids[0] or False
        return res
