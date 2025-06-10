import customtkinter as ctk
import gspread
import os
from google.oauth2.service_account import Credentials
from config import Config
from custom_messagebox import show_error

config = Config()

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def get_credentials():
    """Get Google API credentials from environment or file"""
    try:

        if os.path.exists('credentials.json'):
            #print("Using credentials from file")
            return Credentials.from_service_account_file('credentials.json', scopes=scopes)
        
        else:
            print("No credentials found")
            show_error("Error", "Google API credentials not found. Please configure them in the Settings.")
            return None
        
    except Exception as e:
        print(f"Error getting credentials: {e}")
        import traceback
        traceback.print_exc()
        show_error("Error", f"Failed to load Google credentials: {str(e)}")
        return None

def get_sheet_client():
    creds = get_credentials()
    if creds:
        return gspread.authorize(creds)
    return None

client = get_sheet_client()

def fetch_credentials():
    """Fetch user credentials from Google Sheets"""
    try:
        # Check if client is not None
        if not client:
            print("Google Sheets client is not initialized")
            return {"admin@example.com": ("admin123", "admin")}
        
        # If config is empty, create new sheets
        if not config.get_credentials_sheet_id():
            from sheets_manager import GoogleSheetsManager
            sheets_manager = GoogleSheetsManager('credentials.json')
            sheet_data = sheets_manager.create_and_share_sheets("admin@example.com", "admin123")
            if sheet_data:
                config.save_sheet_urls(sheet_data["inventory_url"], sheet_data["credentials_url"])   
        
        sheet = client.open_by_key(config.get_credentials_sheet_id()).sheet1
        data = sheet.get_all_values()
        
        if not data:
            print("No data found in credentials sheet")
            return {"admin@example.com": ("admin123", "admin")}
            
        # Skip header row if it exists
        if len(data) > 1:
            data = data[1:]
        
        credentials = {}
        for row in data:
            if len(row) >= 3:  # Make sure row has enough elements
                role, email, password = row[0], row[1], row[2]
                credentials[email] = (password, role)
        
        # If no valid credentials were found, use fallback
        if not credentials:
            print("Using fallback credentials")
            return {"admin@example.com": ("admin123", "admin")}

        return credentials
    
    except Exception as e:
        print(f"Error fetching credentials: {e}")
        import traceback
        traceback.print_exc()
        # Fallback credentials for testing
        return {"admin@example.com": ("admin123", "admin")}

class LoginPage(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Inventory Management System")
        self.geometry("425x425")
        self.resizable(0,0)
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.credentials = fetch_credentials()
        self.setup_ui()
        self.mainloop()

    def setup_ui(self):
        # Main Frame
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        # Title Label
        title_label = ctk.CTkLabel(frame, text="Inventory Management System", font=("Helvetica", 20, "bold"))
        title_label.pack(pady=(20, 10))

        subtitle_label = ctk.CTkLabel(frame, text="Log In To Your Account", font=("Helvetica", 14))
        subtitle_label.pack(pady=(0, 20))

        # Email Entry
        self.email_entry = ctk.CTkEntry(frame, placeholder_text="Username", width=250)
        self.email_entry.pack(pady=5)

        # Password Entry
        self.password_entry = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=250)
        self.password_entry.pack(pady=5)

        # Login Button
        login_button = ctk.CTkButton(frame, text="Login", command=self.login_action, fg_color="#007BFF",
                                     hover_color="#0056b3")
        login_button.pack(pady=10)


        frame_frame = ctk.CTkFrame(frame, width=10, fg_color="transparent")
        frame_frame.pack(padx = 0, pady = 0, fill = "both", expand = "True")
        # Configuration Button
        config_button = ctk.CTkButton(frame_frame, text="⚙️", command=self.show_config_dialog, 
                                     width=20, height=20, fg_color="#6c757d", hover_color="#495057")
        config_button.pack(side = "left", anchor = "sw", padx = 5)

        help_button = ctk.CTkButton(frame_frame, width=20, height = 20, text="❓", command = self.first_help)
        help_button.pack(side = "left", anchor = "sw")

        # Error Label
        self.error_label = ctk.CTkLabel(frame, text="", text_color="red")
        self.error_label.pack()

        def show_first_run_help(self):
            import help
            help.show_first_run_help()

    def show_config_dialog(self):
        """Show configuration dialog for Google Sheets setup"""
        from config_window import ConfigWindow
        ConfigWindow()

    def first_help(self):
        from help import getStarted
        getStarted()

    def login_action(self):
        email = self.email_entry.get()
        password = self.password_entry.get()
        role = self.validate_credentials(email, password)

        if role == "admin":
            self.destroy()
            from admin_page import AdminPage
            AdminPage()
        elif role == "user":
            self.destroy()
            from user_page import UserPage
            UserPage(email)
        else:
            self.error_label.configure(text="Invalid Email or Password!")

    def validate_credentials(self, email, password):
        if email in self.credentials and self.credentials[email][0] == password:
            return self.credentials[email][1]  
        return None