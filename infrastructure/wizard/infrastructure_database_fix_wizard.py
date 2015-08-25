# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import Warning
from openerp.addons.models.database import _update_state_vals


class infrastructure_database_fix_wizard(models.TransientModel):
    _name = "infrastructure.database.fix.wizard"
    _description = "infrastructure.database.fix.wizard"

    def _get_database(self):
        database_id = self.env.context.get('active_id', False)
        return self.env['infrastructure.database'].browse(database_id)

    update_state = fields.Selection(
        _update_state_vals,
        'Update Status',
        readonly=True,
        )
    init_and_conf_modules = fields.Text(
        string='Modules to Init',
        readonly=True
        )
    update_modules = fields.Char(
        string='Modules to Update',
        readonly=True
        )
    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        default=_get_database,
        readonly=True,
        ondelete='cascade',
        required=True,
        )

    @api.onchange('database_id')
    def change_db_passwd(self):
        update_state = self.database_id.refresh_update_state()
        state = update_state.get('state', False)
        detail = update_state.get('detail', False)
        init_and_conf_modules = detail.get('init_and_conf_modules')
        update_modules = detail.get('update_modules')
        optional_update_modules = detail.get('optional_update_modules')
        self.init_and_conf_modules = init_and_conf_modules
        self.update_modules = update_modules + optional_update_modules
        self.update_state = state

    @api.multi
    def confirm(self):
        self.ensure_one()
        if self.state not in ['init_and_conf', 'update', 'optional_update']:
            raise Warning(_(
                'Fix form state "%s" not implemented yet. You should fix it '
                'manually') % (self.state))
        return self.database_id.fix_db(
            self.init_and_conf_modules, self.update_modules)
