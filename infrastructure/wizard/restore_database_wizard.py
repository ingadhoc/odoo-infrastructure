# -*- coding: utf-8 -*-

from openerp import fields, api, _
from openerp.osv import osv
from openerp.exceptions import Warning


class infrastructure_restore_database_wizard(osv.osv_memory):
    _name = "infrastructure.restore_database.wizard"
    _description = "Infrastructure Restore Database Wizard"

    def _get_database_backup(self):
        dump_id = self.env.context.get('active_ids', False)
        if dump_id:
            d = self.env['infrastructure.database.backup'].browse(dump_id[0])
            return d
        return False

    def _get_create_date(self):
        d = self._get_database_backup()
        return d.create_date

    def _get_server_id(self):
        d = self._get_database_backup()
        return d.database_id.server_id

    def _get_environment_id(self):
        d = self._get_database_backup()
        return d.database_id.instance_id.environment_id

    def _get_instance_id(self):
        d = self._get_database_backup()
        return d.database_id.instance_id

    def _get_database_id(self):
        d = self._get_database_backup()
        return d.database_id

    database_backup_id = fields.Many2one(
        'infrastructure.database.backup',
        string='Dump File',
        default=_get_database_backup,
        readonly=True
    )

    create_date = fields.Datetime(
        string='Created On',
        default=_get_create_date,
        readonly=True,
    )

    server_id = fields.Many2one(
        'infrastructure.server',
        string='Server',
        default=_get_server_id,
        required=True,
        readonly=False
    )

    environment_id = fields.Many2one(
        'infrastructure.environment',
        string='Environment',
        default=_get_environment_id,
        required=True,
        readonly=False
    )

    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='Instance',
        default=_get_instance_id,
        required=True,
        readonly=False
    )

    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        default=_get_database_id,
        required=True,
        readonly=False,
    )

    overwrite_active = fields.Boolean(
        string='Overwrite Active Database?',
        default=False
    )

    @api.one
    def restore_database(self):
        active_ids = self.env.context.get('active_ids', False)
        if not active_ids:
            raise Warning(
                _("Cannot restore database, no active_ids on context"))
        dumps = self.env['infrastructure.database.backup'].search(
            [('id', 'in', active_ids)])
        for dump in dumps:
            dump.restore(self.database_id, self.overwrite_active)
        return True
