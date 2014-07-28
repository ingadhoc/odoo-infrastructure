# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning
from fabric.api import local, settings, abort, run, cd, sudo
from fabric.contrib.files import exists
import os
# TODO implement log_Event new login method
class server_repository(models.Model):
    """"""
    
    _inherit = 'infrastructure.server_repository'
    _rec_name = 'repository_id'

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
        if not path and not exists(path, use_sudo=True):
            raise except_orm(_('No Repository Folder!'), 
                _("Please check that the setted path exists or empty it in order to donwload for first time '%s'!") % (path,))

        with cd(path):
            try:
                sudo ('git pull')
            except:
                raise except_orm(_('Error Making git pull!'), 
                    _("Error making git pull on '%s'!") % (path))        

        
    @api.one
    def get_update_repository(self):
        self.server_id.get_env()
        if not self.path:
            # Check if repository on path
            path = os.path.join(self.server_id.sources_folder, self.repository_id.folder)
            if exists(path, use_sudo=True):
                # aparentemente ya existe el repo, vamos a intentar actualizarlo
                self.update_repository(path)
                self.path = path
            else:
                self.get_repository()
        else:
            self.update_repository()  
        return True