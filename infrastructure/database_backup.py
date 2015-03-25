# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import requests
import os


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
        [('manual', 'Manual'), ('daily', 'Daily'),
         ('weekly', 'Weekly'), ('monthly', 'Monthly')],
        string='Type',
        required=True
    )

    @api.one
    def restore(
            self, instance, new_database_name, backups_enable, database_type):
        # TODO ver si hacemos un overwrite si hay que borrarla antes
        source_path = os.path.join(self.path, self.name)
        try:
            request = 'http://%s/restore_db/%s/%s/%s/%s' % (
                instance.main_hostname,
                instance.admin_pass,
                source_path,
                new_database_name,
                str(backups_enable),
                )
            res = requests.get(request)
            # res = requests.get(request, auth=('user', 'pass'))
        except Exception, e:
            raise Warning(_(
                'Unable to restore bd %s, this is what we get: \n %s') % (
                new_database_name, e))
        new_db = self.copy({
            'name': new_database_name,
            'backups_enable': backups_enable,
            'issue_date': fields.Date.today(),
            'database_type_id': database_type.id,
            })
        new_db.signal_workflow('sgn_to_active')

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
        return res
    # @api.one
    # def restore(self, new_database_name, backups_enable, database_type):
    #     # TODO cuando implementemos el ws que permita restaurar desde un path podemos restaurar en otra isntancia, por ahora solo restauramos en la misma instancia
    #     # TODO ver si hacemos un overwrite si hay que borrarla antes
    #     client = self.database_id.get_client()
    #     source_path = os.path.join(self.path, self.name)
    #     try:
    #         # TODO ver como podemos mejorar esto sin que quede esperando o aumentar el timeout
    #         client.model('db.database.backup').restore_from_path(
    #             source_path, new_database_name, backups_enable)
    #     except Exception, e:
    #         raise Warning(_(
    #             'Unable to restore bd %s, this is what we get: \n %s') % (
    #             new_database_name, e))
    #     new_db = self.copy({
    #         'name': new_database_name,
    #         'backups_enable': backups_enable,
    #         'issue_date': fields.Date.today(),
    #         'database_type_id': database_type.id,
    #         })
    #     new_db.signal_workflow('sgn_to_active')

    #     # devolvemos la accion de la nueva bd creada
    #     action = self.env['ir.model.data'].xmlid_to_object(
    #         'infrastructure.action_infrastructure_database_databases')
    #     if not action:
    #         return False
    #     res = action.read()[0]
    #     # res['domain'] = [('id', 'in', databases.ids)]
    #     form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
    #         'infrastructure.view_infrastructure_database_form')
    #     res['views'] = [(form_view_id, 'form')]
    #     res['res_id'] = new_db.id
    #     return res

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

    #         # TODO en vez de hacer un get y un put tal vez se pueda pasar de un server a otro
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
