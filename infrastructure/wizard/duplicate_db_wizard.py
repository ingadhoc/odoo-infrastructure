# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _
from openerp.osv import osv
from openerp.exceptions import Warning


class infrastructure_duplicate_db_wizard(osv.osv_memory):
    _name = "infrastructure.duplicate_db.wizard"
    _description = "Infrastructure Duplicate db Wizard"

    new_db_name = fields.Char(
        string='New db Name',
        required=True
    )
    change_user = fields.Boolean(
        string='Change Instance?'
    )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
    )
    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='Instance',
        domain=[('state', '=', 'active')],
    )
    backups_enable = fields.Boolean(
        'Backups Enable on new DB?'
    )
    # database_type_id = fields.Many2one(
    #     'infrastructure.database_type',
    #     string='Database Type',
    #     required=True,
    # )

    # TODO remove this, we no longer use prefix for databases
    # @api.onchange('database_type_id')
    # def onchange_database_type_id(self):
    #     if self.database_type_id:
    #         self.new_db_name = self.database_type_id.prefix + '_'
    # TODO send suggested backup data

    @api.one
    def duplicate_db(self):
        # TODO implementar si hay cambio de usuario
        if self.change_user:
            raise Warning(_("Not Implemented Yet!"))
        active_ids = self.env.context.get('active_ids', False)
        if not active_ids:
            raise Warning(
                _("Can not duplicate database, no active_ids on context"))
        databases = self.env['infrastructure.database'].search(
            [('id', 'in', active_ids)])
        for database in databases:
            database.duplicate_db(
                self.new_db_name, self.backups_enable)
