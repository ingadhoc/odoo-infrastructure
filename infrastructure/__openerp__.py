# -*- coding: utf-8 -*-
##############################################################################
#
#    Infrastructure
#    Copyright (C) 2014 Ingenieria ADHOC
#    No email
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


{   'active': False,
    'author': u'Ingenieria ADHOC',
    'category': u'base.module_category_knowledge_management',
    'demo_xml': [],
    'depends': [u'mail'],
    'description': u'Infrastructure',
    'init_xml': [],
    'installable': True,
    'license': 'AGPL-3',
    'name': u'Infrastructure',
    'test': [],
    'update_xml': [   u'security/infrastructure_group.xml',
                      u'view/server_hostname_view.xml',
                      u'view/instance_host_view.xml',
                      u'view/db_filter_view.xml',
                      u'view/server_repository_view.xml',
                      u'view/partner_view.xml',
                      u'view/mailserver_view.xml',
                      u'view/repository_view.xml',
                      u'view/service_view.xml',
                      u'view/environment_version_view.xml',
                      u'view/environment_repository_view.xml',
                      u'view/db_back_up_policy_view.xml',
                      u'view/environment_view.xml',
                      u'view/instance_view.xml',
                      u'view/service_command_view.xml',
                      u'view/repository_branch_view.xml',
                      u'view/server_configuration_view.xml',
                      u'view/server_change_view.xml',
                      u'view/server_service_view.xml',
                      u'view/database_type_view.xml',
                      u'view/database_view.xml',
                      u'view/server_view.xml',
                      u'view/command_view.xml',
                      u'view/environment_version_command_view.xml',
                      u'view/server_configuration_command_view.xml',
                      u'view/infrastructure_menuitem.xml',
                      u'data/server_hostname_properties.xml',
                      u'data/instance_host_properties.xml',
                      u'data/db_filter_properties.xml',
                      u'data/server_repository_properties.xml',
                      u'data/partner_properties.xml',
                      u'data/mailserver_properties.xml',
                      u'data/repository_properties.xml',
                      u'data/service_properties.xml',
                      u'data/environment_version_properties.xml',
                      u'data/environment_repository_properties.xml',
                      u'data/db_back_up_policy_properties.xml',
                      u'data/environment_properties.xml',
                      u'data/instance_properties.xml',
                      u'data/service_command_properties.xml',
                      u'data/repository_branch_properties.xml',
                      u'data/server_configuration_properties.xml',
                      u'data/server_change_properties.xml',
                      u'data/server_service_properties.xml',
                      u'data/database_type_properties.xml',
                      u'data/database_properties.xml',
                      u'data/server_properties.xml',
                      u'data/command_properties.xml',
                      u'data/environment_version_command_properties.xml',
                      u'data/server_configuration_command_properties.xml',
                      u'data/server_hostname_track.xml',
                      u'data/instance_host_track.xml',
                      u'data/db_filter_track.xml',
                      u'data/server_repository_track.xml',
                      u'data/partner_track.xml',
                      u'data/mailserver_track.xml',
                      u'data/repository_track.xml',
                      u'data/service_track.xml',
                      u'data/environment_version_track.xml',
                      u'data/environment_repository_track.xml',
                      u'data/db_back_up_policy_track.xml',
                      u'data/environment_track.xml',
                      u'data/instance_track.xml',
                      u'data/service_command_track.xml',
                      u'data/repository_branch_track.xml',
                      u'data/server_configuration_track.xml',
                      u'data/server_change_track.xml',
                      u'data/server_service_track.xml',
                      u'data/database_type_track.xml',
                      u'data/database_track.xml',
                      u'data/server_track.xml',
                      u'data/command_track.xml',
                      u'data/environment_version_command_track.xml',
                      u'data/server_configuration_command_track.xml',
                      u'workflow/database_workflow.xml',
                      u'workflow/environment_workflow.xml',
                      u'workflow/instance_workflow.xml',
                      u'workflow/server_workflow.xml',
                      'security/ir.model.access.csv'],
    'version': 'No version',
    'website': ''}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
