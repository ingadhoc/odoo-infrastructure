# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from fabtools import require
import os


class server_hostname(models.Model):
    """"""

    _name = 'infrastructure.server_hostname'
    _description = 'server_hostname'
    _order = 'sequence'

    _sql_constraints = [
        ('name_uniq', 'unique(name, wildcard, server_id)',
            'Hostname/wildcard must be unique per server!'),
    ]

    sequence = fields.Integer(
        'Sequence',
        default=10,
    )
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
    )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        ondelete='cascade',
        required=True
    )
    partner_id = fields.Many2one(
        'res.partner',
        'Partner',
        help='If partner is set, then this hostname will be only availble '
        'for this partner databases and instances'
    )
    ssl_available = fields.Boolean(
        string='SSL Available?',
    )
    ssl_intermediate_certificate = fields.Text(
        string='SSL Intermediate Certificate',
    )
    ssl_certificate = fields.Text(
        string='SSL Certificate',
    )
    ssl_certificate_key = fields.Text(
        string='SSL Certificate KEY',
    )
    ssl_certificate_path = fields.Char(
        string='SSL Certificate',
        compute='get_certificate_paths'
    )
    ssl_certificate_key_path = fields.Char(
        string='SSL Certificate',
        compute='get_certificate_paths'
    )

    @api.one
    @api.depends('name')
    def get_certificate_paths(self):
        name = self.name
        if self.wildcard:
            name += '_wildcard'
        base_file_path = os.path.join(self.server_id.ssl_path, name)
        self.ssl_certificate_path = base_file_path + '.crt'
        self.ssl_certificate_key_path = base_file_path + '.key'

    @api.onchange('wildcard', 'name')
    def _get_domain_regex(self):
        domain_regex = False
        if self.name:
            if self.wildcard:
                domain_regex = '/[@.]' + '\\.'.join(
                    self.name.split('.')) + '$/'
                # "/[@.]domain\.com\.ar$/"
            else:
                domain_regex = '/(.*)' + '\\.'.join(
                    self.name.split('.')) + '$/'
                # "/(.*)tuukan\.com$/"
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

    @api.one
    def load_ssl_certficiate(self):
        self.server_id.get_env()
        if not self.ssl_available:
            return False
        if not self.ssl_certificate or not self.ssl_certificate_key:
            raise Warning(_(
                'To configure SSL you need to set ssl certificates and keys'))
        # TODO add ssl path in server data
        certificate = self.ssl_certificate
        if self.ssl_intermediate_certificate:
            certificate += ('\n%s') % (self.ssl_intermediate_certificate)
        require.files.directory(
            self.server_id.ssl_path, use_sudo=True,
            owner='', group='', mode='600')
        require.file(
            path=self.ssl_certificate_path,
            contents=certificate,
            use_sudo=True)
        require.file(
            path=self.ssl_certificate_key_path,
            contents=self.ssl_certificate_key,
            use_sudo=True)
