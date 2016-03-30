# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class instance_update_add_instances(models.TransientModel):
    _name = 'instance.update.add_instances'

    quantity = fields.Float('Quantity',
                            default='1.0')
    instance_ids = fields.Many2many(
        'infrastructure.instance',
        string='Instances',
        domain=[('state', '=', 'active')],
        # context="{'search_default"
    )

    @api.one
    def confirm(self):
        active_id = self._context['active_id']
        update = self.env['infrastructure.instance.update'].browse(active_id)
        for instance in self.instance_ids:
            vals = {
                'instance_id': instance.id,
                'update_id': update.id,
            }
            update.detail_ids.create(vals)
