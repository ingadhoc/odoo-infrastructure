# -*- coding: utf-8 -*-

from openerp import models, fields


class command(models.Model):

    """"""

    _name = 'infrastructure.command'
    _description = 'command'
    _order = "sequence"

    sequence = fields.Integer(
        string='sequence',
        default=10,
        )
    name = fields.Char(
        string='Name',
        required=True
        )
    command = fields.Text(
        string='Command',
        required=True
        )
