# -*- coding: utf-8 -*-
{
    'name': 'Infrastructure and Contracts Integration',
    'version': '1.0',
    'description': """
Infrastructure Contract
=======================
Provides integration between infrastructure module and web_support modules.
Add on infrastructure databases a link to contracts and the posibility to
upload the contract to the database.
Destiny database must have web_support_client module installed
    """,
    'category': u'base.module_category_knowledge_management',
    'author': u'ADHOC SA',
    'website': 'www.ingadhoc.com',
    'license': 'AGPL-3',
    'depends': [
        'infrastructure',
        'account_analytic_analysis',
    ],
    'sequence': 14,
    'summary': '',
    'installable': True,
    'auto_install': True,
    'application': False,
    'images': [],
    'data': [
        'database_view.xml',
    ],
    'demo': [],
    'test': [],
}
