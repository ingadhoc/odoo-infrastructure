# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class project_issue(models.Model):

    _inherit = "project.issue"

    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        domain=[('state', '=', 'active')],
    )
    db_user = fields.Char(
        string='DB User',
        help='User that has the issue',
    )
    db_company = fields.Char(
        string='DB Company',
        help='Company user is using when having the issue',
    )

    @api.multi
    def open_signup_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Signup URL",
            'target': 'new',
            'url': self.database_id._get_signup_url(self.db_user),
        }
