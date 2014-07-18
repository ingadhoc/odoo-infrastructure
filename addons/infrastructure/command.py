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

class command(osv.osv):
    """"""
    
    _name = 'infrastructure.command'
    _description = 'command'

    _columns = {
        'sequence': fields.integer(string='sequence'),
        'type': fields.selection([(u'installation', 'installation'), (u'maintenance', 'maintenance')], string='Type', required=True),
        'name': fields.char(string='Name', required=True),
        'command': fields.text(string='Command', required=True),
    }

    _defaults = {
        'type': 'maintenance',
    }

    _order = "sequence"

    _constraints = [
    ]




command()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
