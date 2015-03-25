# -*- coding: utf-8 -*-
from openerp import models, fields, tools


class database_type(models.Model):

    _name = 'infrastructure.database_type'
    _description = 'database_type'
    _order = 'sequence'

    sequence = fields.Integer(
        'Sequence',
        default=10,
        )
    name = fields.Char(
        string='Name',
        required=True
        )
    prefix = fields.Char(
        string='Prefix',
        required=True,
        size=4
        )
    url_prefix = fields.Char(
        string='URL Prefix'
        )
    type = fields.Selection(
        [('normal', 'Normal'),
         ('protected', 'Protected'),
         ('auto_deactivation', 'Auto Deactivation'),
         ('auto_drop', 'Auto Drop'),
         ('auto_deact_and_drop', 'Auto Deactivation and Drop')],
        'Type',
        help="Depending on the type:\
        * Normal: nothing special is made\
        * Protected: needs special confirmation before some operations\
        * Auto Deactivation: automatically deactivated on deactivation date\
        * Auto Drop: automatically dropped on deactivation date\
        * Auto Deactivation and Drop: automatically deactivated on deactivation date and automatically dropped on deactivation date\
        ",
        required=True,
        default='normal'
        )
    color = fields.Integer(
        string='Color'
        )
    auto_drop_days = fields.Integer(
        string='Automatic Drop Days'
        )
    protect_db = fields.Boolean(
        string='Protect Databases?'
        )
    auto_deactivation_days = fields.Integer(
        string='Automatic Deactivation Days'
        )
    install_lang_id = fields.Selection(
        tools.scan_languages(),
        string='Install Language',
        )
    instance_admin_pass = fields.Char(
        'Instance Admin Password',
        help='It will be used as default on Instance Admin Password, if not value defined instance name will be suggested',
        )
    db_admin_pass = fields.Char(
        'DB Admin Password',
        help='It will be used as default on Database Admin Password, if not value defined instance name will be suggested',
        )
    db_filter = fields.Many2one(
        'infrastructure.db_filter',
        string='DB Filter',
        help='It will be used as default on Instances',
        )
