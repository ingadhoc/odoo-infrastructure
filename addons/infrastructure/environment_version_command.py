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

class environment_version_command(osv.osv):
    """"""
    
    _name = 'infrastructure.environment_version_command'
    _description = 'environment_version_command'
    _inherits = {  }
    _inherit = [ 'infrastructure.command' ]

    _columns = {
        'environment_version_id': fields.many2one('infrastructure.environment_version', string='Environment Version', ondelete='cascade', required=True), 
    }

    _defaults = {
    }

    _order = "sequence"

    _constraints = [
    ]




environment_version_command()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
