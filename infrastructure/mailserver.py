# -*- coding: utf-8 -*-

from openerp import models, fields


class mailserver(models.Model):
    """"""

    _name = 'infrastructure.mailserver'
    _inherit = 'ir.mail_server'

    external_id = fields.Char(
        'External ID',
        required=True,
        help='External ID used to identify record on record update')
