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

class database(osv.osv):
    """"""
    
    _name = 'infrastructure.database'
    _description = 'database'
    _inherits = {  }
    _inherit = [ 'ir.needaction_mixin','mail.thread' ]

    _states_ = [
        # State machine: untitle
        ('draft','Draft'),
        ('maintenance','Maintenance'),
        ('active','Active'),
        ('deactivated','Deactivated'),
        ('cancel','Cancel'),
    ]
    _track = {
        'state': {
            'infrastructure.database_draft': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'draft',
            'infrastructure.database_maintenance': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'maintenance',
            'infrastructure.database_active': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'active',
            'infrastructure.database_deactivated': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'deactivated',
            'infrastructure.database_cancel': lambda self, cr, uid, obj, ctx=None: obj['state'] == 'cancel',
        },
    }
    _columns = {
        'database_type_id': fields.many2one('infrastructure.database_type', string='Type', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'name': fields.char(string='Name', readonly=True, required=True, states={'draft': [('readonly', False)]}),
        'partner_id': fields.many2one('res.partner', string='Partner', required=True),
        'demo_data': fields.boolean(string='Demo Data?', readonly=True, states={'draft': [('readonly', False)]}),
        'note': fields.html(string='note'),
        'color': fields.integer(string='Color Index'),
        'smtp_server_id': fields.many2one('infrastructure.mailserver', string='SMTP Server'),
        'alias_domain': fields.char(string='Alias Domain'),
        'attachment_loc_type': fields.selection([(u'filesystem', 'filesystem'), (u'database', 'database')], string='Attachment Location Type'),
        'attachment_location': fields.char(string='Attachment Location'),
        'issue_date': fields.date(string='Issue Date'),
        'deactivation_date': fields.date(string='Deactivation Date'),
        'state': fields.selection(_states_, "State"),
        'db_back_up_policy_ids': fields.many2many('infrastructure.db_back_up_policy', 'infrastructure_database_ids_db_back_up_policy_ids_rel', 'database_id', 'db_back_up_policy_id', string='Suggested Backup Policies'), 
        'instance_id': fields.many2one('infrastructure.instance', string='Instance', ondelete='cascade', required=True), 
    }

    _defaults = {
        'state': 'draft',
        'attachment_loc_type': 'filesystem',
    }


    _constraints = [
    ]


    def action_wfk_set_draft(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state':'draft'})
        wf_service = netsvc.LocalService("workflow")
        for obj_id in ids:
            wf_service.trg_delete(uid, 'infrastructure.database', obj_id, cr)
            wf_service.trg_create(uid, 'infrastructure.database', obj_id, cr)
        return True



database()

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
