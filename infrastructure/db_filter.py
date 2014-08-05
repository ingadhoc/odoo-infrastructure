# -*- coding: utf-8 -*-

from openerp import models, fields

class db_filter(models.Model):
    """"""

    _name = 'infrastructure.db_filter'
    _description = 'db_filter'

    name = fields.Char(
        string='Name',
        required=True
    )

    rule = fields.Char(
        string='Rule',
        required=True
    )


db_filter()
