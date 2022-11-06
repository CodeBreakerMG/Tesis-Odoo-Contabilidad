from odoo import api, fields, models



PAYMENT_STATE_SELECTION = [
        ('not_paid', 'Sin Pagar'),
        ('in_payment', 'En Proceso de pago'),
        ('paid', 'Pagado'),
        ('partial', 'Parcialmente Pagado'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
        
        ('draft', 'Borrador'),
        ('posted', 'Publicado'),
        ('canceled', 'Cancelado'),
]
 

class AccountMoveTesoreria(models.Model):

    _inherit = "account.move"

    estado_de_pago =   fields.Selection(PAYMENT_STATE_SELECTION, string="Estado del Pago", store=True, readonly=True, copy=False, tracking=True, compute='_compute_estado_pago')

    @api.depends("state", "payment_state")
    def _compute_estado_pago(self):
        for record in self:
            if record.state != 'posted':
                record.estado_de_pago = record.state
            else:
                record.estado_de_pago = record.payment_state
 