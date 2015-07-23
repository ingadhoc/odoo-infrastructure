# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


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
        compute=False,
        )
    installed_version = fields.Char(
        'Latest Version',
        )
    latest_version = fields.Char(
        'Installed Version',
        )
    published_version = fields.Char(
        'Published Version',
        )
    auto_install = fields.Boolean(
        'Auto Install',
        )

    @api.multi
    def check_one_database(self):
        database = set([x.database_id for x in self])
        if len(database) != 1:
            raise Warning(_(
                'You can only use this function in modules of the same\
                database'))
        return database.pop()

    @api.multi
    def install_modules(self):
        database = self.check_one_database()
        client = self.database_id.get_client()
        # No se como correrlo sin hacer el for
        for module in self:
            client.install(module.name)
        database.update_modules_data(fields=['state'])

    @api.multi
    def upgrade_modules(self):
        database = self.check_one_database()
        client = self.database_id.get_client()
        # No se como correrlo sin hacer el for
        for module in self:
            client.upgrade(module.name)
        database.update_modules_data(fields=['state'])

    @api.multi
    def uninstall_modules(self):
        database = self.check_one_database()
        client = self.database_id.get_client()
        # No se como correrlo sin hacer el for
        for module in self:
            client.uninstall(module.name)
        database.update_modules_data(fields=['state'])
