# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class server_change(models.Model):
    """"""

    _name = 'infrastructure.server_change'
    _description = 'server_change'

    name = fields.Char(
        string='Summary',
        required=True
    )
    date = fields.Date(
        string='Date',
        required=True,
        default=fields.Date.context_today
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self, cr, uid, context: uid
    )
    description = fields.Text(
        string='Description',
        required=True
    )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        ondelete='cascade',
        required=True
    )
