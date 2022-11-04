# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'contabilidad',
    'version' : '1.0',
    'summary': 'Gestión de Contabilidad',
    'sequence': 99,

    'category': 'Accounting',

    'depends': [
        'base',
        'account'
    ],
    'data': [
            'security/ir.model.access.csv',
            'report/balance_general_report.xml',
            'report/estado_resultados_report.xml',
            'views/cuenta_contable_tipo_views.xml',
            'wizard/import_csv_cuenta_contable_tipo_wizard.xml',
            'wizard/import_csv_cuenta_contable_wizard.xml',
            'wizard/cuenta_contable_reporte_wizard.xml',
            'views/cuenta_contable_views.xml',
            'views/cuenta_contable_menus.xml'
            
    ],
    'installable': True,
    'application': True,

    'license': 'LGPL-3',
}