from customtkinter import CTkToplevel, CTkFrame, CTkLabel, CTkButton
from PIL import Image, ImageTk

from src.localization.translator import get_translations


class DeleteConfirmation(CTkToplevel):
    def __init__(self, parent, confirm_function, to_delete, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)

        self.confirm_function = confirm_function
        self.translations = get_translations()

        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # Calculate position to center the toplevel
        toplevel_width = 600
        toplevel_height = 300
        pos_x = (screen_width // 2) - (toplevel_width // 2)
        pos_y = (screen_height // 2) - (toplevel_height // 2)

        # Set the geometry for the toplevel
        self.geometry(f"{toplevel_width}x{toplevel_height}+{pos_x}+{pos_y}")

        self.overrideredirect(True)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Configure the main frame
        main_frame = CTkFrame(self, fg_color="white", corner_radius=10)
        main_frame.grid(sticky="nsew")
        main_frame.grid_columnconfigure((0, 1), weight=1)
        main_frame.grid_rowconfigure((0, 1, 2, 3), weight=1)

        # Load the delete icon
        delete_image = Image.open("src/images/delete.png")  # Update path if needed
        delete_image = delete_image.resize((70, 80), Image.Resampling.LANCZOS)
        self.delete_image = ImageTk.PhotoImage(delete_image)

        # Delete icon label
        icon_label = CTkLabel(
            main_frame, text="", image=self.delete_image, fg_color="white"
        )
        icon_label.grid(row=0, column=0, columnspan=2, pady=10)

        # Head up label
        heads_up_label = CTkLabel(
            main_frame,
            text=self.translations["general"]["heads_up"],
            font=("Inter", 24, "bold"),
            text_color="black",
            fg_color="white",
        )
        heads_up_label.grid(row=1, column=0, columnspan=2, pady=5)

        # Confirmation text label
        confirmation_text = CTkLabel(
            main_frame,
            text=self.translations["admin"]["confirmation_text"].format(to_delete=to_delete),
            font=("Inter", 24),
            text_color="black",
            fg_color="white",
        )
        confirmation_text.grid(row=2, column=0, columnspan=2, pady=5)

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
        cancel_button.grid(row=3, column=0, padx=10, pady=20)

        # Confirm button
        confirm_button = CTkButton(
            main_frame,
            text=self.translations["buttons"]["confirm_button"],
            width=220,
            height=50,
            font=("Inter", 18, "bold"),
            fg_color="#129F07",
            hover_color="#15aF07",
            command=self.confirm_delete_func,
        )
        confirm_button.grid(row=3, column=1, padx=10, pady=20)

    def cancel_delete(self):
        self.destroy()

    def confirm_delete_func(self):
        self.confirm_function()
        self.destroy()