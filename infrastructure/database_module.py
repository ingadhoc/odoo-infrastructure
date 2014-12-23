# -*- coding: utf-8 -*-
from openerp import models, fields


class database(models.Model):

    """"""
    _name = 'infrastructure.database.module'
    _inherit = 'infrastructure.base.module'
    _description = 'Database Module'

    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        ondelete='cascade',
        readonly=True,
        required=True,
    )
    state = fields.Selection([
        ('uninstallable', 'Not Installable'),
        ('uninstalled', 'Not Installed'),
        ('installed', 'Installed'),
        ('to upgrade', 'To be upgraded'),
        ('to remove', 'To be removed'),
        ('to install', 'To be installed')
        ],
        'Status',
        readonly=True,
        required=True,
        compute=False,
    )
    installed_version = fields.Char(
        'Latest Version',
        required=True,
    )
    latest_version = fields.Char(
        'Installed Version',
        required=True,
    )
    published_version = fields.Char(
        'Published Version',
    )
    auto_install = fields.Boolean(
        'Auto Install',
    )
