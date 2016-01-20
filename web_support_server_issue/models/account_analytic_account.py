# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from openerp import models, api, _
import base64


class Contract(models.Model):
    _inherit = 'account.analytic.account'

    @api.model
    def create_issue(
            self, contract_id, db_name, remote_user_id,
            vals, attachments_data):
        contract = self.sudo().search([
            ('id', '=', contract_id), ('state', '=', 'open')], limit=1)
        if not contract:
            return {'error': _(
                "No open contract for id %s" % contract_id)}
        database = self.env['infrastructure.database'].sudo().search(
            [('name', '=', db_name), ('contract_id', '=', contract.id)],
            limit=1)
        if not database:
            return {'error': _(
                "No database found")}
        vals['database_id'] = database.id
        user = database.user_ids.get_user_from_ext_id(
            database, remote_user_id)
        if not user:
            return {'error': _(
                "User is not registered on support provider database")}

        if not user.authorized_for_issues:
            return {'error': _(
                "User is not authorized to register issues")}
        vals['partner_id'] = user.partner_id.id
        vals['email_from'] = user.partner_id.email

        project = self.env['project.project'].sudo().search(
            [('analytic_account_id', '=', contract.id)], limit=1)
        if project:
            vals['project_id'] = project.id

        issue = self.env['project.issue'].sudo().create(vals)

        attachments = []
        for data in attachments_data:
            attachments.append(
                (data['name'], base64.b64decode(data['datas'])))
            # we use b64decode because it will be encoded by message_post
            # attachments.append((data['name'], data['datas']))
        issue.message_post(
            body=None, subject=None, attachments=attachments)
        return {'issue_id': issue.id}
