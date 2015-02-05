# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
from fabric.api import cd, sudo, settings
from fabric.context_managers import hide
from fabric.operations import get, put
from os import path


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

    create_date = fields.Datetime(
        string='Date',
        readonly=True,
        required=True
    )

    name = fields.Char(
        string='Name',
        readonly=True,
        required=True
    )

    @api.one
    def restore(self, target_database, overwrite_active):
        """"""

        source_server = self.database_id.server_id
        target_server = target_database.server_id

        backups_path = self.database_id.instance_id.environment_id.backups_path
        dump_file = path.join(backups_path, self.name)

        cmd = 'pg_restore'
        cmd += ' --clean'
        cmd += ' --disable-triggers'
        cmd += ' --no-privileges'
        cmd += ' --no-owner'
        cmd += ' --ignore'
        cmd += ' --format=c'
        cmd += ' --host localhost'
        cmd += ' --port 5432'
        cmd += ' --username %s --dbname %s' % (
            target_database.instance_id.user,
            target_database.name,
        )

        try:
            if target_database.state == 'active' and not overwrite_active:
                raise except_orm(
                    _("Cannot restore '%s' database") % target_database.name,
                    _('Database is activated. Please set database to draft or \
                      check the overwrite option.')
                )

            source_server.get_env()

            if source_server != target_server:
                tmp_path = '/tmp/'
                local_file = get(dump_file, tmp_path)

                if local_file.succeeded:
                    remote_file = put(local_file[0], tmp_path, mode=0755)
                    if remote_file.succeeded:
                        cmd += ' %s' % (remote_file[0])
                        target_server.get_env()
            else:
                cmd += ' %s' % (dump_file)

            with settings(
                hide('warnings', 'running', 'stdout', 'stderr'),
                warn_only=True
            ):
                sudo(cmd, user='postgres')

        except SystemExit:
            raise except_orm(
                _("Unable to restore database"),
                _("Verify if '%s' target database exists") % target_database.name
            )

    def download(self):
        """Descarga el back up en el exploradorador del usuario"""

    @api.multi
    def unlink(self):
        backups_path = self.database_id.instance_id.environment_id.backups_path
        self.database_id.server_id.get_env()
        with cd(backups_path):
            sudo('rm -f %s' % self.name)
        return super(database_backup, self).unlink()
