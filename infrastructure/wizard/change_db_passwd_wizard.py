# -*- coding: utf-8 -*-

from openerp import fields, api, _
from openerp.osv import osv
from openerp.exceptions import Warning


class infrastructure_change_db_passwd_wizard(osv.osv_memory):
    _name = "infrastructure.change_db_passwd.wizard"
    _description = "Infrastructure Change Database Password Wizard"

    new_passwd = fields.Char(string='New Password', required=True)
    confirm_passwd = fields.Char(string='Confirm Password', required=True)

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
