# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, models
# from openerp.exceptions import Warning


class infrastructure_database_email_wizard(models.TransientModel):
    # do not rename so it don gives errror with mass mailing when more fields
    # are added to view
    # _name = "infrastructure.database.email.wizard"
    _inherit = "mail.compose.message"
    _description = "Infrastructure Database Email Wizard"

    database_email_cc = fields.Selection([
        # ('db_followers', 'DB Followers'),
        # ('db_partner', 'DB Partner'),
        ('db_related_contacts', 'DB Related Contacts'),
        # ('contract_followers', 'Contract Followers'),
        # ('contract_followers', 'Contract Followers'),
    ],
        string='Database Email CC',
        required=False,
    )

    @api.multi
    def send_mail(self):
        self.ensure_one()
        return super(infrastructure_database_email_wizard, self.with_context(
            database_email_cc=self.database_email_cc)).send_mail()
