# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from .non_safe_eval import safe_eval as eval
# from openerp.tools.safe_eval import safe_eval as eval
import time
import os, errno
from fabric.api import local, settings, abort, run, cd, sudo
from fabric.contrib.files import exists
    
class repository(models.Model):
    """"""
    
    _inherit = 'infrastructure.repository'
    # TODO agregar constraint que valide unidicidad de url de repository

    @api.one    
    def get_repository(self, server):
        server.get_env()
        if not exists(server.sources_folder, use_sudo=True):
            raise except_orm(_('No Source Folder!'), 
                _("Please first create the source folder '%s'!") % (server.sources_folder,))
        with cd (server.sources_folder):
            path = False
            if self.type == 'git':
                command = 'git clone ' 
                command += self.url 
                command += ' ' + self.folder
                sudo (command)
                path = os.path.join(server.sources_folder, self.folder)
            # TODO implementar otros tipos de repos
        return path