# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name' : 'Contabilidad PYME',
    'author': "Manuel Moran Cavero - 20160500",
    'version' : '1.0',
    'summary': 'Módulo para la Gestión de Contabilidad',
    'sequence': 12,
    'category': 'Accounting/Accounting',
    'description': """
Módulo de Contabilidad
====================
Generación de Reportes y Estados Financieros
    """,

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