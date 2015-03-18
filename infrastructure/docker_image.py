# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning
import logging
_logger = logging.getLogger(__name__)


class infrastructure_docker_image(models.Model):
    _name = 'infrastructure.docker_image'
    _description = 'Docker Image'

    name = fields.Char(
        'Name',
        required=True,
        )
    prefix = fields.Char(
        'Prefix',
        required=True,
        )
    pull_name = fields.Char(
        'Pull Name',
        required=True,
        )
    tag_ids = fields.One2many(
        'infrastructure.docker_image.tag',
        'docker_image_id',
        'Tags',
        )
    odoo_version_id = fields.Many2one(
        'infrastructure.odoo_version',
        'Version',
        )
    service = fields.Selection(
        [('odoo', 'Odoo'), ('postgresql', 'Postgresql'), ('other', 'Other')],
        string='Servicce',
        default='odoo',
        required=True,
        )
    pg_image_ids = fields.Many2many(
        'infrastructure.docker_image',
        'infrastructure_odoo_pg_image_rel',
        'odoo_image_id', 'pg_image_id',
        string='Postgresql Images',
        domain=[('service', '=', 'postgresql')],
        help='Compatible Postgresql Images',
        )
    odoo_image_ids = fields.Many2many(
        'infrastructure.docker_image',
        'infrastructure_odoo_pg_image_rel',
        'pg_image_id', 'odoo_image_id',
        string='Odoo Images',
        domain=[('service', '=', 'odoo')],
        help='Compatible Odoo Images',
        )


class infrastructure_docker_image_tag(models.Model):
    _name = 'infrastructure.docker_image.tag'
    _description = 'Docker Image Tag'
    _order = 'sequence'

    name = fields.Char(
        'Name',
        required=True,
        )
    sequence = fields.Integer(
        'Name',
        )
    docker_image_id = fields.Many2one(
        'infrastructure.docker_image',
        'Name',
        required=True,
        ondelete='cascade',
        )
