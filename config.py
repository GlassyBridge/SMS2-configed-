
import json
import os

class Config:
    def __init__(self):
        self.load_config()

    def get_inventory_sheet_id(self):
        return self.inventory_sheet_id

    def get_credentials_sheet_id(self):
        return self.credentials_sheet_id

    def get_inventory_url(self):
        return self.inventory_url
        
    def get_credentials_url(self):
        return self.credentials_url

    def save_sheet_urls(self, inventory_url, credentials_url):
        self.inventory_url = inventory_url
        self.credentials_url = credentials_url
        config_data = {
            "google_sheets_ids": {
                "inventory_sheet_id": self.inventory_sheet_id,
                "credentials_sheet_id": self.credentials_sheet_id,
                "inventory_url": inventory_url,
                "credentials_url": credentials_url
            }
        }
        with open('config(44).json', 'w') as f:
            json.dump(config_data, f, indent=2)

    def load_config(self):
        try:
            if os.path.exists('config(44).json'):
                with open('config(44).json', 'r') as f:
                    config_data = json.load(f)
                    google_sheets_ids = config_data.get("google_sheets_ids", {})
                    self.inventory_sheet_id = google_sheets_ids.get("inventory_sheet_id", "")
                    self.credentials_sheet_id = google_sheets_ids.get("credentials_sheet_id", "")
                    self.inventory_url = google_sheets_ids.get("inventory_url", "")
                    self.credentials_url = google_sheets_ids.get("credentials_url", "")
                    
                    # Extract sheet IDs from URLs if IDs are empty
                    if not self.inventory_sheet_id and self.inventory_url:
                        self.inventory_sheet_id = self.inventory_url.split('/d/')[1].split('/')[0]
                    if not self.credentials_sheet_id and self.credentials_url:
                        self.credentials_sheet_id = self.credentials_url.split('/d/')[1].split('/')[0]
            else:
                self.inventory_sheet_id = ""
                self.credentials_sheet_id = ""
                self.inventory_url = ""
                self.credentials_url = ""
        except Exception as e:
            print(f"Error loading config: {e}")
            self.inventory_sheet_id = ""
            self.credentials_sheet_id = ""
            self.inventory_url = ""
            self.credentials_url = ""
