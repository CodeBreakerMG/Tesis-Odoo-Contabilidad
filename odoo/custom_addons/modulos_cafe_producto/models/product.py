# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.tools import format_amount


#----------------------------------------------------------

class ProductCategory(models.Model):
    _inherit = "product.category"
    
    tipo_cafe = fields.Char('Tipo de Producto Café', required = True, default="Café Especialidad - Venta Local")


#class ProductAttribute(models.Model):
#    _inherit = "product.attribute"
#    tipo_cafe = fields.Char('Tipo de Cafe')