# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'tesoreria',
 
    'depends': [
        'base',
        'sale',
        'account',
        'purchase'
    ],
    'data': [
            'security/ir.model.access.csv',
            'view/sale_order_view.xml'

            
    ],
 
}