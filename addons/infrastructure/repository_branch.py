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

class repository_branch(osv.osv):
    """"""
    
    _name = 'infrastructure.repository_branch'
    _description = 'repository_branch'

    _columns = {
        'name': fields.char(string='Name', required=True),
        'repository_ids': fields.many2many('infrastructure.repository', 'infrastructure_repository_ids_branch_ids_rel', 'repository_branch_id', 'repository_id', string='repository_ids'), 
    }

    _defaults = {
    }


    _constraints = [
    ]




repository_branch()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
