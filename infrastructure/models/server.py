# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from fabric.api import env, reboot
from fabric.contrib.files import append, upload_template
from fabric.api import sudo
import fabtools
from fabtools.deb import is_installed, preseed_package, install
from fabtools.require.service import started
import socket
import sys
import os
import logging
import psycopg2
FABRIC_LOCKING_PARAMETER = 'fabric_lock'
_logger = logging.getLogger(__name__)


def synchronize_on_config_parameter(env, parameter, nowait=False):
    """
    If some process are to long we can send nowait=True and it will raise the
    exception to the user
    """
    param_model = env['ir.config_parameter']
    param = param_model.search([('key', '=', parameter)], limit=1)
    if nowait:
        nowait_str = "nowait"
    else:
        nowait_str = ""

    if param:
        try:
            env.cr.execute(
                """select *
                    from ir_config_parameter
                    where id = %s
                    for update %s""" % (param.id, nowait_str)
            )
        except psycopg2.OperationalError, e:
            raise Warning(
                'Cannot synchronize access. Another process lock the parameter'
                'This is what we get: %s' % e
            )


# TODO deberiamos cambiar esto por los metodos propios de fabtools para
# gestionar errores asi tmb, por ejemplo, lo toma fabtools y otros comandos
def custom_sudo(command, user=False, group=False, dont_raise=False):
    # TODO esto habria que pasrlo con *args, **kwargs
    env.warn_only = True
    if user and group:
        res = sudo(command, user=user, group=group)
    elif user:
        res = sudo(command, user=user)
    elif group:
        res = sudo(command, group=group)
    else:
        res = sudo(command)
    if res.failed:
        if dont_raise:
            _logger.warning((
                "Can not run command:\n%s\nThis is what we get:\n%s") % (
                res.real_command, unicode(res.stdout, 'utf-8')))
        else:
            raise Warning(_(
                "Can not run command:\n%s\nThis is what we get:\n%s") % (
                res.real_command, unicode(res.stdout, 'utf-8')))
    env.warn_only = False
    return res


class server(models.Model):

    """"""

    _name = 'infrastructure.server'
    _description = 'server'
    _order = 'sequence'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    _states_ = [
        ('draft', 'Draft'),
        ('to_install', 'To Install'),
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('cancel', 'Cancel'),
    ]

    sequence = fields.Integer(
        'Sequence',
        default=10,
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    ip_address = fields.Char(
        string='IP Address',
        readonly=True,
    )
    ssh_port = fields.Integer(
        string='SSH Port',
        required=True,
        help='Port used for ssh connection to the server',
        default=22,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    smtp_port = fields.Integer(
        string='SMTP Port',
        help='Port used for incoming emails',
        required=True,
        default=25,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    http_port = fields.Integer(
        string='HTTP Port',
        required=True,
        default=80,
        help='Port used to access odoo via web browser',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    https_port = fields.Integer(
        string='HTTPS Port',
        required=True,
        default=443,
        help='Port used to access odoo via web browser over ssl',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    main_hostname = fields.Char(
        string='Main Hostname',
        required=True,
    )
    user_name = fields.Char(
        string='User Name',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    number_of_processors = fields.Integer(
        string='Number of Processors',
        readonly=True,
        help="This is used to suggest instance workers qty, you can get this "
        "information with: grep processor /proc/cpuinfo | wc -l",
    )
    password = fields.Char(
        string='Password',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    server_use_type = fields.Selection(
        [('customer', 'Customer'), ('own', 'Own')],
        'Server Type',
        default='customer',
        required=True,
    )
    holder_id = fields.Many2one(
        'res.partner',
        string='Holder',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Partner that you should contact related to server service.',
    )
    owner_id = fields.Many2one(
        'res.partner',
        string='Owner',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Owner of the server, the one you should contacto to make '
        'changes on, for example, hardware.'
    )
    used_by_id = fields.Many2one(
        'res.partner',
        string='Used By',
        readonly=True,
        states={'draft': [('readonly', False)]},
        help='Partner that can contact you and ask for changes on server '
        'configuration'
    )
    database_ids = fields.One2many(
        'infrastructure.database',
        'server_id',
        string='Databases',
        # domain=[('state', '!=', 'cancel')],
    )
    database_count = fields.Integer(
        string='# Databases',
        compute='_get_databases',
    )
    instance_ids = fields.One2many(
        'infrastructure.instance',
        'server_id',
        string='Databases',
        # domain=[('state', '!=', 'cancel')],
    )
    instance_count = fields.Integer(
        string='# Instances',
        compute='_get_instances',
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
    ssl_path = fields.Char(
        string='SSL path',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='/etc/nginx/ssl',
    )
    afip_homo_pkey_file = fields.Char(
        string='AFIP homo pkey file',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='/opt/odoo/backups/homo.pkey',
    )
    afip_prod_pkey_file = fields.Char(
        string='AFIP prod pkey file',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='/opt/odoo/backups/prod.pkey',
    )
    afip_homo_cert_file = fields.Char(
        string='AFIP homo cert file',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='/opt/odoo/backups/homo.cert',
    )
    afip_prod_cert_file = fields.Char(
        string='AFIP prod cert file',
        readonly=True,
        states={'draft': [('readonly', False)]},
        default='/opt/odoo/backups/prod.cert',
    )
    afip_prod_cert_content = fields.Text(
        string='AFIP prod cert Content',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    afip_homo_cert_content = fields.Text(
        string='AFIP homo cert Content',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    afip_prod_pkey_content = fields.Text(
        string='AFIP prod pkey Content',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    afip_homo_pkey_content = fields.Text(
        string='AFIP homo pkey Content',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    backups_path = fields.Char(
        string='Backups Path',
        readonly=True,
        required=True,
        default='/opt/odoo/backups',
        states={'draft': [('readonly', False)]},
    )
    syncked_backups_path = fields.Char(
        string='Syncked Backups Path',
        readonly=True,
        required=True,
        default='/opt/odoo/backups/syncked',
        states={'draft': [('readonly', False)]},
    )
    mailgate_file = fields.Char(
        string='Mailgate File',
        readonly=True,
        help='Mailgate File is Copided to Server and Computed when installing '
        'postfix'
    )
    color = fields.Integer(
        string='Color Index',
        compute='get_color',
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
    requires_vpn = fields.Boolean(
        string='Requires VPN?',
    )
    state = fields.Selection(
        _states_,
        string="State",
        default='draft',
    )
    server_docker_image_ids = fields.One2many(
        'infrastructure.server_docker_image',
        'server_id',
        string='Docker Images',
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
        # domain=[('state', '!=', 'cancel')],
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
        readonly=True,
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
    @api.depends('state')
    def get_color(self):
        color = 4
        if self.state == 'draft':
            color = 7
        elif self.state == 'cancel':
            color = 1
        elif self.state == 'to_install':
            color = 3
        elif self.state == 'inactive':
            color = 3
        self.color = color

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

    @api.multi
    def get_env(self):
        # TODO ver si usamos env.keepalive = True para timeouts the nginx ()
        synchronize_on_config_parameter(
            self.env, FABRIC_LOCKING_PARAMETER
        )
        self.ensure_one()
        env.user = self.user_name
        env.password = self.password
        env.host_string = self.main_hostname
        env.port = self.ssh_port
        env.timeout = 4     # by default is 10
        return env

    @api.one
    def check_service_exist(self, port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.settimeout(1)
            s.connect((self.main_hostname, port))
            s.close()
        except:
            raise Warning(_(
                'Could not connect to port %s.\n'
                '* Check connection with: "telnet %s %s" (if ok then scale '
                'issue to our technical support)\n'
                '* You can also connect to server and check ports with "%s" or'
                ' "%s" (if ok try folowing step, if not ok scale issue to our '
                'technical support )\n'
                '* You can try opening port with %s (if not ok then it should '
                'be a redirection issue of port %s to the server, ask '
                'customer to check port %s is open and redirected to server)\n'
            ) % (
                port,
                self.main_hostname, port,
                "sudo netstat -plnt |grep :%s" % port,
                "telnet localhost :%s" % port,
                "sudo ufw allow %s/tcp" % port,
                port, port,
            ))
        else:
            _logger.info("Connection to port %s successfully established")
        return True

    @api.multi
    def get_data_and_activate(self):
        """ Check server data"""
        self.test_connection(no_prompt=True)
        server_codename = fabtools.system.distrib_codename()
        server_conf_codename = self.server_configuration_id.distrib_codename
        self.ip_address = socket.gethostbyname(self.main_hostname)
        if server_codename != server_conf_codename:
            raise Warning(_(
                "Server Codename is not the and Server configuration "
                "mismatch\n"
                "* Server Codename: %s\n"
                "* Server Configuration Codename: %s") % (
                server_codename, server_conf_codename))
        self.number_of_processors = fabtools.system.cpus()
        self.add_images()
        self.action_to_install()

    @api.multi
    def action_test_connection(self):
        """Tenemos que crear esta funcion porque test_connection tiene un
        argumento adicional que se confunde con el context
        """
        self.test_connection()

    @api.multi
    def test_connection(self, no_prompt=False):
        """ Ugly way we find to check the connection"""
        self.get_env()
        # if draft state do no test http and smtp because perhups they are
        # not installed
        if self.state != 'draft':
            self.check_service_exist(self.http_port)
            # TODO activate https check, we are not using it yet
            # self.check_service_exist(self.https_port)
            self.check_service_exist(self.smtp_port)
        env.abort_on_prompts = True
        try:
            sudo('ls')
        except:
            raise Warning(_(
                'Could not connect to host. Please check credentials'))
        if no_prompt:
            return True
        raise Warning(_(
            'Connection successful!'))

    @api.multi
    def add_images(self):
        actual_docker_images = [
            x.docker_image_id.id for x in self.server_docker_image_ids]
        images = self.env['infrastructure.docker_image'].search([
            ('id', 'not in', actual_docker_images),
        ])
        for image in images:
            vals = {
                'docker_image_id': image.id,
                'server_id': self.id,
            }
            self.server_docker_image_ids.create(vals)

    @api.multi
    def configure_hosts(self):
        self.load_ssl_certficiates()
        self.add_to_virtual_domains()

    @api.multi
    def load_ssl_certficiates(self):
        self.ensure_one()
        for domain in self.hostname_ids:
            domain.load_ssl_certficiate()

    @api.multi
    def add_to_virtual_domains(self):
        self.ensure_one()
        self.get_env()
        for domain in self.hostname_ids:
            append(
                self.virtual_domains_regex_path,
                domain.domain_regex,
                use_sudo=True,)

    @api.multi
    def show_passwd(self):
        self.ensure_one()
        raise except_orm(
            _("Password for user '%s':") % self.user_name,
            _("%s") % self.password
        )

    @api.multi
    def show_gdrive_passwd(self):
        self.ensure_one()
        raise except_orm(
            _("Password for user '%s':") % self.gdrive_account,
            _("%s") % self.gdrive_passw
        )

    @api.multi
    def configure_gdrive_sync(self):
        self.get_env()
        if not self.gdrive_account or not self.gdrive_passw:
            raise Warning(_(
                'To configure google drive sync you need to set account and '
                'password'))
        fabtools.require.deb.ppa('ppa:twodopeshaggy/drive')
        fabtools.require.deb.package('drive')
        fabtools.require.files.directory(
            self.syncked_backups_path, use_sudo=True, mode='777')
        fabtools.cron.add_task(
            'bu_push_tu_drive',
            '0 4 * * *',
            'root',
            'drive push -quiet -ignore-conflict=true %s' % (
                self.syncked_backups_path))
        raise Warning(_(
            'Please log in into the server and run:\n'
            'sudo drive init %s\n'
            'Follow onscreen steps') % (
            self.syncked_backups_path,
        ))

    @api.multi
    def reboot_server(self):
        self.get_env()
        reboot()

    @api.multi
    def restart_nginx(self):
        _logger.info("Restarting nginx")
        self.get_env()
        try:
            custom_sudo('service nginx restart')
        except Exception, e:
            raise Warning(
                _('Could Not Restart Nginx! This is what we get: \n %s') % (e))

    @api.multi
    def reload_nginx(self):
        _logger.info("Reloading nginx")
        self.get_env()
        try:
            custom_sudo('nginx -s reload')
        except Exception, e:
            raise Warning(
                _('Could Not Reload Nginx! This is what we get: \n %s') % (e))

    @api.multi
    def action_to_draft(self):
        self.write({'state': 'draft'})
        return True

    @api.multi
    def action_to_install(self):
        self.write({'state': 'to_install'})

    @api.multi
    def action_activate(self):
        self.write({'state': 'active'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_inactive(self):
        self.check_to_inactive()
        self.write({'state': 'inactive'})

    @api.one
    def check_to_inactive(self):
        not_inactive_envs = self.environment_ids.filtered(
            lambda x: x.state != 'inactive')
        if not_inactive_envs:
            raise Warning(_(
                'To set a server as inactive you should set all '
                'environments to inactive first'))
        return True

    @api.multi
    def copy_mailgate_file(self):
        self.get_env()
        local_mailgate_file = os.path.join(
            self.module_path(),
            'scripts/openerp_mailgate.py')
        try:
            res = upload_template(
                local_mailgate_file, self.base_path,
                use_sudo=True,
                mode=0777)
        except Exception, e:
            raise Warning(_(
                "Can not run upload mailgate file:\n"
                "This is what we get:\n%s") % e)
        self.mailgate_file = res and res[0] or False

    @api.model
    def we_are_frozen(self):
        # All of the modules are built-in to the interpreter, e.g., by py2exe
        return hasattr(sys, "frozen")

    @api.model
    def module_path(self):
        encoding = sys.getfilesystemencoding()
        if self.we_are_frozen():
            return os.path.dirname(unicode(sys.executable, encoding))
        return os.path.dirname(unicode(__file__, encoding))

    @api.multi
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
        self.copy_mailgate_file()
        # Ensure the package is installed
        if not is_installed('postfix'):
            preseed_package('postfix', {
                'postfix/main_mailer_type': ('select', 'Internet Site'),
                'postfix/mailname': ('string', self.postfix_hostname),
                'postfix/destinations': (
                    'string', '%s, localhost.localdomain, localhost ' % (
                        self.postfix_hostname),)
            })
            install('postfix')

        # Update postfix conf
        custom_sudo("postconf -e 'virtual_alias_domains = regexp:%s'" % (
            self.virtual_domains_regex_path))
        custom_sudo("postconf -e 'virtual_alias_maps = hash:%s'" % (
            self.virtual_alias_path))

        # Restart postfix
        custom_sudo('service postfix restart')

        # Ensure the service is started
        started('postfix')

    @api.multi
    def action_view_environments(self):
        '''
        This function returns an action that display a form or tree view
        '''
        self.ensure_one()
        environments = self.environment_ids.search(
            [('server_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_environment_environments')

        if not action:
            return False
        res = action.read()[0]
        if len(self) == 1:
            res['context'] = {
                'default_server_id': self.id,
                'search_default_server_id': self.id,
                'search_default_not_inactive': 1,
            }
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
        self.ensure_one()
        instances = self.instance_ids.search(
            [('server_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_instance_instances')

        if not action:
            return False
        res = action.read()[0]
        if len(self) == 1:
            res['context'] = {
                'default_server_id': self.id,
                'search_default_server_id': self.id,
                'search_default_not_inactive': 1,
            }
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
        self.ensure_one()
        databases = self.database_ids.search(
            [('server_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')

        if not action:
            return False
        res = action.read()[0]
        if len(self) == 1:
            res['context'] = {
                'default_server_id': self.id,
                'search_default_server_id': self.id,
                'search_default_not_inactive': 1,
            }
        if not len(databases.ids) > 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_database_form')
            res['views'] = [(form_view_id, 'form')]
            # if 1 then we send res_id, if 0 open a new form view
            res['res_id'] = databases and databases.ids[0] or False
        return res
