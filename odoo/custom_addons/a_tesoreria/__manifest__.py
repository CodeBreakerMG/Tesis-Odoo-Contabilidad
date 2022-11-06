# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Tesoreria',
    'author': "Manuel Moran Cavero - 20160500",
    'version' : '1.0',
    'summary': 'Tesorería (Funcionalidades',
    'sequence': 11,
    'category': 'Accounting/Accounting',
    'description': """
Funcionalidades de Tesorería
====================
Funcionalidades de tesorería que involucran los procesos de pago a proveedores y cobros a clientes.
    """,
 
    'depends': [
        'base',
        'sale',
        'account',
        'purchase',
        'board'
    ],
    'data': [
            'security/ir.model.access.csv',
            'security/security.xml',
            'view/sale_order_view.xml',
            'view/tesoreria_facturas_cobros.xml',
            'view/tesoreria_facturas_pagos.xml',
            'view/tesoreria_dashboard.xml',
            'view/tesoreria_menus.xml'


            
    ],

    'license': 'LGPL-3'
 
}