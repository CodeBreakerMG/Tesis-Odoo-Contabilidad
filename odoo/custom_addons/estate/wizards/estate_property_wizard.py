from odoo import models, fields

class EstatePropertyWizard(models.TransientModel):

    _name = "estate.property.wizard"
    _description = "Example of a Wizard for Estate Property"

    bundle_customer_id = fields.Many2one('res.partner', string="Customer")
    from_date = fields.Date('From')
    to_date = fields.Date('To')

    def print_estate_property(self):
        print("Print report button clicked!")