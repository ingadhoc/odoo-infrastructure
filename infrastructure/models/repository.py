# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, fields, api
import os


class repository(models.Model):

    """"""

    _name = 'infrastructure.repository'
    _description = 'repository'
    _order = "sequence"

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
    default_in_new_env = fields.Boolean(
        string='Default in new Environment?',
        help="Not implemented yet",
    )
    server_wide_modules = fields.Char(
        string='Server Wide Modules',
        help="Modules to be load in intance. Eg. web,web_kanban",
    )
    branch_ids = fields.Many2many(
        'infrastructure.repository_branch',
        'infrastructure_repository_ids_branch_ids_rel',
        'repository_id',
        'repository_branch_id',
        string='Branches'
    )
    addons_path = fields.Char(
        string='Addons Path',
        compute='_get_addons_path',
    )
    error_message = fields.Text(
        string='Error Message',
        help='If you set a message here, when someone try to pull this '
        'repository, this message will be displayed and pull will be aborted'
    )

    @api.one
    @api.depends('directory', 'addons_subdirectory')
    def _get_addons_path(self):
        self.addons_path = os.path.join(
            '/mnt/extra-addons',
            self.directory,
            self.addons_subdirectory and self.addons_subdirectory or '',
        )
