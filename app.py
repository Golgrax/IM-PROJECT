import customtkinter as ctk
from PIL import Image
from db_connector import DBManager

class ProjectorReservationSystem:
    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager

        self.root.title("Projector Reservation System")
        self.root.geometry("1000x600")
        self.root.configure(bg="#800000")
        self.root.resizable(True, True)

        ctk.set_appearance_mode("dark")
        image_path = "./IMAGE/PUP_LOGO.png"
        try:
            self.original_image = Image.open(image_path)
        except FileNotFoundError:
            print(f"Warning: Background image not found at {image_path}. Displaying without image.")
            self.original_image = None

        self.bg_label = ctk.CTkLabel(root, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.after(100, self.update_background)
        self.root.bind("<Configure>", self.on_resize)

        self.create_login_frame()

    def on_resize(self, event):
        if event.width > 1 and event.height > 1:
            self.update_background()

    def update_background(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width > 1 and height > 1 and self.original_image:
            resized_image = self.original_image.resize((width, height), Image.LANCZOS)
            self.bg_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(width, height))
            self.bg_label.configure(image=self.bg_image)
        elif not self.original_image:
            self.bg_label.configure(fg_color="#800000")

    def create_login_frame(self):
        for widget in self.root.winfo_children():
            if widget != self.bg_label:
                widget.destroy()

        self.login_frame = ctk.CTkFrame(self.root,
                                        fg_color="maroon",
                                        border_width=2,
                                        corner_radius=10,
                                        width=350,
                                        height=250)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.login_frame,
            text="Projector Reservation System",
            font=("Arial", 16, "bold"),
            text_color="white"
        ).place(relx=0.5, rely=0.15, anchor="center")

        ctk.CTkLabel(self.login_frame,
                     text="Username:",
                     text_color="white",
                     font=("Arial", 12)
                     ).place(x=30, y=60)
        self.username_entry = ctk.CTkEntry(self.login_frame, font=("Arial", 12), width=200)
        self.username_entry.place(x=120, y=60)

        ctk.CTkLabel(self.login_frame,
                     text="Password:",
                     text_color="white",
                     font=("Arial", 12)
                     ).place(x=30, y=100)
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", font=("Arial", 12), width=200)
        self.password_entry.place(x=120, y=100)

        self.error_label = ctk.CTkLabel(self.login_frame, text="", text_color="red", font=("Arial", 10))
        self.error_label.place(relx=0.5, rely=0.85, anchor="center")

        login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            font=("Arial", 12, "bold"),
            fg_color="yellow",
            text_color="black",
            command=self.login
        )
        login_button.place(relx=0.5, rely=0.75, anchor="center")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin":
            self.login_frame.destroy()
            self.show_dashboard()
        else:
            self.error_label.configure(text="Invalid credentials!")

    def show_dashboard(self):
        self.dashboard = ctk.CTkFrame(self.root, fg_color="white", border_width=2, corner_radius=10)
        self.dashboard.place(relx=0.5, rely=0.5, anchor="center")

        self.welcome_label = ctk.CTkLabel(
            self.dashboard,
            text="Welcome to PRS (Projector Reservation System), Admin!",
            font=("Arial", 16, "bold"),
            text_color="black"
        )
        self.welcome_label.pack(padx=20, pady=40)

        self.root.after(2000, self.show_main_interface)

    def show_main_interface(self):
        if self.dashboard:
            self.dashboard.destroy()
            self.dashboard = None

        self.main_frame = ctk.CTkFrame(self.root, fg_color="white", corner_radius=15)
        self.main_frame.pack(expand=True, fill="both", padx=30, pady=30)

        self.create_date_dropdown()
        self.create_table()
        self.create_buttons()

    def create_date_dropdown(self):
        date_frame = ctk.CTkFrame(self.main_frame, fg_color="white")
        date_frame.pack(fill="x", padx=20, pady=(10, 0))

        ctk.CTkLabel(
            date_frame,
            text="Select Date:",
            font=("Arial", 14, "bold"),
            text_color="black"
        ).pack(side="right", padx=(0, 10))

        date_list = ["May 7, 2025", "May 8, 2025", "May 9, 2025", "May 10, 2025", "May 11, 2025"]
        self.date_dropdown = ctk.CTkOptionMenu(date_frame, values=date_list, width=150)
        self.date_dropdown.pack(side="right", padx=(0, 20))

    def create_table(self):
        headers = ["PR. NO.", "SERIAL NO.", "TIME", "PROFESSOR", "SECTION", "REPRESENTATIVE", "STATUS"]

        self.table_frame = ctk.CTkFrame(self.main_frame, fg_color="white", border_width=2, corner_radius=10)
        self.table_frame.pack(padx=20, pady=20, fill="x")

        for widget in self.table_frame.winfo_children():
            widget.destroy()

        for col_index, header in enumerate(headers):
            ctk.CTkLabel(
                self.table_frame,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="black",
                fg_color="#e6e6e6",
                width=120,
                height=30
            ).grid(row=0, column=col_index, padx=1, pady=1, sticky="nsew")

        for i in range(5):
            for col in range(len(headers)):
                ctk.CTkLabel(
                    self.table_frame,
                    text="",
                    font=("Arial", 13),
                    text_color="black",
                    width=120,
                    height=30,
                    fg_color="white"
                ).grid(row=i + 1, column=col, padx=1, pady=1, sticky="nsew")


        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)

    def populate_table_with_data(self, data_rows):
        """Populates the main interface table with data from the database."""
        for widget in self.table_frame.winfo_children():
            if widget.grid_info()['row'] > 0:
                widget.destroy()

        headers = ["PR. NO.", "SERIAL NO.", "TIME", "PROFESSOR", "SECTION", "REPRESENTATIVE", "STATUS"]
        for row_index, row_data in enumerate(data_rows, start=1):
            for col_index, cell in enumerate(row_data):
                ctk.CTkLabel(
                    self.table_frame,
                    text=str(cell),
                    font=("Arial", 13),
                    text_color="black",
                    width=120,
                    height=30,
                    fg_color="white"
                ).grid(row=row_index, column=col_index, padx=1, pady=1, sticky="nsew")

        num_data_rows = len(data_rows)
        if num_data_rows < 5:
            for i in range(num_data_rows, 5):
                for col in range(len(headers)):
                    ctk.CTkLabel(
                        self.table_frame,
                        text="",
                        font=("Arial", 13),
                        text_color="black",
                        width=120,
                        height=30,
                        fg_color="white"
                    ).grid(row=i + 1, column=col, padx=1, pady=1, sticky="nsew")


    def create_buttons(self):
        button_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        button_frame.pack(pady=10)

        button_style = {
            "font": ("Arial", 13, "bold"),
            "fg_color": "#800000",
            "hover_color": "#990000",
            "text_color": "white",
            "corner_radius": 15,
            "width": 140
        }

        ctk.CTkButton(
            button_frame,
            text="ADD",
            command=self.open_add_window,
            **button_style
        ).grid(row=0, column=0, padx=10, pady=5)

        ctk.CTkButton(
            button_frame,
            text="RESERVATION",
            command=self.open_reservation_window,
            **button_style
        ).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkButton(
            button_frame,
            text="CANCELLATION",
            command=self.open_cancellation_window,
            **button_style
        ).grid(row=0, column=2, padx=10, pady=5)

        ctk.CTkButton(
            button_frame,
            text="VIEW",
            command=self.open_view_window,
            **button_style
        ).grid(row=0, column=3, padx=10, pady=5)

    def open_add_window(self):
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("Add Projector Reservation")
        add_window.geometry("400x300")
        add_window.configure(fg_color="white")
        add_window.grab_set()

        ctk.CTkLabel(
            add_window,
            text="Add New Projector",
            font=("Arial", 16, "bold"),
            text_color="black"
        ).pack(pady=10)

        self.add_entries = {}
        fields = [
            ("PR. NO.",  "pr_no"),
            ("Serial No.", "serial_no"),
        ]

        for label_text, key in fields:
            ctk.CTkLabel(add_window, text=label_text, text_color="black", anchor="w", font=("Arial", 12)
                         ).pack(pady=(10, 0), padx=20, anchor="w")
            entry = ctk.CTkEntry(add_window, width=300)
            entry.pack(padx=20)
            self.add_entries[key] = entry

        ctk.CTkButton(
            add_window,
            text="Save",
            fg_color="#800000",
            text_color="white",
            command=lambda: self.save_new_entry(add_window)
        ).pack(pady=20)

    def save_new_entry(self, add_window):
        pr_no = self.add_entries["pr_no"].get().strip()
        serial_no = self.add_entries["serial_no"].get().strip()

        if not pr_no or not serial_no:
            print("PR. NO. and Serial No. are required.")
            ctk.CTkMessagebox.showerror("Input Error", "PR. NO. and Serial No. are required.")
            return

        if self.db.add_projector_entry(pr_no, serial_no):
            print(f"New projector {pr_no} added successfully.")
            ctk.CTkMessagebox.showinfo("Success", f"Projector {pr_no} added successfully.")
            add_window.destroy()
            self.open_view_window()
        else:
            print(f"Failed to add projector {pr_no}.")
            ctk.CTkMessagebox.showerror("Database Error", "Failed to add projector. Check database connection or if PR. NO. already exists.")

    def open_reservation_window(self):
        res_window = ctk.CTkToplevel(self.root)
        res_window.title("Make a Reservation")
        res_window.geometry("400x450")
        res_window.configure(fg_color="white")
        res_window.grab_set()

        ctk.CTkLabel(
            res_window,
            text="Make a Reservation",
            font=("Arial", 16, "bold"),
            text_color="black"
        ).pack(pady=10)

        available_list = self.db.get_available_projector_nos()
        if not available_list:
            ctk.CTkLabel(res_window, text="No available projectors found.", text_color="red").pack(pady=10)
            return

        ctk.CTkLabel(res_window, text="Select Projector (PR. NO.):", text_color="black", anchor="w", font=("Arial", 12)
                     ).pack(pady=(10, 0), padx=20, anchor="w")
        self.res_pr_dropdown = ctk.CTkOptionMenu(res_window, values=available_list, width=200)
        self.res_pr_dropdown.pack(pady=(5, 15))

        self.res_entries = {}
        fields = [
            ("Time", "time_slot"),
            ("Professor", "professor"),
            ("Section", "section"),
            ("Representative", "representative")
        ]
        for label_text, key in fields:
            ctk.CTkLabel(res_window, text=label_text, text_color="black", anchor="w", font=("Arial", 12)
                         ).pack(pady=(10, 0), padx=20, anchor="w")
            entry = ctk.CTkEntry(res_window, width=300)
            entry.pack(padx=20)
            self.res_entries[key] = entry

        ctk.CTkButton(
            res_window,
            text="Submit Reservation",
            fg_color="#800000",
            text_color="white",
            command=lambda: self.submit_reservation(res_window)
        ).pack(pady=20)

    def submit_reservation(self, res_window):
        pr_no = self.res_pr_dropdown.get()
        time_slot = self.res_entries["time_slot"].get().strip()
        professor = self.res_entries["professor"].get().strip()
        section = self.res_entries["section"].get().strip()
        representative = self.res_entries["representative"].get().strip()

        if not all([pr_no, time_slot, professor, section, representative]):
            print("All fields are required for reservation.")
            ctk.CTkMessagebox.showerror("Input Error", "All fields are required for reservation.")
            return

        if self.db.update_reservation_details(pr_no, time_slot, professor, section, representative):
            print(f"Projector {pr_no} reserved successfully.")
            ctk.CTkMessagebox.showinfo("Success", f"Projector {pr_no} reserved successfully.")
            res_window.destroy()
            self.open_view_window()
        else:
            print(f"Failed to reserve projector {pr_no}.")
            ctk.CTkMessagebox.showerror("Database Error", "Failed to reserve projector.")

    def open_cancellation_window(self):
        cancel_window = ctk.CTkToplevel(self.root)
        cancel_window.title("Cancel Reservation")
        cancel_window.geometry("350x250")
        cancel_window.configure(fg_color="white")
        cancel_window.grab_set()

        ctk.CTkLabel(
            cancel_window,
            text="Cancel a Reservation",
            font=("Arial", 16, "bold"),
            text_color="black"
        ).pack(pady=10)

        reserved_list = self.db.get_reserved_projector_nos()
        if not reserved_list:
            ctk.CTkLabel(cancel_window, text="No reserved projectors found.", text_color="red").pack(pady=10)
            return

        ctk.CTkLabel(cancel_window, text="Select Projector (PR. NO.):", text_color="black", anchor="w", font=("Arial", 12)
                     ).pack(pady=(10, 0), padx=20, anchor="w")
        self.cancel_pr_dropdown = ctk.CTkOptionMenu(cancel_window, values=reserved_list, width=200)
        self.cancel_pr_dropdown.pack(pady=(5, 15))

        ctk.CTkButton(
            cancel_window,
            text="Cancel Reservation",
            fg_color="#800000",
            text_color="white",
            command=lambda: self.submit_cancellation(cancel_window)
        ).pack(pady=20)

    def submit_cancellation(self, cancel_window):
        pr_no = self.cancel_pr_dropdown.get()
        if not pr_no:
            print("Please select a projector to cancel.")
            ctk.CTkMessagebox.showerror("Input Error", "Please select a projector to cancel.")
            return

        if self.db.cancel_projector_reservation(pr_no):
            print(f"Reservation for {pr_no} has been cancelled.")
            ctk.CTkMessagebox.showinfo("Success", f"Reservation for {pr_no} has been cancelled.")
            cancel_window.destroy()
            self.open_view_window()
        else:
            print(f"Failed to cancel reservation for {pr_no}.")
            ctk.CTkMessagebox.showerror("Database Error", "Failed to cancel reservation.")

    def open_view_window(self):

        all_reservations = self.db.get_all_reservations()
        if all_reservations:
            self.populate_table_with_data(all_reservations)
            print("Main table refreshed with current data.")
        else:
            self.populate_table_with_data([])
            print("No reservations found to display.")