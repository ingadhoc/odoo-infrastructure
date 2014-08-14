# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


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

    @api.multi
    def name_get(self):
        res = []
        if self.wildcard:
            name = self.name
            name += _(' - Wildcard')
            res.append((self.id, name))
        return res


server_hostname()
