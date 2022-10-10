from email.policy import default
from odoo import exceptions, fields, models, api
from dateutil.relativedelta import relativedelta
import dateutil.parser

class EstatePropertyOffer(models.Model):

    _name = "estate.property.offer"
    _description = "Real Estate Property Offer"
 

    price = fields.Float('Prices')
    status = fields.Selection([('accepted', 'Accepted'), ('refused', 'Refused'), ('received', 'Received')], string='Status', copy=False, default= 'received')
    validity = fields.Integer('Days of Validity', default=7)
    date_deadline = fields.Date('Date Deadline', compute = "_compute_date_deadline", inverse ="_inverse_date_deadline" )
    partner_id = fields.Many2one("res.partner", string="Partner", required = True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)

    _sql_constraints = [
        ('check_price', 'CHECK(price >= 0 )', 'Price must be a positive number'),
        ('check_validity', 'CHECK(validity > 0 )', 'There must be at least one day of validity'),
         
    ]

    @api.model
    def create(self,vals):
        if self.env['estate.property'].browse(vals['property_id']):
            best_price = self.env['estate.property'].browse(vals['property_id']).best_price
            if vals['price'] < best_price:
                raise exceptions.UserError('No se puede agregar una oferta menor a la actual mejor\nOferta Actual: ' + str(vals['price'] ) + '\nMejor Oferta: ' +str(best_price) )
                return {}
        
        return super().create(vals)

    @api.depends("validity")
    def _compute_date_deadline(self):
        for record in self:
            
            if record.create_date:
                record.date_deadline = record.create_date + relativedelta(days=record.validity)
            else:
                record.date_deadline = fields.Date.today() + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        
        for record in self:
            if not record.create_date:
                record.validity = record.validity
            else:
                create_date_in_date = (record.create_date).date()
                record.validity = (record.date_deadline - create_date_in_date).days
            
    def estate_property_type_action_accept(self):
        for record in self:

            record.property_id.reject_all_offers()
            record.property_id.set_price(record.price)
            record.property_id.set_partner(record.partner_id)
            
            record.status = 'accepted'
        return True

    def estate_property_type_action_refuse(self):
        
        for record in self:
            record.status = 'refused'
        return True