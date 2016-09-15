# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class instance_update_add_instances(models.TransientModel):
    _name = 'instance.update.add_instances'

    @api.model
    def get_update(self):
        return self.env['infrastructure.instance.update'].browse(
            self.env.context.get('active_id', False))

    update_id = fields.Many2one(
        'infrastructure.instance.update',
        'Update',
        default=get_update,
        required=True,
        ondelete='cascade',
    )
    actual_instance_ids = fields.Many2many(
        'infrastructure.instance',
        compute='get_actual_instances',
    )
    instance_ids = fields.Many2many(
        'infrastructure.instance',
        string='Instances',
    )

    @api.one
    @api.depends('update_id')
    def get_actual_instances(self):
        self.actual_instance_ids = self.update_id.detail_ids.mapped(
            'instance_id')

    @api.multi
    def confirm(self):
        self.ensure_one()
        for instance in self.instance_ids:
            vals = {
                'instance_id': instance.id,
                'update_id': self.update_id.id,
            }
            self.update_id.detail_ids.create(vals)
