# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

 


class CuentaContableTipo(models.Model):
    
    _name = 'account.account.tipo'
    
    
    name = fields.Char('Tipo de Cuenta Contable', required=True)
    description = fields.Text('Descripcion')
    elemento = fields.Integer('N° Elemento',  required=True,
                help="Número de elemento según el Plan Contable General Empresarial propuesto por el MEF")
    reporte = fields.Selection([
                ('bg', 'Balance General'),
                ('egp', 'Estado de Ganancias y Pérdidas'),
                ('otros', 'Otros')  
                
            ],  string="Tipo de Reporte",
                required=True,
                help="The 'Internal Group' is used to filter accounts based on the internal group set on the account type.")
    

    
    _sql_constraints = [
        ('check_elemento', 'UNIQUE(elemento)', 'El número de elemento tiene que ser único.')
    ]

    
    @api.constrains('elemento')
    def _check_elemento(self):
        for record in self:
            if (record.elemento < 0):
                raise ValidationError("El número de elemento no puede ser menor a 0.")