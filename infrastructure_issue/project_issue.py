 #-*- coding: utf-8 -*-
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _

class project_issue(osv.Model):
    _inherit = "project.issue"
    
    _columns = {
        'database_id': fields.many2one('infrastructure.database', string="Database"),
    }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
