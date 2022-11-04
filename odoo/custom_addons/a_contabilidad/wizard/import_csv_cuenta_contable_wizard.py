import pandas as pd
import numpy as np
import base64
import csv
import io
import os
from odoo import api, models, fields, exceptions

 
class ImportCsvCuentaContableWizard(models.TransientModel):

    _name = "import.csv.account.account.wizard"
    _description = "Cargar Plan Contable"

    csv_file = fields.Binary(string='Archivo en formato CSV')
    downloadable_file_name = fields.Char(string='Nombre del Archivo', readonly=True)
    downloadable_file = fields.Binary('File Data', readonly=True)

   
    def import_csv(self):

        if not self.csv_file:
            raise exceptions.ValidationErr("No se ha subido algún archivo en formato CSV.")          

        csv_data = base64.b64decode(self.csv_file)
        data_file = io.StringIO(csv_data.decode("utf-8"))
        data_file.seek(0)
        file_reader = []
        csv_dict = csv.DictReader(data_file, delimiter=',')
        csv_reader = csv.reader(data_file, delimiter=',')
        file_reader.extend(csv_reader)
        file_reader[0] = [x.lower() for x in  file_reader[0] ]
        file_reader[0] = [x.replace(" ", "_") for x in  file_reader[0] ]
        file_reader[0] = [x.replace("nombre", "name") for x in  file_reader[0] ]
        file_reader[0] = [x.replace("codigo", "code") for x in  file_reader[0] ]
        
        
        df = pd.DataFrame(file_reader[1:], columns = file_reader[0])

        
        df['moneda'] = df['moneda'].str.lower()
        df['moneda'] = np.where(df['moneda'] == 'me', 'me', 'mn')
        df['code'] = df['code'].str.rstrip()
        #df['currency_id'] = df.apply (lambda row: label_race(row), axis=1)
        df['currency_id'] = np.where(df['moneda'] == 'me', 2, 154)
        
        df['user_type_id'] = df.apply (lambda row: self.convert_to_hierachy_en(row.code), axis=1)
        df['company_id'] = df.apply (lambda row: 1, axis=1)
        df['name'] = df['name'].str.rstrip()
        df['jerarquia'] = df.apply (lambda row: min(6,len(str(row.code))), axis=1)
        
        df['tipo_de_cuenta'] = df.apply (lambda row: self.env['account.account.tipo'].search([('elemento', '=', int((str(row.code))[0]) )]).id, axis=1)
        
        return self.bulk_create_account_account(df)        

        
    def bulk_create_account_account(self, df):

     
        dictionary_of_properties = df.to_dict('records')
        
        for entry in dictionary_of_properties:
            
            self.env['account.account'].create(entry)
            
    def convert_to_hierachy_en(self,code):

        element = int((str(code))[0])
        if element < 4:
            return 5
        elif element == 4: 
            return 9
        elif element == 5: 
            return 11
        elif element == 7 or element == 8: 
            return 13
        elif element == 6 or element == 9: 
            return 15
        else:
            return 18

    def download_example_file(self):
        
        dir_path = os.getcwd() + '/odoo/custom_addons/a_contabilidad/data/' 
        name = 'plan_contable.csv'
        
        self.downloadable_file = base64.b64encode((open(dir_path + name, "rb")).read())
        self.downloadable_file_name = name
        url_string = '/web/content/'+ self._name + '/' + str(self.id) + '/downloadable_file/'+ self.downloadable_file_name +'?download=true'

        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': url_string
        }