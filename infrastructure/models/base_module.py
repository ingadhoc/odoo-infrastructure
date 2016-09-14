# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class base_module(models.Model):

    """"""
    _name = 'infrastructure.base.module'
    _description = 'Infrastructure Base Module'

    name = fields.Char(
        'Name',
        required=True,
    )
    shortdesc = fields.Char(
        'Module Name',
    )
    author = fields.Char(
        'Author',
    )
    sequence = fields.Integer(
        'Sequence',
        default=10,
    )
