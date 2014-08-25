# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from fabric.api import cd, sudo
from fabric.contrib.files import exists
import os
from ast import literal_eval
# TODO implement log_Event new login method


class environment_repository(models.Model):

    """"""

    _name = 'infrastructure.environment_repository'
    _description = 'environment_repository'

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

    environment_id = fields.Many2one(
        'infrastructure.environment',
        string='environment_id',
        ondelete='cascade',
        required=True
    )

    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        related='environment_id.server_id'
    )

    branch_ids = fields.Many2many(
        'infrastructure.repository_branch',
        string='Branches',
        related='server_repository_id.repository_id.branch_ids',
        readonly=True
    )

    @api.one
    def clone_repository(self):
        print 'Getting repository'
        # Update server repository
        self.server_repository_id.get_update_repository()
        command = 'cp -r '
        command += self.server_repository_id.path

        if not exists(self.environment_id.sources_path, use_sudo=True):
            raise except_orm(_('No Sources Folder!'),
                             _("Sources folder '%s' does not exists. \
                                Please create the environment first!")
                             % (self.environment_id.sources_path))
        command += ' ' + self.environment_id.sources_path

        sudo(command)
        folder = os.path.basename(
            os.path.normpath(self.server_repository_id.path))
        self.path = os.path.join(self.environment_id.sources_path, folder)

    @api.one
    def update_repository(self, path=False):
        print 'Updating repository'
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
        elif self.server_repository_id.repository_id.addons_subfolder:
            res = [os.path.join(
                self.path,
                self.server_repository_id.repository_id.addons_subfolder)]
        else:
            res = [self.path]
        return res

    @api.one
    def repository_pull_clone_and_checkout(self):
        self.server_id.get_env()

        # Create if not path defined
        if not self.path:
            # See if there folder for future repository exists
            path = os.path.join(
                self.environment_id.sources_path,
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

        # install pip packages
        self.install_pip_packages()

    @api.one
    def install_pip_packages(self):
        self.server_id.get_env()
        if self.environment_id.type == 'virtualenv':
            if self.server_repository_id.repository_id.pip_packages:
                pip_packages = self.server_repository_id.repository_id.pip_packages
                activate_environment_command = ' source ' + \
                    os.path.join(
                        self.environment_id.path, 'bin/activate') + ' && '
                pip_packages_install_command = 'pip install --upgrade ' + \
                    pip_packages
                sudo(
                    activate_environment_command + pip_packages_install_command
                )
        else:
            raise Warning(_("Type '%s' not implemented yet.") %
                          (self.environment_id.type))


environment_repository()
