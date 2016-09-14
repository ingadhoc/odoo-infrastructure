# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from datetime import datetime
import os
from fabtools.require.git import working_copy
import fabtools
import logging
# import time
_logger = logging.getLogger(__name__)


class instance_repository(models.Model):

    """"""

    _name = 'infrastructure.instance_repository'
    _description = 'instance_repository'
    _order = 'sequence'

    repository_id = fields.Many2one(
        'infrastructure.repository',
        string='Repository',
        required=True
    )
    sequence = fields.Integer(
        related='repository_id.sequence',
        store=True,
    )
    sources_from_id = fields.Many2one(
        'infrastructure.instance',
        related='instance_id.sources_from_id',
        string='Source Instance',
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
    path = fields.Char(
        string='Path',
        compute='get_path'
    )

    _sql_constraints = [
        ('repository_uniq', 'unique(repository_id, instance_id)',
            'Repository Must be Unique per Ìnstance'),
    ]

    @api.one
    @api.depends('instance_id.sources_path', 'repository_id.directory')
    def get_path(self):
        self.path = os.path.join(
            self.instance_id.sources_path,
            self.repository_id.directory
        )

    @api.onchange('repository_id')
    def change_repository(self):
        environment = self.instance_id.environment_id
        default_branch_id = environment.odoo_version_id.default_branch_id.id
        repo_branch_ids = [
            x.id for x in self.repository_id.branch_ids]
        if default_branch_id and default_branch_id in repo_branch_ids:
            self.branch_id = default_branch_id

    @api.one
    def unlink(self):
        if self.actual_commit:
            raise Warning(_(
                'You cannot delete a repository that has Actual Commit '
                'You should first delete it with the delete button.'))
        return super(instance_repository, self).unlink()

    @api.multi
    def action_repository_pull_clone_and_checkout(self):
        # TODO view is not refreshing
        self.repository_pull_clone_and_checkout()
        self.instance_id.check_instance_and_bds()

    @api.multi
    def action_delete(self):
        self.instance_id.environment_id.server_id.get_env()
        try:
            fabtools.files.remove(
                self.path, recursive=True, use_sudo=True)
            self.actual_commit = False
        except Exception, e:
            raise Warning(_(
                'Error Removing Folder %s. This is what we get:\n'
                '%s' % (self.path, e)))

    @api.multi
    def action_pull_source_and_active(self):
        """This method is used from instance that clone repositories from other
        instance, with this method, first source repository is pulled, then
        active one."""
        self.ensure_one()
        if not self.sources_from_id:
            raise Warning(_(
                'this method must be call from a repository that '
                'belongs to an instance with Other Instance Repositories'))
        _logger.info(
            "Searching source repository for repo %s and instance %s" % (
                self.repository_id.name, self.instance_id.name))
        source_repository = self.search([
            ('repository_id', '=', self.repository_id.id),
            ('instance_id', '=', self.sources_from_id.id),
        ], limit=1)
        if not source_repository:
            raise Warning(_(
                'Source repository not found for %s on instance %s') % (
                self.repository_id.name, self.sources_from_id.name))
        source_repository.repository_pull_clone_and_checkout()
        source_repository.instance_id.check_instance_and_bds()
        self.repository_pull_clone_and_checkout()
        self.instance_id.check_instance_and_bds()

    @api.one
    def repository_pull_clone_and_checkout(self, update=True):
        _logger.info("Updateing/getting repository %s with update=%s" % (
            self.repository_id.name, update))
        if self.repository_id.error_message:
            raise Warning(self.repository_id.error_message)
        if self.actual_commit and not update:
            return True
        self.instance_id.environment_id.server_id.get_env()
        path = self.path
        if self.sources_from_id:
            # check if repository exists
            source_repository = self.search([
                ('repository_id', '=', self.repository_id.id),
                ('instance_id', '=', self.sources_from_id.id),
            ], limit=1)
            if not source_repository:
                raise Warning(_(
                    'Source repository not found for %s on instance %s') % (
                    self.repository_id.name, self.sources_from_id.name))
            if source_repository.branch_id != self.branch_id:
                raise Warning(_(
                    'Source repository branch and target branch must be the '
                    'same\n'
                    '* Source repository branch: %s\n'
                    '* Target repository branch: %s\n') % (
                    source_repository.branch_id.name, self.branch_id.name))
            actual_commit = "%s / %s" % (
                source_repository.actual_commit,
                fields.Datetime.to_string(
                    fields.Datetime.context_timestamp(self, datetime.now())))
            remote_url = os.path.join(
                self.sources_from_id.sources_path,
                self.repository_id.directory
            )
        else:
            remote_url = self.repository_id.url
            actual_commit = fields.Datetime.to_string(
                fields.Datetime.context_timestamp(self, datetime.now()))
        try:
            # TODO mejorar aca y usar la api de github para pasar depth = 1 y
            # manejar errores
            working_copy(
                remote_url,
                path=path,
                branch=self.branch_id.name,
                update=update,
            )
            self._cr.commit()
        except Exception, e:
            raise Warning(_(
                'Error pulling git repository. This is what we get:\n'
                '%s' % e))

        # por ahora lo usamos para chequear que ya se descargo
        self.actual_commit = actual_commit

        return True
