# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class odoo_version(models.Model):
    """"""

    _name = 'infrastructure.odoo_version'
    _description = 'Odoo Version'
    _order = 'sequence'

    name = fields.Char(
        # _odoo_versions_,
        string='Name',
        required=True
    )
    sequence = fields.Integer(
        string='Sequence',
        default=10,
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
