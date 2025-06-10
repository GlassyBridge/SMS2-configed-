
import customtkinter as ctk

class CustomMessagebox(ctk.CTkToplevel):
    def __init__(self, title, message, type="info"):
        super().__init__()
        
        self.title(title)
        self.geometry("400x200")
        self.resizable(False, False)
        self.grab_set()
        
        # Configure colors based on message type
        colors = {
            "info": "#2196F3",
            "error": "#F44336",
            "warning": "#FF9800",
            "question": "#4CAF50"
        }
        
        color = colors.get(type, colors["info"])
        
        # Message
        message_frame = ctk.CTkFrame(self, fg_color="transparent")
        message_frame.pack(expand=True, fill="both", padx=20, pady=(20,10))
        
        ctk.CTkLabel(message_frame, text=message, font=("Helvetica", 14),
                    wraplength=350).pack(expand=True)
        
        # Buttons
        button_frame = ctk.CTkFrame(self, fg_color="transparent")
        button_frame.pack(fill="x", padx=20, pady=(0,20))
        
        if type == "question":
            self.result = False
            
            def on_yes():
                self.result = True
                self.destroy()
                
            def on_no():
                self.result = False
                self.destroy()
            
            ctk.CTkButton(button_frame, text="Yes", command=on_yes,
                         fg_color=color, width=100).pack(side="left", padx=10)
            ctk.CTkButton(button_frame, text="No", command=on_no,
                         fg_color="#555555", width=100).pack(side="right", padx=10)
        else:
            ctk.CTkButton(button_frame, text="OK", command=self.destroy,
                         fg_color=color, width=100).pack(pady=10)

def show_info(title, message):
    dialog = CustomMessagebox(title, message, "info")
    dialog.wait_window()

def show_error(title, message):
    dialog = CustomMessagebox(title, message, "error")
    dialog.wait_window()

def show_warning(title, message):
    dialog = CustomMessagebox(title, message, "warning")
    dialog.wait_window()

def askyesno(title, message):
    dialog = CustomMessagebox(title, message, "question")
    dialog.wait_window()
    return dialog.result
