# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import ValidationError


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
    protected = fields.Boolean(
        related='database_id.protected',
        readonly=True,
    )
    db_name_check = fields.Char(
        'Database full name',
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        # if instance or db protected we can force with name check
        if (
                self.protected and
                self.database_id.name != self.db_name_check):
            raise ValidationError(_('Database name mismatch'))
        else:
            self = self.with_context(by_pass_protection=True)
        return self.database_id.drop_db()
