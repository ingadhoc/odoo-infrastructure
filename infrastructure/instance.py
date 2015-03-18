# -*- coding: utf-8 -*-

from openerp import netsvc
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from fabric.api import shell_env
# from fabric.api import sudo, shell_env
# utilizamos nuestro custom sudo que da un warning
from .server import custom_sudo as sudo
from fabric.contrib.files import exists, append, sed
from ast import literal_eval
import os
import re
from fabric.api import settings, env
import logging
import fabtools
_logger = logging.getLogger(__name__)


class instance(models.Model):

    """"""
    # TODO agregar bloqueo de volver a estado cancel. Solo se debe poder
    # volver si no existe el path ni el source path y si no existen ambienets
    # activo
    _name = 'infrastructure.instance'
    _rec_name = 'display_name'
    _description = 'instance'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _states_ = [
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('cancel', 'Cancel'),
    ]

    _track = {
        'state': {
            'infrastructure.instance_draft':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'infrastructure.instance_active':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active',
            'infrastructure.instance_cancel':
            lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }

    @api.model
    def get_database_type_id(self):
        return self.env['infrastructure.database_type'].search([], limit=1)

    number = fields.Integer(
        string='Number',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    database_type_id = fields.Many2one(
        'infrastructure.database_type',
        string='Database Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        track_visibility='onchange',
        default=get_database_type_id,
        copy=False,
    )
    display_name = fields.Char(
        'Name',
        compute='get_display_name',
        store=True,
        )
    name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        # default='main',
    )
    type = fields.Selection(
        [(u'secure', u'Secure'), (u'none_secure', u'None Secure')],
        string='Instance Type',
        required=True,
        default='none_secure',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    db_filter = fields.Many2one(
        'infrastructure.db_filter',
        string='DB Filter',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    limit_time_real = fields.Integer(
        string='Limit Time Real',
        required=True,
        default=120,
        help='Maximum allowed Real time per request. The default odoo value is 120 but sometimes we use 300 to avoid some workers timeout error',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    limit_time_cpu = fields.Integer(
        string='Limit Time CPU',
        required=True,
        default=120,
        help='Maximum allowed CPU time per request. The default odoo value is 60 but sometimes we use 120 to avoid some workers timeout error',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    db_maxconn = fields.Integer(
        string='DB Max connections',
        required=True,
        default=32,
        help='Specify the the maximum number of physical connections to posgresql. Default odoo config is 64, we use 32.',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    note = fields.Html(
        string='Note'
    )

    color = fields.Integer(
        string='Color Index'
    )

    run_server_command = fields.Char(
        string='Run Server Command',
        required=True,
        default='odoo.py',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    proxy_mode = fields.Boolean(
        string='Proxy Mode?',
        default=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    # TODO borrar esta opcion, que sea asi por defecto
    run_on_sys_boot = fields.Boolean(
        string='Run On System Boot?',
        default=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    log_level = fields.Selection([
        (u'info', 'info'), (u'debug_rpc', 'debug_rpc'),
        (u'warn', 'warn'), (u'test', 'test'), (u'critical', 'critical'),
        (u'debug_sql', 'debug_sql'), (u'error', 'error'), (u'debug', 'debug'),
        (u'debug_rpc_answer', 'debug_rpc_answer')],
        string='Log Level',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    workers = fields.Integer(
        string='Workers',
        default=0,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    admin_pass = fields.Char(
        string='Admin Password',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    unaccent = fields.Boolean(
        string='Enable Unaccent',
        readonly=True,
        default=True,
        states={'draft': [('readonly', False)]},
    )

    module_load = fields.Char(
        string='Load default modules',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    main_hostname = fields.Char(
        string='Main Hostname',
        compute='_get_main_hostname',
        # required=True,
        # help="Specified the port if port different from 80. For eg you can use: \
        # * ingadho.com\
        # * ingadhoc.com:8069"
    )

    state = fields.Selection(
        _states_,
        string="State",
        default='draft'
    )

    instance_host_ids = fields.One2many(
        'infrastructure.instance_host',
        'instance_id',
        string='Hosts',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    environment_id = fields.Many2one(
        'infrastructure.environment',
        string='Environment',
        ondelete='cascade',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    database_ids = fields.One2many(
        'infrastructure.database',
        'instance_id',
        string='Databases',
        context={'from_instance': True}
    )

    addons_path = fields.Char(
        string='Addons Path',
        compute='_get_addons_path',
        # store=True,
        # readonly=False,
        required=True
    )

    user = fields.Char(
        string='User',
        # compute='_get_user',
        # store=True,
        required=True,
        # readonly=True,
        states={'draft': [('readonly', False)]}
    )

    service_file = fields.Char(
        string='Service Name',
        # compute='_get_user',
        # store=True,
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    base_path = fields.Char(
        string='Base Path',
        # compute='_get_paths',
        # store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    conf_path = fields.Char(
        string='Config. Path',
        # compute='_get_paths',
        # store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    pg_data_path = fields.Char(
        string='Pg Data Path',
        # compute='_get_paths',
        # store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    conf_file_path = fields.Char(
        string='Config. File Path',
        # compute='_get_paths',
        # store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    data_dir = fields.Char(
        string='Data Dir',
        # compute='_get_paths',
        # store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    logfile = fields.Char(
        string='Log File Path',
        # compute='_get_paths',
        # store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    xml_rpc_port = fields.Integer(
        string='XML-RPC Port',
        # compute='_get_ports',
        # store=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        required=True
    )

    xml_rpcs_port = fields.Integer(
        string='XML-RPCS Port',
        # compute='_get_ports',
        # store=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    longpolling_port = fields.Integer(
        string='Longpolling Port',
        # compute='_get_ports',
        # store=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )

    database_count = fields.Integer(
        string='# Databases',
        compute='_get_databases'
    )

    sources_path = fields.Char(
        string='Sources Path',
        # compute='_get_env_paths',
        # store=True,
        readonly=True,
        required=True,
        states={
            'draft': [('readonly', False)]
        }
    )

    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        related='environment_id.server_id',
        store=True,
        readonly=True
    )
    docker_image_ids = fields.Many2many(
        'infrastructure.docker_image',
        string='Docker Images',
        compute='_get_docker_images',
    )
    env_type = fields.Selection(
        related='environment_id.type',
        string='Environment Type',
        # store=True,
        readonly=True
    )
    odoo_image_id = fields.Many2one(
        'infrastructure.docker_image',
        string='Odoo Image',
        readonly=True,
        domain="[('id', 'in', docker_image_ids[0][2]), ('service', '=', 'odoo')]",
        states={'draft': [('readonly', False)]}
    )
    pg_image_id = fields.Many2one(
        'infrastructure.docker_image',
        string='Postgres Image',
        readonly=True,
        domain="[('id', 'in', docker_image_ids[0][2]), ('service', '=', 'postgresql')]",
        states={'draft': [('readonly', False)]}
    )
    odoo_container = fields.Char(
        string='Odoo Container',
        compute='get_container_names',
        # readonly=True,
        # states={'draft': [('readonly', False)]}
    )
    pg_container = fields.Char(
        string='Postgresql Container',
        # readonly=True,
        compute='get_container_names',
        # states={'draft': [('readonly', False)]}
    )

    _sql_constraints = [
        ('xml_rpc_port_uniq', 'unique(xml_rpc_port, server_id)',
            'xmlrpc Port must be unique per server!'),
        ('xml_rpcs_port_uniq', 'unique(xml_rpcs_port, server_id)',
            'xmlrpcs Port must be unique per server!'),
        ('longpolling_port_uniq', 'unique(longpolling_port, server_id)',
            'Longpolling Port must be unique per server!'),
        ('logfile_uniq', 'unique(logfile, server_id)',
            'Log File Path must be unique per server!'),
        ('user_uniq', 'unique(user, server_id)',
            'User must be unique per server!'),
        ('data_dir_uniq', 'unique(data_dir, server_id)',
            'Data Dir must be unique per server!'),
        ('base_path_uniq', 'unique(base_path, server_id)',
            'Base Path must be unique per server!'),
        ('conf_file_path_uniq', 'unique(conf_file_path, server_id)',
            'Config. File Path must be unique per server!'),
        ('service_file_uniq', 'unique(service_file, server_id)',
            'Service File Path must be unique per server!'),
        ('number_uniq', 'unique(number, environment_id)',
            'Number must be unique per environment!'),
        ('name_uniq', 'unique(name, environment_id)',
            'Name must be unique per environment!'),
    ]

    @api.one
    @api.depends('server_id')
    def _get_main_hostname(self):
        main_host = self.instance_host_ids.filtered(
            lambda r: r.type == 'main')
        # main_host = self.instance_host_ids.filtered("type='main'")
        if not main_host:
            main_host = self.instance_host_ids.filtered(
                lambda r: r.type == 'other')
        self.main_hostname = main_host and main_host[0].name or False

    @api.one
    @api.depends('server_id')
    def _get_docker_images(self):
        self.docker_image_ids = self.env['infrastructure.docker_image']
        self.docker_image_ids = [
            x.docker_image_id.id for x in self.server_id.server_docker_image_ids]

    @api.one
    @api.depends(
        'name',
        'environment_id',
        'environment_id.name',
        )
    def get_display_name(self):
        self.display_name = "%s-%s" % (
            self.environment_id.name or '', self.name or '')

    # TODO borrar el campo name del mapa, lo dejamos para aquellas instancias viejas creadas con main y demas
    @api.onchange('database_type_id')
    def onchange_database_type_id(self):
        if self.database_type_id:
            self.name = self.database_type_id.prefix
            instance_admin_pass = self.database_type_id.instance_admin_pass
            self.admin_pass = instance_admin_pass or self.display_name
            self.db_filter = self.database_type_id.db_filter

    @api.one
    @api.depends('display_name')
    def get_container_names(self):
        self.odoo_container = 'odoo-' + self.display_name
        self.pg_container = 'db-' + self.display_name

    @api.one
    def get_user(self):
        """"""
        raise NotImplementedError

    @api.one
    def show_passwd(self):
        raise except_orm(
            _("Password for user '%s':") % self.user,
            _("%s") % self.admin_pass
        )

    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.instance', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.instance', obj_id, cr)
        return True

    @api.one
    @api.constrains('number')
    def _check_number(self):
        if not self.number or self.number < 1 or self.number > 9:
            raise Warning(_('Number should be between 1 and 9'))

    @api.one
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise Warning(_(
                'You cannot delete an instance which \
                is not draft or cancelled.'))
        return super(instance, self).unlink()

# Calculated fields
    @api.one
    @api.depends('database_ids')
    def _get_databases(self):
        self.database_count = len(self.database_ids)

    @api.one
    @api.depends(
        'environment_id',
        'environment_id.environment_repository_ids',
        'environment_id.environment_repository_ids.addons_paths'
    )
    def _get_addons_path(self):
        # TODO simplificar esto y los addons path y demas, hacer algo mucho mas simpe
        _logger.info("Getting Addons Path")
        addons_path = []
        if self.env_type == 'docker':
            for path in self.environment_id.environment_repository_ids:
                repository = path.server_repository_id.repository_id
                addons_path.append(
                    os.path.join(
                        '/mnt/extra-addons',
                        repository.directory,
                        repository.addons_subdirectory and repository.addons_subdirectory or '',
                        )
                    )
        else:
            try:
                for repository in self.environment_id.environment_repository_ids:
                    if repository.addons_paths:
                        for addon_path in literal_eval(repository.addons_paths):
                            addons_path.append(addon_path)
            except:
                _logger.error("Error trying to get addons path")
        if not addons_path:
            addons_path = '[]'
        self.addons_path = addons_path

    @api.one
    @api.onchange('environment_id')
    def _onchange_environment(self):
        instances = self.search(
            [('environment_id', '=', self.environment_id.id)],
            order='number desc',
            )
        self.number = instances and instances[0].number + 1 or 1
        number_of_processors = self.environment_id.server_id.number_of_processors
        self.workers = (number_of_processors * 2) + 1

    @api.one
    @api.onchange('name', 'environment_id')
    def _get_user(self):
        user = False
        if self.name and self.environment_id.name:
            user = self.environment_id.name + '-' + self.name
        self.user = user
        self.service_file = user

    @api.one
    @api.onchange('name', 'number', 'environment_id')
    def _get_ports_and_ports(self):
        xml_rpc_port = False
        xml_rpcs_port = False
        longpolling_port = False
        conf_path = False
        conf_file_path = False
        base_path = False
        pg_data_path = False
        logfile = False
        data_dir = False
        sources_path = False
        if self.environment_id.number and self.number:
            prefix = str(self.environment_id.number) + str(self.number)
            xml_rpc_port = int(prefix + '1')
            xml_rpcs_port = int(prefix + '2')
            longpolling_port = int(prefix + '3')
        self.xml_rpc_port = xml_rpc_port
        self.xml_rpcs_port = xml_rpcs_port
        self.longpolling_port = longpolling_port
        if self.environment_id.path and self.name:
            base_path = os.path.join(
                self.environment_id.path, self.name)
            conf_path = os.path.join(base_path, 'config')
            pg_data_path = os.path.join(base_path, 'postgresql')
            conf_file_path = os.path.join(conf_path, 'openerp-server.conf')
            logfile = os.path.join(base_path, 'odoo.log')
            data_dir = os.path.join(base_path, 'data_dir')
            sources_path = os.path.join(base_path, 'sources')
        self.pg_data_path = pg_data_path
        self.pg_data_path = pg_data_path
        self.conf_path = conf_path
        self.sources_path = sources_path
        self.base_path = base_path
        self.conf_file_path = conf_file_path
        self.logfile = logfile
        self.data_dir = data_dir

    # Actions
    @api.multi
    def delete(self):
        _logger.info("Deleting Instance")
        if self.database_ids:
            raise Warning(_(
                'You can not delete an instance that has databases'))
        self.stop_service()
        self.stop_pg_service()
        if self.env_type != 'docker':
            self.stop_run_on_start()
        self.delete_service_files()
        self.delete_nginx_site()
        self.delete_user()
        self.delete_pg_user()
        self.delete_paths()
        self.signal_workflow('sgn_cancel')

    @api.multi
    def create_instance(self):
        _logger.info("Creating Instance")
        self.make_paths()
        self.update_nginx_site()
        if self.env_type != 'docker':
            self.create_user()
            self.create_pg_user()
        else:
            self.update_pg_service_file()
            self.start_pg_service()

        self.update_conf_file()
        self.update_service_file()
        self.start_service()
        if self.env_type != 'docker':
            self.run_on_start()
        self.signal_workflow('sgn_to_active')

    @api.one
    def remove_containers(self):
        self.environment_id.server_id.get_env()
        for container in [self.odoo_container, self.pg_container]:
            _logger.info("Removing Container %s" % container)
            try:
                sudo('docker rm -f %s' % container)
            except Exception, e:
                _logger.warning(("Can not delete container %s, this is what we get: \n %s") % (
                    container, e))

    @api.multi
    def run_odoo_command(self):
        command = (
            '%s \
            -p 127.0.0.1:%i:8069 \
            -p 127.0.0.1:%i:8072 \
            -v %s:/etc/odoo \
            -v %s:/mnt/extra-addons \
            -v %s:/var/lib/odoo \
            --link %s:db \
            --name %s \
            %s \
            ' % (
                self.odoo_image_id.prefix,
                self.xml_rpc_port,
                self.longpolling_port,
                self.conf_path,
                self.environment_id.sources_path,
                # TODO agregar el sources de la instance
                self.data_dir,
                self.pg_container,
                self.odoo_container,
                self.odoo_image_id.pull_name,
            ))
        return command

    @api.one
    def run_odoo_container(self):
        command = self.run_odoo_command()
        sudo('docker %s' % command)
        _logger.info("Running docker command: %s" % command)

    @api.multi
    def run_pg_command(self):
        command = (
            '%s \
            -v %s:/var/lib/postgresql/data \
            --name %s\
            %s \
            ' % (
                self.pg_image_id.prefix,
                self.pg_data_path,
                self.pg_container,
                self.pg_image_id.pull_name,
            ))
        return command

    @api.one
    def run_pg_container(self):
        command = self.run_pg_command()
        sudo('docker %s' % command)
        _logger.info("Running docker command: %s" % command)

    @api.one
    def delete_paths(self):
        _logger.info("Deleting path and subpath of: %s " % self.base_path)
        self.environment_id.server_id.get_env()
        sudo('rm -r %s' % self.base_path, dont_raise=True)

    @api.one
    def make_paths(self):
        _logger.info("Creating paths")
        self.environment_id.server_id.get_env()
        # el path de postgres dejamos que se cree solo para que no les ponga
        # 777 de permisos porque da error
        paths = [
            self.base_path,
            self.sources_path,
            self.conf_path,
            self.data_dir,
            ]
        for path in paths:
            if exists(path, use_sudo=True):
                _logger.warning(("Folder '%s' already exists") % (path))
                continue
            _logger.info(("Creating path '%s'") % (path))
            sudo('mkdir -m 777 -p ' + path)

    @api.one
    def update_conf_file(self, force_no_workers=False):
        _logger.info("Updating conf file")
        self.environment_id.server_id.get_env()
        try:
            self.stop_service()
            start_service = True
        except:
            start_service = False

        if not exists(self.environment_id.path, use_sudo=True):
            raise except_orm(_('No Environment Path!'),
                             _("Environment path '%s' does not exists. \
                                Please create it first!")
                             % (self.environment_id.path))

        # Remove file if it already exists, we do it so we can put back some
        # booelan values as unaccent
        if exists(self.conf_file_path, use_sudo=True):
            sudo('rm ' + self.conf_file_path)

        # Build addons path
        # Todo usar ', '.join
        # addons_path = False
        addons_paths = literal_eval(self.addons_path)
        # for path in addons_paths:
        #     # path.replace
        addons_path = ','.join(addons_paths)
        # for addon_path in literal_eval(self.addons_path):
        #     if not exists(addon_path, use_sudo=True):
        #         raise except_orm(_('Addons path does not exist!'),
        #                          _("Addons path '%s' does not exists. \
        #                             Please create it first!") % (addon_path))
        #     if not addons_path:
        #         addons_path = addon_path
        #     addons_path += ',' + addon_path

        # Construimos commando
        if self.env_type == 'docker':
            command = 'docker %s --' % self.run_odoo_command()
        else:
            command = '%s/bin/%s -c %s' % (
                self.environment_id.path,
                self.run_server_command,
                self.conf_file_path,
                )
        command += ' --stop-after-init -s'

        if addons_path:
            command += ' --addons-path=' + addons_path
        # agregamos ' para que no de error con ciertos dominios
        command += ' --db-filter=' + "'%s'" % self.db_filter.rule
        # TODO ver para ambientes de docker que hacemos con el log
        if self.env_type != 'docker':
            command += ' --xmlrpc-port=' + str(self.xml_rpc_port)
            command += ' --logfile=' + self.logfile
        command += ' --limit-time-real=' + str(self.limit_time_real)
        command += ' --limit-time-cpu=' + str(self.limit_time_cpu)
        command += ' --db_maxconn=' + str(self.db_maxconn)

        if self.environment_id.odoo_version_id.name in ('8.0', 'master'):
            # Para docker el data dir lo usamos en el montaje del volume con -v
            if self.env_type != 'docker':
                if self.data_dir:
                    command += ' --data-dir=' + self.data_dir
                if self.longpolling_port:
                    command += ' --longpolling-port=' + str(self.longpolling_port)
            else:
                # if docker, we force this data dir
                if self.data_dir:
                    command += ' --data-dir=/var/lib/odoo/'

        if self.module_load:
            command += ' --load=' + self.module_load

        if self.unaccent:
            command += ' --unaccent'

        if self.proxy_mode:
            command += ' --proxy-mode'

        if force_no_workers:
            command += ' --workers=' + '0'
        elif self.workers:
            command += ' --workers=' + str(self.workers)

        if self.type == 'secure':
            command += ' --xmlrpcs-port=' + str(self.xml_rpcs_port)
        else:
            command += ' --no-xmlrpcs'

        # TODO --cert-file and --pkey-file
        # TODO ver de agregar --log-db=LOG_DB
        # TODO check that user exists
        # TODO tal vez -r -w para database data
        try:
            if self.env_type == 'docker':
                print 'command'
                print 'command'
                print 'command', command
                sudo(command)
            else:
                sudo('chown ' + self.user + ':odoo -R ' + self.environment_id.path)
                _logger.info("Running command: %s" % command)
                eggs_dir = '/home/%s/.python-eggs' % self.user
                if not exists(eggs_dir, use_sudo=True):
                    sudo('mkdir %s' % eggs_dir, user=self.user)
                with shell_env(PYTHON_EGG_CACHE=eggs_dir):
                    sudo('chmod g+rw -R ' + self.environment_id.path)
                    sudo(command, user=self.user)
        except Exception, e:
            raise Warning(_("Can not create/update configuration file, this is what we get: \n %s") % (
                e))
        # TODO cambiar esto por el webservice que permite cambiar el admin pass
        sed(self.conf_file_path, '(admin_passwd).*', 'admin_passwd = ' + self.admin_pass, use_sudo=True)
        if start_service:
            self.start_service()

    @api.multi
    def delete_service_files(self):
        _logger.info("Deleting service file")
        if self.env_type == 'docker':
            pg_service_file_path = os.path.join(
                '/etc/init', self.pg_container + '.conf')
            service_file_path = os.path.join(
                '/etc/init', self.odoo_container + '.conf')
        else:
            self.environment_id.server_id.service_path
            service_file_path = os.path.join('/etc/init.d', self.service_file)
        try:
            sudo('rm ' + service_file_path)
            if self.env_type == 'docker':
                sudo('rm ' + pg_service_file_path)
        except Exception, e:
            _logger.warning(("Could delete service file '%s', this is what we get: \n %s") % (
                self.service_file, e))

    @api.multi
    def update_pg_service_file(self):
        _logger.info("Updating Postgresql service file")
        service_path = '/etc/init'
        service_file_path = os.path.join(
            service_path, self.pg_container + '.conf')
        service_content = template_upstar_file % (
            self.pg_container,
            '',
            self.run_pg_command(),
            'rm -f %s' % self.pg_container
            )
        # Check if service already exist
        if exists(service_file_path, use_sudo=True):
            sudo('rm ' + service_file_path)
        # Create file
        append(service_file_path, service_content, use_sudo=True,)
        sudo('chmod 777 ' + service_file_path)

    @api.multi
    def update_service_file(self):
        _logger.info("Updating service file")

        if self.env_type == 'docker':
            service_file_path = os.path.join(
                '/etc/init', self.odoo_container + '.conf')
            service_content = template_upstar_file % (
                self.odoo_container,
                'and started %s' % self.pg_container,
                self.run_odoo_command(),
                'rm -f %s' % self.odoo_container
                )
        else:
            self.environment_id.server_id.service_path
            service_file_path = os.path.join('/etc/init.d', self.service_file)
            # Build file
            daemon = os.path.join(
                self.environment_id.path, 'bin', self.run_server_command)
            service_content = template_service_file % (
                self.user, self.conf_file_path, daemon)

        # Check if service already exist
        if exists(service_file_path, use_sudo=True):
            sudo('rm ' + service_file_path)

        # Create file
        append(service_file_path, service_content, use_sudo=True,)
        # por un tema de ejeucion...
        if self.env_type != 'docker':
            sudo('chmod 777 ' + service_file_path)

    @api.one
    def create_user(self):
        _logger.info("Creating unix user")
        self.environment_id.server_id.get_env()
        try:
            sudo('adduser --system --ingroup odoo ' + self.user)
        except Exception, e:
            raise Warning(_("Can not create linux user %s, this is what we get: \n %s") % (
                self.user, e))

    @api.one
    def delete_user(self):
        _logger.info("Deleting unix user")
        self.environment_id.server_id.get_env()
        try:
            sudo('deluser %s' % self.user)
        except Exception, e:
            _logger.warning(("Can not delete linux user %s, this is what we get: \n %s") % (
                self.user, e))

    @api.one
    def create_pg_user(self):
        if not fabtools.postgres.user_exists(self.user):
            _logger.info("Creating pg User")
            self.environment_id.server_id.get_env()
            try:
                sudo('sudo -u postgres createuser -d -R -S ' + self.user)
            except Exception, e:
                raise Warning(_("Can not create postgres user %s, this is what we get: \n %s") % (
                    self.user, e))

    @api.one
    def delete_pg_user(self):
        if fabtools.postgres.user_exists(self.user):
            _logger.info("Deleting pg User")
            self.environment_id.server_id.get_env()
            try:
                sudo('sudo -u postgres dropuser %s' % self.user)
            except Exception, e:
                raise Warning(_("Can not delete postgres user %s, this is what we get: \n %s") % (
                    self.user, e))

    @api.one
    def start_service(self):
        if self.env_type == 'docker':
            service = self.odoo_container
        else:
            service = self.service_file

        _logger.info("Starting Service %s " % service)
        self.environment_id.server_id.get_env()
        self.stop_service()
        # TODO no anda este verificador de fabric seguramente porque el servicio esta mal, habria que mejroarlo robando lo nuevo de odoo
        # if not fabtools.service.is_running(self.service_file):
        env.warn_only = True
        fabtools.service.start(service)
        env.warn_only = False
        # service.started(self.service_file)
        # sudo('service ' + self.service_file + ' start')

    @api.one
    def stop_service(self):
        if self.env_type == 'docker':
            service = self.odoo_container
        else:
            service = self.service_file

        _logger.info("Stopping Service %s " % service)
        self.environment_id.server_id.get_env()
        # if fabtools.service.is_running(self.service_file):
        env.warn_only = True
        fabtools.service.stop(service)
        env.warn_only = False
        # sudo('service ' + self.service_file + ' stop')
        # TODO probar bajar con fabtools pero me daba error
        # service.stopped(self.service_file)

    @api.one
    def restart_service(self):
        if self.env_type == 'docker':
            service = self.odoo_container
        else:
            service = self.service_file

        _logger.info("Restarting Service")
        self.environment_id.server_id.get_env()
        try:
            sudo('service ' + service + ' restart')
        except Exception, e:
            raise Warning(_("Could not restart service '%s', this is what we get: \n %s") % (
                service, e))

    @api.one
    def start_pg_service(self):
        _logger.info("Starting Postgresql Service")
        self.environment_id.server_id.get_env()
        self.stop_pg_service()
        env.warn_only = True
        fabtools.service.start(self.pg_container)
        env.warn_only = False

    @api.one
    def stop_pg_service(self):
        _logger.info("Stopping Postgresql Service")
        self.environment_id.server_id.get_env()
        env.warn_only = True
        fabtools.service.stop(self.pg_container)
        env.warn_only = False

    @api.one
    def run_on_start(self):
        _logger.info("Adding run on start")
        self.environment_id.server_id.get_env()
        try:
            sudo('update-rc.d  ' + self.service_file + ' defaults')
        except Exception, e:
            raise Warning(_("Could not add service '%s' to run on start, this is what we get: \n %s") % (
                self.service_file, e))

    @api.one
    def stop_run_on_start(self):
        _logger.info("Stopping run on start")
        self.environment_id.server_id.get_env()
        try:
            sudo('update-rc.d  -f ' + self.service_file + ' remove')
        # we dont raise and exception, jus print on logg
        except Exception, e:
            _logger.warning(("Could not stop service '%s' to run on start, this is what we get: \n %s") % (
                self.service_file, e))

    @api.one
    def delete_nginx_site(self):
        _logger.info("Deleting conf file")
        self.environment_id.server_id.get_env()
        nginx_sites_path = self.environment_id.server_id.nginx_sites_path
        nginx_site_file_path = os.path.join(
            nginx_sites_path,
            self.service_file
        )
        try:
            sudo('rm -f %s' % nginx_site_file_path)
        except Exception, e:
            _logger.warning(("Could remove nginx site file '%s', this is what we get: \n %s") % (
                self.service_file, e))

    @api.one
    def update_nginx_site(self):
        _logger.info("Updating nginx site")
        if not self.main_hostname:
            raise Warning(_('Can Not Configure Nginx if Main Site is not Seted!'))

        self.environment_id.server_id.get_env()
        if self.type == 'none_secure':
            listen_port = 80
        else:
            raise Warning(_('Secure instances not implemented yet!'))

        server_names = [
            x.name for x in self.instance_host_ids if x.type != 'redirect_to_main']
        redirect_server_names = ['www.' + x for x in server_names]
        redirect_server_names += [
            x.name for x in self.instance_host_ids if x.type == 'redirect_to_main']

        if not server_names:
            raise Warning(_('You Must set at least one instance host!'))

        acces_log = os.path.join(
            self.environment_id.server_id.nginx_log_path,
            'access_' + re.sub('[-]', '_', self.service_file))
        error_log = os.path.join(
            self.environment_id.server_id.nginx_log_path,
            'error_' + re.sub('[-]', '_', self.service_file))
        xmlrpc_port = self.xml_rpc_port

        nginx_long_polling = ''

        if self.longpolling_port:
            nginx_long_polling = nginx_long_polling_template % (
                self.longpolling_port)

        nginx_site_file = nginx_site_template % (
            ' '.join(redirect_server_names),
            self.main_hostname,
            listen_port, ' '.join(server_names),
            acces_log,
            error_log,
            xmlrpc_port,
            nginx_long_polling
        )

        # Check nginx sites-enabled directory exists
        nginx_sites_path = self.environment_id.server_id.nginx_sites_path
        if not exists(nginx_sites_path):
            raise Warning(
                _("Nginx '%s' directory not found! \
                Check if Nginx is installed!") % nginx_sites_path
            )

        # Check if file already exists and delete it
        nginx_site_file_path = os.path.join(
            nginx_sites_path,
            self.service_file
        )
        if exists(nginx_site_file_path, use_sudo=True):
            sudo('rm ' + nginx_site_file_path)

        # Create file
        append(nginx_site_file_path, nginx_site_file, use_sudo=True,)
        sudo('chmod 777 ' + nginx_site_file_path)

        # Restart nginx
        self.environment_id.server_id.reload_nginx()

    @api.multi
    def action_view_databases(self):
        '''
        This function returns an action that display a form or tree view
        '''
        databases = self.database_ids.search(
            [('instance_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')

        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('id', 'in', databases.ids)]
        if len(self) == 1:
            res['context'] = {'default_instance_id': self.id}
        if not len(databases.ids) > 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_database_form')
            res['views'] = [(form_view_id, 'form')]
            # if 1 then we send res_id, if 0 open a new form view
            res['res_id'] = databases and databases.ids[0] or False
        return res

# TODO llevar esto a un archivo y leerlo de alli
nginx_long_polling_template = """
    location /longpolling {
        proxy_pass   http://127.0.0.1:%i;
    }
"""
nginx_site_template = """
server   {
        server_name %s;
        rewrite  ^/(.*)$  http://%s/$1 permanent;
}
server {
        listen %i;
        server_name %s;
        access_log %s;
        error_log %s;

        location / {
                proxy_pass              http://127.0.0.1:%i;
                proxy_set_header        X-Forwarded-Host $host;
        }

    %s

}
"""
# odoo_upstar = template_upstar_file % ()
template_upstar_file = """
description "%s Container"
author "ADHOC SA"

start on filesystem and started docker %s
stop on runlevel [!2345]

# The process wil be restarted if ended unexpectedly
respawn

# If the process is respawned more than 10 times within an interval of 90 timeout seconds, the process will be stopped automatically, and not $
respawn limit 10 90

script
  /usr/bin/docker %s
end script
post-stop script
  /usr/bin/docker %s
end script
"""

# TODO llevar esto a un archivo y leerlo de alli
template_service_file = """
#!/bin/sh

### BEGIN INIT INFO
# Provides:             openerp-server
# Required-Start:       $remote_fs $syslog
# Required-Stop:        $remote_fs $syslog
# Should-Start:         $network
# Should-Stop:          $network
# Default-Start:        2 3 4 5
# Default-Stop:         0 1 6
# Short-Description:    Enterprise Resource Management software
# Description:          odoo is a complete ERP and CRM software.
### END INIT INFO

# EDITABLE
USER=%s
CONFIG=%s
DAEMON=%s

# NO TOCAR
PATH=/sbin:/bin:/usr/sbin:/usr/bin
NAME=odoo-$USER
DESC=odoo-$USER

test -x ${DAEMON} || exit 0

set -e

case "${1}" in
        start)
                echo -n "Starting ${DESC}: "
        sleep 5

                start-stop-daemon --start --quiet --pidfile /var/run/${NAME}.pid \
                        --chuid ${USER} --background --make-pidfile \
            --exec ${DAEMON} -- --config=${CONFIG}  \


                echo "${NAME}."
                ;;

        stop)
                echo -n "Stopping ${DESC}: "

                start-stop-daemon --stop --quiet --pidfile /var/run/${NAME}.pid \
                        --oknodo

                echo "${NAME}."
                ;;

        restart|force-reload)
                echo -n "Restarting ${DESC}: "

                start-stop-daemon --stop --quiet --pidfile /var/run/${NAME}.pid \
                        --oknodo

                sleep 1

                start-stop-daemon --start --quiet --pidfile /var/run/${NAME}.pid \
                        --chuid ${USER} --background --make-pidfile \
            --exec ${DAEMON} -- --config=${CONFIG}  \


                echo "${NAME}."
                ;;

        restart-with-update)
                start-stop-daemon --stop --quiet --pidfile /var/run/${NAME}.pid \
                        --oknodo

                sleep 1

                if [ -z ${2} ]
                then
                    echo -n "Restarting ${DESC}: "
                    start-stop-daemon --start --quiet --pidfile /var/run/${NAME}.pid \
                        --chuid ${USER} --background --make-pidfile \
            --exec ${DAEMON} -- --config=${CONFIG}  \
                else
                    if [ -z ${3} ]
                    then
                        echo -n "Restarting with update ${DESC} all modules on database ${2}: "
                        start-stop-daemon --start --quiet --pidfile /var/run/${NAME}.pid \
                                --chuid ${USER} --background --make-pidfile \
                --exec ${DAEMON} -- --config=${CONFIG}  \
                                    --update=all -d ${2}
                    else
                        echo -n "Restarting with update ${DESC} modules ${3} on database ${2}: "
                        start-stop-daemon --start --quiet --pidfile /var/run/${NAME}.pid \
                                --chuid ${USER} --background --make-pidfile \
                --exec ${DAEMON} -- --config=${CONFIG}  \
                                    --update=${3} -d ${2}
                    fi
                fi

                echo "${NAME}."
                ;;

        *)

                N=/etc/init.d/${NAME}
                echo "Usage: ${NAME} {start|stop|restart|force-reload|restart-with-update [database [modules]]}" >&2
                exit 1
                ;;

esac

exit 0
"""
