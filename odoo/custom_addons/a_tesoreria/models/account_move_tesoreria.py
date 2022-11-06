from odoo import api, fields, models



PAYMENT_STATE_SELECTION = [
        ('draft', 'Borrador'),
        ('not_paid', 'Sin Pagar'),
        ('in_payment', 'En Proceso de pago'),
        
        ('partial', 'Parcialmente Pagado'),
        ('paid', 'Pagado'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
        
        
        ('posted', 'Publicado'),
        ('canceled', 'Cancelado'),
]
 

class AccountMoveTesoreria(models.Model):

    _inherit = "account.move"

    estado_de_pago =   fields.Selection(PAYMENT_STATE_SELECTION, string="Estado del Pago", store=True, readonly=True, copy=False, tracking=True, compute='_compute_estado_pago')
    saldo_pendiente = fields.Float("Saldo Pendiente", default=lambda self: self.amount_total, store=True, readonly=True, copy=False, tracking=True, compute='_compute_saldos')
    saldo_pagado = fields.Float("Saldo Pagado", default = 0.0, store=True, readonly=True, copy=False, tracking=True, compute='_compute_saldos')
    
    @api.depends("state", "payment_state")
    def _compute_estado_pago(self):
        for record in self:
            if record.state != 'posted':
                record.estado_de_pago = record.state
            else:
                record.estado_de_pago = record.payment_state

    @api.depends("amount_total", "amount_residual")
    def _compute_saldos(self):
        for record in self:
            record.saldo_pagado = record.amount_total - record.amount_residual
            record.saldo_pendiente = record.amount_residual
         
    @api.onchange("amount_residual")
    def _onchange_saldos(self):
        
        self.saldo_pagado = self.amount_total - self.amount_residual
        self.saldo_pendiente = self.amount_residual
 
    def open_action(self):
        return {
                'name': self.name,
                'res_model': 'account.move',
                'type': 'ir.actions.act_window',
                'res_id' : self.id,
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref("account.view_move_form").id,
                'target': 'current',
                #'context': {'active_id': self.id, 'id': self.id }
            }

