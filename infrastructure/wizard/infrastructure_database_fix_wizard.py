# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import Warning


class infrastructure_database_fix_wizard(models.TransientModel):
    _name = "infrastructure.database.fix.wizard"
    _description = "infrastructure.database.fix.wizard"

    init_and_conf = fields.Text(string='Init and Conf Modules', readonly=True)
    update = fields.Char(string='Update Modules', readonly=True)

    @api.one
    def change_db_passwd(self):
        active_ids = self.env.context.get('active_ids', False)
        databases = self.env['infrastructure.database'].browse(active_ids)
        for database in databases:
            if len(self.new_passwd) < 5:
                raise Warning(
                    _("Password is too short. \
                      At least 5 characters are required."))
            if self.new_passwd != self.confirm_passwd:
                raise Warning(
                    _("Passwords mismatch!"))
            res = database.change_admin_passwd(
                database.admin_password,
                self.new_passwd
            )
            if res:
                database.admin_password = self.new_passwd
