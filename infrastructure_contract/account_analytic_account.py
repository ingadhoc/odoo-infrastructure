# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class account_analytic_account(models.Model):
    _inherit = "account.analytic.account"

    database_ids = fields.One2many(
        'infrastructure.database',
        'contract_id',
        'Databases',
        )
    database_count = fields.Integer(
        string='# Databases',
        compute='_get_databases'
        )

    @api.one
    @api.depends('database_ids')
    def _get_databases(self):
        self.database_count = len(self.database_ids)

    @api.constrains('state', 'database_ids')
    def check_databases_state(self):
        not_inactive_dbs = self.database_ids.filtered(
            lambda x: x.state != 'inactive')
        if self.state == 'close' and not_inactive_dbs:
            raise Warning(_(
                'You can not close a contract if there are related dbs in '
                'other state than "inactive".\n'
                '* DBS: %s') % not_inactive_dbs.ids)

    @api.multi
    def action_view_databases(self):
        '''
        This function returns an action that display a form or tree view
        '''
        self.ensure_one()
        databases = self.database_ids
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')

        if not action:
            return False
        res = action.read()[0]
        if len(self) == 1:
            res['context'] = {
                # 'default_instance_id': self.id,
                # 'search_default_instance_id': self.id,
                'search_default_contract_id': self.id,
                'search_default_not_inactive': 1,
                }
        if not len(databases.ids) > 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_database_form')
            res['views'] = [(form_view_id, 'form')]
            # if 1 then we send res_id, if 0 open a new form view
            res['res_id'] = databases and databases.ids[0] or False
        return res
