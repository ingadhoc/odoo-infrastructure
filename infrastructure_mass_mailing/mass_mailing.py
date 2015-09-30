# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields
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
