# -*- coding: utf-8 -*-

from openerp import models, fields, _


class server_hostname(models.Model):
    """"""

    _name = 'infrastructure.server_hostname'
    _description = 'server_hostname'

    _sql_constraints = [
        ('name_uniq', 'unique(name, wildcard)',
            'Hostname/wildcard must be unique per server!'),
    ]

    name = fields.Char(
        string='Name',
        required=True
    )

    wildcard = fields.Boolean(
        string='Wild Card'
    )

    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        ondelete='cascade',
        required=True
    )

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


server_hostname()
