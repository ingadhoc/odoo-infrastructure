# -*- coding: utf-8 -*-

from openerp import models, fields


class environment_version(models.Model):
    """"""

    _odoo_versions_ = [
        ('6.1', 'OpenERP 6.1'),
        ('7.0', 'OpenERP 7.0'),
        ('saas-3', 'OpenERP saas-3'),
        ('saas-4', 'OpenERP saas-4'),
        ('saas-5', 'OpenERP saas-5'),
        ('master', 'Odoo master'),
        ('8.0', 'Odoo 8.0'),
    ]

    _name = 'infrastructure.environment_version'
    _description = 'environment_version'

    name = fields.Selection(
        _odoo_versions_,
        string='Name',
        required=True
    )

    default_branch_id = fields.Many2one(
        'infrastructure.repository_branch',
        string='Default Branch',
        required=True
    )


environment_version()
