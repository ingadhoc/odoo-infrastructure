# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2015  ADHOC SA  (http://www.adhoc.com.ar)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Infrastructure',
    'version': '0.2.0',
    'description': 'Infrastructure Management',
    'category': 'base.module_category_knowledge_management',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': ['mail'],
    'external_dependencies': {
        'python': ['fabric', 'fabtools', 'erppeek']
        },
    'data': [
        'wizard/duplicate_db_wizard_view.xml',
        'wizard/change_db_passwd_wizard_view.xml',
        'wizard/restore_database_wizard_view.xml',
        'wizard/rename_db_wizard_view.xml',
        'wizard/copy_data_from_instance_view.xml',
        'wizard/duplicate_instance_wizard_view.xml',
        'wizard/restore_from_file_view.xml',
        'security/infrastructure_group.xml',
        'view/infrastructure_menuitem.xml',
        'view/base_module_view.xml',
        'view/server_hostname_view.xml',
        'view/instance_host_view.xml',
        'view/partner_view.xml',
        'view/mailserver_view.xml',
        'view/repository_view.xml',
        'view/odoo_version_view.xml',
        'view/database_module_view.xml',
        'view/database_view.xml',
        'view/db_filter_view.xml',
        'view/instance_view.xml',
        'view/repository_branch_view.xml',
        'view/server_configuration_view.xml',
        'view/server_change_view.xml',
        'view/database_type_view.xml',
        'view/database_user_view.xml',
        'view/command_view.xml',
        'view/server_configuration_command_view.xml',
        'view/environment_view.xml',
        'view/server_view.xml',
        'view/database_backup_view.xml',
        'view/docker_image_view.xml',
        'view/server_docker_image_view.xml',
        'view/instance_repository_view.xml',
        'data/cron.xml',
        'workflow/database_workflow.xml',
        'workflow/environment_workflow.xml',
        'workflow/instance_workflow.xml',
        'workflow/server_workflow.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'demo': [
        # TODO fix demo data
        # 'data/demo/res.partner.csv',
        # 'data/demo/infrastructure.repository_branch.csv',
        # 'data/demo/infrastructure.repository.csv',
        # 'data/demo/infrastructure.server_configuration.csv',
        # 'data/demo/infrastructure.server.csv',
        # 'data/demo/infrastructure.server_hostname.csv',
        # 'data/demo/infrastructure.odoo_version.csv',
        # 'data/demo/infrastructure.environment.csv',
        # 'data/demo/infrastructure.db_filter.csv',
        # 'data/demo/infrastructure.database_type.csv',
        # 'data/demo/infrastructure.instance.csv',
        # 'data/demo/infrastructure.instance_host.csv',
        # 'data/demo/infrastructure.server_configuration_command.csv',
        # 'data/demo/infrastructure.database.csv'
        ],
    }
