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

class environment(osv.osv):
    """"""
    
    _name = 'infrastructure.environment'
    _description = 'environment'
    _inherits = {  }
    _inherit = [ 'ir.needaction_mixin','mail.thread' ]

    _states_ = [
        # State machine: untitle
        ('draft','Draft'),
        ('active','Active'),
        ('cancel','Cancel'),
    ]
    _track = {
        'state': {
            'infrastructure.environment_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'infrastructure.environment_active': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active',
            'infrastructure.environment_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }
    _columns = {
        'number': fields.integer(string='Number', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'name': fields.char(string='Name', readonly=True, required=True, size=16, states={'draft': [('readonly', False)]}),
        'type': fields.selection([(u'virtualenv', u'Virtualenv'), (u'oerpenv', u'Oerpenv')], string='Type', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'description': fields.char(string='Description'),
        'partner_id': fields.many2one('res.partner', string='Partner', required=True),
        'environment_version_id': fields.many2one('infrastructure.environment_version', string='Version', required=True),
        'note': fields.html(string='Note'),
        'color': fields.integer(string='Color Index'),
        'path': fields.char(string='Path', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'sources_path': fields.char(string='Sources Path', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'install_server_command': fields.char(string='Install Server Command', required=True),
        'state': fields.selection(_states_, "State"),
        'environment_repository_ids': fields.one2many('infrastructure.environment_repository', 'environment_id', string='Repositories'), 
        'server_id': fields.many2one('infrastructure.server', string='Server', ondelete='cascade', required=True), 
        'instance_ids': fields.one2many('infrastructure.instance', 'environment_id', string='Instances', context={'from_environment':True}), 
    }

    _defaults = {
        'state': 'draft',
        'install_server_command': 'python setup.py install',
        'type': 'virtualenv',
    }


    _constraints = [
    ]


    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.environment', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.environment', obj_id, cr)
        return True



environment()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
