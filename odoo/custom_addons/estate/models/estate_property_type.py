from odoo import fields, models


class EstatePropertyType(models.Model):

    _name = "estate.property.type"
    _description = "Real Estate Property Type"
 

    name = fields.Char('Property Type', required=True)
    description = fields.Char('Description')


    _sql_constraints = [
        ('check_type_name', 'UNIQUE(name)', 'Type name already exists')    
    ]
