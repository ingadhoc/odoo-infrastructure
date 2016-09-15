# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, models
# from openerp.exceptions import Warning
from openerp.addons.infrastructure.models.database import _update_state_vals
# from ast import literal_eval
import logging
_logger = logging.getLogger(__name__)


class infrastructure_database_fix_wizard(models.TransientModel):
    _name = "infrastructure.database.fix.wizard"
    _description = "infrastructure.database.fix.wizard"

    def _get_database(self):
        database_id = self.env.context.get('active_id', False)
        return self.env['infrastructure.database'].browse(database_id)

    update_state = fields.Selection(
        _update_state_vals,
        'Update Status',
        compute='get_data',
    )
    update_state_detail = fields.Text(
        'Update Status Detail',
        compute='get_data',
    )
    init_and_conf_required = fields.Text(
        string='Init and Config Required Modules',
        compute='get_data',
        help='Sometimes, modules on this state need adittional configurations'
        ' or others modules to be installed manually. Check module changes.'
    )
    modules_to_update = fields.Char(
        string='Modules To Update',
        compute='get_data',
    )
    modules_to_install = fields.Char(
        string='Modules To Install',
        compute='get_data',
    )
    modules_to_remove = fields.Char(
        string='Modules To Remove',
        compute='get_data',
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
    def get_data(self):
        update_state = self.database_id.refresh_update_state()
        state = update_state.get('state', False)
        detail = update_state.get('detail', False)
        self.update_state = state
        self.update_state_detail = detail

        init_and_conf_required = detail.get('init_and_conf_required', [])
        update_required = detail.get('update_required', [])
        optional_update = detail.get('optional_update', [])
        on_to_install = detail.get('on_to_install', [])
        on_to_remove = detail.get('on_to_remove', [])
        installed_uninstallable = detail.get('installed_uninstallable', [])
        on_to_upgrade = detail.get('on_to_upgrade', [])
        unmet_deps = detail.get('unmet_deps', [])
        uninstalled_auto_install = detail.get('uninstalled_auto_install', [])
        not_installable = detail.get('not_installable', [])

        self.init_and_conf_required = init_and_conf_required
        self.modules_to_update = (
            update_required + optional_update + on_to_upgrade)
        self.modules_to_install = (
            on_to_install + unmet_deps + uninstalled_auto_install)
        self.modules_to_remove = (
            on_to_remove + not_installable + installed_uninstallable)

    @api.multi
    def confirm(self):
        self.ensure_one()
        # if self.update_state not in [
        #         'init_and_conf', 'update', 'optional_update']:
        #     raise Warning(_(
        #         'Fix form state "%s" not implemented yet. You should fix it '
        #         'manually') % (self.update_state))
        # return self.database_id.fix_db(
        #     literal_eval(self.init_and_conf_modules),
        #     literal_eval(self.update_modules))
        _logger.info('Confirmed fix db for db %s' % self.database_id.name)
        return self.database_id.fix_db()
