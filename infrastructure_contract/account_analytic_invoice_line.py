# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
import logging

_logger = logging.getLogger(__name__)


class AccountAnalyticInvoiceLine(models.Model):
    _inherit = 'account.analytic.invoice.line'

    db_quantity = fields.Float(
        'Db Qty',
        help='Quantity readed on remote database',
        readonly=True,
    )
