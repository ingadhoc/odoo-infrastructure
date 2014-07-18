# -*- coding: utf-8 -*-
import re
from openerp import netsvc
from openerp.osv import osv, fields
# from openerp.tools.safe_eval import safe_eval as eval
from .non_safe_eval import safe_eval as eval
import time
import os, errno
from fabric.api import local, settings, abort, run, cd, env, sudo, put

class environment_version_command(osv.osv):
    """"""
    
    _inherit = 'infrastructure.environment_version_command'

    def execute_command(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        result = []
        environment_id = context.get('environment_id',False)
        if not environment_id:
            # TODO raise error
            print 'no environment_id on context'
            return False
        environment = self.pool['infrastructure.environment'].browse(cr, uid, environment_id, context=context)            
        for command in self.browse(cr, uid, ids, context=context):
            command_result = False
            env.user=environment.server_id.user_name
            env.password=environment.server_id.password
            env.host_string=environment.server_id.main_hostname
            env.port=environment.server_id.ssh_port
            cxt = {
                'self': self,
                'os': os,
                'errno': errno,
                'command': command,
                'run': run,
                'sudo': sudo,
                'environment': environment,
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

