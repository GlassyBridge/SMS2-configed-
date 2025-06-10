import gspread
import customtkinter as ctk
import os
from google.oauth2.service_account import Credentials
from login import LoginPage
from config import Config
from custom_messagebox import show_error, show_info

config = Config()

scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

def initialize_sheets():
    global client, inventory_sheet, user_assignments_sheet

    try:
        if os.path.exists('credentials.json'):
            print("Using credentials from file")
            creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
        else:
            print("No credentials found")
            show_error("Error", "Google API credentials not found. Please configure them in the Settings.")
            return None, None, None

        client = gspread.authorize(creds)

        # Google Sheets IDs from config
        inventory_sheetid = config.get_inventory_sheet_id()
        user_assignments_sheetid = config.get_credentials_sheet_id()  # Reusing credentials sheet for assignments

        # Access the sheets with error handling
        inventory_sheet = client.open_by_key(inventory_sheetid).sheet1

        # Create user_assignments worksheet if it doesn't exist
        try:
            user_assignments_sheet = client.open_by_key(user_assignments_sheetid).worksheet("user_assignments")
        except gspread.exceptions.WorksheetNotFound:
            # If the worksheet doesn't exist, create it
            credentials_sheet = client.open_by_key(user_assignments_sheetid)
            user_assignments_sheet = credentials_sheet.add_worksheet(title="user_assignments", rows=100, cols=20)
            # Add headers
            user_assignments_sheet.append_row(["Email", "Material", "Quantity", "Date"])

        return client, inventory_sheet, user_assignments_sheet

    except Exception as e:
        print(f"Error authenticating with Google Sheets: {e}")
        import traceback
        traceback.print_exc()
        show_error("Error", f"Failed to connect to Google Sheets: {str(e)}")
        return None, None, None

client, inventory_sheet, user_assignments_sheet = initialize_sheets()

class UserPage:
    def __init__(self, email):
        self.email = email
        self.display = ctk.CTk()
        self.display.title("Inventory Management - User Dashboard")
        self.display.geometry("700x500")
        self.display.config(bg="#2E2E2E")
        
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        self.setup_ui()
        self.display.mainloop()

    def setup_ui(self):
        # Header frame with logout and user info
        header_frame = ctk.CTkFrame(self.display, fg_color="#333333", corner_radius=0, height=50)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)
        
        # Logo/Title
        ctk.CTkLabel(header_frame, text="Inventory Management", font=("Helvetica", 16, 'bold'),
                     text_color="#4CAF50").pack(side="left", padx=20)
        
        # User email display
        ctk.CTkLabel(header_frame, text=f"User: {self.email}", font=("Helvetica", 12),
                     text_color="#e0e0e0").pack(side="left", padx=20)
        
        # Logout button
        ctk.CTkButton(header_frame, text="Log Out", fg_color="#F44336", text_color="white", 
                      font=("Helvetica", 12, 'bold'), width=100,
                      command=self.logout).pack(side="right", padx=20)

        # Main content area
        content_frame = ctk.CTkFrame(self.display, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Left column - Inventory access
        left_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        inventory_frame = ctk.CTkFrame(left_column, fg_color="#222222", corner_radius=10)
        inventory_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(inventory_frame, text="Inventory Access", font=("Helvetica", 16, 'bold'),
                     text_color="#4CAF50").pack(pady=15)
                     
        ctk.CTkButton(inventory_frame, text="View Inventory", command=self.view_inventory, width=200,
                      fg_color="#4CAF50", text_color="white").pack(pady=10)
        
        # Add refresh inventory button
        ctk.CTkButton(inventory_frame, text="Refresh Inventory Data", command=self.refresh_sheets, width=200,
                      fg_color="#2196F3", text_color="white").pack(pady=10)
        
        # Status indicator
        self.connection_status = ctk.CTkLabel(inventory_frame, text="Connection Status: Checking...", 
                                            font=("Helvetica", 12),
                                            text_color="#888888")
        self.connection_status.pack(pady=15)
        
        # Update connection status
        self.display.after(1000, self.update_connection_status)
        
        # Right column - Material management
        right_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))
        
        material_frame = ctk.CTkFrame(right_column, fg_color="#222222", corner_radius=10)
        material_frame.pack(fill="both", expand=True)
        
        ctk.CTkLabel(material_frame, text="Material Management", font=("Helvetica", 16, 'bold'),
                     text_color="#4CAF50").pack(pady=15)
                     
        ctk.CTkButton(material_frame, text="Add Material Request", command=self.add_update_material, width=200,
                      fg_color="#FF9800", text_color="white").pack(pady=10)
                      
        ctk.CTkButton(material_frame, text="View My Requests", command=self.view_my_requests, width=200,
                      fg_color="#9C27B0", text_color="white").pack(pady=10)
                      
        # Footer with status
        footer_frame = ctk.CTkFrame(self.display, fg_color="#333333", corner_radius=0, height=30)
        footer_frame.pack(fill="x", side="bottom")
        footer_frame.pack_propagate(False)
                    
    def update_connection_status(self):
        """Update the connection status indicator"""
        global inventory_sheet
        
        if inventory_sheet is not None:
            try:
                # Try a simple operation to verify connection
                inventory_sheet.cell(1, 1)
                self.connection_status.configure(text="Connection Status: Connected ✓", text_color="#4CAF50")
            except Exception:
                self.connection_status.configure(text="Connection Status: Disconnected ✗", text_color="#F44336")
        else:
            self.connection_status.configure(text="Connection Status: Not Configured ⚠", text_color="#FF9800")
            
        # Schedule the next update
        self.display.after(60000, self.update_connection_status)  # Check every minute
        
    def refresh_sheets(self):
        """Refresh Google Sheets connection"""
        global client, inventory_sheet, user_assignments_sheet
        
        try:
            client, inventory_sheet, user_assignments_sheet = initialize_sheets()
            if inventory_sheet is not None:
                show_info("Success", "Connection to Google Sheets refreshed successfully!")
                self.update_connection_status()
            else:
                show_error("Error", "Failed to connect to Google Sheets")
        except Exception as e:
            show_error("Error", f"Error refreshing connection: {str(e)}")
            
    def view_my_requests(self):
        """View the user's material requests"""
        if user_assignments_sheet is None:
            show_error("Error", "Cannot connect to Google Sheets")
            return
            
        top = ctk.CTkToplevel(self.display)
        top.title("My Material Requests")
        top.geometry("600x500")
        top.grab_set()  # Make window modal
        
        ctk.CTkLabel(top, text="My Material Requests", font=("Helvetica", 18, 'bold'), 
                    text_color="#4CAF50").pack(pady=10)
                    
        # Create scrollable frame
        frame = ctk.CTkScrollableFrame(top, fg_color="#16191a")
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        try:
            # Get all rows
            all_rows = user_assignments_sheet.get_all_values()
            
            # Check if there's at least a header row
            if len(all_rows) > 0:
                # Add header
                header_frame = ctk.CTkFrame(frame, fg_color="#333333")
                header_frame.pack(fill="x", pady=5)
                
                ctk.CTkLabel(header_frame, text="Material", font=("Helvetica", 12, "bold"), 
                            text_color="#ffffff", width=200).pack(side="left", padx=10)
                ctk.CTkLabel(header_frame, text="Quantity", font=("Helvetica", 12, "bold"), 
                            text_color="#ffffff", width=100).pack(side="left", padx=10)
                ctk.CTkLabel(header_frame, text="Date", font=("Helvetica", 12, "bold"), 
                            text_color="#ffffff", width=150).pack(side="left", padx=10)
                
                # Filter for this user's requests
                user_rows = [row for row in all_rows if len(row) >= 2 and row[0] == self.email]
                
                if not user_rows:
                    ctk.CTkLabel(frame, text="You have no material requests", font=("Helvetica", 12), 
                                text_color="#888").pack(pady=20)
                else:
                    for i, row in enumerate(user_rows):
                        # Extract data
                        material = row[1] if len(row) > 1 else "Unknown"
                        quantity = row[2] if len(row) > 2 else "Unknown"
                        date = row[3] if len(row) > 3 else "Unknown"
                        
                        # Create row
                        row_color = "#1e1e1e" if i % 2 == 0 else "#151515"
                        row_frame = ctk.CTkFrame(frame, fg_color=row_color)
                        row_frame.pack(fill="x", pady=2)
                        
                        ctk.CTkLabel(row_frame, text=material, font=("Helvetica", 12), 
                                    text_color="#ffffff", width=200).pack(side="left", padx=10)
                        ctk.CTkLabel(row_frame, text=quantity, font=("Helvetica", 12), 
                                    text_color="#ffffff", width=100).pack(side="left", padx=10)
                        ctk.CTkLabel(row_frame, text=date, font=("Helvetica", 12), 
                                    text_color="#ffffff", width=150).pack(side="left", padx=10)
            else:
                ctk.CTkLabel(frame, text="No data available", font=("Helvetica", 12), 
                            text_color="#888").pack(pady=20)
                
        except Exception as e:
            ctk.CTkLabel(frame, text=f"Error: {str(e)}", font=("Helvetica", 12), 
                        text_color="#F44336").pack(pady=20)
                
        # Close button
        ctk.CTkButton(top, text="Close", command=top.destroy, fg_color="#555555", 
                    text_color="white").pack(pady=15)

    def logout(self):
        self.display.destroy()
        LoginPage()

    def view_inventory(self):
        top = ctk.CTkToplevel(self.display)
        top.title("View Inventory")
        top.geometry("600x500")

        ctk.CTkLabel(top, text="Inventory List", font=("Helvetica", 18, 'bold'), text_color="#4CAF50").pack(pady=10)

        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(top, textvariable=search_var, placeholder_text="Search Inventory", width=300)
        search_entry.pack(pady=5)

        frame = ctk.CTkScrollableFrame(top, fg_color="#16191a")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        def update_inventory():
            for widget in frame.winfo_children():
                widget.destroy()

            search_text = search_var.get().lower()
            try:
                rows = inventory_sheet.get_all_values()
                if not rows:
                    ctk.CTkLabel(frame, text="No inventory found", font=("Helvetica", 12), text_color="#888").pack(
                        pady=10)
                else:
                    for i, row in enumerate(rows):
                        name, qty = row
                        if search_text in name.lower():
                            row_color = "#04090a" if i % 2 == 0 else "#04090a"
                            item_frame = ctk.CTkFrame(frame, fg_color=row_color, corner_radius=5)
                            item_frame.pack(fill="x", pady=5, padx=10)
                            ctk.CTkLabel(item_frame, text=f"{name}", font=("Helvetica", 12),
                                         text_color="#ffffff").pack(
                                side="left", padx=10)
                            ctk.CTkLabel(item_frame, text=f"{qty}", font=("Helvetica", 12),
                                         text_color="#ffffff").pack(
                                side="right", padx=10)
            except Exception as e:
                ctk.CTkLabel(frame, text=f"Error: {e}", font=("Helvetica", 12), text_color="#888").pack(pady=10)

        search_entry.bind("<KeyRelease>", lambda event: update_inventory())
        update_inventory()

    def add_update_material(self):
        """Add or update a material request"""
        if user_assignments_sheet is None:
            show_error("Error", "Cannot connect to Google Sheets")
            return
            
        top = ctk.CTkToplevel(self.display)
        top.title("Add Material Request")
        top.geometry("450x400")
        top.grab_set()  # Make window modal
        
        # Title
        ctk.CTkLabel(top, text="Add Material Request", font=("Helvetica", 18, 'bold'), 
                    text_color="#4CAF50").pack(pady=(20, 30))
                    
        # Material name with dropdown for existing materials
        material_frame = ctk.CTkFrame(top, fg_color="transparent")
        material_frame.pack(fill="x", padx=40, pady=5)
        
        ctk.CTkLabel(material_frame, text="Material Name:", font=("Helvetica", 12), 
                    anchor="w", width=120).pack(side="left")
                    
        # Create a combobox with material options
        material_options = ["Type to search..."]
        try:
            if inventory_sheet:
                materials = inventory_sheet.get_all_values()
                if materials and len(materials) > 0:
                    material_options.extend([item[0] for item in materials if len(item) > 0 and item[0]])
        except Exception:
            pass
            
        material_var = ctk.StringVar()
        name_entry = ctk.CTkComboBox(material_frame, width=250, values=material_options,
                                  variable=material_var)
        name_entry.pack(side="left", padx=(10, 0))
        
        # Quantity
        quantity_frame = ctk.CTkFrame(top, fg_color="transparent")
        quantity_frame.pack(fill="x", padx=40, pady=15)
        
        ctk.CTkLabel(quantity_frame, text="Quantity:", font=("Helvetica", 12), 
                    anchor="w", width=120).pack(side="left")
                    
        quantity_entry = ctk.CTkEntry(quantity_frame, width=250)
        quantity_entry.pack(side="left", padx=(10, 0))
        
        # Current date - automatically set
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        date_frame = ctk.CTkFrame(top, fg_color="transparent")
        date_frame.pack(fill="x", padx=40, pady=15)
        
        ctk.CTkLabel(date_frame, text="Date:", font=("Helvetica", 12), 
                    anchor="w", width=120).pack(side="left")
                    
        date_entry = ctk.CTkEntry(date_frame, width=250)
        date_entry.pack(side="left", padx=(10, 0))
        date_entry.insert(0, current_date)
        
        # Notes/Comments
        notes_frame = ctk.CTkFrame(top, fg_color="transparent")
        notes_frame.pack(fill="x", padx=40, pady=15)
        
        ctk.CTkLabel(notes_frame, text="Notes:", font=("Helvetica", 12), 
                    anchor="w", width=120).pack(side="left")
                    
        notes_entry = ctk.CTkEntry(notes_frame, width=250)
        notes_entry.pack(side="left", padx=(10, 0))

        def save_material():
            # Get values
            material_name = name_entry.get()
            quantity = quantity_entry.get()
            date = date_entry.get()
            notes = notes_entry.get()
            
            # Validate
            if not material_name or material_name == "Type to search...":
                show_error("Error", "Please enter a material name")
                return
                
            if not quantity:
                show_error("Error", "Please enter a quantity")
                return
                
            try:
                # Convert to number to validate
                float(quantity)
            except ValueError:
                show_error("Error", "Quantity must be a number")
                return
                
            try:
                # Prepare data
                row_data = [self.email, material_name, quantity, date]
                if notes:
                    row_data.append(notes)
                    
                # Append to sheet
                user_assignments_sheet.append_row(row_data)
                show_info("Success", "Material request added successfully!")
                top.destroy()
                
            except Exception as e:
                show_error("Error", f"An error occurred: {e}")

        # Buttons
        button_frame = ctk.CTkFrame(top, fg_color="transparent")
        button_frame.pack(fill="x", padx=40, pady=30)
        
        # Cancel button
        ctk.CTkButton(button_frame, text="Cancel", command=top.destroy, width=120, 
                    fg_color="#555555", text_color="white").pack(side="left")
                    
        # Submit button  
        ctk.CTkButton(button_frame, text="Submit", command=save_material, width=120, 
                    fg_color="#4CAF50", text_color="white").pack(side="right")