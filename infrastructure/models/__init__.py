# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from . import command
from . import repository
from . import repository_branch
from . import odoo_version
from . import base_module
from . import database
from . import database_type
from . import database_backup
from . import database_user
from . import db_filter
from . import environment
from . import instance
from . import instance_repository
from . import instance_host
from . import instance_update
from . import mailserver
from . import server
from . import server_change
from . import server_configuration
from . import server_configuration_command
from . import server_hostname
from . import docker_image
from . import server_docker_image
# To avoid error with auto generated certificates:
try:
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
except:
    print "Could not disable SSL checks on odoo infrastructure"
