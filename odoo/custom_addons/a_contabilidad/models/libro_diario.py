# -*- coding: utf-8 -*-
from odoo import api, fields, models, _, tools
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError

 
class LibroDiario(models.Model):
    
    _inherit = 'account.journal'
    """"""
    account_control_ids = fields.Many2many('account.account', 'journal_account_control_rel', 'journal_id', 'account_id', string='Allowed accounts',
        check_company=True,
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('is_off_balance', '=', False),('utilizable', '=', True)]")
    
    default_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, copy=False, ondelete='restrict',
        string='Default Account',
        domain="[('deprecated', '=', False), ('company_id', '=', company_id), ('utilizable', '=', True),"
               "'|', ('user_type_id', '=', default_account_type), ('user_type_id', 'in', type_control_ids),"
               "('user_type_id.type', 'not in', ('receivable', 'payable'))]")

    suspense_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True, ondelete='restrict', readonly=False, store=True,
        compute='_compute_suspense_account_id',
        help="Bank statements transactions will be posted on the suspense account until the final reconciliation "
             "allowing finding the right account.", string='Suspense Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), \
                             ('user_type_id.type', 'not in', ('receivable', 'payable')), \
                             ('utilizable', '=', True), \
                             ('user_type_id', '=', %s)]" % self.env.ref('account.data_account_type_current_assets').id)
    
    profit_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True,
        help="Registro de Ganancias",
        string='Profit Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), ('utilizable', '=', True),\
                             ('user_type_id.type', 'not in', ('receivable', 'payable')), \
                             ('user_type_id', 'in', %s)]" % [self.env.ref('account.data_account_type_revenue').id,
                                                             self.env.ref('account.data_account_type_other_income').id])
    loss_account_id = fields.Many2one(
        comodel_name='account.account', check_company=True,
        help="Cuenta para registrar las pérdidas",
        string='Loss Account',
        domain=lambda self: "[('deprecated', '=', False), ('company_id', '=', company_id), ('utilizable', '=', True),\
                             ('user_type_id.type', 'not in', ('receivable', 'payable')), \
                             ('user_type_id', '=', %s)]" % self.env.ref('account.data_account_type_expenses').id)

 