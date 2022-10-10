from odoo import fields, models


class EstatePropertyTag(models.Model):

    _name = "estate.property.tag"
    _description = "Real Estate Property Tag"
 

    name = fields.Char('Property tag', required=True)
    description = fields.Char('Description')
    property_ids = fields.Many2many("estate.property", string="Properties", default=lambda self: self.env['estate.property'].search([]))

    _sql_constraints = [
        ('check_tag_name', 'UNIQUE(name)', 'Tag name already exists')    
    ]