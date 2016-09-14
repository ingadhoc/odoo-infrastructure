# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class repository_branch(models.Model):
    """"""

    _name = 'infrastructure.repository_branch'
    _description = 'repository_branch'

    name = fields.Char(
        string='Name',
        required=True
    )
    repository_ids = fields.Many2many(
        'infrastructure.repository',
        'infrastructure_repository_ids_branch_ids_rel',
        'repository_branch_id',
        'repository_id',
        string='repository_ids'
    )
