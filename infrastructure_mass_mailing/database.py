# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, _
import logging
_logger = logging.getLogger(__name__)


class database(models.Model):

    """"""
    _inherit = 'infrastructure.database'
    _mail_mass_mailing = _('Databases')

# class database_user(models.Model):
#     _inherit = "infrastructure.database.user"

    # _mail_mass_mailing = _('Database Users')
    # we don not inherit from db user because we use related partner instead
    # for messaging. So we need to add message_get_default_recipients function
    # _inherit = ['ir.needaction_mixin', 'mail.thread']

    # en realidad, tal vez mas que sobreescribir esta, deberiamos indicar de
    # otra manera que va en partners, porque si no quedan asociados los
    # mensajes a esta clase y no a partner... igual por ahora usamos database
    # para mandar mensajes
    # @api.multi
    # def message_get_default_recipients(self):
    #     res = {}
    #     for record in self.filtered('partner_id'):
    #         res[record.id] = {
    #             'partner_ids': [record.partner_id.id],
    #             'email_to': False,
    #             'email_cc': False}
    #     return res
