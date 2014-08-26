# -*- coding: utf-8 -*-

from openerp import models, fields, api, netsvc, _
import xmlrpclib
from dateutil.relativedelta import relativedelta
from datetime import datetime
from fabric.api import sudo


class database_backup(models.Model):

    """"""
    _name = 'infrastructure.database.backup'
    _description = 'Database Back Up'

    database_id = fields.Many2one(
        'infrastructure.database',
        string='Database',
        readonly=True,
        required=True,
    )

    create_date = fields.Datetime(
        string='Date',
        readonly=True,
        required=True,
    )

    # TODO name se debe componer con prefijo de backup policiy, nombre bd y datetime de creacion
    name = fields.Char(
        string='Name',
        readonly=True,
        required=True,
    )

    db_back_up_policy_id = fields.Many2one(
        'infrastructure.db_back_up_policy',
        string='Backup Policy',
        readonly=True,
    )

    def restore(self):
        """ Se debe crear un wizard y un boton que llame a dicho wizard,
        luego el wizard va a llamar a esta funcion pasando determiandos argumentos.
            # type = [('new','New'),('overwrite','Overwrite')]
            instance_id = listas de instancias
            database_id = campo m2o a database de esa instancia
                Se va poder elegir una bd o elegir el widget del m2o el "create" y a la nueva bd se le passa por contexto la instance seleccionada
            Luego, al confirmar el wizard, se hace el restore de la bd y se pasa la database_id al estado "active"
        """

    def download(self):
        """Descarga el back up en el exploradorador del usuario"""