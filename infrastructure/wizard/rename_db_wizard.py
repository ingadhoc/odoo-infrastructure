# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, api, models


class infrastructure_rename_db_name(models.TransientModel):
    _name = "infrastructure.rename_database.name"
    _description = "Infrastructure Rename Database Name Wizard"

    name = fields.Char(
        'New Database Name',
        size=64,
        required=True
    )
    # database_type_id = fields.Many2one(
    #     'infrastructure.database_type',
    #     string='Database Type',
    #     required=True,
    # )

# TODO rmeove as we no longer use db prefix
    # @api.onchange('database_type_id')
    # def onchange_database_type_id(self):
    #     if self.database_type_id:
    #         self.name = self.database_type_id.prefix + '_'
    # TODO send suggested backup data

    @api.multi
    def action_confirm(self):
        active_id = self._context.get('active_id')
        if not active_id:
            return False
        active_record = self.env['infrastructure.database'].browse(active_id)
        active_record.rename_db(self.name)
        # active_record.database_type_id = self.database_type_id
