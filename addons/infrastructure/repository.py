# -*- coding: utf-8 -*-
##############################################################################
#
#    Infrastructure
#    Copyright (C) 2014 Ingenieria ADHOC
#    No email
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


import re
from openerp import netsvc
from openerp.osv import osv, fields

class repository(osv.osv):
    """"""
    
    _name = 'infrastructure.repository'
    _description = 'repository'

    _columns = {
        'sequence': fields.integer(string='sequence'),
        'name': fields.char(string='Name', required=True),
        'folder': fields.char(string='Folder', required=True),
        'type': fields.selection([(u'git', 'git')], string='Type', required=True),
        'addons_subfolder': fields.char(string='Addons Subfolder'),
        'url': fields.char(string='URL', required=True),
        'pip_packages': fields.char(string='PIP Packages'),
        'is_server': fields.boolean(string='Is Server?'),
        'install_server_command': fields.char(string='Install Server Command'),
        'branch_ids': fields.many2many('infrastructure.repository_branch', 'infrastructure_repository_ids_branch_ids_rel', 'repository_id', 'repository_branch_id', string='Branches'), 
    }

    _defaults = {
        'install_server_command': 'python setup.py install',
    }

    _order = "sequence"

    _constraints = [
    ]




repository()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
