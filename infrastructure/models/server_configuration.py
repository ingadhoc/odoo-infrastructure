# -*- coding: utf-8 -*-
from openerp import models, fields


class server_configuration(models.Model):
    """"""

    _name = 'infrastructure.server_configuration'
    _description = 'server_configuration'

    name = fields.Char(
        string='Name',
        required=True
        )
    distrib_codename = fields.Char(
        string='Distribution Codename',
        required=True
        )
    install_command_ids = fields.One2many(
        'infrastructure.server_configuration_command',
        'server_configuration_id',
        string='Installation Commands',
        )
    server_ids = fields.One2many(
        'infrastructure.server',
        'server_configuration_id',
        string='server_ids'
        )
