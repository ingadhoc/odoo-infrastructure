# -*- coding: utf-8 -*-
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
        for module in self.mapped('product_ids.module_ids'):
            try:
                client.install(module.name)
            except Exception, e:
                _logger.warning(
                    "Unable to install module %s. This is what we get %s." % (
                        module.name, e))
        self.update_modules_data(fields=['state'])
