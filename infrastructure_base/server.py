from openerp import models, fields


class user(models.Model):
    _inherit = 'res.users'
    server_ids = fields.One2many('server', 'employee_id')


class server_tags(models.Model):
    _name = 'server.tag'
    name = fields.Char()


class server(models.Model):
    _name = 'server'
    # _rec_name = 'date'

    name = fields.Char()
    used = fields.Boolean()
    date = fields.Date()
    datetime = fields.Datetime()
    quantity = fields.Float()
    numbres = fields.Integer()
    employee_id = fields.Many2one('res.users',)
    owner_id = fields.Many2one('res.users')
    state = fields.Selection([('draft', 'Draft'), ('open', 'Open')])
    tag_ids = fields.Many2many(
        'server.tag', 'server_server_tag_rel', 'server_id', 'tag_id', 'Tags')

    def open_server(self):
        self.state = 'open'
