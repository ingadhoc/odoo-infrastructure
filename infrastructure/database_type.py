# -*- coding: utf-8 -*-

from openerp import models, fields


class database_type(models.Model):

    _name = 'infrastructure.database_type'
    _description = 'database_type'

    name = fields.Char(
        string='Name',
        required=True
    )

    prefix = fields.Char(
        string='Prefix',
        required=True,
        size=4
    )

    url_prefix = fields.Char(
        string='URL Prefix'
    )

    automatic_drop = fields.Boolean(
        string='Automatic Drop'
    )

    automatic_drop_days = fields.Integer(
        string='Automatic Drop Days'
    )

    protect_db = fields.Boolean(
        string='Protect Databases?'
    )

    color = fields.Integer(
        string='Color'
    )

    automatic_deactivation = fields.Boolean(
        string='Automatic Deactivation?'
    )

    auto_deactivation_days = fields.Integer(
        string='Automatic Deactivation Days'
    )

    url_example = fields.Char(
        string='URL Example'
    )

    db_name_example = fields.Char(
        string='Database Name Example'
    )

    db_back_up_policy_ids = fields.Many2many(
        'infrastructure.db_back_up_policy',
        'infrastructure_database_type_ids_db_back_up_policy_ids_rel',
        'database_type_id',
        'db_back_up_policy_id',
        string='Suggested Backup Policies'
    )

database_type()
