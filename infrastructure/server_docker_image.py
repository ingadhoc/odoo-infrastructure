# -*- coding: utf-8 -*-
from openerp import models, fields, api
from .server import custom_sudo as sudo
import logging
_logger = logging.getLogger(__name__)


class server_docker_image(models.Model):

    """"""
    _name = 'infrastructure.server_docker_image'
    _description = 'Server Docker Image'
    _rec_name = 'docker_image_id'

    docker_image_id = fields.Many2one(
        'infrastructure.docker_image',
        'Docker Image',
        required=True,
    )
    server_id = fields.Many2one(
        'infrastructure.server',
        'Server',
        required=True,
        ondelete='cascade',
    )

    @api.multi
    def pull_image(self, context=None, detached=False):
        """ Tuvimos que ponerle el context porque desde la vista lo pasa sin
        enmascararlo en self"""
        self.server_id.get_env()
        image_name = self.docker_image_id.pull_name
        _logger.info("Pulling Image %s" % image_name)
        if detached:
            sudo('dtach -n `mktemp -u /tmp/dtach.XXXX` docker pull %s' %
                 image_name)
        else:
            sudo('docker pull %s' % image_name)

    @api.multi
    def pull_image_detached(self):
        self.pull_image(detached=True)
