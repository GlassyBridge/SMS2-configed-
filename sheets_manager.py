import json
import gspread
from google.oauth2 import service_account
from googleapiclient.discovery import build

class GoogleSheetsManager:
    def __init__(self, json_keyfile):
        self.creds = service_account.Credentials.from_service_account_file(
            json_keyfile,
            scopes=[
                'https://www.googleapis.com/auth/spreadsheets',
                'https://www.googleapis.com/auth/drive'
            ]
        )
        self.service = build('sheets', 'v4', credentials=self.creds)
        self.client = gspread.authorize(self.creds)

    def create_spreadsheet(self, title):
        spreadsheet_body = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self.service.spreadsheets().create(body=spreadsheet_body, fields='spreadsheetId').execute()
        return spreadsheet.get('spreadsheetId')

    def share_spreadsheet(self, spreadsheet_id, email):
        try:
            # Share with the user with editor access
            self.client.open_by_key(spreadsheet_id).share(
                email,
                perm_type='user',
                role='writer',
                notify=True,
                with_link=True
            )
            return True
        except Exception as e:
            error_msg = str(e)
            if "drive.googleapis.com" in error_msg:
                print("Please enable the Google Drive API in your Google Cloud Console")
                print("Visit: https://console.cloud.google.com/apis/library/drive.googleapis.com")
            print(f"Error sharing spreadsheet: {error_msg}")
            return False

    def create_and_share_sheets(self, user_email, user_password):
        try:
            # Create spreadsheets
            inventory_id = self.create_spreadsheet('Inventory Management')
            credentials_id = self.create_spreadsheet('Credentials')
            
            # Generate URLs
            inventory_url = f"https://docs.google.com/spreadsheets/d/{inventory_id}"
            credentials_url = f"https://docs.google.com/spreadsheets/d/{credentials_id}"
            
            # Share spreadsheets
            self.share_spreadsheet(inventory_id, user_email)
            self.share_spreadsheet(credentials_id, user_email)
            
            # Add user to credentials sheet
            self.add_user_to_credentials(credentials_id, user_email, user_password)

            # Save sheet IDs to config
            from config import Config
            config = Config()
            config_data = {
                "google_sheets_ids": {
                    "inventory_sheet_id": inventory_id,
                    "credentials_sheet_id": credentials_id,
                    "inventory_url": inventory_url,
                    "credentials_url": credentials_url
                }
            }
            with open('config(44).json', 'w') as f:
                json.dump(config_data, f, indent=2)
            
            # Return the IDs for config
            return {
                "inventory_sheet_id": inventory_id,
                "credentials_sheet_id": credentials_id,
                "inventory_url": inventory_url,
                "credentials_url": credentials_url
            }
        except Exception as e:
            print(f"Error creating and sharing sheets: {e}")
            return None

    def add_user_to_credentials(self, credentials_sheet_id, user_email, user_password):
        # First clear any existing data
        self.service.spreadsheets().values().clear(
            spreadsheetId=credentials_sheet_id,
            range='A1:Z1000'
        ).execute()
        
        # Then add the header and admin user
        values = [
            ['Role', 'Email', 'Password'],
            ['admin', user_email, user_password]
        ]
        body = {'values': values}
        self.service.spreadsheets().values().update(
            spreadsheetId=credentials_sheet_id,
            range='A1',
            valueInputOption='RAW',
            body=body
        ).execute()