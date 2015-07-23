# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning


class database(models.Model):
    _inherit = "infrastructure.database"

    contract_id = fields.Many2one(
        'account.analytic.account',
        string='Contract',
        domain="[('partner_id','child_of',partner_id),('state','=','open')]",
    )

    @api.one
    def upload_contract_data(self):
        client = self.get_client()
        modules = ['web_support_client']
        for module in modules:
            if client.modules(name=module, installed=True) is None:
                raise Warning(
                    _("You can not Upload a Contract if module '%s' is not\
                    installed in the database") % (module))
        if not self.contract_id:
            raise Warning(
                _("You can not Upload a Contract if not contracted is linked"))
        imp_fields = [
            'id',
            'name',
            'user',
            'database',
            'server_host',
            'contract_id']
        ['self.asd', ]
        commercial_partner = self.contract_id.partner_id.commercial_partner_id

        server_host = self.env['ir.config_parameter'].get_param('web.base.url')

        # search for user related to commercial partner
        user = self.env['res.users'].search([(
            'partner_id', '=', commercial_partner.id)], limit=1)
        if not user:
            user = user.search([(
                'partner_id', 'child_of', commercial_partner.id)])
        if not user:
            raise Warning(
                _("You can not Upload a Contract if there is not user related\
                 to the contract Partner"))
        rows = [[
            'infrastructure_contract.contract_id_%i' % self.contract_id.id,
            self.contract_id.name,
            user.login,
            self._cr.dbname,
            server_host,
            self.contract_id.id,
            ]]
        client.model('support.contract').load(imp_fields, rows)
