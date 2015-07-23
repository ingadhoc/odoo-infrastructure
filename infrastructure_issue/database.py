# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class database(models.Model):

    """"""
    _inherit = 'infrastructure.database'

    issue_ids = fields.One2many(
        'project.issue',
        'database_id',
        string='Issues',
        )
    issue_count = fields.Integer(
        string='# Issues',
        compute='_get_issues',
        )

    @api.one
    @api.depends('issue_ids')
    def _get_issues(self):
        self.issue_count = len(self.issue_ids)
