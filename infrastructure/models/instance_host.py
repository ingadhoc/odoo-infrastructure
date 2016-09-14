# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api


class instance_host(models.Model):

    """"""

    _name = 'infrastructure.instance_host'
    _description = 'instance_host'

    server_hostname_id = fields.Many2one(
        'infrastructure.server_hostname',
        string='Server Hostname',
        required=True
    )
    subdomain = fields.Char(
        string='Subdomain'
    )
    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='instance_id',
        ondelete='cascade',
        required=True
    )
    redirect_page = fields.Char(
        'Redirect Page'
    )
    prefix = fields.Char(
        'Prefix',
        required=False,
    )
    name = fields.Char(
        'Name',
        compute='get_name',
        store=True,
    )
    partner_id = fields.Many2one(
        'res.partner',
        related='instance_id.environment_id.partner_id',
        readonly=True,
    )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        related='instance_id.environment_id.server_id',
        store=True,
        readonly=True
    )
    type = fields.Selection(
        [('main', 'Main'),
         ('redirect_to_main', 'Redirect To Main'),
         ('other', 'Other')],
        string='Main?',
        default='main',
    )
    wildcard = fields.Boolean(
        string='Wildcard',
        related='server_hostname_id.wildcard'
    )

    _sql_constraints = [
        ('name_uniq', 'unique(name, server_id)',
            'Name must be unique per server!'),
    ]

    @api.one
    @api.depends('prefix', 'server_hostname_id.name')
    def get_name(self):
        name = self.server_hostname_id.name
        if self.prefix and name and self.server_hostname_id.wildcard:
            name = self.prefix + '.' + name
        self.name = name

    @api.onchange('subdomain')
    def _change_subdomain(self):
        prefix = False
        if self.subdomain:
            prefix = self.subdomain
        if self.instance_id.database_type_id.url_prefix:
            url_prefix = self.instance_id.database_type_id.url_prefix
            if prefix:
                prefix = url_prefix + '_' + prefix
            else:
                prefix = url_prefix
        self.prefix = prefix

    @api.onchange('server_hostname_id', 'instance_id')
    def _get_name(self):
        # dont know why partner related field is not being updated
        self.partner_id = self.instance_id.environment_id.partner_id
        if not self.server_hostname_id:
            server_hostname = self.env[
                'infrastructure.server_hostname'].search([
                    ('server_id', '=', self.server_id.id),
                    ('partner_id', '=', self.partner_id.id),
                ],
                    limit=1)
            if not server_hostname:
                server_hostname = self.env[
                    'infrastructure.server_hostname'].search([
                        ('server_id', '=', self.server_id.id)],
                        limit=1)
            self.server_hostname_id = server_hostname.id
        if self.server_hostname_id.wildcard:
            if not self.subdomain:
                self.subdomain = self.instance_id.environment_id.name
        else:
            self.subdomain = False
        self._change_subdomain()
