# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import Warning


class infrastructure_database_email_wizard(models.TransientModel):
    _name = "infrastructure.database.email.wizard"
    _inherit = "mail.compose.message"
    _description = "Infrastructure Database Email Wizard"

    public = fields.Selection([
        ('db_followers', 'DB Followers'),
        ('db_partner', 'DB Partner'),
        ('db_related_contacts', 'DB Related Contacts'),
        ('contract_followers', 'Contract Followers'),
        ('contract_followers', 'Contract Followers'),
        ],
        string='Mail Options',
        required=True
        )


    # def send_mail(self, cr, uid, ids, context=None):
    #     """ Process the wizard content and proceed with sending the related
    #         email(s), rendering any template patterns on the fly if needed """
    #     if context is None:
    #         context = {}

    #     survey_response_obj = self.pool.get('survey.user_input')
    #     partner_obj = self.pool.get('res.partner')
    #     mail_mail_obj = self.pool.get('mail.mail')
    #     try:
    #         model, anonymous_id = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'portal', 'group_anonymous')
    #     except ValueError:
    #         anonymous_id = None
