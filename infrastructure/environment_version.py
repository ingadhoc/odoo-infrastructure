# -*- coding: utf-8 -*-

from openerp import models, fields


class environment_version(models.Model):
    """"""

    _name = 'infrastructure.environment_version'
    _description = 'environment_version'

    name = fields.Char(
        string='Name',
        required=True
    )

    default_branch_id = fields.Many2one(
        'infrastructure.repository_branch',
        string='Default Branch',
        required=True
    )
