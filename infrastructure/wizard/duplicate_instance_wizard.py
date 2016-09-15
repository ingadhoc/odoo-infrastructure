# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, api, models


class infrastructure_duplicate_instance_wizard(models.TransientModel):
    _name = "infrastructure.duplicate_instance.wizard"
    _description = "Infrastructure Duplicate Instance Wizard"

    @api.model
    def get_source_instance(self):
        return self.env['infrastructure.instance'].browse(
            self.env.context.get('active_id', False))

    source_instance_id = fields.Many2one(
        'infrastructure.instance',
        'Source Instance',
        readonly=True,
        required=True,
        default=get_source_instance,
        ondelete='cascade',
    )
    environment_id = fields.Many2one(
        'infrastructure.environment',
        string='Environment',
        required=True,
        domain=[('state', '=', 'active')],
        ondelete='cascade',
    )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Environment',
        required=True,
        compute='get_server',
        ondelete='cascade',
    )
    database_type_id = fields.Many2one(
        'infrastructure.database_type',
        string='Database Type',
        required=True,
        ondelete='cascade',
    )
    sufix = fields.Char(
        string='Sufix',
    )
    number = fields.Integer(
        string='Number',
        required=True
    )

    @api.depends('source_instance_id')
    def get_server(self):
        self.server_id = self.source_instance_id.server_id
        self.environment_id = self.source_instance_id.environment_id
        instances = self.env['infrastructure.instance'].search(
            [('environment_id', '=', self.environment_id.id)],
            order='number desc',
        )
        actual_db_type_ids = [x.database_type_id.id for x in instances]
        self.number = instances and instances[0].number + 1 or 1
        self.database_type_id = self.env[
            'infrastructure.database_type'].search(
                [('id', 'not in', actual_db_type_ids)],
                limit=1
        )

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        return self.source_instance_id.duplicate(
            self.environment_id, self.database_type_id,
            self.sufix, self.number)
