# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from fabric.api import cd
from .server import custom_sudo as sudo
from fabric.contrib.files import exists
import os
from ast import literal_eval


class instance_repository(models.Model):

    """"""

    _name = 'infrastructure.instance_repository'
    _description = 'instance_repository'

    server_repository_id = fields.Many2one(
        'infrastructure.server_repository',
        string='Server Repository',
        required=True
        )
    branch_id = fields.Many2one(
        'infrastructure.repository_branch',
        string='Specific Branch',
        required=True
        )
    path = fields.Char(
        string='Path'
        )
    addons_paths = fields.Char(
        string='Addons Path',
        required=True,
        default='[]'
        )
    branch_ids = fields.Many2one(
        'infrastructure.repository_branch',
        string='branch_ids',
        readonly=True
        )
    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='Instance',
        ondelete='cascade',
        required=True
        )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        related='instance_id.environment_id.server_id',
        required=False,
        )
    branch_ids = fields.Many2many(
        'infrastructure.repository_branch',
        string='Branches',
        related='server_repository_id.repository_id.branch_ids',
        readonly=True
        )

    _sql_constraints = [
        ('repository_uniq', 'unique(server_repository_id, instance_id)',
            'Repository Must be Unique per Ìnstance'),
    ]

    @api.onchange('server_repository_id')
    def change_server_repository(self):
        default_branch_id = self.instance_id.environment_id.odoo_version_id.default_branch_id.id
        repo_branch_ids = [
            x.id for x in self.server_repository_id.repository_id.branch_ids]
        if default_branch_id and default_branch_id in repo_branch_ids:
            self.branch_id = default_branch_id

    @api.one
    def clone_repository(self):
        # Update server repository
        self.server_repository_id.get_update_repository()
        command = 'cp -r '
        command += self.server_repository_id.path

        if not exists(self.instance_id.sources_path, use_sudo=True):
            raise except_orm(_('No Sources Folder!'),
                             _("Sources directory '%s' does not exists. \
                                Please create the instance first!")
                             % (self.instance_id.sources_path))
        command += ' ' + self.instance_id.sources_path

        sudo(command)
        directory = os.path.basename(
            os.path.normpath(self.server_repository_id.path))
        self.path = os.path.join(self.instance_id.sources_path, directory)

    @api.one
    def update_repository(self, path=False):
        self.server_id.get_env()
        if not path:
            path = self.path
        if not exists(path, use_sudo=True):
            raise except_orm(_('No Repository Folder!'),
                             _("Please check that the setted path exists \
                                or empty it in order to donwload for \
                                first time '%s'!") % (path,))

        with cd(path.strip()):
            try:
                sudo('git pull')
            except:
                raise except_orm(_('Error Making git pull!'),
                                 _("Error making git pull on '%s'!") % (path))

    @api.multi
    def check_for_addons_paths(self):
        if self.server_repository_id.repository_id.is_server:
            res = [os.path.join(self.path, 'addons'), os.path.join(
                self.path, 'openerp/addons')]
        elif self.server_repository_id.repository_id.addons_subdirectory:
            res = [os.path.join(
                self.path,
                self.server_repository_id.repository_id.addons_subdirectory)]
        else:
            res = [self.path]
        return res

    @api.one
    def repository_pull_clone_and_checkout(self):
        self.server_id.get_env()

        # Create if not path defined
        if not self.path:
            # See if there directory for future repository exists
            if not self.server_repository_id.path:
                raise Warning(
                    _('You should first clone server repositories'))
            print '.self.instance_id.sources_path', self.instance_id.sources_path
            path = os.path.join(
                self.instance_id.sources_path,
                os.path.basename(
                    os.path.normpath(self.server_repository_id.path))
                    )
            if exists(path, use_sudo=True):
                self.update_repository(path)
                self.path = path
            else:
                self.clone_repository()

        # Try to update if path defined
        else:
            self.update_repository()

        # make checkout
        with cd(self.path):
            sudo('git checkout ' + self.branch_id.name)

        if not literal_eval(self.addons_paths):
            self.addons_paths = self.check_for_addons_paths()
