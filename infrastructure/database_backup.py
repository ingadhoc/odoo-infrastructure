# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
# from openerp.exceptions import except_orm
# from fabric.api import cd, sudo, settings
# from fabric.context_managers import hide
# from fabric.operations import get, put
# from os import path
import os
import base64


class database_backup(models.Model):

    """"""
    _name = 'infrastructure.database.backup'
    _description = 'Database Backup'
    _order = "create_date desc"

    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        readonly=True,
        required=True
    )
    date = fields.Datetime(
        string='Date',
        readonly=True,
        required=True
    )
    name = fields.Char(
        string='Name',
        readonly=True,
        required=True
    )
    path = fields.Char(
        string='Path',
        readonly=True,
        required=True
    )
    type = fields.Selection(
        [('daily', 'Daily'), ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        string='Type',
        required=True
    )

    @api.one
    def restore(self, target_database, overwrite_active, backups_enable):
        # TODO ver si hacemos un overwrite si hay que borrarla antes
        new_database_name = target_database.name
        f = file(os.path.join(self.path, self.name), 'r')
        data_b64 = base64.encodestring(f.read())
        f.close()
        sock = self.target_database.get_sock()
        try:
            print 'target_database.instance_id.admin_pass', target_database.instance_id.admin_pass
            print 'new_database_name', new_database_name
            print 'data_b64', data_b64
            # sock.restore(
            #     target_database.instance_id.admin_pass,
            #     new_database_name, data_b64)
        except Exception, e:
            raise Warning(_(
                'Unable to restore bd %s, this is what we get: \n %s') % (
                new_database_name, e))
        # client = self.target_database.get_client()
        # client.model('db.database').backups_state(
        #     new_database_name, backups_enable)

# TODO tomar de esta vieja funcion lo que permite restaurar en otro servidor
    # @api.one
    # def restore(self, target_database, overwrite_active):
    #     """"""

    #     source_server = self.database_id.server_id
    #     target_server = target_database.server_id

    #     backups_path = self.database_id.instance_id.environment_id.backups_path
    #     dump_file = path.join(backups_path, self.name)

    #     cmd = 'pg_restore'
    #     cmd += ' --clean'
    #     cmd += ' --disable-triggers'
    #     cmd += ' --no-privileges'
    #     cmd += ' --no-owner'
    #     cmd += ' --ignore'
    #     cmd += ' --format=c'
    #     cmd += ' --host localhost'
    #     cmd += ' --port 5432'
    #     cmd += ' --username %s --dbname %s' % (
    #         target_database.instance_id.user,
    #         target_database.name,
    #     )

    #     try:
    #         if target_database.state == 'active' and not overwrite_active:
    #             raise except_orm(
    #                 _("Cannot restore '%s' database") % target_database.name,
    #                 _('Database is activated. Please set database to draft or \
    #                   check the overwrite option.')
    #             )

    #         source_server.get_env()

    #         if source_server != target_server:
    #             tmp_path = '/tmp/'
    #             local_file = get(dump_file, tmp_path)

    #             if local_file.succeeded:
    #                 remote_file = put(local_file[0], tmp_path, mode=0755)
    #                 if remote_file.succeeded:
    #                     cmd += ' %s' % (remote_file[0])
    #                     target_server.get_env()
    #         else:
    #             cmd += ' %s' % (dump_file)

    #         with settings(
    #             hide('warnings', 'running', 'stdout', 'stderr'),
    #             warn_only=True
    #         ):
    #             sudo(cmd, user='postgres')

    #     except SystemExit:
    #         raise except_orm(
    #             _("Unable to restore database"),
    #             _("Verify if '%s' target database exists") % target_database.name
            # )

    # def download(self):
    #     """Descarga el back up en el exploradorador del usuario"""

    # @api.multi
    # def unlink(self):
    #     backups_path = self.database_id.instance_id.environment_id.backups_path
    #     self.database_id.server_id.get_env()
    #     with cd(backups_path):
    #         sudo('rm -f %s' % self.name)
    #     return super(database_backup, self).unlink()
