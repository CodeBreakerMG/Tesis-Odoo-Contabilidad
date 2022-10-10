# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'estate',
 
    'depends': [
        'base'
    ],
    'data': [
            'security/ir.model.access.csv',
            'wizards/import_csv_estate_property_wizard.xml',
            'wizards/estate_property_wizard.xml',
            'view/res_users_views.xml',
            'view/estate_property_type_views.xml',
            'view/estate_property_offer_views.xml',
            'view/estate_property_tag_views.xml',
            'view/estate_property_views.xml',
            'view/estate_menus.xml'

            
    ],
    'application': True
}