# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, tools, api, _
from openerp.exceptions import Warning


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
    service_type = fields.Selection([
        ('docker', 'Docker Restart'),
        # ('upstart', 'Upstart Service'),
        ('no_service', 'No Service')],
        default='docker',
        required=True,
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
        * Auto Deactivation and Drop: automatically deactivated on\
        deactivation date and automatically dropped on deactivation date\
        ",
        required=True,
        default='normal'
        )
    sources_from_id = fields.Many2one(
        'infrastructure.database_type',
        string='Sources From',
        help='If none is selected sources are cloned from host, if you want to\
        clone them from other instance, choose the databse type from where the\
        sources are going to be clone',
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
        help='It will be used on OWN SERVERS as default on Instance Admin\
        Password, if not value defined instance name will be suggested',
        )
    db_admin_pass = fields.Char(
        'DB Admin Password',
        # esta si la usamos siempre porque total va encriptada
        help='It will be used as default on Database Admin Password,\
        if not value defined instance name will be suggested',
        )
    db_filter = fields.Many2one(
        'infrastructure.db_filter',
        string='DB Filter',
        help='It will be used as default on Instances',
        )
    workers = fields.Selection(
        [('clasic_rule', 'Clasic Rule'), ('fix_number', 'Fix Number')],
        string='Workers Filter',
        required=True,
        default='clasic_rule',
        help='Clasic Rule means workers = server_processors * 2 + 1'
        )
    workers_number = fields.Integer(
        'Workers Number',
        )
    server_mode_value = fields.Char(
        'Server Mode Value',
        )
    instance_log_level = fields.Selection([
        (u'info', 'info'), (u'debug_rpc', 'debug_rpc'),
        (u'warn', 'warn'), (u'test', 'test'), (u'critical', 'critical'),
        (u'debug_sql', 'debug_sql'), (u'error', 'error'), (u'debug', 'debug'),
        (u'debug_rpc_answer', 'debug_rpc_answer')],
        string='Default Instance Log Level',
        default='info',
        required=True,
        )

    @api.multi
    def show_instance_admin_pass(self):
        raise Warning(_("Password: '%s'") % self.instance_admin_pass)

    @api.multi
    def show_db_admin_pass(self):
        raise Warning(_("Password: '%s'") % self.db_admin_pass)
