# -*- coding: utf-8 -*-

from openerp import models, fields


class db_backup_policy(models.Model):
    """"""

    _name = 'infrastructure.db_backup_policy'
    _description = 'db_backup_policy'

    name = fields.Char(
        string='Name',
        required=True
    )

    backup_prefix = fields.Char(
        string='Back Up Prefix',
        required=True
    )

    cron_id = fields.Many2one(
        'ir.cron',
        string='Cron',
        ondelete='cascade',
        required=True
    )

    database_ids = fields.Many2many(
        'infrastructure.database',
        'infrastructure_database_ids_db_backup_policy_ids_rel',
        'db_backup_policy_id',
        'database_id',
        string='database_ids'
    )

    database_type_ids = fields.Many2many(
        'infrastructure.database_type',
        'infrastructure_database_type_ids_db_backup_policy_ids_rel',
        'db_backup_policy_id',
        'database_type_id',
        string='database_type_ids'
    )
