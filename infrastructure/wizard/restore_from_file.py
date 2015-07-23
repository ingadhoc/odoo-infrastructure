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
        return self.database_id.restore(self.file_path, self.file_name)
