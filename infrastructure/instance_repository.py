# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import Warning
import os
from fabtools.require.git import working_copy
import logging
_logger = logging.getLogger(__name__)


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
    actual_commit = fields.Char(
        string='Actual Commit',
        readonly=True,
        # copy=False, # lo desactivamos porque en el unico caso en que se copia
        # es en el duplicate de instance y queremos que se copie
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
    def action_repository_pull_clone_and_checkout(self):
        return self.repository_pull_clone_and_checkout()

    @api.one
    def repository_pull_clone_and_checkout(self, update=True):
        _logger.info("Updateing/getting repository %s with update=%s" % (
            self.repository_id.name, update))
        if self.actual_commit and not update:
            return True
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
            # TODO mejorar aca y usar la api de github para pasar depth = 1 y manejar errores
            working_copy(
                remote_url,
                path=path,
                branch=self.branch_id.name,
                update=update,
                use_sudo=True,
                user=None
                )
        except Exception, e:
            raise Warning(_('Error pulling git repository. This is what we get:\
                \n%s' % e))
        self.actual_commit = 'TODO'     #por ahora lo usamos para chequear que ya se descargo
