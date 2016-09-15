# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import Warning


class infrastructure_database_drop_wizard(models.TransientModel):
    _name = "infrastructure.database.drop.wizard"
    _description = "Infrastructure database drop Wizard"

    def _get_database(self):
        database_id = self.env.context.get('active_id', False)
        return self.env['infrastructure.database'].browse(database_id)

    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        default=_get_database,
        readonly=True,
        required=True,
        ondelete='cascade',
    )
    advance_type = fields.Selection(
        related='database_id.advance_type',
        readonly=True,
    )
    db_name_check = fields.Char(
        'Database full name',
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        if (
                self.advance_type == 'protected' and
                self.database_id.name != self.db_name_check):
            raise Warning(_('Database name mismatch'))
        else:
            self = self.with_context(by_pass_protection=True)
        return self.database_id.drop_db()
