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

    product_ids = fields.Many2many(
        'product.product',
        string='Product',
        domain=[('type', '=', 'odoo_pack')],
        context={'default_type': 'odoo_pack'},
        )

    @api.one
    def install_product_modules(self):
        client = self.get_client()
        modules = self.mapped('product_ids.module_ids.name')
        _logger.info('Installing modules %s' % str(modules))
        try:
            client.install(*modules)
        except Exception, e:
            _logger.warning(
                "Unable to install modules %s. This is what we get %s." % (
                    str(modules), e))
        self.update_modules_data(fields=['state'])
