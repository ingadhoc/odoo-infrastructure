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

class server_configuration(osv.osv):
    """"""
    
    _name = 'infrastructure.server_configuration'
    _description = 'server_configuration'

    _columns = {
        'name': fields.char(string='Name', required=True),
        'install_command_ids': fields.one2many('infrastructure.server_configuration_command', 'server_configuration_id', string='Installation Commands', context={'default_type':'installation'}, domain=[('type','=','installation')]), 
        'server_ids': fields.one2many('infrastructure.server', 'server_configuration_id', string='server_ids'), 
    }

    _defaults = {
    }


    _constraints = [
    ]




server_configuration()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
