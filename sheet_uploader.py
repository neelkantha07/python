
import csv
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Authenticate using service account credentials
credentials = service_account.Credentials.from_service_account_file(
    'credentials.json',
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)

# Initialize the Sheets API
service = build('sheets', 'v4', credentials=credentials)

# Load data from CSV file
data = []
with open('navtara.csv', 'r', newline='') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        data.append(row)

# Define the spreadsheet ID and range
spreadsheet_id = '1KBsDIfw8UIzSwH452CcA6y_40zc93-M1h207O1JKP0U'
range_name = 'Transit_data'  # Adjust the sheet name if needed

# Clear existing data (optional)
service.spreadsheets().values().clear(
    spreadsheetId=spreadsheet_id,
    range=range_name
).execute()

# Upload new data
service.spreadsheets().values().update(
    spreadsheetId=spreadsheet_id,
    range=range_name,
    valueInputOption='RAW',
    body={'values': data}
).execute()

print('Data uploaded to Google Sheets successfully.')
