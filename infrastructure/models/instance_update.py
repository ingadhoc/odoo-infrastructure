# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################

from openerp import fields, api, models
from openerp.exceptions import Warning
import logging
_logger = logging.getLogger(__name__)


class infrastructure_instance_update(models.Model):
    _name = "infrastructure.instance.update"
    _inherit = ['ir.needaction_mixin', 'mail.thread']

    run_after = fields.Datetime(
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    date = fields.Date(
        required=True,
        default=fields.Date.context_today,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    pull_source_and_active = fields.Boolean(
        help='Pool source and active repositories when available?',
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    uninstall_modules = fields.Boolean(
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    name = fields.Char(
        required=True,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    detail_ids = fields.One2many(
        'infrastructure.instance.update.detail',
        'update_id',
        'Instances',
        readonly=True,
        states={
            'draft': [('readonly', False)],
            'to_review': [('readonly', False)],
        },
    )
    user_id = fields.Many2one(
        'res.users',
        string='User',
        required=True,
        default=lambda self: self.env.user,
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    notify_email = fields.Char(
        readonly=True,
        states={'draft': [('readonly', False)]},
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
        readonly=True,
        states={'draft': [('readonly', False)]},
    )
    state = fields.Selection([
        ('draft', 'Draft'), ('to_run', 'To Run'), ('to_review', 'To Review'),
        ('done', 'Done'), ('cancel', 'Cancel')],
        readonly=True,
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
        if not self.detail_ids.filtered(lambda x: x.state == 'to_run'):
            raise Warning('There are no lines to run')
        self.write({'state': 'to_run'})

    @api.multi
    def action_done(self):
        self.write({'state': 'done'})

    @api.model
    def cron_instance_update(self):
        instances_to_update = self.search([
            ('state', '=', 'to_run'),
            '|', ('run_after', '=', False),
            ('run_after', '<=', fields.Datetime.now())
        ])
        for record in instances_to_update:
            record.update(True)
            record.state = 'to_review'
        return True

    @api.multi
    def update(self, commit=False):
        self.ensure_one()
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
                        if (
                                instance_repo.sources_from_id and
                                self.pull_source_and_active):
                            instance_repo.action_pull_source_and_active()
                        else:
                            instance_repo.repository_pull_clone_and_checkout()
                        updated_repositories += repository
                    except Exception, e:
                        error_msg = error_template % (
                            'pull repository',
                            'instance %s (%s), repository %s (%s)' % (
                                instance.name, instance.id,
                                repository.name, repository.id
                            ),
                            e)
                        _logger.warning(error_msg)
                        errors.append(error_msg)
            # TODO tal vez saquemos el restart y el fix y que sean
            # hechos automaticamente por la bd de destino
            # podemos empezar solamente con el fix de ultima aunque si
            # el cron ejecuta el fix sin haber realizado restart no iria bien
            _logger.info('Restarting odoo instance %s' % instance.id)

            # search for depending instances
            use_from_instances = instance.search([
                ('database_type_id.sources_type', '=', 'use_from'),
                ('database_type_id.sources_from_id', '=',
                    instance.database_type_id.id),
                ('environment_id', '=', instance.environment_id.id)])

            all_instances = (use_from_instances + instance)
            for inst in all_instances:
                try:
                    inst.restart_odoo_service()
                except Exception, e:
                    error_msg = error_template % (
                        'restart instance',
                        'instance %s (%s)' % (inst.name, inst.id),
                        e)
                    _logger.warning(error_msg)
                    errors.append(error_msg)
            _logger.info('Fixind dbs for instance %s' % instance.id)
            for database in all_instances.mapped('database_ids'):
                try:
                    database.fix_db(uninstall_modules=self.uninstall_modules)
                except Exception, e:
                    error_msg = error_template % (
                        'fix ',
                        'database %s (%s)' % (database.name, database.id),
                        e)
                    _logger.warning(error_msg)
                    errors.append(error_msg)

            result = (
                "* Updated repositories: %s\n"
                "* Depending instances updated: %s\n"
                "* Databases updated: %s\n"
                "* Errors: %s\n" % (
                    updated_repositories.mapped('name'),
                    use_from_instances.mapped('name'),
                    all_instances.mapped('database_ids.name'),
                    errors
                ))
            # self.message_post(
            #     body='result,
            #     subject='Result for instance %s (id: %s)' % (
            #         instance.name,
            #         instance.id))
            detail.write({
                'state': errors and 'error' or 'done',
                'result': result,
            })

            if commit:
                self._cr.commit()
        template = self.env.ref(
            'infrastructure.email_template_update_instances_result', False)
        if template and self.notify_email:
            # context['to_update'] = to_update
            template.with_context(to_update=to_update).send_mail(
                self.id, force_send=False)
        return True


class infrastructure_instance_update_detail(models.Model):
    _name = "infrastructure.instance.update.detail"

    update_id = fields.Many2one(
        'infrastructure.instance.update',
        'Update',
        required=True,
        ondelete='cascade'
    )
    server_id = fields.Many2one(
        related='instance_id.server_id',
        readonly=True,
    )
    instance_id = fields.Many2one(
        'infrastructure.instance',
        'Instance',
        required=True,
        ondelete='cascade'
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

    @api.multi
    def action_open_instance(self):
        self.ensure_one()
        action = self.env['ir.model.data'].xmlid_to_object(
            'infrastructure.action_infrastructure_instance_instances')
        if not action:
            return False
        res = action.read()[0]
        form_view_id = self.env['ir.model.data'].xmlid_to_res_id(
            'infrastructure.view_infrastructure_instance_form')
        res['views'] = [(form_view_id, 'form')]
        res['res_id'] = self.instance_id.id
        return res

    _sql_constraints = [
        ('instance_uniq', 'unique(update_id, instance_id)',
            'Instance must be unique per instance update'),
    ]
