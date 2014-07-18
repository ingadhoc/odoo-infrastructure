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

class database_type(osv.osv):
    """"""
    
    _name = 'infrastructure.database_type'
    _description = 'database_type'

    _columns = {
        'name': fields.char(string='Name', required=True),
        'prefix': fields.char(string='Prefix', required=True, size=4),
        'url_prefix': fields.char(string='URL Prefix'),
        'automatic_drop': fields.boolean(string='Automatic Drop'),
        'automatic_drop_days': fields.integer(string='Automatic Drop Days'),
        'protect_db': fields.boolean(string='Protect DBs?'),
        'color': fields.integer(string='Color'),
        'automatic_deactivation': fields.boolean(string='Atumatic Deactivation?'),
        'auto_deactivation_days': fields.integer(string='Automatic Drop Days'),
        'url_example': fields.char(string='URL Example'),
        'bd_name_example': fields.char(string='BD Name Example'),
        'db_back_up_policy_ids': fields.many2many('infrastructure.db_back_up_policy', 'infrastructure_database_type_ids_db_back_up_policy_ids_rel', 'database_type_id', 'db_back_up_policy_id', string='Suggested Backup Policies'), 
    }

    _defaults = {
    }


    _constraints = [
    ]




database_type()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
