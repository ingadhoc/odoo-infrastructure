# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class database_user(models.Model):
    _name = "infrastructure.database.user"
    _description = "Infrastructure Database User"

    login = fields.Char(
        'Login',
        required=True,
        readonly=True,
    )
    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
    )
    email = fields.Char(
        'Name',
        readonly=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Related Partner',
    )
    database_id = fields.Many2one(
        'infrastructure.database',
        required=True,
        ondelete='cascade',
    )
    signup_url = fields.Char(
        compute='_compute_signup_url'
    )

    _sql_constraints = [
        ('login_uniq', 'unique(login, database_id)',
            'Login must be unique per database'),
    ]

    @api.multi
    def _compute_signup_url(self):
        for rec in self:
            rec.signup_url = rec.database_id._get_signup_url(rec.login)

    @api.multi
    def open_signup_url(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_url',
            'name': "Signup URL",
            'target': 'new',
            'url': self.signup_url,
        }
