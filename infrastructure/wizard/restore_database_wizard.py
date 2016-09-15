# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import fields, api, models, _
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class infrastructure_restore_database_wizard(models.TransientModel):
    _name = "infrastructure.restore_database.wizard"
    _description = "Infrastructure Restore Database Wizard"

    def _get_database_backup(self):
        dump_id = self.env.context.get('active_id', False)
        return self.env['infrastructure.database.backup'].browse(dump_id)

    def _get_instance(self):
        d = self._get_database_backup()
        return d.database_id.instance_id

    def _get_target_database(self):
        d = self._get_database_backup()
        return d.database_id

    type = fields.Selection(
        [('overwrite', 'Overwrite Database'), ('new', 'New Database')],
        required=True,
        default='new',
    )
    target_db_name_check = fields.Char(
        'Database full name',
    )
    target_advance_type = fields.Selection(
        related='target_database_id.advance_type',
        string='Type',
        readonly=True,
    )
    database_backup_id = fields.Many2one(
        'infrastructure.database.backup',
        string='Dump File',
        default=_get_database_backup,
        readonly=True,
        required=True,
        ondelete='cascade',
    )
    target_database_id = fields.Many2one(
        'infrastructure.database',
        string='Target Database',
        default=_get_target_database,
    )
    instance_id = fields.Many2one(
        'infrastructure.instance',
        string='Instance',
        required=True,
        domain=[('state', '=', 'active')],
        default=_get_instance,
        ondelete='cascade',
    )
    # database_type_id = fields.Many2one(
    #     'infrastructure.database_type',
    #     string='Database Type',
    #     # required=True,
    # )
    new_db_name = fields.Char(
        string='New db Name',
        # required=True
    )
    backups_enable = fields.Boolean(
        'Backups Enable on new DB?'
    )

    # @api.onchange('instance_id')
    # def change_instance(self):
    #     if self.instance_id:
    #         self.database_type_id = self.instance_id.database_type_id

    # @api.onchange('database_type_id')
    # def onchange_database_type_id(self):
    #     if self.database_type_id:
    #         self.new_db_name = self.database_type_id.prefix + '_'

    @api.multi
    def restore_database(self):
        self.ensure_one()
        overwrite = False
        db_name = self.new_db_name
        instance = self.instance_id
        backups_enable = self.backups_enable
        # database_type = self.database_type_id
        if self.type == 'overwrite':
            if (
                    self.target_advance_type == 'protected' and
                    self.target_database_id.name != self.target_db_name_check):
                raise Warning(_('Target db name mismatch'))
            overwrite = True
            db_name = self.target_database_id.name

        # restore database
        self.database_backup_id.restore(
            instance, db_name,
            backups_enable, overwrite=overwrite)

        if self.type == 'overwrite':
            database = self.target_database_id
        else:
            _logger.info('Creating new database data on infra')
            database = self.database_backup_id.database_id.copy({
                'name': db_name,
                'backups_enable': backups_enable,
                'issue_date': fields.Date.today(),
                # 'database_type_id': database_type.id,
                'instance_id': instance.id,
            })
        database.action_activate()

        # we run it because it is not enaught what database_tools does with
        # this parameter, it could be necesary to load new data of backups
        if backups_enable:
            database.config_backups()

        # devolvemos la accion de la nueva bd creada
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_database_databases')
        if not action:
            return False
        res = action.read()[0]

        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'infrastructure.view_infrastructure_database_form')
        res['views'] = [(form_view_id, 'form')]
        res['res_id'] = database.id
        return res
