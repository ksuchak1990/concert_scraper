# Imports
from Worker import Worker
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# # Set up sheet interaction
# sheet = client.open('sample_gigs').sheet1

# # Get all records
# list_of_hashes = sheet.get_all_records()
# print(list_of_hashes)

# # Records as list of lists
# lOL = sheet.get_all_values()

# # Records from individual row, column or cell
# row = sheet.row_values(1)
# column = sheet.col_values(1)
# sheet.cell(1,1).value()

# # Writing to sheet
# sheet.update_cell(1, 1, "Inserting this text here")

# # Writing a row
# row = ['This', 'Is', 'A', 'Row']
# index = 1
# sheet.insert_row(row, index)

# # Deleting a row
# sheet.delete_row(1)

# # Getting number of rows
# numberOfRows = sheet.row_count()

# Class
class GoogleSheetsWorker(Worker):
    def __init__(self):
        super().__init__()

        self.product = 'none'

        # Stages
        self.stageList = ['readData', 'processData', 'writeData']
        self.stageDict = {'readData': self.readData,
                            'processData': self.readData,
                            'writeData': self.writeData}

        # Creating client
        scope = ['https://spreadsheets.google.com/feeds']
        creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
        client = gspread.authorize(creds)

    def readData(self):
        pass

    def processData(self, data):
        pass

    def writeData(self, data):
        pass
