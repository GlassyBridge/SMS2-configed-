import json
import customtkinter as ctk

class getStarted():
    def __init__(self):
        self.welcome = ctk.CTk()
        self.welcome.title("Welcome to Inventory Management System")
        self.welcome.geometry("800x800")

        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Add content
        ctk.CTkLabel(self.welcome, text="Welcome to Inventory Management System", 
                font=("Helvetica", 24, 'bold'), text_color="#4CAF50").pack(pady=(30, 15))
                
        ctk.CTkLabel(self.welcome, text="Getting Started Guide", 
                font=("Helvetica", 16, 'bold'), text_color="#ffffff").pack(pady=(0, 20))

        # Create scrollable frame for instructions
        self.info_frame = ctk.CTkScrollableFrame(self.welcome, width=650, height=300)
        self.info_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Add setup instructions
        self.instructions = [
            ("1. Set up Google Cloud Project", "Create a project in Google Cloud Console and enable the Google Sheets API."),
            ("2. Create Service Account", "In Google Cloud Console, create a service account with appropriate permissions."),
            ("3. Generate API Key", "Create and download a JSON key for your service account."),
            ("4. Configure the App", "Use the Settings (⚙️) button on the login screen to configure settings."),
            ("5. Enter your email", "Enter the email you want to use as the admin account."),
            ("6. Upload JSON Key", "Upload the JSON key file you downloaded from Google Cloud Console."),
            ("7. Create Sheets", "Click the 'Create Sheets' button to create the required Google Sheets."),
            ("8. Now you're all set!", "You can now login to the app and start managing your inventory."),
            ("## Default Login", "If the configuration didnt work, use admin@example.com / admin123 to login as admin initially.")
        ]

        for i, (title, desc) in enumerate(self.instructions):
            self.step_frame = ctk.CTkFrame(self.info_frame, fg_color=("#e0e0e0" if i % 2 == 0 else "#d0d0d0"))
            self.step_frame.pack(fill="x", pady=5, padx=5)
            
            ctk.CTkLabel(self.step_frame, text=title, font=("Helvetica", 14, 'bold'), 
                    text_color="#1a1a1a").pack(anchor="w", padx=10, pady=(10, 5))
            ctk.CTkLabel(self.step_frame, text=desc, font=("Helvetica", 12), 
                    text_color="#333333", wraplength=600).pack(anchor="w", padx=20, pady=(0, 10))

        # Service account info
        self.email = self.get_service_account_email()
        self.account_frame = ctk.CTkFrame(self.welcome, fg_color="#333333", corner_radius=10)
        self.account_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(self.account_frame, text="Service Account Email:", 
                font=("Helvetica", 12, 'bold'), text_color="#4CAF50").pack(anchor="w", padx=10, pady=(10, 5))
        ctk.CTkLabel(self.account_frame, text=self.email, font=("Helvetica", 12), 
                text_color="#ffffff").pack(anchor="w", padx=20, pady=(0, 10))

        # Continue button
        ctk.CTkButton(self.welcome, text="Continue to Login", 
                    command=self.welcome.destroy, width=200, height=40,
                    fg_color="#4CAF50", text_color="white", 
                    font=("Helvetica", 14, 'bold')).pack(pady=20)

        # Run the window
        self.welcome.mainloop()

    def get_service_account_email(self):
        try:
            with open('credentials.json', 'r') as f:
                creds = json.load(f)
                return creds.get('client_email', 'Email not found')
        except Exception as e:
            return f"Error: {str(e)}"