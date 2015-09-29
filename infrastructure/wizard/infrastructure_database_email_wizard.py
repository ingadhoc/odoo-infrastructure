# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import Warning


class infrastructure_database_email_wizard(models.TransientModel):
    _name = "infrastructure.database.email.wizard"
    _description = "Infrastructure Database Email Wizard"
