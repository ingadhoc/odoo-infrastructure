# -*- coding: utf-8 -*-
import re
from openerp import netsvc
from openerp.osv import osv, fields
from openerp.tools.safe_eval import safe_eval as eval
import time
import os, errno
from fabric.api import local, settings, abort, run, cd, env, sudo

class server_configuration_command(osv.osv):
    """"""
    
    _inherit = 'infrastructure.server_configuration_command'

    _columns = {
    }

    def execute_command(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        result = []
        server_id = context.get('server_id',False)
        if not server_id:
            # TODO raise error
            print 'no server_id on context'
            return False
        server = self.pool['infrastructure.server'].browse(cr, uid, server_id, context=context)
        for command in self.browse(cr, uid, ids, context=context):
            command_result = False
            env.user=server.user_name
            env.password=server.password
            env.host_string=server.main_hostname
            env.port=server.ssh_port
            cxt = {
                'self': self,
                'os': os,
                'errno': errno,
                'command': command,
                'run': run,
                'sudo': sudo,
                'server': server,
                'cd': cd,
                'pool': self.pool,
                'time': time,
                'cr': cr,
                'context': dict(context), # copy context to prevent side-effects of eval
                'uid': uid,
                'user': user,
            }
            print 'command.command', command.command
            print 'command.command.strip()', command.command.strip()
            eval(command.command.strip(), cxt, mode="exec") # nocopy allows to return 'action'
            if 'result' in cxt['context']:
                command_result = cxt['context'].get('result')
            result.append(command_result)
        return result
