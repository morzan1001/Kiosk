from customtkinter import *

from src.localization.translator import get_translations

class AddBarcodeFrame(CTkToplevel):
    def __init__(self, parent, confirm_function, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Initialize a variable to store the barcode
        self.barcode: str = ""
        self.confirm_function = confirm_function
        self.translations = get_translations()

        # Bind the event for handling barcode input (keypress events)
        self.bind("<Key>", self.on_barcode_scan)

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        self.parent = parent
        # Calculate position to center the toplevel
        toplevel_width = 600
        toplevel_height = 300
        pos_x = (screen_width // 2) - (toplevel_width // 2)
        pos_y = (screen_height // 2) - (toplevel_height // 2)

        # Set the geometry for the toplevel
        self.geometry(f"{toplevel_width}x{toplevel_height}+{pos_x}+{pos_y}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.overrideredirect(True)

        # Configure the main frame
        main_frame = CTkFrame(self, fg_color="white", corner_radius=10)
        main_frame.grid(sticky="nsew")
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure((0, 1, 2), weight=1)

        # Head up label
        barcode_label = CTkLabel(
            main_frame,
            text=self.translations["items"]["barcode"],
            font=("Inter", 24, "bold"),
            text_color="black",
            fg_color="white",
        )
        barcode_label.grid(
            row=0, column=0, columnspan=2, pady=5, sticky="w", padx=(40, 0)
        )
        # Confirmation text label
        self.barcode_entry = CTkEntry(
            main_frame,
            font=("Inter", 18, "bold"),
            width=520,
            height=50,
            text_color="black",
            fg_color="#EFEFEF",
            border_color="#656565",
            border_width=2,
        )
        self.barcode_entry.grid(row=1, column=0, columnspan=2, pady=5)

        # Cancel button
        cancel_button = CTkButton(
            main_frame,
            text=self.translations["buttons"]["cancel_button"],
            width=220,
            height=50,
            font=("Inter", 18, "bold"),
            fg_color="#FFFFFF",
            hover_color="#DDDDDD",
            text_color="green",
            border_width=2,
            border_color="green",
            command=self.cancel_delete,
        )
        cancel_button.grid(row=2, column=0, padx=10, pady=20)

        # Confirm button
        confirm_button = CTkButton(
            main_frame,
            text=self.translations["items"]["add_barcode"],
            width=220,
            height=50,
            font=("Inter", 18, "bold"),
            fg_color="#129F07",
            hover_color="#15aF07",
            command=self.confirm_barcode,
        )
        confirm_button.grid(row=2, column=1, padx=10, pady=20)
        
    def on_barcode_scan(self, event):
        # Check if Enter key is pressed, which typically signals the end of a barcode scan
        if event.keysym == "Return":
            # Call the function to process the scanned barcode
            self.process_barcode(self.barcode)
            # Reset the barcode value after processing
            self.barcode = ""
        else:
            # Append the scanned character to the barcode string
            self.barcode += event.char

    def process_barcode(self, barcode_value: str):
        # Function to handle the barcode value
        self.barcode_entry.delete(0, 'end')  # Clear the previous entry to avoid appending
        self.barcode_entry.insert(0, str(barcode_value))

    def confirm_barcode(self):
        self.confirm_function()
        self.grab_release()
        self.destroy()

    def get(self):
        return self.barcode_entry.get()

    def cancel_delete(self):
        # Allow interaction with the main window
        self.parent.grab_release()
        self.destroy()