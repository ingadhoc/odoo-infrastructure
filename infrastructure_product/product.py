# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class product_template(models.Model):

    _inherit = "product.template"

    type = fields.Selection(
        selection_add=[('odoo_pack', 'Odoo Pack')]
    )
    module_ids = fields.One2many(
        'product.template.module',
        'template_id',
        'Modules',
        )


class product_module(models.Model):

    _name = "product.template.module"
    _description = "product.template.module"

    name = fields.Char(
        string='Name',
        required=True,
    )
    module_id = fields.Many2one(
        'ir.module.module',
        string='Module',
    )
    template_id = fields.Many2one(
        'product.template',
        string='Product Template',
        required=True,
        ondelete='cascade',
    )

    @api.onchange('module_id')
    def change_module(self):
        self.name = self.module_id.name
