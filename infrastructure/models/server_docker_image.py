# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
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

    _sql_constraints = [
        ('image_uniq', 'unique(docker_image_id, server_id)',
            'Docker Image Must be Unique per server'),
    ]

    @api.multi
    def pull_image(self, context=None, detached=False):
        """ Tuvimos que ponerle el context porque desde la vista lo pasa sin
        enmascararlo en self"""
        self.server_id.get_env()
        image = self.docker_image_id
        image_name = image.pull_name
        # if any tag, pull the first one
        if image.tag_ids:
            image_name = '%s:%s' % (image_name, image.tag_ids[0].name)
        _logger.info("Pulling Image %s" % image_name)
        if detached:
            sudo('dtach -n `mktemp -u /tmp/dtach.XXXX` docker pull %s' %
                 image_name)
        else:
            sudo('docker pull %s' % image_name)

    @api.multi
    def pull_image_detached(self):
        self.pull_image(detached=True)
