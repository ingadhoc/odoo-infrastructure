# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class database_user(models.Model):
    _name = "infrastructure.database.user"
    _description = "Infrastructure Database User"

    login = fields.Char(
        'Login',
        required=True,
        readonly=True,
        )
    name = fields.Char(
        'Name',
        required=True,
        readonly=True,
        )
    email = fields.Char(
        'Name',
        readonly=True,
        )
    partner_id = fields.Many2one(
        'res.partner',
        'Related Partner',
        )
    database_id = fields.Many2one(
        'infrastructure.database',
        required=True,
        ondelete='cascade',
        )

    @api.model
    def get_user_from_ext_id(self, database, external_user_id):
        module_name = 'infra_db_%i_user' % database.id
        return self.env.ref('%s.%s' % (module_name, external_user_id), False)
