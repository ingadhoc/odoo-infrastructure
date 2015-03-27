# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import os
from fabric.api import cd
# utilizamos nuestro custom sudo que da un warning
from .server import custom_sudo as sudo
from fabric.contrib.files import exists


class repository(models.Model):

    """"""

    _name = 'infrastructure.repository'
    _description = 'repository'

    sequence = fields.Integer(
        string='Sequence',
        default=10,
    )
    name = fields.Char(
        string='Name',
        required=True
    )
    directory = fields.Char(
        string='Directory',
        required=True
    )
    type = fields.Selection(
        [(u'git', 'git')],
        string='Type',
        required=True
    )
    addons_subdirectory = fields.Char(
        string='Addons Subdirectory'
    )
    url = fields.Char(
        string='URL',
        required=True
    )
    pip_packages = fields.Char(
        string='PIP Packages'
    )
    is_server = fields.Boolean(
        string='Is Server?'
    )
    default_in_new_env = fields.Boolean(
        string='Default in new Environment?',
        help="Not implemented yet",
    )
    server_wide_modules = fields.Char(
        string='Server Wide Modules',
        help="Modules to be load in intance. Eg. web,web_kanban",
    )
    install_server_command = fields.Char(
        string='Install Server Command',
        default='python setup.py install'
    )
    branch_ids = fields.Many2many(
        'infrastructure.repository_branch',
        'infrastructure_repository_ids_branch_ids_rel',
        'repository_id',
        'repository_branch_id',
        string='Branches'
    )
    _order = "sequence"

    @api.one
    def get_repository(self, server):
        server.get_env()
        if not exists(server.sources_path, use_sudo=True):
            raise except_orm(
                _('No Source Directory!'),
                _("Please first create the source directory '%s'!")
                % (server.sources_path,))
        with cd(server.sources_path):
            path = False
            if self.type == 'git':
                command = 'git clone '
                command += self.url
                command += ' ' + self.directory
                sudo(command)
                path = os.path.join(server.sources_path, self.directory)
                # TODO implementar otros tipos de repos
        return path
