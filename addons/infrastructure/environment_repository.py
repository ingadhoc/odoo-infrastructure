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

class environment_repository(osv.osv):
    """"""
    
    _name = 'infrastructure.environment_repository'
    _description = 'environment_repository'

    _columns = {
        'server_repository_id': fields.many2one('infrastructure.server_repository', string='Server Repository', required=True),
        'branch_id': fields.many2one('infrastructure.repository_branch', string='Specific Branch', required=True),
        'path': fields.char(string='Path'),
        'addons_paths': fields.char(string='Addons Path', required=True),
        'branch_ids': fields.many2one('infrastructure.repository_branch', string='branch_ids', readonly=True),
        'environment_id': fields.many2one('infrastructure.environment', string='environment_id', ondelete='cascade', required=True), 
    }

    _defaults = {
        'addons_paths': '[]',
    }


    _constraints = [
    ]




environment_repository()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
