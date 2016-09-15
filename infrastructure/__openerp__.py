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
    'name': 'Odoo Infrastructure Management',
    'version': '9.0.1.0.0',
    'category': 'base.module_category_knowledge_management',
    'author': 'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'mail',
        'web_widget_many2many_tags_multi_selection',
        'server_mode',
        # 'web_ir_actions_act_window_message',
    ],
    'external_dependencies': {
        'python': ['fabric', 'fabtools', 'erppeek']
    },
    'data': [
        'wizard/duplicate_db_wizard_view.xml',
        'wizard/infrastructure_database_email_wizard_view.xml',
        'wizard/change_db_passwd_wizard_view.xml',
        'wizard/restore_database_wizard_view.xml',
        'wizard/rename_db_wizard_view.xml',
        'wizard/copy_data_from_instance_view.xml',
        'wizard/duplicate_instance_wizard_view.xml',
        'wizard/restore_from_file_view.xml',
        'wizard/infrastructure_database_backup_now_view.xml',
        'wizard/infrastructure_database_drop_wizard_view.xml',
        'wizard/infrastructure_instance_delete_wizard_view.xml',
        'wizard/infrastructure_database_fix_wizard_view.xml',
        'wizard/infrastructure_check_module_version_view.xml',
        'wizard/instance_update_add_instances_view.xml',
        'security/infrastructure_group.xml',
        'view/infrastructure_menuitem.xml',
        'view/base_module_view.xml',
        'view/server_hostname_view.xml',
        'view/instance_host_view.xml',
        'view/partner_view.xml',
        'view/mailserver_view.xml',
        'view/repository_view.xml',
        'view/odoo_version_view.xml',
        'view/database_view.xml',
        'view/db_filter_view.xml',
        'view/instance_view.xml',
        'view/instance_update_view.xml',
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
        'data/ir_parameter.xml',
        'data/email_template.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'demo': [
        'demo/infrastructure.repository_branch.csv',
        'demo/infrastructure.repository.csv',
        'demo/infrastructure.server_configuration.csv',
        'demo/infrastructure.server_configuration_command.csv',
        'demo/infrastructure.server.csv',
        'demo/infrastructure.server_hostname.csv',
        'demo/infrastructure.odoo_version.csv',
        'demo/infrastructure.docker_image.csv',
        'demo/infrastructure.docker_image.tag.csv',
        'demo/infrastructure.environment.csv',
        'demo/infrastructure.db_filter.csv',
        'demo/infrastructure.database_type.csv',
        'demo/infrastructure.instance.csv',
        'demo/infrastructure.instance_host.csv',
        'demo/infrastructure.database.csv',
        'demo/infrastructure.base.module.csv',
        'demo/ir_parameter_demo.xml',
    ],
}
