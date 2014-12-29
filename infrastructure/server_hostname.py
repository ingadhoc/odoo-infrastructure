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

    domain_regex = fields.Char(
        string='Domain Regex',
        required=True,
        help="""
        For domains use something like '/(.*)tuukan\.com$/'
        For wildcards use something line '/[@.]domain\.com\.ar$/'
        """
    )

    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        ondelete='cascade',
        required=True
    )

    @api.one
    @api.onchange('wildcard', 'name')
    def _get_domain_regex(self):
        domain_regex = False
        if self.name:
            if self.wildcard:
                domain_regex = '/[@.]' + '\\.'.join(self.name.split('.')) + '$/'
                "/[@.]domain\.com\.ar$/"
            else:
                domain_regex = '/(.*)' + '\\.'.join(self.name.split('.')) + '$/'
                "/(.*)tuukan\.com$/"
        self.domain_regex = domain_regex

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
