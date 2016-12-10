# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class MassMailing(models.Model):
    """ MassMailing models a wave of emails for a mass mailign campaign.
    A mass mailing is an occurence of sending emails. """

    _inherit = 'mail.mass_mailing'

    database_email_cc = fields.Selection([
        # ('db_followers', 'DB Followers'),
        # ('db_partner', 'DB Partner'),
        ('db_related_contacts', 'DB Related Contacts'),
        # ('contract_followers', 'Contract Followers'),
        # ('contract_followers', 'Contract Followers'),
    ],
        string='Database Email CC',
    )

    @api.multi
    def send_mail(self, auto_commit=False):
        for record in self:
            if record.database_email_cc:
                super(MassMailing, self.with_context(
                    # database_email_cc=record.database_email_cc,
                    default_database_email_cc=record.database_email_cc,
                )).send_mail(auto_commit=auto_commit)
            else:
                super(MassMailing, self).send_mail()
        return True
