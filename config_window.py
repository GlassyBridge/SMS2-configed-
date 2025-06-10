import customtkinter as ctk
from tkinter import filedialog
from config import Config 
import re
import json
import os
from custom_messagebox import show_error, show_info

class ConfigWindow:
    def __init__(self):
        self.config = Config()
        self.window = ctk.CTkToplevel()
        self.window.title("Google Sheets Configuration")
        self.window.geometry("500x500")

        # Set color themes
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.setup_ui()

        # Wait for window to be ready before grabbing
        self.window.update()
        self.window.grab_set()

    def setup_ui(self):
        # Main container
        container = ctk.CTkFrame(self.window)
        container.pack(fill="both", expand=True, padx=20, pady=20)

        # Title and Save Button Frame
        header_frame = ctk.CTkFrame(container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))

        title = ctk.CTkLabel(header_frame, text="Configuration Menu", 
                           font=("Helvetica", 20, "bold"))
        title.pack(side="left", padx=5)

        save_button = ctk.CTkButton(
            header_frame, text="Save Configuration", command=self.save_configuration,
            fg_color="#4CAF50", text_color="white", width=160
        )
        save_button.pack(side="right", padx=5)

        # Admin Setup Frame
        admin_frame = ctk.CTkFrame(container)
        admin_frame.pack(fill="x", pady=10)

        # Check for existing admin
        has_admin = False
        try:
            if os.path.exists('credentials.json'):
                from sheets_manager import GoogleSheetsManager
                manager = GoogleSheetsManager('credentials.json')
                sheet = manager.client.open_by_key(self.config.get_credentials_sheet_id()).sheet1
                admins = [row for row in sheet.get_all_values()[1:] if row[0].lower() == 'admin']
                has_admin = len(admins) > 0
        except Exception:
            pass

        status_text = "Admin account already exists for this service account." if has_admin else "Admin Setup"
        admin_label = ctk.CTkLabel(admin_frame, text=status_text, 
                                font=("Helvetica", 12, "bold"))
        admin_label.pack(pady=5)

        self.admin_email = ctk.CTkEntry(admin_frame, placeholder_text="Admin Email", 
                                      state="disabled" if has_admin else "normal")
        self.admin_email.pack(fill="x", padx=10, pady=5)

        self.admin_password = ctk.CTkEntry(admin_frame, placeholder_text="Admin Password", 
                                         show="*", state="disabled" if has_admin else "normal")
        self.admin_password.pack(fill="x", padx=10, pady=5)

        # Create sheets button - Moved higher
        create_button = ctk.CTkButton(
            container, text="Create New Sheets", command=self.create_new_sheets,
            fg_color="#2196F3" if has_admin else "#0c4370", text_color="white", width=160,
            state="disabled" if has_admin else "normal"
        )
        create_button.pack(pady=5)

        # Service Account JSON
        json_label = ctk.CTkLabel(container, text="Service Account JSON:", 
                                font=("Helvetica", 12))
        json_label.pack(anchor="w", pady=(10, 5))

        self.json_text = ctk.CTkTextbox(container, width=360, height=150)
        self.json_text.pack(pady=(0, 10), fill="x")

        # Load current credentials if exists
        try:
            if os.path.exists('credentials.json'):
                with open('credentials.json', 'r') as f:
                    json_obj = json.load(f)
                    self.json_text.insert("1.0", json.dumps(json_obj, indent=2))
        except Exception as e:
            show_error("Error", f"Unable to load credentials: {e}")

        # Browse button
        browse_button = ctk.CTkButton(container, text="Browse for JSON File", 
                                    command=self.browse_json_file)
        browse_button.pack(pady=(0, 10), fill="x")

        '''# Help text
        help_text = """
1. Create a service account in Google Cloud Console
2. Generate a JSON key for the service account
3. Paste the complete JSON key above
4. Click 'Create New Sheets' to set up your spreadsheets
        """
        help_label = ctk.CTkLabel(container, text=help_text, 
                                font=("Helvetica", 11),
                                justify="left",
                                text_color="#6c757d")
        help_label.pack(anchor="w", pady=(10, 15))'''

        # Button frame
        button_frame = ctk.CTkFrame(container, fg_color="transparent")
        button_frame.pack(pady=20, fill="x")

    def extract_id(self, url):
        """ Extract the Sheet ID from the URL """
        match = re.search(r"/d/([a-zA-Z0-9-_]+)", url)
        return match.group(1) if match else None

    def browse_json_file(self):
        file_path = filedialog.askopenfilename(
            title="Select API Credentials JSON File", 
            filetypes=[("JSON files", "*.json")]
        )
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    self.json_text.delete("1.0", "end")
                    self.json_text.insert("1.0", content)
            except Exception as e:
                show_error("Error", f"Could not load file: {str(e)}")

    def save_configuration(self):
        # Save API credentials
        api_json = self.json_text.get("1.0", "end-1c").strip()
        if api_json:
            try:
                json_obj = json.loads(api_json)
                required_fields = ['client_email', 'private_key', 'type']
                missing_fields = [field for field in required_fields if field not in json_obj]

                if missing_fields:
                    show_error("Error", f"JSON missing required fields: {', '.join(missing_fields)}")
                    return

                if json_obj.get('type') != 'service_account':
                    show_error("Error", "JSON must be a service account key")
                    return

                with open('credentials.json', 'w') as f:
                    f.write(api_json)

                show_info("Success", f"Configuration saved!")
                self.window.destroy()

            except json.JSONDecodeError:
                show_error("Error", "Invalid JSON format!")
            except Exception as e:
                show_error("Error", f"Error: {str(e)}")
        else:
            show_error("Error", "Service account JSON required!")

    def create_new_sheets(self):
        email = self.admin_email.get().strip()
        password = self.admin_password.get().strip()

        if not email or not password:
            show_error("Error", "Admin email and password required for new sheets")
            return

        if not os.path.exists('credentials.json'):
            show_error("Error", "Please configure Google credentials first")
            return

        try:
            from sheets_manager import GoogleSheetsManager
            manager = GoogleSheetsManager('credentials.json')
            sheet_ids = manager.create_and_share_sheets(email, password)

            if sheet_ids:
                # Try sharing again directly with admin email
                success1 = manager.share_spreadsheet(sheet_ids["inventory_sheet_id"], email)
                success2 = manager.share_spreadsheet(sheet_ids["credentials_sheet_id"], email)

                if success1 and success2:
                    show_info("Success", f"Sheets created and shared with {email} successfully!")
                else:
                    show_info("Warning", "Sheets created but sharing may have failed. Please check your email access.")
            else:
                show_error("Error", "Failed to create sheets")

        except Exception as e:
            show_error("Error", f"Failed to create sheets: {str(e)}")

    def restart_app(self):
        # Close the current window
        self.window.destroy()

        # Import needed to restart the application
        import sys
        import os

        # Restart the application
        python = sys.executable
        os.execl(python, python, *sys.argv)