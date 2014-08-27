# -*- coding: utf-8 -*-

from openerp import models, fields


class service_command(models.Model):
    """"""

    _name = 'infrastructure.service_command'
    _description = 'service_command'

    name = fields.Char(
        string='name',
        required=True
    )

    command = fields.Char(
        string='command',
        required=True
    )

    service_id = fields.Many2one(
        'infrastructure.service',
        string='Service',
        ondelete='cascade',
        required=True
    )
