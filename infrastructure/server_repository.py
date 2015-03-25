# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm
from fabric.api import cd
from .server import custom_sudo as sudo
from fabric.contrib.files import exists
import os


class server_repository(models.Model):
    """"""

    _name = 'infrastructure.server_repository'
    _description = 'server_repository'
    _rec_name = 'repository_id'

    repository_id = fields.Many2one(
        'infrastructure.repository',
        string='Repository',
        required=True
        )
    path = fields.Char(
        string='Path'
        )
    server_id = fields.Many2one(
        'infrastructure.server',
        string='server_id',
        ondelete='cascade',
        required=True
        )

    @api.one
    def get_repository(self):
        print 'Getting repository'
        self.path = self.repository_id.get_repository(self.server_id)[0]

    @api.one
    def update_repository(self, path=False):
        print 'Updating repository'
        self.server_id.get_env()
        if not path:
            path = self.path
        if not path or not exists(path, use_sudo=True):
            cmd = 'git clone %s %s' % (self.repository_id.url, path)
            try:
                sudo(cmd, user='odoo', group='odoo')
            except SystemExit, e:
                raise except_orm(
                    _("Error executing '%s' on '%s'") % (cmd, path),
                    _('Unknown system error')
                )
        else:
            cmd = 'git pull'
            with cd(path.strip()):
                try:
                    sudo(cmd)
                except Exception, e:
                    raise except_orm(
                        _("Error executing '%s' on '%s'") % (cmd, path),
                        _('Command output: %s') % e
                    )
                except SystemExit, e:
                    raise except_orm(
                        _("Error executing '%s' on '%s'") % (cmd, path),
                        _('Unknown system error')
                    )

    @api.one
    def get_update_repository(self):
        self.server_id.get_env()
        if not self.path:
            # Check if repository on path
            path = os.path.join(
                self.server_id.sources_path, self.repository_id.directory)
            if exists(path, use_sudo=True):
                # aparentemente ya existe el repo, intentamos actualizarlo
                self.update_repository(path)
                self.path = path
            else:
                self.get_repository()
        else:
            self.update_repository()
        return True
