# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import Warning


class infrastructure_instance_delete_wizard(models.TransientModel):
    _name = "infrastructure.instance.delete.wizard"
    _description = "Infrastructure database drop Wizard"

    def _get_database(self):
        instance_id = self.env.context.get('active_id', False)
        return self.instance_id.browse(instance_id)

    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='Database',
        default=_get_database,
        readonly=True,
        required=True,
        ondelete='cascade',
    )
    advance_type = fields.Selection(
        related='instance_id.database_type_id.type',
        readonly=True,
    )
    instance_name_check = fields.Char(
        'Instance full name',
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        if (
                self.advance_type == 'protected' and
                self.instance_id.name != self.instance_name_check):
            raise Warning(_('Instance name mismatch'))
        else:
            self = self.with_context(by_pass_protection=True)
        return self.instance_id.delete()
