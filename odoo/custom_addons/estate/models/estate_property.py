from odoo import exceptions, fields, models, api
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):

    _name = "estate.property"
    _description = "Real Estate Property"
 

    name = fields.Char('Property Name', required=True, translate=True)
    property_type_id = fields.Many2one("estate.property.type", string="Type", default=lambda self: self.env['estate.property.type'].search([]))
    property_tag_ids = fields.Many2many("estate.property.tag", string="Type", default=lambda self: self.env['estate.property.tag'].search([]))
    description = fields.Text('Description')
    post_code = fields.Char('Postcode' )
    selling_price = fields.Float('Selling Price', readonly = True, copy = False)
    size = fields.Float('Living Area (m2)')
    number_of_bedrooms = fields.Integer('Bedrooms', default = 2)
    availability_date = fields.Datetime('Availability Date', default=lambda self: (fields.Datetime.now() + relativedelta(months=3)), copy=False )
    active = fields.Boolean('Active', default=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    salesperson_id = fields.Many2one("res.users", string="Salesperson")
    offer_id = fields.One2many("estate.property.offer", "property_id", string="Offer")
    total_size = fields.Float(string= "Total Size (in square feet)", compute = "_compute_total_area")
    best_price = fields.Float(string="Best Offered Price", compute = "_compute_best_price")
    status = fields.Selection([('available', 'Available'), ('sold', 'Sold'), ('cancelled', 'Cancelled')], string='Status', copy=False, default = 'available')

    _sql_constraints = [
        ('check_size', 'CHECK(size >= 0 )', 'Size must be a positive number'),
   
        ('check_post_code', 'CHECK(LENGTH(post_code) = 5 )', 'Postal Code must contain exactly 5 numbers')
    ]


    @api.model
    def ondelete(self):
        for record in self:
            if record.status == 'available' or record.status == 'cancelled':
                raise exceptions.UserError('No se puede eliminar una propiedad que esté nueva o cancelada.')
            return super().ondelete()

    @api.depends("size")
    def _compute_total_area(self):
        for record in self:
            record.total_size = record.size * 10.764 

    @api.depends("offer_id")
    def _compute_best_price(self):
        for record in self:
            if record.offer_id:
                record.best_price = max(record.offer_id.mapped('price'))
            else:
                record.best_price = 0.0

    def estate_property_action_sell(self):
        for record in self:
            if (record.status == 'cancel'):
                raise exceptions.UserError("No se puede vender una propiedad cancelada.")
                return False
            record.status = 'sold'
        return True

    def estate_property_action_cancel(self):
        
        for record in self:
            if (record.status == 'sold'):
                raise exceptions.UserError("No se puede cancelar una propiedad vendida.")
                return False
            record.status = 'cancel'
        return True
    
    def set_price(self, price):
        
        for record in self:
            record.selling_price = price
        return True

    def set_partner(self, partner):
        
        for record in self:
            record.partner_id = partner
        return True

    def reject_all_offers(self):
        for record in self:
          
            record.offer_id.mapped(  lambda obj: obj.estate_property_type_action_refuse())           
           # estate_property_type_action_refuse
            #record.best_price = max(record.offer_id.mapped('price'))
        return True     


#Some Field attributes (See Odoo API)