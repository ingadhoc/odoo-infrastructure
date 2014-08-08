# -*- coding: utf-8 -*-

from openerp import models, fields


class server_service(models.Model):
    """"""

    _name = 'infrastructure.server_service'
    _description = 'server_service'

    service_id = fields.Many2one(
        'infrastructure.service',
        string='Service',
        required=True
    )

    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        required=True
    )


server_service()
