# -*- coding: utf-8 -*-
import re
from openerp import netsvc
from openerp.osv import osv, fields

class server_configuration(osv.osv):
    """"""
    
    _inherit = 'infrastructure.server_configuration'

    _columns = {
        'maint_command_ids': fields.one2many('infrastructure.server_configuration_command', 'server_configuration_id', string='Maintenance Commands', context={'default_type':'maintenance'}, domain=[('type','=','maintenance')]), 
    }
