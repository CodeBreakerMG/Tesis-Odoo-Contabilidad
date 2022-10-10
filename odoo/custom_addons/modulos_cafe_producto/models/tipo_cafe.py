from odoo import api, fields, models
from odoo.tools import format_amount


#----------------------------------------------------------

class TipoCafe(models.Model):
    _name = "tipo.cafe"
    name = fields.Char('Tipo de Producto Café', required = True, default="Café Especialidad - Venta Local")
    
 

#class ProductAttribute(models.Model):
#    _inherit = "product.attribute"
#    tipo_cafe = fields.Char('Tipo de Cafe')