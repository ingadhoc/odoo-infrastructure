# -*- coding: utf-8 -*-

from openerp import models, fields, api
from openerp.tools.safe_eval import safe_eval as eval
from fabric.api import run, cd, env, sudo
from fabric.contrib.files import exists, append, sed
import errno
import time
import os


class server_configuration_command(models.Model):
    """"""

    _name = 'infrastructure.server_configuration_command'
    _description = 'server_configuration_command'
    _inherit = ['infrastructure.command']

    server_configuration_id = fields.Many2one(
        'infrastructure.server_configuration',
        string='server_configuration_id',
        ondelete='cascade',
        required=True
    )

    _order = "sequence"

    # @api.one
    # def execute_command(self):
    #     context = self._context
    #     if context is None:
    #         context = {}
    #     recs = self.browse()
    #     user = recs.env['res.users'].browse(recs.env.uid)
    #     res = []
    #     server_id = context.get('server_id', False)
    #     if server_id:
    #         server = recs.env['infrastructure.server'].browse(server_id)

    #         command = self.browse(self.id)
    #         command_result = False
    #         # QUEDE ACA
    #         env.user = server.user_name
    #         env.password = server.password
    #         env.host_string = server.main_hostname
    #         env.port = server.ssh_port
    #         cxt = {
    #             'self': self,
    #             'os': os,
    #             'errno': errno,
    #             'command': command,
    #             'run': run,
    #             'sudo': sudo,
    #             'server': server,
    #             'cd': cd,
    #             'pool': self.pool,
    #             'time': time,
    #             'cr': cr,
    #             # copy context to prevent side-effects of eval
    #             'context': dict(context),
    #             'uid': uid,
    #             'user': user,
    #         }
    #         print 'command.command', command.command
    #         print 'command.command.strip()', command.command.strip()
    #         # nocopy allows to return 'action'
    #         eval(command.command.strip(), cxt, mode="exec")
    #         if 'result' in cxt['context']:
    #             command_result = cxt['context'].get('result')
    #         result.append(command_result)
    #     return result

    #     else:
    #         # TODO raise error
    #         print
    #         print 'no server_id on context'
    #         print
    #         return False

    #         --------

    #     for command in self.browse(cr, uid, ids, context=context):
    #         command_result = False
    #         env.user = server.user_name
    #         env.password = server.password
    #         env.host_string = server.main_hostname
    #         env.port = server.ssh_port
    #         cxt = {
    #             'self': self,
    #             'os': os,
    #             'errno': errno,
    #             'command': command,
    #             'run': run,
    #             'sudo': sudo,
    #             'server': server,
    #             'cd': cd,
    #             'pool': self.pool,
    #             'time': time,
    #             'cr': cr,
    #             # copy context to prevent side-effects of eval
    #             'context': dict(context),
    #             'uid': uid,
    #             'user': user,
    #         }
    #         print 'command.command', command.command
    #         print 'command.command.strip()', command.command.strip()
    #         # nocopy allows to return 'action'
    #         eval(command.command.strip(), cxt, mode="exec")
    #         if 'result' in cxt['context']:
    #             command_result = cxt['context'].get('result')
    #         result.append(command_result)
    #     return result



    def execute_command(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.users').browse(cr, uid, uid)
        result = []
        server_id = context.get('server_id', False)
        if not server_id:
            # TODO raise error
            print 'no server_id on context'
            return False
        server = self.pool['infrastructure.server'].browse(
            cr, uid, server_id, context=context)
        for command in self.browse(cr, uid, ids, context=context):
            command_result = False
            env.user = server.user_name
            env.password = server.password
            env.host_string = server.main_hostname
            env.port = server.ssh_port
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
                # Fabric file commands
                'exists': exists,
                'append': append,
                'sed': sed,
                # copy context to prevent side-effects of eval
                'context': dict(context),
                'uid': uid,
                'user': user,
            }
            print 'command.command', command.command
            print 'command.command.strip()', command.command.strip()
            # nocopy allows to return 'action'
            eval(command.command.strip(), cxt, mode="exec")
            if 'result' in cxt['context']:
                command_result = cxt['context'].get('result')
            result.append(command_result)
        return result
