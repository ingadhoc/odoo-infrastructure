# -*- coding: utf-8 -*-

from openerp import netsvc
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from fabric.api import sudo, shell_env, settings
from fabric.contrib.files import exists, append, sed
from fabric.context_managers import hide
from ast import literal_eval
import os
import re


class instance(models.Model):

    """"""
    # TODO agregar bloqueo de volver a estado cancel. Solo se debe poder
    # volver si no existe el path ni el source path y si no existen ambienets
    # activo
    _name = 'infrastructure.instance'
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

    number = fields.Integer(
        string='Number',
        required=True,
        default=1
    )

    name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='main'
    )

    type = fields.Selection(
        [(u'secure', u'Secure'), (u'none_secure', u'None Secure')],
        string='Instance Type',
        required=True,
        default='none_secure'
    )

    xml_rpc_port = fields.Integer(
        string='XML-RPC Port',
        required=True
    )

    xml_rpcs_port = fields.Integer(
        string='XML-RPCS Port'
    )

    longpolling_port = fields.Integer(
        string='Longpolling Port'
    )

    db_filter = fields.Many2one(
        'infrastructure.db_filter',
        string='DB Filter',
        required=True
    )

    user = fields.Char(
        string='User / Service File',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    note = fields.Html(
        string='Note'
    )

    color = fields.Integer(
        string='Color Index'
    )

    addons_path = fields.Text(
        string='Addons Path',
        required=True,
        default='[]'
    )

    conf_file_path = fields.Char(
        string='Config File Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    run_server_command = fields.Char(
        string='Run Server Command',
        required=True,
        default='odoo.py'
    )

    proxy_mode = fields.Boolean(
        string='Proxy Mode?',
        default=True
    )

    logfile = fields.Char(
        string='Log File Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    log_level = fields.Selection([
        (u'info', 'info'), (u'debug_rpc', 'debug_rpc'),
        (u'warn', 'warn'), (u'test', 'test'), (u'critical', 'critical'),
        (u'debug_sql', 'debug_sql'), (u'error', 'error'), (u'debug', 'debug'),
        (u'debug_rpc_answer', 'debug_rpc_answer')],
        string='Log Level'
    )

    workers = fields.Integer(
        string='Workers',
        default=9
    )

    data_dir = fields.Char(
        string='Data Directory',
        readonly=True,
        states={'draft': [('readonly', False)]}
    )

    admin_pass = fields.Char(
        string='Admin Password',
        required=True,
        default='admin'
    )

    unaccent = fields.Boolean(
        string='Enable Unaccent'
    )

    module_load = fields.Char(
        string='Load default modules'
    )

    service_file = fields.Char(
        string='Service/Nginx File Name',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    main_hostname = fields.Char(
        string='Main Hostname',
        required=True
    )

    state = fields.Selection(
        _states_,
        string="State",
        default='draft'
    )

    instance_host_ids = fields.One2many(
        'infrastructure.instance_host',
        'instance_id',
        string='Hosts'
    )

    environment_id = fields.Many2one(
        'infrastructure.environment',
        string='Environment',
        ondelete='cascade',
        required=True
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
        store=True,
        readonly=False,
        required=True
    )

    user = fields.Char(
        string='User',
        compute='_get_user',
        store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    service_file = fields.Char(
        string='Service File Name',
        compute='_get_user',
        store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    conf_file_path = fields.Char(
        string='Config. File Path',
        compute='_get_paths',
        store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    data_dir = fields.Char(
        string='Data Dir',
        compute='_get_paths',
        store=True,
        readonly=True,
        required=False,
        states={'draft': [('readonly', False)]}
    )

    logfile = fields.Char(
        string='Log File Path',
        compute='_get_paths',
        store=True,
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]}
    )

    xml_rpc_port = fields.Integer(
        string='XML-RPC Port',
        compute='_get_ports',
        store=True,
        readonly=False,
        required=True
    )

    xml_rpcs_port = fields.Integer(
        string='XML-RPCS Port',
        compute='_get_ports',
        store=True,
        readonly=False
    )

    longpolling_port = fields.Integer(
        string='Longpolling Port',
        compute='_get_ports',
        store=True,
        readonly=False
    )

    database_count = fields.Integer(
        string='# Databases',
        compute='_get_databases'
    )

    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        related='environment_id.server_id',
        store=True,
        readonly=True
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
        ('data_dir_uniq', 'unique(data_dir, server_id)',
            'Data Dir must be unique per server!'),
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
    def get_user(self):
        """"""
        raise NotImplementedError

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
        addons_path = []
        try:
            for repository in self.environment_id.environment_repository_ids:
                if repository.addons_paths:
                    for addon_path in literal_eval(repository.addons_paths):
                        addons_path.append(addon_path)
        except:
            print 'error al querer calcular el addons_path'
        if not addons_path:
            addons_path = '[]'
        self.addons_path = addons_path

    @api.one
    @api.depends('name', 'environment_id', 'environment_id.name')
    def _get_user(self):
        user = False
        if self.name and self.environment_id.name:
            user = self.environment_id.name + '-' + self.name
        self.user = user
        self.service_file = user

    @api.one
    @api.depends('number', 'environment_id', 'environment_id.number')
    def _get_ports(self):
        xml_rpc_port = False
        xml_rpcs_port = False
        longpolling_port = False
        if self.environment_id.number and self.number:
            prefix = str(self.environment_id.number) + str(self.number)
            xml_rpc_port = int(prefix + '1')
            xml_rpcs_port = int(prefix + '2')
            longpolling_port = int(prefix + '3')
        self.xml_rpc_port = xml_rpc_port
        self.xml_rpcs_port = xml_rpcs_port
        self.longpolling_port = longpolling_port

    @api.one
    @api.depends('name', 'environment_id', 'environment_id.path',)
    def _get_paths(self):
        conf_file_path = False
        logfile = False
        data_dir = False
        # TODO notar que aca se toma el valor del campo function y no el valor
        # stored en el path, hay que arreglarlo
        if self.environment_id.path and self.name:
            conf_file_path = os.path.join(
                self.environment_id.path, 'conf_' + self.name) + '.conf'
            logfile = os.path.join(
                self.environment_id.path, 'log_' + self.name) + '.log'
            data_dir = os.path.join(
                self.environment_id.path, '.local/share/odoo', self.name)
        self.conf_file_path = conf_file_path
        self.logfile = logfile
        self.data_dir = data_dir

    # Actions
    @api.multi
    def create_instance(self):
        self.update_nginx_site()
        self.create_user()
        self.create_pg_user()
        self.update_conf_file()
        self.update_service_file()
        self.start_service()
        self.run_on_start()
        self.signal_workflow('sgn_to_active')

    @api.one
    def update_conf_file(self):
        self.environment_id.server_id.get_env()
        # TODO: chequear si el servicio esta levantado y bajarlo,
        # si estaba levantado volver a iniciarlo
        # self.stop_service()
        if not exists(self.environment_id.path, use_sudo=True):
            raise except_orm(_('No Environment Path!'),
                             _("Environment path '%s' does not exists. \
                                Please create it first!")
                             % (self.environment_id.path))

        command = self.environment_id.path + '/bin/' + self.run_server_command
        command += ' --stop-after-init -s -c ' + self.conf_file_path

        # Remove file if it already exists, we do it so we can put back some
        # booelan values as unaccent
        if exists(self.conf_file_path, use_sudo=True):
            sudo('rm ' + self.conf_file_path)

        addons_path = False
        for addon_path in literal_eval(self.addons_path):
            if not exists(addon_path, use_sudo=True):
                raise except_orm(_('Addons path does not exist!'),
                                 _("Addons path '%s' does not exists. \
                                    Please create it first!") % (addon_path))
            if not addons_path:
                addons_path = addon_path
            addons_path += ',' + addon_path

        if addons_path:
            command += ' --addons-path=' + addons_path
        command += ' --db-filter=' + self.db_filter.rule
        command += ' --xmlrpc-port=' + str(self.xml_rpc_port)
        command += ' --logfile=' + self.logfile

        # TODO ver si no da error este parametro en algunas versiones de odoo y
        # sacarlo
        if self.environment_id.environment_version_id.name in ('8.0', 'master'):
            if self.data_dir:
                command += ' --data-dir=' + self.data_dir
            if self.longpolling_port:
                command += ' --longpolling-port=' + str(self.longpolling_port)

        if self.module_load:
            command += ' --load=' + self.module_load

        if self.unaccent:
            command += ' --unaccent'

        if self.proxy_mode:
            command += ' --proxy-mode'

        if self.workers:
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
            sudo('chown ' + self.user + ':odoo -R ' + self.environment_id.path)
            print
            print command
            print
            eggs_dir = '/home/%s/.python-eggs' % self.user
            if not exists(eggs_dir, use_sudo=True):
                sudo('mkdir %s' % eggs_dir, user=self.user, group='odoo')
            with shell_env(PYTHON_EGG_CACHE=eggs_dir):
                sudo('chmod g+rw -R ' + self.environment_id.path)
                sudo(command, user=self.user, group='odoo')
        except:
            raise except_orm(
                _('Error creating configuration file!'),
                _("Try stopping the instance and then try again.")
            )
        sed(self.conf_file_path,
            '(admin_passwd).*', 'admin_passwd = ' + self.admin_pass,
            use_sudo=True
        )

    @api.multi
    def update_service_file(self):
        # Build file
        daemon = os.path.join(
            self.environment_id.path, 'bin', self.run_server_command)
        service_file = template_service_file % (
            self.user, self.conf_file_path, daemon)

        # Check service_path exists
        service_path = self.environment_id.server_id.service_path
        if not exists(service_path):
            raise except_orm(_('Server Service Folder not Found!'),
                             _("Service folter '%s' not found. \
                                Please create it first!") % (service_path))

        # Check if service already exist
        service_file_path = os.path.join(service_path, self.service_file)
        if exists(service_file_path, use_sudo=True):
            sudo('rm ' + service_file_path)

        # Create file
        append(service_file_path, service_file, use_sudo=True,)
        sudo('chmod 777 ' + service_file_path)

    @api.one
    def create_user(self):
        self.environment_id.server_id.get_env()
        sudo('adduser --system ' + self.user)
        try:
            sudo("sudo usermod -a -G %s %s" % (
                self.environment_id.server_id.instance_user_group, self.user))
        except:
            raise Warning(_("Error changing group '%s' of user '%s'. \
                Please verifify that user and group exists!") % (
                self.environment_id.server_id.instance_user_group, self.user))

    @api.one
    def create_pg_user(self):
        self.environment_id.server_id.get_env()
        # TODO si ya existe el usuario no habria que crearlo
        try:
            sudo('sudo -u postgres createuser -d -R -S ' + self.user)
        except:
            print 'PG user already exists'

    @api.one
    def start_service(self):
        self.environment_id.server_id.get_env()
        sudo('service ' + self.service_file + ' start')

    @api.one
    def stop_service(self):
        self.environment_id.server_id.get_env()
        sudo('service ' + self.service_file + ' stop')

    @api.one
    def restart_service(self):
        self.environment_id.server_id.get_env()
        sudo('service ' + self.service_file + ' restart')

    @api.one
    def run_on_start(self):
        self.environment_id.server_id.get_env()
        sudo('update-rc.d  ' + self.service_file + ' defaults')

    @api.one
    def stop_run_on_start(self):
        self.environment_id.server_id.get_env()
        sudo('update-rc.d  -f ' + self.service_file + ' remove')

    @api.one
    def update_nginx_site(self):
        self.environment_id.server_id.get_env()
        if self.type == 'none_secure':
            listen_port = 80
        else:
            raise Warning(_('Secure instances not implemented yet!'))

        server_names = ''
        for host in self.instance_host_ids:
            server_names += host.name + ' '

        if server_names == '':
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
            listen_port, server_names,
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
        self.environment_id.server_id.restart_nginx()

# TODO llevar esto a un archivo y leerlo de alli
nginx_long_polling_template = """
    location /longpolling {
        proxy_pass   http://127.0.0.1:%i;
    }
"""
nginx_site_template = """
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
