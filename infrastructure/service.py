# -*- coding: utf-8 -*-

from openerp import models, fields


class service(models.Model):
    """"""

    _name = 'infrastructure.service'
    _description = 'service'

    name = fields.Char(
        string='Name',
        required=True
    )

    note = fields.Text(
        string='Command'
    )

    service_command_ids = fields.One2many(
        'infrastructure.service_command',
        'service_id',
        string='Commands'
    )


service()
