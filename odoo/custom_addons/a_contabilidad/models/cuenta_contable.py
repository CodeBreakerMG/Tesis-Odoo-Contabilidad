# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

 
class CuentaContable(models.Model):
    
    _inherit = 'account.account'
    
    jerarquia = fields.Integer('Nivel de Jerarquía')
    tipo_de_cuenta = fields.Many2one("account.account.tipo", required = True, string="Tipo de Cuenta")
    
    moneda = fields.Selection([
                ('mn', 'Moneda Nacional (S/)'),
                ('me', 'Moneda Extranjera (USD $)'),
                
                
            ],  string="Moneda",
                required=True,
                help="Tipo de Moneda: Nacional (MN), Extranjera (ME)")

    utilizable = fields.Boolean('Utilizable', readonly = True,  help="Cuenta Utilizable para asientos contables", compute = "_compute_utilizable",  store=True)
 
    @api.onchange("code")
    def _onchange_partner_id(self):
        self.jerarquia = max(1,min(6, len(str(self.code))))
            
    @api.constrains('code')
    def _check_code_len(self):
        for record in self:
            if len(str(record.code)) > 10 or len(str(record.code)) < 1 :
                raise ValidationError("El código de la cuenta contable tiene que tener una longitud de máximo 6 dígitos.")

    @api.depends("jerarquia")
    def _compute_utilizable(self):
        for record in self:
            if (record.jerarquia == 6):
                record.utilizable = True 
            else:
                record.utilizable = False
                
    @api.onchange("moneda")
    def _onchange_currency(self):
        
        if self.moneda == 'me':
            self.currency_id  = self.env['res.currency'].search([('name', '=', 'USD')])
        else: 
            self.currency_id  = self.env['res.currency'].search([('name', '=', 'PEN')])
        #list_currenciesself.currency_id.mapped('price'))

                
    @api.onchange("tipo_de_cuenta")
    def _onchange_currency(self):
        
        if self.tipo_de_cuenta.elemento < 4:
            self.user_type_id  = self.env['account.account.type'].search([('name', '=', 'Current Assets')])
        elif self.tipo_de_cuenta.elemento == 4: 
            self.user_type_id  = self.env['account.account.type'].search([('name', '=', 'Current Liabilities')])
        elif self.tipo_de_cuenta.elemento == 5: 
            self.user_type_id  = self.env['account.account.type'].search([('name', '=', 'Equity')])
        elif self.tipo_de_cuenta.elemento == 7 or self.tipo_de_cuenta.elemento == 8: 
            self.user_type_id  = self.env['account.account.type'].search([('name', '=', 'Income')])
        elif self.tipo_de_cuenta.elemento == 6 or self.tipo_de_cuenta.elemento == 9: 
            self.user_type_id  = self.env['account.account.type'].search([('name', '=', 'Expenses')])
        else:
            self.user_type_id  = self.env['account.account.type'].search([('name', '=', 'Off-Balance Sheet')])