# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.tools.parse_version import parse_version


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
    update_state = fields.Selection([
        ('to_init_and_conf', 'To Init and Config'),
        ('to_update', 'To Update'),
        ('optional_update', 'Optional Updaet'),
        ('ok', 'Ok'),   # ok if not installed or up to date
        ],
        'Update Status',
        readonly=True,
        compute='get_update_state',
        store=True,
        )

    @api.one
    @api.depends('installed_version', 'latest_version')
    def get_update_state(self):
        """
        We use version number Guidelines x.y.z from
        https://github.com/OCA/maintainer-tools/blob/master/CONTRIBUTING.md#version-numbers
        """
        update_state = 'ok'
        if self.installed_version and self.latest_version:
            (ix, iy, iz) = self.get_versions(self.installed_version)
            (lx, ly, lz) = self.get_versions(self.latest_version)
            if ix > lx:
                update_state = 'to_init_and_conf'
            elif iy > ly:
                update_state = 'to_update'
            elif iz > lz:
                update_state = 'optional_update'
        self.update_state = update_state

    @api.model
    def get_versions(self, version):
        # we take out mayor version
        parsed = list(parse_version(version)[2:])
        x = parsed and parsed.pop(0) or False
        y = parsed and parsed.pop(0) or False
        z = parsed and parsed.pop(0) or False
        return (x, y, z)

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
