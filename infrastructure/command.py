# -*- coding: utf-8 -*-

from openerp import models, fields


class command(models.Model):

    """"""

    _name = 'infrastructure.command'
    _description = 'command'

    sequence = fields.Integer(string='sequence')

    type = fields.Selection(
        [(u'installation', 'installation'), (u'maintenance', 'maintenance')],
        string='Type',
        required=True,
        default='maintenance'
    )

    name = fields.Char(
        string='Name',
        required=True
    )

    command = fields.Text(
        string='Command',
        required=True
    )

    _order = "sequence"
