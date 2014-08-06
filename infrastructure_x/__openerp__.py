# -*- coding: utf-8 -*-

{
    'name': 'Infrastructure Management',
    'version': '1.0',
    'category': '',
    'sequence': 14,
    'summary': '',
    'description': """
        Infrastructure Management
        =========================
        Require:
        + pip install openerp-client-lib
        + pip install Fabric
    """,
    'author':  'Ingenieria ADHOC',
    'website': 'www.ingadhoc.com',
    'images': [],
    'depends': ['infrastructure'],
    'data': [
        'wizard/duplicate_db_wizard_view.xml',
        'view/server_view.xml',
        'view/command_view.xml',
        'view/environment_view.xml',
        'view/server_configuration_command_view.xml',
        'view/server_repository_view.xml',
        'view/environment_repository_view.xml',
        'view/instance_view.xml',
        'view/database_view.xml',
        'view/instance_host_view.xml',
        'data/cron.xml',
        'data/db_back_up_policy.xml',
    ],
    'demo': [
        'data/demo/res.partner.csv',
        'data/demo/infrastructure.repository_branch.csv',
        'data/demo/infrastructure.repository.csv',
        'data/demo/infrastructure.server_configuration.csv',
        'data/demo/infrastructure.server.csv',
        'data/demo/infrastructure.server_hostname.csv',
        'data/demo/infrastructure.environment_version.csv',
        'data/demo/infrastructure.environment.csv',
        'data/demo/infrastructure.db_filter.csv',
        'data/demo/infrastructure.server_repository.csv',
        'data/demo/infrastructure.instance.csv',
        'data/demo/infrastructure.instance_host.csv',
        'data/demo/infrastructure.server_configuration_command.csv',
    ],
    'test': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
