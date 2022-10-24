from odoo import api, fields, models



PAYMENT_STATE_SELECTION = [
        ('not_paid', 'Not Paid'),
        ('in_payment', 'In Payment'),
        ('paid', 'Paid'),
        ('partial', 'Partially Paid'),
        ('reversed', 'Reversed'),
        ('invoicing_legacy', 'Invoicing App Legacy'),
]
 
class AccountMoveTesoreria(models.Model):

    _inherit = "account.move"

    estado_de_pago =   fields.Selection(PAYMENT_STATE_SELECTION, string="Payment Status", store=True,
        readonly=True, copy=False, tracking=True, compute='_compute_amount')

    
 