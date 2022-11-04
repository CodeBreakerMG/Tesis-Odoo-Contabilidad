import base64
import csv
import io
import os
from odoo import api, models, fields, exceptions


class ImportCsvCuentaContableTipoWizard(models.TransientModel):

    _name = "import.csv.account.account.tipo.wizard"
    _description = "Wizard to load Properties from CSV"

    
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
        file_reader[0] = [x.replace("descripcion", "description") for x in  file_reader[0] ]
        #reader = csv.DictReader(base64.b64decode(self.csv_file).split('\n'))
        #reader = csv.DictReader(base64.b64decode(self.csv_file).decode('file_encoding').encode('utf-8').split('\n')) #For files with different encoding
        
        return self.bulk_create_account_account_tipo(file_reader)

    def bulk_create_account_account_tipo(self, list_reader):

        headers, values = list_reader[0], list_reader[1:]
        dictionary_of_properties = [dict(zip(headers, value)) for value in values]
        
        for entry in dictionary_of_properties:
            
            self.env['account.account.tipo'].create(entry)
            
        
    def delete_cuentas(self):
        account_id_list = self.env['account.account'].search([])
        for record in account_id_list:
            
            account_complete = account_id_list.browse(record.id)
            try:
                account_complete.unlink()
            except:
                pass

    def download_example_file(self):
        
        dir_path = os.getcwd() + '/odoo/custom_addons/a_contabilidad/data/' 
        name = 'tipos_cuentas_contables.csv'
        
        self.downloadable_file = base64.b64encode((open(dir_path + name, "rb")).read())
        self.downloadable_file_name = name
        url_string = '/web/content/'+ self._name + '/' + str(self.id) + '/downloadable_file/'+ self.downloadable_file_name +'?download=true'

        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': url_string
        }
