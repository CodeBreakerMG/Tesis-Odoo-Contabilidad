from symbol import yield_arg
import pandas as pd
import numpy as np
import base64
import os
import warnings
from odoo import api, models, fields
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from datetime import datetime, timedelta

from odoo.exceptions import ValidationError

FONT_SIZE = 8
FONT_TYPE = 'Helvetica'
LINE_SEPARATION = 15
PATH_DIR = "./reports"
YEARS = [(str(x), str(x)) for x in range(datetime.today().year - 10, datetime.today().year + 1)]
MONTHS = [('1', 'Enero'),
          ('2', 'Febrero'),
          ('3', 'Marzo'),
          ('4', 'Abril'),
          ('5', 'Mayo'),
          ('6', 'Junio'),
          ('7', 'Julio'),
          ('8', 'Agosto'),
          ('9', 'Septiembre'),
          ('10', 'Octubre'),
          ('11', 'Noviembre'),
          ('12', 'Diciembre')]

class BalanceGeneralReport(models.TransientModel):

    _name = "balance.general.report"
    _description = "Módulo para generar el reporte de balance General"

    downloadable_file_name = fields.Char(string='Nombre del Archivo', required=True, readonly=True, compute = "_compute_downloadable_file_name")
    downloadable_file = fields.Binary('File Data', readonly=True)
    year = fields.Selection(YEARS, string='Año',default=str(datetime.today().year),required=True, help="Último año a considerar en el reporte.")
    month = fields.Selection(MONTHS, string='Mes',default=str(datetime.today().month),required=True, help="Último mes a considerar en el reporte. Se considera la totalidad del mes en cuestión.")
    currency = fields.Selection([('mn', 'S/ (Soles)'), ('me', 'US$ (Dólares)')], string='Moneda', default='mn',required=True, help = "Moneda En la que se se generará el reporte. Puede ser en soles o en dólares.")
    unit = fields.Selection([('1', 'En Unidades'), ('1000', 'En Miles'),('1000000', 'En Millones')], string='Numeración', default='1',required=True, help = "Unidades en la que se generará el reporte. Puede ser en miles o millones.")

    @api.onchange("year")
    def _onchange_year(self):
        
        for record in self:
            if record.year != str(datetime.today().year):
                record.month = '12'
            else:
                record.month = str(datetime.today().month)

    @api.depends("month")
    def _compute_downloadable_file_name(self):
        for record in self:
            document_name = record.month + '_' + record.year if int(record.month) >= 10 else '0' + record.month + '_' + record.year 
            record.downloadable_file_name = 'BG_' + document_name + '.pdf'

    @api.constrains("month")
    def _check_month(self):
      
        if self.year != str(datetime.today().year):
            return
        if int(self.month) > datetime.today().month:
            raise ValidationError("La fecha actual es menor a la fecha introducida.")

    def save_to_file(self):
        
        self.downloadable_file = base64.b64encode(self.export_balance_sheet().read())
        url_string = '/web/content/'+ self._name + '/' + str(self.id) + '/downloadable_file/'+ self.downloadable_file_name +'?download=true'

        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': url_string
        }

    def export_balance_sheet(self):

        warnings.simplefilter(action='ignore', category=FutureWarning)
        account_id_list = self.env['account.account'].search([('jerarquia', '=', '6')])
        df = pd.DataFrame(columns=['code', 'name','nombre_elemento' , 'elemento', 'debe', 'haber'])

        exchange_rate = self.get_exchange_rate()
        selected_date = datetime(int(self.year), int(self.month), self.last_day_of_month(datetime(int(self.year), int(self.month), 1)))
        units_rate = float(self.unit)
        if account_id_list:
            
            for record in account_id_list:
                account_complete = account_id_list.browse(record.id)
                element = account_complete.tipo_de_cuenta.elemento
                name_element = account_complete.tipo_de_cuenta.name
                account_debit = 0.0
                account_credit = 0.0    
                account_moves_id_list = self.env['account.move.line'].search([('account_id', '=', record.id)]) #this only obtains ids
                
                if len(account_moves_id_list) > 0 :
                    for i in range(0, len(account_moves_id_list.ids)):
                        
                        account_move =  account_moves_id_list.browse(account_moves_id_list.ids[i])
                        if (account_move.date > selected_date.date()):
                            continue
                        account_debit += account_move.debit / units_rate
                        account_credit += account_move.credit / units_rate
                    
                    account_debit = account_debit * exchange_rate if account_complete.moneda != self.currency else account_debit
                    account_credit = account_credit * exchange_rate if account_complete.moneda != self.currency else account_credit

                df.loc[len(df.index)] = [account_complete.code, account_complete.name, name_element, element, account_debit, account_credit]

                df['PARENT_ACCOUNT_CODE'] = df['code'].str[0:2]
                account_parent_id_list = self.env['account.account'].search([('jerarquia', '=', '2')])
                account_parent_list = [[account_parent_id_list.browse(account_parent_id_list.ids[i]).code, account_parent_id_list.browse(account_parent_id_list.ids[i]).name] for i in range(0,len(account_parent_id_list.ids))]
                account_parent_dict = dict(account_parent_list)
                

                df['PARENT_ACCOUNT_NAME'] = df["PARENT_ACCOUNT_CODE"].apply(lambda x: account_parent_dict.get(str(x)))
                df.drop(['code','name'], axis = 1, inplace = True)
                df.rename(columns={"PARENT_ACCOUNT_CODE":"code", "PARENT_ACCOUNT_NAME":"name"}, inplace=True)
                df = df[['code', 'name','nombre_elemento' , 'elemento', 'debe', 'haber']]
                df = df.replace(to_replace='None', value=np.nan).dropna()

                df = df.groupby(['code', 'name','nombre_elemento', 'elemento'],as_index=False)['debe','haber'].sum()
                
                df["elemento"] = pd.to_numeric(df["elemento"])
                df = df.drop(df[df.elemento > 5].index) 
                
            if not os.path.exists(PATH_DIR):
                os.makedirs(PATH_DIR)   

            return self.make_pdf_report(PATH_DIR + "/", self.downloadable_file_name, df)

    def make_pdf_report(self, dir_path, name, df : pd.DataFrame):

        width, height = A4
        
        my_canvas = canvas.Canvas(dir_path + name, pagesize=A4)
        my_canvas.setLineWidth(.3)
        my_canvas.setFont(FONT_TYPE+"-Bold", FONT_SIZE + 2)

        my_canvas.drawCentredString(width/2, 800, self.env.company.name )
        my_canvas.drawCentredString(width/2, 785, 'BALANCE GENERAL')

        last_day = self.last_day_of_month(datetime(int(self.year), int(self.month), 1))        
        month_string = dict(self._fields['month'].selection).get(self.month).lower()
        date_string = 'Al ' + str(last_day) + ' de ' + month_string + ' de ' + self.year
        my_canvas.drawCentredString(width/2, 770, date_string)      

        units_string = (dict(self._fields['unit'].selection).get(self.unit)).lower() + " de " if self.unit != '1' else ''
        currency_string = dict(self._fields['currency'].selection).get(self.currency) if self.unit != '1' else 'en ' + dict(self._fields['currency'].selection).get(self.currency)
        my_canvas.setFont(FONT_TYPE+"-Oblique", FONT_SIZE + 2)
        my_canvas.drawCentredString(width/2, 755, "Expresado " + units_string + currency_string)      
        my_canvas.setFont(FONT_TYPE+"-Bold", FONT_SIZE + 2)

        x_axis = 10 #Left to right: Value increase
        y_axis = 730 #Bottom to top: Value increase

        df_list = [ df.loc[df['elemento'] == i] for i in range(1,6)]
        names_list = df['nombre_elemento'].unique().tolist()

        my_canvas.drawString(x_axis, y_axis, 'ACTIVOS')
        y_axis -= LINE_SEPARATION
        
        aux_summ = 0.0
        total_activos = 0.0
        total_pasivo_patrimonio = 0.0

        for i in range(0,3):

            y_axis, aux_summ = self.print_accounts(True, my_canvas, x_axis, y_axis, df_list[i], names_list[i])
            total_activos += aux_summ
 
        x_axis = width/2 + 10 #Left to right: Value increase
        y_axis = 730 #Bottom to top: Value increase

        my_canvas.setFont(FONT_TYPE+"-Bold", FONT_SIZE + 2)
        my_canvas.drawString(x_axis, y_axis, 'PASIVOS')
        y_axis -= LINE_SEPARATION
        y_axis, aux_summ = self.print_accounts(False, my_canvas, x_axis, y_axis, df_list[3], names_list[3])
        total_pasivo_patrimonio += aux_summ
        y_axis -= LINE_SEPARATION
        my_canvas.setFont(FONT_TYPE+"-Bold", FONT_SIZE + 2)
        my_canvas.drawString(x_axis, y_axis, 'PATRIMONIO')
        y_axis -= LINE_SEPARATION
        y_axis, aux_summ = self.print_accounts(False, my_canvas, x_axis, y_axis, df_list[4], names_list[4])
        total_pasivo_patrimonio += aux_summ
      

        my_canvas.setFont(FONT_TYPE+"-Bold", FONT_SIZE + 2)
        my_canvas.drawString(10, 50, 'TOTAL ACTIVO')
        my_canvas.drawRightString(255, 50,  '{:,.2f}'.format(total_activos))
        my_canvas.drawString(width/2 + 10, 50, 'TOTAL PASIVO Y PATRIMONIO')
        my_canvas.drawRightString(width/2 + 255, 50, '{:,.2f}'.format(total_pasivo_patrimonio))

        my_canvas.save()
        print("*********IMPRESION DEL PDF *********")
        return open(dir_path + name, "rb")


    def last_day_of_month(self, any_day : datetime):
        # The day 28 exists in every month. 4 days later, it's always next month
        next_month = any_day.replace(day=28) + timedelta(days=4)
        # subtracting the number of the current day brings us back one month
        last_date = next_month - timedelta(days=next_month.day)
        return int(last_date.day)

    def print_accounts(self, es_activo : bool , canvas_file : canvas.Canvas, x_axis : int , y_axis : int, df : pd.DataFrame, group_name ):

        canvas_file.setFont(FONT_TYPE+"-Bold", FONT_SIZE)
        canvas_file.drawString(x_axis, y_axis, group_name)
        y_axis -= LINE_SEPARATION
        
        canvas_file.setFont(FONT_TYPE, FONT_SIZE)

        for index, row  in df.iterrows():
 
            canva_code = str(row['code'])
            canva_name = row['name']
            canva_debit = float(row['debe'])
            canva_credit = float(row['haber'])

            x_line = x_axis + 5
            if len(canva_name) > 42:
                canva_name = (canva_name[:43]).rstrip() + '.'
            ##anvas_file.drawString(x_line, y_axis, canva_code)
            #_line += 100
            canvas_file.drawString(x_line, y_axis, canva_name )
            x_line += 250 #- len(canva_name)
            canva_result = canva_debit - canva_credit if es_activo else canva_credit - canva_debit
            canvas_file.drawRightString(x_line, y_axis, '{:,.2f}'.format(canva_result))
 
            
            if (y_axis <= 20):
                canvas_file.showPage()
                y_axis = 730
            else: 
                y_axis -= 15
       
        
        canvas_file.setFont(FONT_TYPE+"-Bold", FONT_SIZE)
        total_result = df['debe'].sum() - df['haber'].sum() if es_activo else df['haber'].sum() - df['debe'].sum()
        canvas_file.drawString(x_axis + 5, y_axis, 'TOTAL ' + group_name.upper())
        canvas_file.drawRightString(x_axis + 255, y_axis,  '{:,.2f}'.format(total_result))
        
        y_axis -= LINE_SEPARATION

        return y_axis, total_result

    def get_exchange_rate(self):

        """
        # base currency or reference currency
        base="USD"

        # required currency for plot
        out_curr="PEN"

        if (self.currency == 'me'):
            base, out_curr = out_curr, base

        # exchange data till a date
        end_date=datetime.strftime(datetime(int(self.year), int(self.month), 1),'%Y-%m-%d')

        # api url for request 
        url = 'https://api.exchangerate.host/timeseries?base={0}&start_date={1}&end_date={2}&symbols={3}'.format(base,end_date,end_date,out_curr)
        response = requests.get(url)

        # retrive response in json format
        data = response.json()
        """
        if (self.currency == 'me'):
            return (1.00/3.95)
        else :
            return 3.95
        