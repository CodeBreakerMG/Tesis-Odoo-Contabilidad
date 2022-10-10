import pandas as pd
import numpy as np
import base64
import csv
import io
from odoo import api, models, fields

 

class ImportCsvCuentaContableWizard(models.TransientModel):

    _name = "import.csv.account.account.wizard"
    _description = "Cargar Plan Contable"

    # your file will be stored here:
    csv_file = fields.Binary(string='CSV File', required=True)
    #property_ids = fields.Many2one("account.account", string="Name", default=lambda self: self.env['account.account'].search([]))

   
    def import_csv(self):
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
    """        
    url, db, username, password = 'https://localhost:8069', 'odoo_tesis_db1', 'a20160500', 'test'

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))

    uid = common.authenticate(db, username, password, {}) #authentication

    if uid:
        print("authentication succeeded")
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        property_types = models.execute_kw(db, uid, password, 'account.account.type', 'read', [list(range(1,100))], {'fields': ['name']})
        for row in csv_reader:
            print("---row---: ", row)
            
        print("Property Types from BD")
        print(property_types)
    else:
        print("authentication failed")
    """