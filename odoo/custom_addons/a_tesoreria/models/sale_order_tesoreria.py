from odoo import fields, models

class SaleOrderTesoreria(models.Model):

    _inherit = "sale.order"
  
    #property_ids = fields.One2many("estate.property", "salesperson_id", domain="[('status', '=', available)]" , string="Properties")
 