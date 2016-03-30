# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, _, models
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class infrastructure_instance_update(models.Model):
    _name = "infrastructure.instance.update"
    _inherit = ['ir.needaction_mixin', 'mail.thread']

    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        )
    uninstall_modules = fields.Boolean(
        )
    name = fields.Char(
        required=True,
        )
    detail_ids = fields.One2many(
        'infrastructure.instance.update.detail',
        'update_id',
        'Instances',
        )
    # instance_ids = fields.Many2many(
    #     'infrastructure.instance',
    #     'infrastructure_instance_update_instance_rel',
    #     'update_id', 'instance_id',
    #     'Instances',
    #     required=True,
    #     )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        )
    notify_email = fields.Char(
        )
    # TODO agregar funcionalidad
    # update_odoo_docker_image = fields.Boolean(
    #     'Update Odoo Docker Image?'
    #     )
    repository_ids = fields.Many2many(
        'infrastructure.repository',
        'infrastructure_instance_update_repository_rel',
        'update_id', 'repository_id',
        string='Repositories',
        )
    result = fields.Text(
        readonly=True,
        )
    state = fields.Selection([
        ('draft', 'Draft'), ('to_run', 'To Run'),
        ('done', 'Done'), ('cancel', 'Cancel')],
        required=True,
        default='draft',
        )

    @api.onchange('user_id')
    def change_user(self):
        self.notify_email = self.user_id.email

    @api.multi
    def action_to_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_confirm(self):
        self.write({'state': 'to_run'})

    @api.model
    def cron_instance_update(self):
        instances_to_update = self.search([
                ('state', '=', 'to_run'),
            ])
        for record in instances_to_update:
            record.update(True)
            record.state = 'done'
            # TODO send email, tenemos que usar un template y algo tipo
            # template.send_mail(user_id, force_send=True)
            # if self.notify_email:
        return True

    @api.multi
    def update(self, commit=False):
        self.ensure_one()
        # instances = self.instance_ids
        # for instance in instances:
        to_update = self.detail_ids.filtered(lambda x: x.state == 'to_run')
        _logger.info('Updating repositories %s on instance ids %s' % (
            ', '.join(self.repository_ids.mapped('name')),
            to_update.mapped('instance_id').ids))
        for detail in to_update:
            instance = detail.instance_id
            errors = []
            _logger.info(
                'Pulling repositories for instance %s' % instance.id)
            error_template = 'Could not %s (%s).\nThis is what we get:\n%s'
            updated_repositories = self.env['infrastructure.repository']
            for repository in self.repository_ids:
                instance_repo = self.env[
                    'infrastructure.instance_repository'].search([
                        ('repository_id', '=', repository.id),
                        ('instance_id', '=', instance.id),
                        ], limit=1)
                if instance_repo:
                    try:
                        if instance_repo.sources_from_id:
                            instance_repo.action_pull_source_and_active()
                        else:
                            instance_repo.repository_pull_clone_and_checkout()
                        updated_repositories += repository
                    except Exception, e:
                        error_msg = error_template % (
                            'pull repository',
                            'instance %s, repository %s' % (
                                instance.id, repository.id),
                            e)
                        _logger.warning(error_msg)
                        errors.append(error_msg)
            _logger.info('Restarting odoo instance %s' % instance.id)
            # TODO tal vez saquemos el restart y el fix y que sean
            # hechos automaticamente por la bd de destino
            # podemos empezar solamente con el fix de ultima aunque si
            # el cron ejecuta el fix sin haber realizado restart no iria bien
            try:
                instance.restart_odoo_service()
            except Exception, e:
                error_msg = error_template % (
                    'restart instance',
                    'instance %ss' % (instance.id),
                    e)
                _logger.warning(error_msg)
                errors.append(error_msg)
            _logger.info('Fixind dbs for instance %s' % instance.id)
            for database in instance.database_ids:
                try:
                    database.fix_db(uninstall_modules=self.uninstall_modules)
                except Exception, e:
                    error_msg = error_template % (
                        'fix ',
                        'database %ss' % (database.id),
                        e)
                    _logger.warning(error_msg)
                    errors.append(error_msg)

            result = '<p>Updated repositories: %s</p><p>%s</p>' % (
                    ', '.join(updated_repositories.mapped('name')),
                    errors)
            # self.message_post(
            #     body='result,
            #     subject='Result for instance %s (id: %s)' % (
            #         instance.name,
            #         instance.id))
            # if errors:
            #     state = 'error'
            #     result = 'error'
            # else:
            #     detail.state = 'done'
            detail.write({
                'state': errors and 'error' or 'done',
                'result': result,
                })
            if commit:
                self._cr.commit()
        return True


class infrastructure_instance_update_detail(models.Model):
    _name = "infrastructure.instance.update.detail"

    update_id = fields.Many2one(
        'infrastructure.instance.update',
        'Update',
        required=True,
        ondelte='cascade'
        )
    instance_id = fields.Many2one(
        'infrastructure.instance',
        'Instance',
        required=True,
        ondelte='cascade'
        )
    state = fields.Selection([
        ('to_run', 'To Run'),
        ('done', 'Done'),
        ('error', 'Error')],
        required=True,
        default='to_run',
        )
    result = fields.Html(
        readonly=True,
        )

    @api.multi
    def view_result(self):
        self.ensure_one()
        raise Warning(self.result)
