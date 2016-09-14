# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _
from openerp.osv import osv
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from datetime import date


class infrastructure_database_backup_now_wizard(osv.osv_memory):
    _name = "infrastructure.database.backup_now.wizard"
    _description = "Infrastructure Database Backup Now Wizard"

    @api.model
    def get_default_keep_till_date(self):
        return date.strftime(date.today() + relativedelta(days=30), '%Y-%m-%d')

    backup_format = fields.Selection([
        ('zip', 'zip (With Filestore)'),
        ('pg_dump', 'pg_dump (Without Filestore)')],
        'Backup Format',
        default='zip',
        required=True,
    )
    name = fields.Char(
        string='Name',
        required=True,
    )
    keep_till_date = fields.Date(
        'Keep Till Date',
        help="Only for manual backups, if not date is configured then backup "
        "won't be deleted.",
        default=get_default_keep_till_date,
    )

    @api.multi
    def confirm(self):
        self.ensure_one()
        active_id = self.env.context.get('active_id', False)
        if not active_id:
            raise Warning(
                _("Can not run backup now, no active_id on context"))
        database = self.env['infrastructure.database'].browse(active_id)
        name = "%s.%s" % (self.name, self.backup_format)
        return database.backup_now(
            name=name,
            keep_till_date=self.keep_till_date,
            backup_format=self.backup_format
        )
