# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, api, models, _
from openerp.exceptions import Warning
from fabric.contrib.files import exists
import os


class infrastructure_restore_from_file_wizard(models.TransientModel):
    _name = "infrastructure.restore_from_file.wizard"
    _description = "Infrastructure Restore From File Wizard"

    def _get_database(self):
        dump_id = self.env.context.get('active_id', False)
        return self.env['infrastructure.database'].browse(dump_id)

    file_path = fields.Char(
        string='File Path',
        required=True,
        default='/opt/odoo/backups/tmp/',
    )
    file_name = fields.Char(
        string='File Name',
        required=True,
    )
    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        default=_get_database,
        readonly=True,
        ondelete='cascade',
        required=True,
    )

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        self.database_id.server_id.get_env()
        if not exists(
                os.path.join(self.file_path, self.file_name),
                use_sudo=True):
            raise Warning(_("File was not found on path '%s'") % (
                self.file_path))
        database = self.database_id
        instance = database.instance_id
        self.database_id.restore(
            instance.main_hostname,
            instance.admin_pass,
            database.name,
            self.file_path,
            self.file_name,
            database.backups_enable,
            remote_server=False
        )

        # we run it because it is not enaught what database_tools does with
        # this parameter, it could be necesary to load new data of backups
        if database.backups_enable:
            database.config_backups()

        database.action_activate()
        return True
