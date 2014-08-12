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

    install_command_ids = fields.One2many(
        'infrastructure.server_configuration_command',
        'server_configuration_id',
        string='Installation Commands',
        context={'default_type': 'installation'},
        domain=[('type', '=', 'installation')]
    )

    server_ids = fields.One2many(
        'infrastructure.server',
        'server_configuration_id',
        string='server_ids'
    )

    maint_command_ids = fields.One2many(
        'infrastructure.server_configuration_command',
        'server_configuration_id',
        string='Maintenance Commands',
        context={'default_type': 'maintenance'},
        domain=[('type', '=', 'maintenance')]
    )


server_configuration()
