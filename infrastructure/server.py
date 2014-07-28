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

class server(osv.osv):
    """"""
    
    _name = 'infrastructure.server'
    _description = 'server'
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
            'infrastructure.server_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'infrastructure.server_active': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active',
            'infrastructure.server_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }
    _columns = {
        'name': fields.char(string='Name', required=True),
        'ip_address': fields.char(string='IP Address', required=True),
        'ssh_port': fields.char(string='SSH Port', required=True),
        'main_hostname': fields.char(string='Main Hostname', required=True),
        'user_name': fields.char(string='User Name'),
        'password': fields.char(string='Password'),
        'holder_id': fields.many2one('res.partner', string='Holder', required=True),
        'owner_id': fields.many2one('res.partner', string='Owner', required=True),
        'user_id': fields.many2one('res.partner', string='Used By', required=True),
        'software_data': fields.html(string='Software Data'),
        'hardware_data': fields.html(string='Hardware Data'),
        'contract_data': fields.html(string='Contract Data'),
        'note': fields.html(string='Note'),
        'base_path': fields.char(string='Base path', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'color': fields.integer(string='Color Index'),
        'sources_folder': fields.char(string='Sources Folder', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'service_folder': fields.char(string='Service Folder', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'instance_user_group': fields.char(string='Instance Users Group', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'nginx_log_folder': fields.char(string='Nginx Log Folder', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'nginx_sites_path': fields.char(string='Nginx Sites Path', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'gdrive_account': fields.char(string='Gdrive Account', readonly=True, states={'draft': [('readonly', False)]}),
        'gdrive_passw': fields.char(string='Gdrive Password', readonly=True, states={'draft': [('readonly', False)]}),
        'gdrive_space': fields.char(string='Gdrive Space'),
        'open_ports': fields.char(string='Open Ports'),
        'requires_vpn': fields.boolean(string='Requires VPN?'),
        'state': fields.selection(_states_, "State"),
        'server_service_ids': fields.one2many('infrastructure.server_service', 'server_id', string='Services'), 
        'server_repository_ids': fields.one2many('infrastructure.server_repository', 'server_id', string='server_repository_ids'), 
        'hostname_ids': fields.one2many('infrastructure.server_hostname', 'server_id', string='Hostnames'), 
        'change_ids': fields.one2many('infrastructure.server_change', 'server_id', string='Changes'), 
        'environment_ids': fields.one2many('infrastructure.environment', 'server_id', string='Environments', context={'from_server':True}), 
        'server_configuration_id': fields.many2one('infrastructure.server_configuration', string='Server Config.', required=True), 
    }

    _defaults = {
        'state': 'draft',
        'base_path': '/opt/odoo/',
        'sources_folder': '/opt/odoo/sources',
        'service_folder': '/etc/init.d',
        'instance_user_group': 'odoo',
        'nginx_log_folder': '/var/log/nginx',
        'nginx_sites_path': '/etc/nginx/sites-enabled',
    }


    _constraints = [
    ]


    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.server', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.server', obj_id, cr)
        return True



server()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
