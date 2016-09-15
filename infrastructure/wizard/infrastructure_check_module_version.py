# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import Warning


class infrastructure_check_module_version_wizard(models.TransientModel):
    _name = "infrastructure.check.module.version.wizard"
    _description = "Infrastructure Check Module Version"

    name = fields.Char(
        'Name',
        required=True,
    )
    version = fields.Char(
        'Version',
        required=True,
        default='8.0.0.0.0',
    )
    operador = fields.Char(
        'Operador',
        required=True,
        default='<',
    )

    @api.multi
    def test(self):
        raise Warning(_('Databases: %s') % (
            ', '.join(self.get_databases().mapped('name'))))

    @api.multi
    def confirm(self):
        databases = self.get_databases()
        if not databases:
            raise Warning(_('No databases found for the requested data'))
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')
        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('id', 'in', databases.ids)]
        if len(databases) == 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_database_form')
            res['views'] = [(form_view_id, 'form')]
            res['res_id'] = databases.ids
        return res

    @api.multi
    def get_databases(self):
        self.ensure_one()
        databases = self.env['infrastructure.database'].browse(
            self._context.get('active_ids'))
        # for database in databases:
        return databases.check_module_version(
            self.name, self.version, self.operador)
