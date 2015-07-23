# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import requests
import os
import simplejson
import logging
_logger = logging.getLogger(__name__)


class database_backup(models.Model):

    """"""
    _name = 'infrastructure.database.backup'
    _description = 'Database Backup'
    _order = "create_date desc"

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
    def get_backup_msg(self):
        self.ensure_one()
        raise Warning(_('Run on your terminal:\n\
            %s\n\
            Password: %s') % (
            self.backup_cmd,
            self.database_id.server_id.password))

    @api.one
    def get_backup_cmd(self):
        server = self.database_id.server_id
        self.backup_cmd = 'scp -P %s %s@%s:%s' % (
            server.ssh_port, server.user_name,
            server.main_hostname, self.full_path)

    @api.multi
    def restore(
            self, instance, new_database_name,
            backups_enable, database_type):
        self.ensure_one()
        # TODO podriamos nosotors cambiar workers a 0
        if instance.workers != 0:
            raise Warning(_('You can not restore a database to a instance with\
                workers, you should first set them to 0, reconfig and try\
                again. After saccesfull restore you can reactivate workers'))
        # TODO ver si hacemos un overwrite si hay que borrarla antes
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
        try:
            url = "%s/%s" % (instance.main_hostname, 'restore_db')
            headers = {'content-type': 'application/json'}
            data = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    'admin_pass': instance.admin_pass,
                    'db_name': new_database_name,
                    'file_path': self.path,
                    'file_name': self.name,
                    'backups_state': backups_enable,
                    'remote_server': remote_server,
                    },
            }
            _logger.info(
                'Restoring backup %s, you can also watch target instance\
                log' % new_database_name)
            response = requests.post(
                url,
                data=simplejson.dumps(data),
                headers=headers,
                verify=False,
                # TODO fix this, we disable verify because an error we have
                # with certificates. Aca se explica ele error
                # http://docs.python-requests.org/en/latest/community/faq/
                # #what-are-hostname-doesn-t-match-errors
                ).json()
            _logger.info('Restored complete, result: %s' % response)
            if response['result'].get('error', False):
                raise Warning(_(
                    'Unable to restore bd %s, you can try restartin target\
                    instance. This is what we get: \n %s') % (
                    new_database_name, response['result'].get('error')))
            _logger.info('Back Up %s Restored Succesfully' % new_database_name)
        except Exception, e:
            raise Warning(_(
                'Unable to restore bd %s, you can try restartin target\
                instance. This is what we get: \n %s') % (
                new_database_name, e))
        _logger.info('Creating new database data on infra')
        new_db = self.database_id.copy({
            'name': new_database_name,
            'backups_enable': backups_enable,
            'issue_date': fields.Date.today(),
            'database_type_id': database_type.id,
            'instance_id': instance.id,
            })
        new_db.signal_workflow('sgn_to_active')
        if backups_enable:
            new_db.config_backups()
        # devolvemos la accion de la nueva bd creada
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')
        if not action:
            return False
        res = action.read()[0]
        # res['domain'] = [('id', 'in', databases.ids)]
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'infrastructure.view_infrastructure_database_form')
        res['views'] = [(form_view_id, 'form')]
        res['res_id'] = new_db.id
        _logger.info('Database restored succesfully!')
        return res
