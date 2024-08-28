from customtkinter import *
from PIL import Image, ImageTk

class HeadingFrame(CTkFrame):
    def __init__(self, parent, heading_text, back_button_function, delete_button_function=None, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        # Configure the frame
        self.configure(fg_color="transparent")
        self.grid(row=0, column=0, sticky="new", padx=50, pady=20)
        self.grid_columnconfigure((0, 1, 2), weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Load the back button image
        back_image = Image.open("src/images/back.png")
        back_image = back_image.resize((42, 32), Image.Resampling.LANCZOS)
        self.back_image = ImageTk.PhotoImage(back_image)

        # Create the back button
        self.back_button = CTkButton(
            self, 
            text="", 
            image=self.back_image, 
            width=42, 
            height=32, 
            fg_color="transparent", 
            hover=False, 
            command=back_button_function
        )
        self.back_button.grid(row=0, column=0, sticky="w")

        # Create the heading label
        self.heading_label = CTkLabel(
            self, 
            text=heading_text, 
            font=("Inter", 24, "bold"), 
            text_color="white"
        )
        self.heading_label.grid(row=0, column=1)

        if delete_button_function:    
            # Load the delete button image
            delete_image = Image.open("src/images/delete.png")
            delete_image = delete_image.resize((30, 35), Image.Resampling.LANCZOS)
            self.delete_image = ImageTk.PhotoImage(delete_image)
                
            # Create the delete button
            self.delete_button = CTkButton(
                self, 
                text="", 
                image=self.delete_image, 
                width=30, 
                height=35, 
                fg_color="transparent", 
                hover=False, 
                command=delete_button_function
            )
            self.delete_button.grid(row=0, column=3, sticky="w")