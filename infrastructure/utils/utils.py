from openerp import exceptions


def synchronize_on_config_parameter(env, parameter):
    param_model = env['ir.config_parameter']
    param = param_model.search([('key', '=', parameter)])
    if param:
        try:
            env.cr.execute(
                '''select *
                    from ir_config_parameter
                    where id = %s
                    for update nowait''',
                param.id,
                log_exceptions=False
            )
        except psycopg2.OperationalError, e:
            raise exceptions.UserError(
                'Cannot synchronize access. Another process lock the parameter'
            )
