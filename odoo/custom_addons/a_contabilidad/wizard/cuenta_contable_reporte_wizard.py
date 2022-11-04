import pandas as pd
import numpy as np
import base64
import os
import warnings

from odoo import api, models, fields, exceptions
from reportlab.pdfgen import canvas
from datetime import datetime

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

            
            if (int(self.jerarquia_selection) < 6):
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
            return self.make_pdf_report("./reports/", "reporte_cuentas.pdf", df)

    def save_to_file(self):
        # code snipet for downloading zip file
        #self.export_plan_contable()
        #self.downloadable_file = base64.b64encode(open(self.csv_file_path, "rb").read())
        self.downloadable_file = base64.b64encode(self.export_plan_contable().read())
        url_string = '/web/content/'+ self._name + '/' + str(self.id) + '/downloadable_file/reporte.pdf?download=true'

        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': url_string
        }

    def make_pdf_report(self, dir_path, name, df : pd.DataFrame):

        font_size = 8

        my_canvas = canvas.Canvas(dir_path + name, pagesize='A4')
        my_canvas.setLineWidth(.3)
        my_canvas.setFont('Helvetica', 12)

        my_canvas.drawString(30, 750, 'REPORTE DE CUENTAS CONTABLES')
        my_canvas.drawString(30, 735, self.env.company.name )
        
        my_canvas.drawString(500, 750, datetime.today().strftime('%d-%m-%Y'))
        
        x_axis = 30 #Left to right: Value increase
        y_axis = 700 #Bottom to top: Value increase
        my_canvas.setFont('Helvetica', font_size)

        canva_element_name = df['nombre_elemento'].iloc[0]
        canva_element = str(df['elemento'].iloc[0])
        formatted_line_data = []
        for index, row  in df.iterrows():

            if (canva_element != str(row['elemento'])) or (index == 0):
                y_axis -= 10
                canva_element_name = row['nombre_elemento']
                canva_element = str(row['elemento'])
                my_canvas.setFont('Helvetica-Bold', font_size + 2)
                my_canvas.drawString(x_axis, y_axis, canva_element)
                my_canvas.drawString(x_axis + 20, y_axis, canva_element_name)

                if (y_axis <= 20):
                    my_canvas.showPage()
                    y_axis = 700
                else: 
                    y_axis -= 20
                my_canvas.setFont('Helvetica', font_size)
            
            canva_code = str(row['code'])
            canva_name = row['name']
            canva_debit = float(row['debe'])
            canva_credit = float(row['haber'])

            x_line = x_axis + 5
            """
            line_data = [canva_code, canva_name, canva_debit, canva_credit]

            for item in line_data:
                ptext = "<font size="%s">%s</font>" % (font_size-1, item)
                p = Paragraph(ptext, 'centered')
                formatted_line_data.append(p)
            """
            my_canvas.drawString(x_line, y_axis, canva_code)
            x_line += 100
            my_canvas.drawString(x_line, y_axis, canva_name )
            x_line += 300 #- len(canva_name)
            my_canvas.drawRightString(x_line, y_axis, "{:10.2f}".format(canva_debit))
            x_line += 100
            my_canvas.drawRightString(x_line, y_axis, "{:10.2f}".format(canva_credit))

            if (y_axis <= 20):
                my_canvas.showPage()
                my_canvas.setFont('Helvetica', font_size)
                y_axis = 700
            else: 
                y_axis -= 15

        my_canvas.save()
        print("*********IMPRESION DEL PDF *********")
        return open(dir_path + name, "rb")
