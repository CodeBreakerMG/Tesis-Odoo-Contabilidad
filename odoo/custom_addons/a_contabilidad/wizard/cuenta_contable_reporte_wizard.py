import pandas as pd
import numpy as np
import base64
import os
import csv
import io
from odoo import api, models, fields
import xmlrpc.client
import warnings


 

class CuentaContableReporte(models.TransientModel):

    _name = "cuenta.contable.reporte.wizard"
    _description = "Reporte de Cuentas Contables"
    
    csv_file_path = "./reports/reporte_cuentas_contables.csv"
    downloadable_file = fields.Binary('File data', readonly=True)
    
    jerarquia_selection = fields.Selection([('1', '1'),('2', '2'),('3', '3'),('4', '4'),('5', '5'),('6', '6')],string='Nivel de Jerarquía',default='6',required=True)

    def export_plan_contable(self):
        warnings.simplefilter(action='ignore', category=FutureWarning)
        account_id_list = self.env['account.account'].search([('jerarquia', '=', '6')])

        df = pd.DataFrame(columns=['code', 'name','nombre_elemento' , 'elemento', 'debe', 'haber'])

        if account_id_list:
            
            for record in account_id_list:
                account_complete = account_id_list.browse(record.id)
                element = account_complete.tipo_de_cuenta.elemento
                name_element = account_complete.tipo_de_cuenta.name
                account_debit = 0.0
                account_credit = 0.0    
                account_moves_id_list = self.env['account.move.line'].search([('account_id', '=', record.id)]) #this only obtains ids
                
                if len(account_moves_id_list) > 0:
                    for i in range(0, len(account_moves_id_list.ids)):
                        account_move =  account_moves_id_list.browse(account_moves_id_list.ids[i])
                        account_debit += account_move.debit
                        account_credit += account_move.credit
                    #account_moves_list = account_moves_id_list.browse(account_moves_id_list.ids)
                    #print(account_moves_list)
                    #account_debit_list = self.env['account.move.line'].search(['account_'])
                    #account_credit_list = self.env['account.move.line'].search([])
                df.loc[len(df.index)] = [account_complete.code, account_complete.name, name_element, element, account_debit, account_credit]

            if (int(self.jerarquia_selection) >= 6):
                x =2

            else:
                df['PARENT_ACCOUNT_CODE'] = df['code'].str[0:int(self.jerarquia_selection)]
                account_parent_id_list = self.env['account.account'].search([('jerarquia', '=', self.jerarquia_selection)])
                account_parent_list = [[account_parent_id_list.browse(account_parent_id_list.ids[i]).code, account_parent_id_list.browse(account_parent_id_list.ids[i]).name] for i in range(0,len(account_parent_id_list.ids))]
                account_parent_dict = dict(account_parent_list)
                

                df['PARENT_ACCOUNT_NAME'] = df["PARENT_ACCOUNT_CODE"].apply(lambda x: account_parent_dict.get(str(x)))
                df.drop(['code','name'], axis = 1, inplace = True)
                df.rename(columns={"PARENT_ACCOUNT_CODE":"code", "PARENT_ACCOUNT_NAME":"name"}, inplace=True)
                df = df[['code', 'name','nombre_elemento' , 'elemento', 'debe', 'haber']]
                df = df.replace(to_replace='None', value=np.nan).dropna()
                
                #df = df.mask(df.astype(object).eq('None')).dropna()
                #agrupamiento:
                df = df.groupby(['code', 'name','nombre_elemento' , 'elemento'],as_index=False)['debe','haber'].sum()
            if not os.path.exists("./reports"):
                os.makedirs("./reports")   
            df.to_csv(self.csv_file_path, index=False)
            print("*********IMPRESION DEL LISTADO DE CUENTAS EXITOSO*********")
 


    def save_to_file(self):
        # code snipet for downloading zip file
        self.export_plan_contable()
        self.downloadable_file = base64.b64encode(open(self.csv_file_path, "rb").read())
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/cuenta.contable.reporte.wizard/%s/downloadable_file/reporte.csv?download=true' %(self.id), 
        }

        