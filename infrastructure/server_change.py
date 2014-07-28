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

class server_change(osv.osv):
    """"""
    
    _name = 'infrastructure.server_change'
    _description = 'server_change'

    _columns = {
        'name': fields.char(string='Summary', required=True),
        'date': fields.date(string='Date', required=True),
        'user_id': fields.many2one('res.users', string='User', required=True),
        'description': fields.text(string='Description', required=True),
        'server_id': fields.many2one('infrastructure.server', string='Server', ondelete='cascade', required=True), 
    }

    _defaults = {
        'date': fields.date.context_today,
        'user_id': lambda self, cr, uid, context: uid,
    }


    _constraints = [
    ]




server_change()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
