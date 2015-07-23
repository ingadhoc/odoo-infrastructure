# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


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
