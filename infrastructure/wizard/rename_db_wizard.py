# -*- coding: utf-8 -*-
from openerp import fields, api, models


class infrastructure_rename_db_name(models.TransientModel):
    _name = "infrastructure.rename_database.name"
    _description = "Infrastructure Rename Database Name Wizard"

    name = fields.Char('New Database Name', size=64, required=True)

    @api.multi
    def action_confirm(self):
        active_id = self._context.get('active_id')
        if not active_id:
            return False
        active_record = self.env['infrastructure.database'].browse(active_id)
        active_record.rename_db(self.name)
