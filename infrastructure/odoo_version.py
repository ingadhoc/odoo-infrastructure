# -*- coding: utf-8 -*-

from openerp import models, fields


class odoo_version(models.Model):
    """"""

    _name = 'infrastructure.odoo_version'
    _description = 'odoo_version'

    # _odoo_versions_ = [
    #     ('6.1', 'OpenERP 6.1'),
    #     ('7.0', 'OpenERP 7.0'),
    #     ('saas-3', 'OpenERP saas-3'),
    #     ('saas-4', 'OpenERP saas-4'),
    #     ('saas-5', 'OpenERP saas-5'),
    #     ('master', 'Odoo master'),
    #     ('8.0', 'Odoo 8.0'),
    # ]

    name = fields.Char(
        # _odoo_versions_,
        string='Name',
        required=True
    )
    default_branch_id = fields.Many2one(
        'infrastructure.repository_branch',
        string='Default Branch',
        required=True
    )
    sufix = fields.Char(
        string='Sufix',
        required=True
    )
