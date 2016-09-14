# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import os
import logging
_logger = logging.getLogger(__name__)


class database_backup(models.Model):

    """"""
    _name = 'infrastructure.database.backup'
    _description = 'Database Backup'
    _order = "date desc"

    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        ondelete='cascade',
        required=True,
    )
    date = fields.Datetime(
        string='Date',
    )
    name = fields.Char(
        string='Name',
    )
    path = fields.Char(
        string='Path',
    )
    type = fields.Selection(
        [('manual', 'Manual'), ('automatic', 'Automatic')],
        string='Type',
    )
    keep_till_date = fields.Datetime(
        string='Keep Till date',
        help="Only for manual backups, if not date is configured then backup "
        "won't be deleted.",
    )
    backup_cmd = fields.Char(
        compute='get_backup_cmd',
        string='Get Backup',
        help='Command to run on terminal and get backup to local path',
    )
    full_path = fields.Char(
        string='Path',
        compute='get_full_path',
    )

    @api.one
    @api.depends('path', 'name')
    def get_full_path(self):
        self.full_path = os.path.join(self.path, self.name)

    @api.multi
    def delete_backup(self):
        self.ensure_one()
        client = self.database_id.get_client()
        try:
            remote_ids = client.model('db.database.backup').search([
                ('name', '=', self.name)])
            if not remote_ids:
                raise Warning(_('No backup found on remote with name "%s"') % (
                    self.name))
            client.model('db.database.backup').unlink(remote_ids)
        except Exception, e:
            raise Warning(_(
                'Could not delete backup! This is what we get %s' % e))
        # return self.database_id.update_backups_data()
        # # return self.unlink()

    @api.multi
    def get_backup_msg(self):
        self.ensure_one()
        raise Warning(_(
            'Run on your terminal:\n%s\nPassword: %s') % (
            self.backup_cmd,
            self.database_id.server_id.password))

    @api.one
    def get_backup_cmd(self):
        server = self.database_id.server_id
        self.backup_cmd = 'scp -P %s %s@%s:%s .' % (
            server.ssh_port, server.user_name,
            server.main_hostname, self.full_path)

    @api.multi
    def restore(
            self, instance, db_name,
            backups_enable, overwrite=False):
        self.ensure_one()
        source_server = self.database_id.server_id
        target_server = instance.server_id
        remote_server = False
        if source_server != target_server:
            # We use get in target server because using scp is difficult
            # (passing password) and also can not use put on source server
            remote_server = {
                'user_name': source_server.user_name,
                'password': source_server.password,
                'host_string': source_server.main_hostname,
                'port': source_server.ssh_port,
            }
        self.env['infrastructure.database'].restore(
            instance.main_hostname,
            instance.admin_pass,
            db_name,
            self.path,
            self.name,
            backups_enable,
            remote_server=remote_server,
            overwrite=overwrite,
        )
        _logger.info('Database restored succesfully!')
        return True
