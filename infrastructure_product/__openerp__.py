# -*- coding: utf-8 -*-

{
    'name': 'Infrastructure Product',
    'version': '1.0',
    'description': u'Infrastructure Product',
    'category': u'base.module_category_knowledge_management',
    'author': u'ADHOC SA',
    'website': 'www.adhoc.com.ar',
    'license': 'AGPL-3',
    'depends': [
        'infrastructure',
        'project_issue',
    ],
    'sequence': 14,
    'summary': '',
    'installable': True,
    'auto_install': False,
    'application': False,
    'images': [],
    'data': [
        'product_view.xml',
        'database_view.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'test': [],
}
