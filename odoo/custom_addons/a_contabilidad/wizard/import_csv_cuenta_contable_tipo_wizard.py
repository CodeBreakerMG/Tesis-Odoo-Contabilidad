import base64
import csv
import io
from odoo import api, models, fields
import xmlrpc.client
 

class ImportCsvCuentaContableTipoWizard(models.TransientModel):

    _name = "import.csv.account.account.tipo.wizard"
    _description = "Wizard to load Properties from CSV"

    # your file will be stored here:
    csv_file = fields.Binary(string='CSV File', required=True)
    #property_ids = fields.Many2one("account.account.tipo", string="Name", default=lambda self: self.env['account.account.tipo'].search([]))

   
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
        file_reader[0] = [x.replace("descripcion", "description") for x in  file_reader[0] ]
        #reader = csv.DictReader(base64.b64decode(self.csv_file).split('\n'))
        #reader = csv.DictReader(base64.b64decode(self.csv_file).decode('file_encoding').encode('utf-8').split('\n')) #For files with different encoding
        
        return self.bulk_create_account_account_tipo(file_reader)

    def bulk_create_account_account_tipo(self, list_reader):

        headers, values = list_reader[0], list_reader[1:]
        dictionary_of_properties = [dict(zip(headers, value)) for value in values]
        
        for entry in dictionary_of_properties:
            
            self.env['account.account.tipo'].create(entry)
            
        

    """        
    url, db, username, password = 'https://localhost:8069', 'odoo_tesis_db1', 'a20160500', 'test'

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))

    uid = common.authenticate(db, username, password, {}) #authentication

    if uid:
        print("authentication succeeded")
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
        property_types = models.execute_kw(db, uid, password, 'account.account.tipo.type', 'read', [list(range(1,100))], {'fields': ['name']})
        for row in csv_reader:
            print("---row---: ", row)
            
        print("Property Types from BD")
        print(property_types)
    else:
        print("authentication failed")
    """