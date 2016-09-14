# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields


class db_filter(models.Model):
    """"""

    _name = 'infrastructure.db_filter'
    _description = 'db_filter'

    name = fields.Char(
        string='Name',
        required=True
    )
    rule = fields.Char(
        string='Rule',
        required=True
    )
    add_bd_name_to_host = fields.Boolean(
        string='Add BD to host',
        help="Add BD name to host on databases, for example "
        "[bd_name].adhoc.com.ar",
    )
