# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
from fabric.api import cd
from .server import custom_sudo as sudo
from fabric.contrib.files import exists
import os
from ast import literal_eval
from fabtools.require.git import working_copy


class instance_repository(models.Model):

    """"""

    _name = 'infrastructure.instance_repository'
    _description = 'instance_repository'

    repository_id = fields.Many2one(
        'infrastructure.repository',
        string='Repository',
        required=True
        )
    branch_id = fields.Many2one(
        'infrastructure.repository_branch',
        string='Specific Branch',
        required=True
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
    branch_ids = fields.Many2many(
        'infrastructure.repository_branch',
        string='Branches',
        related='repository_id.branch_ids',
        readonly=True
        )

    _sql_constraints = [
        ('repository_uniq', 'unique(repository_id, instance_id)',
            'Repository Must be Unique per Ìnstance'),
    ]

    @api.onchange('repository_id')
    def change_repository(self):
        default_branch_id = self.instance_id.environment_id.odoo_version_id.default_branch_id.id
        repo_branch_ids = [
            x.id for x in self.repository_id.branch_ids]
        if default_branch_id and default_branch_id in repo_branch_ids:
            self.branch_id = default_branch_id

    @api.one
    def repository_pull_clone_and_checkout(self):
        self.instance_id.environment_id.server_id.get_env()
        path = os.path.join(
                self.instance_id.sources_path,
                self.repository_id.directory
                )
        if self.instance_id.sources_from_id:
            remote_url = os.path.join(
                self.instance_id.sources_from_id.sources_path,
                self.repository_id.directory
                )
        else:
            remote_url = self.repository_id.url
        try:
            working_copy(
                remote_url,
                path=path,
                branch=self.branch_id.name,
                update=True,
                use_sudo=True,
                user=None
                )
        except:
            raise Warning('TODO error!!!')
