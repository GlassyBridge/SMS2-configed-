import gspread
from google.oauth2.service_account import Credentials
import customtkinter as ctk
from custom_messagebox import show_info, show_error, askyesno
from login import LoginPage
import os
import json
from config import Config

config = Config()

scopes = ["https://www.googleapis.com/auth/spreadsheets"]

try:
    creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)

    client = gspread.authorize(creds)
except Exception as e:
    print(f"Error authenticating with Google Sheets: {e}")

try:
    inventory_sheetid = config.get_inventory_sheet_id()
    credentials_sheetid = config.get_credentials_sheet_id()

    inventory_sheet = client.open_by_key(inventory_sheetid).sheet1
    credentials_sheet = client.open_by_key(credentials_sheetid).sheet1
except Exception as e:
    print(f"Error accessing sheets: {e}")
    inventory_sheet = None
    credentials_sheet = None

class AdminPage:
    def __init__(self):
        self.display = ctk.CTk()
        self.display.title("Admin Page")
        self.display.geometry("600x600")
        self.display.config(background="#2E2E2E")
        self.setup_ui()
        self.display.mainloop()

    def setup_ui(self):
        # Set appearance mode
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")

        # Header frame with logout
        header_frame = ctk.CTkFrame(self.display, fg_color="#333333", corner_radius=0, height=50)
        header_frame.pack(fill="x", pady=(0, 20))
        header_frame.pack_propagate(False)

        # Logo/Title
        ctk.CTkLabel(header_frame, text="Inventory Management", font=("Helvetica", 16, 'bold'),
                     text_color="#4CAF50").pack(side="left", padx=20)

        # Admin label
        ctk.CTkLabel(header_frame, text="Admin Dashboard", font=("Helvetica", 12),
                     text_color="#e0e0e0").pack(side="left", padx=20)

        # Logout button
        ctk.CTkButton(header_frame, text="Log Out", fg_color="#F44336", text_color="white", 
                      font=("Helvetica", 12, 'bold'), width=100,
                      command=self.logout).pack(side="right", padx=20)

        # Admin Dashboard Label
        ctk.CTkLabel(self.display, text="Admin Control Panel", font=("Helvetica", 24, 'bold'), 
                    text_color="#4CAF50").pack(pady=10)

        # Two-column layout
        content_frame = ctk.CTkFrame(self.display, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Left column
        left_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        left_column.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Inventory Management Frame
        inventory_frame = ctk.CTkFrame(left_column, fg_color="#222222", corner_radius=10)
        inventory_frame.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(inventory_frame, text="Inventory Management", font=("Helvetica", 18, 'bold'), 
                    text_color="#4CAF50").pack(pady=10)

        ctk.CTkButton(inventory_frame, text="Add Material", command=self.add_material, 
                    width=200, fg_color="#4CAF50", text_color="white", 
                    font=("Helvetica", 12)).pack(pady=5)

        ctk.CTkButton(inventory_frame, text="Update Material", command=self.update_material, 
                    width=200, fg_color="#FF9800", text_color="white", 
                    font=("Helvetica", 12)).pack(pady=5)

        ctk.CTkButton(inventory_frame, text="Remove Material", command=self.remove_material, 
                    width=200, fg_color="#F44336", text_color="white", 
                    font=("Helvetica", 12)).pack(pady=5)

        ctk.CTkButton(inventory_frame, text="Show All Inventory", command=self.show_all_inventory, 
                    width=200, fg_color="#2196F3", text_color="white", 
                    font=("Helvetica", 12)).pack(pady=10)

        # User Management Frame
        user_frame = ctk.CTkFrame(left_column, fg_color="#222222", corner_radius=10)
        user_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(user_frame, text="User Management", font=("Helvetica", 18, 'bold'), 
                    text_color="#4CAF50").pack(pady=10)

        ctk.CTkButton(user_frame, text="Add User", command=self.add_user, 
                    width=200, fg_color="#4CAF50", text_color="white",
                    font=("Helvetica", 12)).pack(pady=5)

        ctk.CTkButton(user_frame, text="Remove User", command=self.remove_user, 
                    width=200, fg_color="#F44336", text_color="white",
                    font=("Helvetica", 12)).pack(pady=5)

        ctk.CTkButton(user_frame, text="Show All Users", command=self.show_all_users,
                    width=200, fg_color="#2196F3", text_color="white",
                    font=("Helvetica", 12)).pack(pady=5)

        # Right column
        right_column = ctk.CTkFrame(content_frame, fg_color="transparent")
        right_column.pack(side="right", fill="both", expand=True, padx=(10, 0))

        # Requests Management Frame
        requests_frame = ctk.CTkFrame(right_column, fg_color="#222222", corner_radius=10)
        requests_frame.pack(fill="both", expand=True, pady=(0, 10))
        ctk.CTkLabel(requests_frame, text="Material Requests", font=("Helvetica", 18, 'bold'), 
                    text_color="#4CAF50").pack(pady=10)

        ctk.CTkButton(requests_frame, text="View User Requests", command=self.view_user_requests, 
                    width=200, fg_color="#9C27B0", text_color="white",
                    font=("Helvetica", 12)).pack(pady=5)

        ctk.CTkButton(requests_frame, text="Process Requests", command=self.process_requests, 
                    width=200, fg_color="#00BCD4", text_color="white",
                    font=("Helvetica", 12)).pack(pady=5)

        # System Frame
        system_frame = ctk.CTkFrame(right_column, fg_color="#222222", corner_radius=10)
        system_frame.pack(fill="both", expand=True)
        ctk.CTkLabel(system_frame, text="System Settings", font=("Helvetica", 18, 'bold'), 
                    text_color="#4CAF50").pack(pady=10)

        ctk.CTkButton(system_frame, text="Test Connection", 
                    command=self.test_connection, width=200, 
                    fg_color="#795548", text_color="white",
                    font=("Helvetica", 12)).pack(pady=5)

    def logout(self):
        self.display.destroy()
        LoginPage()

    def modify_credentials(self, email, password, role="user", remove=False):
        try:
            if remove:
                cell = credentials_sheet.find(email)
                if cell:
                    credentials_sheet.delete_row(cell.row)
                    show_info("Success", "User removed successfully!")
                else:
                    show_error("Error", "User not found!")
            else:
                credentials_sheet.append_row([role, email, password])
                show_info("Success", "User added successfully!")
        except Exception as e:
            show_error("Error", f"An error occurred: {e}")

    def modify_inventory(self, name, quantity=None, remove=False):
        try:
            if remove:
                cell = inventory_sheet.find(name)
                if cell:
                    inventory_sheet.delete_row(cell.row)
                    show_info("Success", "Material removed successfully!")
                else:
                    show_error("Error", "Material not found!")
            else:
                cell = inventory_sheet.find(name)
                if cell:
                    if quantity:
                        inventory_sheet.update_cell(cell.row, 2, quantity)
                        show_info("Success", "Material updated successfully!")
                else:
                    if quantity:
                        inventory_sheet.append_row([name, quantity])
                        show_info("Success", "Material added successfully!")
        except gspread.exceptions.CellNotFound:
            if not remove:
                inventory_sheet.append_row([name, quantity])
                show_info("Success", "Material added successfully!")
        except Exception as e:
            show_error("Error", f"An error occurred: {e}")

    def add_user(self):
        self.manage_users("add")
    
    def remove_user(self):
        self.manage_users("remove")

    def manage_users(self, action):
        top = ctk.CTkToplevel(self.display)
        top.title("Manage Users")
        top.geometry("400x300")

        ctk.CTkLabel(top, text="Role (admin/user):", font=("Helvetica", 12)).pack(pady=10)
        role_entry = ctk.CTkEntry(top, width=200, font=("Helvetica", 12))
        role_entry.pack(pady=5)
        role_entry.insert(0, "user")

        ctk.CTkLabel(top, text="Username (Email):", font=("Helvetica", 12)).pack(pady=10)
        email_entry = ctk.CTkEntry(top, width=200, font=("Helvetica", 12))
        email_entry.pack(pady=5)

        ctk.CTkLabel(top, text="Password:", font=("Helvetica", 12)).pack(pady=10)
        password_entry = ctk.CTkEntry(top, width=200, show="*", font=("Helvetica", 12))
        password_entry.pack(pady=5)

        def save_user():
            role = role_entry.get()
            email = email_entry.get()
            password = password_entry.get()

            if role not in ["admin", "user"]:
                show_error("Error", "Invalid role! Please choose 'admin' or 'user'.")
                return

            if action == "add":
                self.modify_credentials(email, password, role)
            elif action == "remove":
                self.modify_credentials(email, password, remove=True)
            top.destroy()

        ctk.CTkButton(top, text="Submit", command=save_user, width=200, fg_color="#4CAF50", text_color="white",
                      font=("Helvetica", 12)).pack(pady=20)

    def add_material(self):
        self.manage_inventory("add")

    def update_material(self):
        self.manage_inventory("update")

    def remove_material(self):
        self.manage_inventory("remove")

    def manage_inventory(self, action):
        top = ctk.CTkToplevel(self.display)
        top.title("Manage Inventory")
        top.geometry("400x300")

        ctk.CTkLabel(top, text="Material Name:", font=("Helvetica", 12)).pack(pady=10)
        name_entry = ctk.CTkEntry(top, width=200, font=("Helvetica", 12))
        name_entry.pack(pady=5)

        ctk.CTkLabel(top, text="Quantity:", font=("Helvetica", 12)).pack(pady=10)
        quantity_entry = ctk.CTkEntry(top, width=200, font=("Helvetica", 12))
        quantity_entry.pack(pady=5)

        def save_inventory():
            name = name_entry.get()
            quantity = quantity_entry.get()
            if action == "add":
                self.modify_inventory(name, quantity)
            elif action == "update":
                self.modify_inventory(name, quantity)
            elif action == "remove":
                self.modify_inventory(name, remove=True)
            top.destroy()

        ctk.CTkButton(top, text="Submit", command=save_inventory, width=200, fg_color="#4CAF50", text_color="white",
                      font=("Helvetica", 12)).pack(pady=20)

    def show_all_inventory(self):
        top = ctk.CTkToplevel(self.display)
        top.title("All Inventory")
        top.geometry("700x500")
        top.grab_set()  # Make window modal

        ctk.CTkLabel(top, text="Inventory List", font=("Helvetica", 18, 'bold'), text_color="#4CAF50").pack(pady=10)

        # Search and filter area
        search_frame = ctk.CTkFrame(top, fg_color="transparent")
        search_frame.pack(pady=5)

        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame, textvariable=search_var, placeholder_text="🔍 Search Inventory", width=300
        )
        search_entry.pack(side="left", padx=5)

        # Add export button
        ctk.CTkButton(search_frame, text="Export CSV", 
                     command=lambda: self.export_data(inventory_sheet, "inventory"),
                     width=100, height=30, 
                     fg_color="#009688", text_color="white").pack(side="right", padx=5)

        # Inventory display with headers
        header_frame = ctk.CTkFrame(top, fg_color="#333333", height=40)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(header_frame, text="Material Name", font=("Helvetica", 12, "bold"),
                    text_color="#ffffff", width=300).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Quantity", font=("Helvetica", 12, "bold"),
                    text_color="#ffffff", width=100).pack(side="right", padx=10)

        # Scrollable inventory list
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
                        if len(row) >= 2:  # Make sure row has at least 2 elements
                            name, qty = row[0], row[1]
                            if search_text in name.lower():
                                row_color = "#04090a" if i % 2 == 0 else "#0a0f10"
                                item_frame = ctk.CTkFrame(frame, fg_color=row_color, corner_radius=5, height=40)
                                item_frame.pack(fill="x", pady=2, padx=5)
                                item_frame.pack_propagate(False)

                                # Left side with name
                                name_label = ctk.CTkLabel(item_frame, text=name, font=("Helvetica", 12),
                                                      text_color="#ffffff", width=300, anchor="w")
                                name_label.pack(side="left", padx=(20, 0))

                                # Right side with buttons and quantity
                                right_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                                right_frame.pack(side="right", padx=(0, 20))

                                # Update button
                                update_btn = ctk.CTkButton(right_frame, text="Update", width=70, height=25,
                                                       fg_color="#2196F3", command=lambda i=i: self.update_material_inline(i+1))
                                update_btn.pack(side="left", padx=5)

                                # Remove button
                                remove_btn = ctk.CTkButton(right_frame, text="Remove", width=70, height=25,
                                                       fg_color="#F44336", command=lambda i=i: self.remove_material_inline(i+1))
                                remove_btn.pack(side="left", padx=5)

                                # Quantity
                                qty_label = ctk.CTkLabel(right_frame, text=qty, font=("Helvetica", 12),
                                                     text_color="#ffffff", width=50)
                                qty_label.pack(side="left", padx=5)

                                # Row index for edit reference
                                item_frame.rowindex = i + 1  # Sheet rows are 1-indexed
            except Exception as e:
                ctk.CTkLabel(frame, text=f"Error: {e}", font=("Helvetica", 12), text_color="#888").pack(pady=10)

        update_inventory()

    def export_data(self, sheet, filename_prefix):

        import csv
        from datetime import datetime
        from tkinter import filedialog

        if not sheet:
            show_error("Error", "Sheet not available")
            return

        try:
            # Get data
            data = sheet.get_all_values()

            # Ask for save location
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"{filename_prefix}_{timestamp}.csv"

            file_path = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                initialfile=default_filename
            )

            if not file_path:
                return  # User cancelled

            # Write to CSV
            with open(file_path, 'w', newline='') as file:
                writer = csv.writer(file)
                for row in data:
                    writer.writerow(row)

            show_info("Success", f"Data exported to {file_path}")

        except Exception as e:
            show_error("Error", f"Export failed: {str(e)}")

    def view_user_requests(self):
        """View all user material requests"""
        # Ensure we can access the user assignments sheet
        try:
            user_assignments_sheet = None
            # Get sheets client
            creds = None

            if 'GOOGLE_CREDENTIALS' in os.environ and os.environ['GOOGLE_CREDENTIALS'].strip():
                credentials_dict = json.loads(os.environ['GOOGLE_CREDENTIALS'])
                creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
            elif os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)

            if not creds:
                show_error("Error", "No Google credentials available")
                return

            client = gspread.authorize(creds)

            # Try to open the user assignments worksheet
            try:
                sheet = client.open_by_key(config.get_credentials_sheet_id())
                try:
                    user_assignments_sheet = sheet.worksheet("user_assignments")
                except gspread.exceptions.WorksheetNotFound:
                    # Create it if it doesn't exist
                    user_assignments_sheet = sheet.add_worksheet(title="user_assignments", rows=100, cols=20)
                    user_assignments_sheet.append_row(["Email", "Material", "Quantity", "Date", "Notes"])
            except Exception as e:
                show_error("Error", f"Could not access user assignments: {str(e)}")
                return

            # Create the requests window
            top = ctk.CTkToplevel(self.display)
            top.title("User Material Requests")
            top.geometry("800x600")
            top.grab_set()

            ctk.CTkLabel(top, text="User Material Requests", font=("Helvetica", 18, 'bold'), 
                        text_color="#4CAF50").pack(pady=10)

            # Filter controls
            filter_frame = ctk.CTkFrame(top, fg_color="transparent")
            filter_frame.pack(fill="x", padx=20, pady=5)

            # Email filter
            email_var = ctk.StringVar()
            ctk.CTkLabel(filter_frame, text="Filter by Email:", 
                       font=("Helvetica", 12)).pack(side="left", padx=(0, 5))
            email_entry = ctk.CTkEntry(filter_frame, textvariable=email_var, width=200)
            email_entry.pack(side="left", padx=5)

            # Date filter
            date_var = ctk.StringVar()
            ctk.CTkLabel(filter_frame, text="Date:", 
                       font=("Helvetica", 12)).pack(side="left", padx=(10, 5))
            date_entry = ctk.CTkEntry(filter_frame, textvariable=date_var, width=100)
            date_entry.pack(side="left", padx=5)

            # Export button
            ctk.CTkButton(filter_frame, text="Export CSV", 
                         command=lambda: self.export_data(user_assignments_sheet, "requests"),
                         width=100, height=30, 
                         fg_color="#009688", text_color="white").pack(side="right", padx=5)

            # Table header
            header_frame = ctk.CTkFrame(top, fg_color="#333333", height=40)
            header_frame.pack(fill="x", padx=20, pady=(10, 0))

            ctk.CTkLabel(header_frame, text="Email", font=("Helvetica", 12, "bold"),
                        text_color="#ffffff", width=200).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Material", font=("Helvetica", 12, "bold"),
                        text_color="#ffffff", width=150).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Quantity", font=("Helvetica", 12, "bold"),
                        text_color="#ffffff", width=80).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Date", font=("Helvetica", 12, "bold"),
                        text_color="#ffffff", width=100).pack(side="left", padx=5)
            ctk.CTkLabel(header_frame, text="Notes", font=("Helvetica", 12, "bold"),
                        text_color="#ffffff", width=150).pack(side="left", padx=5)

            # Scrollable frame for requests
            frame = ctk.CTkScrollableFrame(top, fg_color="#16191a")
            frame.pack(fill="both", expand=True, padx=20, pady=10)

            def update_requests():
                for widget in frame.winfo_children():
                    widget.destroy()

                email_filter = email_var.get().lower()
                date_filter = date_var.get()

                try:
                    rows = user_assignments_sheet.get_all_values()

                    if len(rows) <= 1:  # Only header or empty
                        ctk.CTkLabel(frame, text="No requests found", font=("Helvetica", 12),
                                   text_color="#888888").pack(pady=20)
                        return

                    # Skip header if it exists
                    if rows[0][0].lower() == "email":
                        rows = rows[1:]

                    # Display filtered rows
                    for i, row in enumerate(rows):
                        # Ensure row has enough elements
                        if len(row) < 3:
                            continue

                        email = row[0] if len(row) > 0 else ""
                        material = row[1] if len(row) > 1 else ""
                        quantity = row[2] if len(row) > 2 else ""
                        date = row[3] if len(row) > 3 else ""
                        notes = row[4] if len(row) > 4 else ""

                        # Apply filters
                        if email_filter and email_filter not in email.lower():
                            continue

                        if date_filter and date_filter not in date:
                            continue

                        # Create row frame
                        row_color = "#04090a" if i % 2 == 0 else "#0a0f10"
                        row_frame = ctk.CTkFrame(frame, fg_color=row_color, corner_radius=5, height=40)
                        row_frame.pack(fill="x", pady=2, padx=5)
                        row_frame.pack_propagate(False)

                        # Row data
                        ctk.CTkLabel(row_frame, text=email, font=("Helvetica", 12),
                                   text_color="#ffffff", width=200).pack(side="left", padx=5)
                        ctk.CTkLabel(row_frame, text=material, font=("Helvetica", 12),
                                   text_color="#ffffff", width=150).pack(side="left", padx=5)
                        ctk.CTkLabel(row_frame, text=quantity, font=("Helvetica", 12),
                                   text_color="#ffffff", width=80).pack(side="left", padx=5)
                        ctk.CTkLabel(row_frame, text=date, font=("Helvetica", 12),
                                   text_color="#ffffff", width=100).pack(side="left", padx=5)
                        ctk.CTkLabel(row_frame, text=notes, font=("Helvetica", 12),
                                   text_color="#ffffff", width=150).pack(side="left", padx=5)

                except Exception as e:
                    ctk.CTkLabel(frame, text=f"Error: {str(e)}", font=("Helvetica", 12),
                               text_color="#F44336").pack(pady=20)

            # Update on filter change
            email_var.trace_add("write", lambda *args: update_requests())
            date_var.trace_add("write", lambda *args: update_requests())

            # Load initial data
            update_requests()

        except Exception as e:
            show_error("Error", f"Could not load user requests: {str(e)}")

    def process_requests(self):
        show_info("Feature Coming Soon", "This feature will be available in the next update!")

    def update_material_inline(self, row_index):
        """Update material directly from the list"""
        try:
            row = inventory_sheet.row_values(row_index)
            name = row[0]
            qty = row[1]

            update_window = ctk.CTkToplevel(self.display)
            update_window.title("Update Material")
            update_window.geometry("400x200")

            ctk.CTkLabel(update_window, text=f"Update: {name}", font=("Helvetica", 14, "bold")).pack(pady=(20,10))

            qty_frame = ctk.CTkFrame(update_window, fg_color="transparent")
            qty_frame.pack(pady=10)

            ctk.CTkLabel(qty_frame, text="Quantity:").pack(side="left", padx=(0,10))
            qty_entry = ctk.CTkEntry(qty_frame)
            qty_entry.pack(side="left")
            qty_entry.insert(0, qty)

            def save():
                new_qty = qty_entry.get()
                inventory_sheet.update_cell(row_index, 2, new_qty)
                show_info("Success", "Material updated successfully!")
                update_window.destroy()
                # Refresh the inventory view if open
                for widget in self.display.winfo_children():
                    if isinstance(widget, ctk.CTkToplevel) and widget.title() == "All Inventory":
                        widget.destroy()
                        self.show_all_inventory()

            ctk.CTkButton(update_window, text="Save", command=save, fg_color="#4CAF50").pack(pady=20)

        except Exception as e:
            show_error("Error", f"Failed to update material: {str(e)}")

    def remove_material_inline(self, row_index):
        """Remove material directly from the list"""
        try:
            name = inventory_sheet.cell(row_index, 1).value
            if askyesno("Confirm Delete", f"Are you sure you want to delete {name}?"):
                inventory_sheet.delete_rows(row_index)
                show_info("Success", "Material removed successfully!")
                # Close current inventory window and open a new one
                for widget in self.display.winfo_children():
                    if isinstance(widget, ctk.CTkToplevel) and widget.title() == "All Inventory":
                        widget.destroy()
                        self.show_all_inventory()
                        return
        except Exception as e:
            show_error("Error", f"Failed to remove material: {str(e)}")

    def test_connection(self):
        """Test the connection to Google Sheets"""
        try:
            # Try to get credentials
            creds = None
            if 'GOOGLE_CREDENTIALS' in os.environ and os.environ['GOOGLE_CREDENTIALS'].strip():
                credentials_dict = json.loads(os.environ['GOOGLE_CREDENTIALS'])
                creds = Credentials.from_service_account_info(credentials_dict, scopes=scopes)
            elif os.path.exists('credentials.json'):
                creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)

            if not creds:
                show_error("Connection Failed", "No Google credentials available")
                return

            # Try to connect
            client = gspread.authorize(creds)

            # Test access to sheets
            inventory_sheet = client.open_by_key(config.get_inventory_sheet_id()).sheet1
            credentials_sheet = client.open_by_key(config.get_credentials_sheet_id()).sheet1

            # Try to read data
            inventory_sheet.cell(1, 1)
            credentials_sheet.cell(1, 1)

            # All tests passed
            show_info("Connection Successful", 
                              "Successfully connected to Google Sheets!\n\n" + 
                              f"Inventory Sheet ID: {config.get_inventory_sheet_id()}\n" +
                              f"Credentials Sheet ID: {config.get_credentials_sheet_id()}")

        except Exception as e:
            show_error("Connection Failed", f"Error: {str(e)}")

    def show_all_users(self):
        """Show all users in the system"""
        top = ctk.CTkToplevel(self.display)
        top.title("All Users")
        top.geometry("700x500")
        top.grab_set()

        ctk.CTkLabel(top, text="User List", font=("Helvetica", 18, 'bold'), 
                    text_color="#4CAF50").pack(pady=10)

        # Search and filter area
        search_frame = ctk.CTkFrame(top, fg_color="transparent")
        search_frame.pack(pady=5)

        search_var = ctk.StringVar()
        search_entry = ctk.CTkEntry(
            search_frame, textvariable=search_var, placeholder_text="🔍 Search Users", width=300
        )
        search_entry.pack(side="left", padx=5)

        # Add export button
        ctk.CTkButton(search_frame, text="Export CSV", 
                     command=lambda: self.export_data(credentials_sheet, "users"),
                     width=100, height=30, 
                     fg_color="#009688", text_color="white").pack(side="right", padx=5)

        # Users display with headers
        header_frame = ctk.CTkFrame(top, fg_color="#333333", height=40)
        header_frame.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(header_frame, text="Role", font=("Helvetica", 12, "bold"),
                    text_color="#ffffff", width=100).pack(side="left", padx=10)
        ctk.CTkLabel(header_frame, text="Email", font=("Helvetica", 12, "bold"),
                    text_color="#ffffff", width=300).pack(side="left", padx=10)

        # Scrollable users list
        frame = ctk.CTkScrollableFrame(top, fg_color="#16191a")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        def update_users():
            for widget in frame.winfo_children():
                widget.destroy()

            search_text = search_var.get().lower()
            try:
                rows = credentials_sheet.get_all_values()
                if not rows:
                    ctk.CTkLabel(frame, text="No users found", font=("Helvetica", 12), 
                               text_color="#888").pack(pady=10)
                else:
                    # Skip header row if it exists
                    if rows[0][0].lower() == "role":
                        rows = rows[1:]

                    for i, row in enumerate(rows):
                        if len(row) >= 2:  # Make sure row has role and email
                            role, email = row[0], row[1]
                            if search_text in email.lower() or search_text in role.lower():
                                row_color = "#04090a" if i % 2 == 0 else "#0a0f10"
                                item_frame = ctk.CTkFrame(frame, fg_color=row_color, corner_radius=5)
                                item_frame.pack(fill="x", pady=5, padx=10)

                                # Role label
                                role_label = ctk.CTkLabel(item_frame, text=role.capitalize(), 
                                                      font=("Helvetica", 12),
                                                      text_color="#ffffff", width=100)
                                role_label.pack(side="left", padx=10)

                                # Email label
                                email_label = ctk.CTkLabel(item_frame, text=email,
                                                       font=("Helvetica", 12),
                                                       text_color="#ffffff", width=300)
                                email_label.pack(side="left", padx=10)
            except Exception as e:
                ctk.CTkLabel(frame, text=f"Error: {e}", font=("Helvetica", 12), 
                           text_color="#888").pack(pady=10)

        search_entry.bind("<KeyRelease>", lambda event: update_users())
        update_users()