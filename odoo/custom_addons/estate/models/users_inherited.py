from odoo import fields, models

class UsersInherited(models.Model):

    _inherit = "res.users"
    property_ids = fields.One2many("estate.property", "salesperson_id", string="Properties")
    #property_ids = fields.One2many("estate.property", "salesperson_id", domain="[('status', '=', available)]" , string="Properties")
 