# -*- coding: utf-8 -*-

from openerp import models, fields


class db_back_up_policy(models.Model):
    """"""

    _name = 'infrastructure.db_back_up_policy'
    _description = 'db_back_up_policy'

    name = fields.Char(
        string='name',
        required=True
    )

    cron_id = fields.Many2one(
        'ir.cron',
        string='Cron',
        required=True
    )

    database_ids = fields.Many2many(
        'infrastructure.database',
        'infrastructure_database_ids_db_back_up_policy_ids_rel',
        'db_back_up_policy_id',
        'database_id',
        string='database_ids'
    )

    database_type_ids = fields.Many2many(
        'infrastructure.database_type',
        'infrastructure_database_type_ids_db_back_up_policy_ids_rel',
        'db_back_up_policy_id',
        'database_type_id',
        string='database_type_ids'
    )


db_back_up_policy()
