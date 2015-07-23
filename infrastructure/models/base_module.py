# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class database(models.Model):

    """"""
    _name = 'infrastructure.base.module'
    _description = 'Infrastructure Base Module'

    name = fields.Char(
        'Name',
        required=True,
        )
    shortdesc = fields.Char(
        'Module Name',
        )
    author = fields.Char(
        'Author',
        )
    default_on_new_db = fields.Boolean(
        string='Default on New Database',
        default=True,
        )
    sequence = fields.Integer(
        'Sequence',
        default=10,
        )
    state = fields.Selection([
        ('not_available', 'Not Available'),
        ('uninstallable', 'Not Installable'),
        ('uninstalled', 'Not Installed'),
        ('installed', 'Installed'),
        ('to upgrade', 'To be upgraded'),
        ('to remove', 'To be removed'),
        ('to install', 'To be installed')
        ],
        'Status',
        compute='get_state',
        )

    @api.one
    def get_state(self):
        database_id = self._context.get('database_id', False)
        state = False
        if database_id:
            domain = [
                ('name', '=', self.name), ('database_id', '=', database_id)]
            db_modules = self.env[
                'infrastructure.database.module'].search(domain)
            state = db_modules and db_modules[0].state or 'not_available'
        self.state = state
