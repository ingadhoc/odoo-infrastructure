# -*- coding: utf-8 -*-
from openerp import osv, models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
   
class server_hostname(models.Model):
    """"""
    _inherit = 'infrastructure.server_hostname'

    _sql_constraints = [
        ('name_uniq', 'unique(name, wildcard)',
            'Hostname/wildcard must be unique per server!'),
    ]    

    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        if isinstance(ids, (int, long)):
                    ids = [ids]
        reads = self.read(cr, uid, ids, ['name', 'wildcard'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['wildcard']:
                name += _(' - Wildcard')
            res.append((record['id'], name))
        return res    