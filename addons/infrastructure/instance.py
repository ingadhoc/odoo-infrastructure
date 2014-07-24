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

class instance(osv.osv):
    """"""
    
    _name = 'infrastructure.instance'
    _description = 'instance'
    _inherits = {  }
    _inherit = [ 'mail.thread','ir.needaction_mixin' ]

    _states_ = [
        # State machine: untitle
        ('draft','Draft'),
        ('active','Active'),
        ('cancel','Cancel'),
    ]
    _track = {
        'state': {
            'infrastructure.instance_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'infrastructure.instance_active': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active',
            'infrastructure.instance_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }
    _columns = {
        'number': fields.integer(string='Number', required=True),
        'name': fields.char(string='Name', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'type': fields.selection([(u'secure', u'Secure'), (u'none_secure', u'None Secure')], string='Instance Type', required=True),
        'xml_rpc_port': fields.integer(string='xml rpc Port', required=True),
        'xml_rpcs_port': fields.integer(string='xml rpcs Port'),
        'longpolling_port': fields.integer(string='Longpolling Port'),
        'db_filter': fields.many2one('infrastructure.db_filter', string='Db filter', required=True),
        'user': fields.char(string='User / Service File', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'note': fields.html(string='Note'),
        'color': fields.integer(string='Color Index'),
        'addons_path': fields.text(string='Addons Path', required=True),
        'conf_file_path': fields.char(string='Config File Path', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'run_server_command': fields.char(string='Run Server Command', required=True),
        'proxy_mode': fields.boolean(string='Proxy Mode?'),
        'logfile': fields.char(string='Log File Path', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'log_level': fields.selection([(u'info', 'info'), (u'debug_rpc', 'debug_rpc'), (u'warn', 'warn'), (u'test', 'test'), (u'critical', 'critical'), (u'debug_sql', 'debug_sql'), (u'error', 'error'), (u'debug', 'debug'), (u'debug_rpc_answer', 'debug_rpc_answer')], string='Log Level'),
        'workers': fields.integer(string='Workers'),
        'data_dir': fields.char(string='Data Directory Path', readonly=True, states={'draft': [('readonly', False)]}),
        'admin_pass': fields.char(string='Admin Password', required=True),
        'unaccent': fields.boolean(string='Enable Unaccent'),
        'module_load': fields.char(string='Load default modules'),
        'service_file': fields.char(string='Service/Nginx File Name', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'main_hostname': fields.char(string='Main Hostname', required=True),
        'state': fields.selection(_states_, "State"),
        'instance_host_ids': fields.one2many('infrastructure.instance_host', 'instance_id', string='Hosts'), 
        'environment_id': fields.many2one('infrastructure.environment', string='Environment', ondelete='cascade', required=True), 
        'database_ids': fields.one2many('infrastructure.database', 'instance_id', string='Databases', context={'from_instance':True}), 
    }

    _defaults = {
        'state': 'draft',
        'number': 1,
        'name': 'main',
        'addons_path': '[]',
        'run_server_command': 'odoo.py',
        'proxy_mode': True,
        'workers': 9,
        'admin_pass': 'admin',
        'type': 'none_secure',
    }


    _constraints = [
    ]


    def get_user(self, cr, uid, ids, context=None):
        """"""
        raise NotImplementedError

    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.instance', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.instance', obj_id, cr)
        return True



instance()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
