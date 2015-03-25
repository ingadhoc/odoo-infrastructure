# -*- coding: utf-8 -*-
import string
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from fabric.api import cd
from .server import custom_sudo as sudo
from fabric.contrib.files import exists
import os


class environment(models.Model):

    """"""
    _name = 'infrastructure.environment'
    _description = 'environment'
    _inherit = ['ir.needaction_mixin', 'mail.thread']

    _states_ = [
        # State machine: untitle
        ('draft', 'Draft'),
        ('active', 'Active'),
        ('cancel', 'Cancel'),
    ]

    @api.model
    def get_odoo_version(self):
        return self.env['infrastructure.odoo_version'].search([], limit=1)

    number = fields.Integer(
        string='Number',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        )
    name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
        size=16,
        states={'draft': [('readonly', False)]},
        )
    type = fields.Selection(
        [(u'virtualenv', u'Virtualenv'),
         (u'docker', u'Docker'),
         (u'oerpenv', u'Oerpenv')],
        string='Type',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        default='docker'
        )
    description = fields.Char(
        string='Description'
        )
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        )
    odoo_version_id = fields.Many2one(
        'infrastructure.odoo_version',
        string='Odoo Version',
        required=True,
        readonly=True,
        default=get_odoo_version,
        states={'draft': [('readonly', False)]},
        )
    note = fields.Html(
        string='Note'
        )
    color = fields.Integer(
        string='Color Index'
        )
    install_server_command = fields.Char(
        string='Install Server Command',
        default='python setup.py install'
        )
    state = fields.Selection(
        _states_,
        string="State",
        default='draft',
        )
    environment_repository_ids = fields.One2many(
        'infrastructure.environment_repository',
        'environment_id',
        string='Repositories',
        )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        ondelete='cascade',
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
        )
    instance_ids = fields.One2many(
        'infrastructure.instance',
        'environment_id',
        string='Instances',
        context={'from_environment': True},
        )
    sources_path = fields.Char(
        string='Sources Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        )
    backups_path = fields.Char(
        string='Backups Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        )
    path = fields.Char(
        string='Path',
        readonly=True,
        required=True,
        states={'draft': [('readonly', False)]},
        )
    instance_count = fields.Integer(
        string='# Instances',
        compute='_get_instances'
        )
    database_ids = fields.One2many(
        'infrastructure.database',
        'environment_id',
        string='Databases'
        )
    database_count = fields.Integer(
        string='# Databases',
        compute='_get_databases'
        )
    sever_copied = fields.Boolean(
        string='Server Copied?',
        compute='_get_sever_copied'
        )

    @api.multi
    def repositories_pull_clone_and_checkout(self):
        self.environment_repository_ids.repository_pull_clone_and_checkout()

    @api.one
    @api.depends(
        'environment_repository_ids',
        'environment_repository_ids.path',
        'environment_repository_ids.server_repository_id.repository_id.is_server',
            )
    def _get_sever_copied(self):
        sever_copied = False
        servers = [
            x for x in self.environment_repository_ids if x.server_repository_id.repository_id.is_server and x.path]
        if servers:
            sever_copied = True
        self.sever_copied = sever_copied

    @api.one
    @api.depends('database_ids')
    def _get_databases(self):
        self.database_count = len(self.database_ids)

    @api.one
    @api.depends('instance_ids')
    def _get_instances(self):
        self.instance_count = len(self.instance_ids)

    @api.one
    @api.constrains('number')
    def _check_number(self):
        if not self.number or self.number < 10 or self.number > 99:
            raise Warning(_('Number should be between 10 and 99'))

    @api.one
    def unlink(self):
        if self.state not in ('draft', 'cancel'):
            raise Warning(
                _('You cannot delete a environment which is not \
                    draft or cancelled.'))
        return super(environment, self).unlink()

    @api.onchange('server_id')
    def _get_number(self):
        environments = self.search(
            [('server_id', '=', self.server_id.id)],
            order='number desc',
                )
        self.number = environments and environments[0].number + 1 or 10

    @api.onchange('partner_id', 'odoo_version_id')
    def _get_name(self):
        name = False
        if self.partner_id and self.odoo_version_id:
            partner_name = self.partner_id.commercial_partner_id.name
            sufix = self.odoo_version_id.sufix
            name = '%s-%s' % (partner_name, sufix)
            valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
            name = ''.join(c for c in name if c in valid_chars)
            name = name.replace(' ', '').replace('.', '').lower()
        self.name = name

    @api.onchange('name', 'server_id')
    def _get_path(self):
        path = False
        if self.server_id.base_path and self.name:
            path = os.path.join(self.server_id.base_path, self.name)
        self.path = path

    @api.onchange('path')
    def _get_env_paths(self):
        sources_path = False
        backups_path = False
        if self.path:
            sources_path = os.path.join(self.path, 'sources')
            backups_path = os.path.join(self.path, 'backups')
        self.sources_path = sources_path
        self.backups_path = backups_path

    @api.one
    def make_environment(self):
        if self.type == 'virtualenv':
            self.server_id.get_env()
            if exists(self.path, use_sudo=True):
                raise Warning(
                    _("It seams that the environment already exists \
                        because there is a folder '%s'") % (self.path))
            sudo('virtualenv ' + self.path)
        elif self.type == 'oerpenv':
            raise Warning(_("Type '%s' not implemented yet.") % (self.type))

    @api.multi
    def add_repositories(self):
        branch_id = self.odoo_version_id.default_branch_id.id
        server_actual_repository_ids = [
            x.server_repository_id.id for x in self.environment_repository_ids]
        repositories = self.env['infrastructure.server_repository'].search([
            ('repository_id.default_in_new_env', '=', 'True'),
            ('server_id', '=', self.server_id.id),
            ('repository_id.branch_ids', '=', branch_id),
            ('id', 'not in', server_actual_repository_ids),
            ])

        for server_repository in repositories:
            vals = {
                'server_repository_id': server_repository.id,
                'branch_id': branch_id,
                'environment_id': self.id,
            }
            self.environment_repository_ids.create(vals)

    @api.one
    def make_env_paths(self):
        self.server_id.get_env()
        if exists(self.sources_path, use_sudo=True):
            raise Warning(_("Folder '%s' already exists") %
                          (self.sources_path))
        sudo('mkdir -p ' + self.sources_path)
        if exists(self.backups_path, use_sudo=True):
            raise Warning(_("Folder '%s' already exists") %
                          (self.backups_path))
        sudo('mkdir -p ' + self.backups_path)

    @api.one
    @api.returns('infrastructure.environment_repository')
    def check_repositories(self):
        self.server_id.get_env()
        environment_repository = False
        for repository in self.environment_repository_ids:
            if repository.server_repository_id.repository_id.is_server:
                environment_repository = repository
        if not environment_repository:
            raise Warning(
                _("No Server Repository Found on actual environment"))
        if not exists(environment_repository.path, use_sudo=True):
            raise Warning(_("Server Path '%s' does not exist, check \
                server repository path. It is probable that repositories \
                have not been copied to this environment yet.") % (
                environment_repository.path))
        return environment_repository

    @api.one
    def install_odoo(self):
        if self.type == 'virtualenv':
            self.server_id.get_env()
            environment_repository = self.check_repositories()
            with cd(environment_repository.path):
                sudo(
                    'source ' + os.path.join(
                        self.path, 'bin/activate') + ' && ' + \
                    environment_repository.server_repository_id.repository_id.install_server_command)
            self.change_path_group_and_perm()
        else:
            raise Warning(_("Type '%s' not implemented yet.") % (self.type))

    @api.one
    def change_path_group_and_perm(self):
        self.server_id.get_env()
        try:
            sudo('chown -R :%s %s' %
                 (self.server_id.instance_user_group, self.path))
            sudo('chmod -R g+rw %s' % (self.path))
        except:
            raise Warning(_("Error changing group '%s' to path '%s'.\
             Please verifify that group and path exists") % (
                self.server_id.instance_user_group, self.path))

    @api.multi
    def create_environment(self):
        self.make_environment()
        self.make_env_paths()
        self.add_repositories()
        self.signal_workflow('sgn_to_active')

    @api.multi
    def delete(self):
        if self.instance_ids:
            raise Warning(_(
                'You can not delete an environment that has instances'))
        self.server_id.get_env()
        paths = [self.sources_path, self.backups_path, self.path]
        for path in paths:
            sudo('rm -f -r ' + path)
        self.signal_workflow('sgn_cancel')

    @api.multi
    def action_wfk_set_draft(self):
        self.write({'state': 'draft'})
        self.delete_workflow()
        self.create_workflow()
        return True

    _sql_constraints = [
        ('name_uniq', 'unique(name, server_id)',
            'Name must be unique per server!'),
        ('path_uniq', 'unique(path, server_id)',
            'Path must be unique per server!'),
        ('sources_path_uniq', 'unique(path, server_id)',
            'Sources Path must be unique per server!'),
        ('sources_number', 'unique(number, server_id)',
            'Number must be unique per server!'),
    ]

    @api.multi
    def action_view_instances(self):
        '''
        This function returns an action that display a form or tree view
        '''
        instances = self.instance_ids.search(
            [('environment_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_instance_instances')

        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('id', 'in', instances.ids)]
        if len(self) == 1:
            res['context'] = {'default_environment_id': self.id}
        if not len(instances.ids) > 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_instance_form')
            res['views'] = [(form_view_id, 'form')]
            # if 1 then we send res_id, if 0 open a new form view
            res['res_id'] = instances and instances.ids[0] or False
        return res

    @api.multi
    def action_view_databases(self):
        '''
        This function returns an action that display a form or tree view
        '''
        databases = self.database_ids.search(
            [('environment_id', 'in', self.ids)])
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')

        if not action:
            return False
        res = action.read()[0]
        res['domain'] = [('id', 'in', databases.ids)]
        if len(self) == 1:
            res['context'] = {'default_server_id': self.id}
        if not len(databases.ids) > 1:
            form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
                'infrastructure.view_infrastructure_database_form')
            res['views'] = [(form_view_id, 'form')]
            # if 1 then we send res_id, if 0 open a new form view
            res['res_id'] = databases and databases.ids[0] or False
        return res
