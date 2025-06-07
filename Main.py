import customtkinter as ctk
from PIL import Image
#import mysql.connector
#from mysql.connector import Error pangabang para sa pag combine ng database

class ProjectorReservationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Projector Reservation System")
        self.root.geometry("1000x600")
        self.root.configure(bg="#800000")
        self.root.resizable(True, True)

        ctk.set_appearance_mode("dark")

        # Load background image
        image_path = r"C:\Users\Desktop\Downloads\IM PROJECT\IMAGE\PUP_LOGO.png"  # Adjust this path
        self.original_image = Image.open(image_path)
        self.bg_label = ctk.CTkLabel(root, text="")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        self.root.after(100, self.update_background)
        self.root.bind("<Configure>", self.on_resize)

        # Start with login screen
        self.create_login_frame()

    def on_resize(self, event):
        if event.width > 1 and event.height > 1:
            self.update_background()

    def update_background(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width > 1 and height > 1:
            resized_image = self.original_image.resize((width, height), Image.LANCZOS)
            self.bg_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(width, height))
            self.bg_label.configure(image=self.bg_image)

    def create_login_frame(self):
        # Remove any existing widgets except the background
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

        # After 2 seconds, transition to main interface
        self.root.after(2000, self.show_main_interface)

    def show_main_interface(self):
        self.dashboard.destroy()

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

        # Placeholder rows; will be updated when "VIEW" is clicked
        for i in range(10):
            for col in range(len(headers)):
                if col == 0:
                    text = f"P{str(i + 1).zfill(3)}"
                elif col == 6:
                    text = "Available" if i % 2 == 0 else "Not Available"
                else:
                    text = ""
                ctk.CTkLabel(
                    self.table_frame,
                    text=text,
                    font=("Arial", 13),
                    text_color="black",
                    width=120,
                    height=30,
                    fg_color="white"
                ).grid(row=i + 1, column=col, padx=1, pady=1, sticky="nsew")

        for col in range(len(headers)):
            self.table_frame.grid_columnconfigure(col, weight=1)

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

    #  DATABASE CONNECTION HELPER
    
    def get_db_connection(self):
        """
        Adjust host, user, password, database as needed.
        """
        try:
            conn = mysql.connector.connect(
                host="localhost",
                user="root",           # ← your DB user
                password="",           # ← your DB password
                database="reservationprojector"
            )
            return conn
        except OSError as e:
            print(f"Error connecting to database: {e}")
            return None


    #  ADD BUTTON → OPEN FORM TO INSERT A NEW RECORD
   
    def open_add_window(self):
        add_window = ctk.CTkToplevel(self.root)
        add_window.title("Add Projector Reservation")
        add_window.geometry("400x450")
        add_window.configure(fg_color="white")

        ctk.CTkLabel(
            add_window,
            text="Add Projector Reservation",
            font=("Arial", 16, "bold"),
            text_color="black"
        ).pack(pady=10)

        # Fields: PR_NO, SERIAL_NO, TIME, PROFESSOR, SECTION, REPRESENTATIVE
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

        # Save button
        ctk.CTkButton(
            add_window,
            text="Save",
            fg_color="#800000",
            text_color="white",
            command=self.save_new_entry
        ).pack(pady=20)

    def save_new_entry(self):
        data = {key: entry.get().strip() for key, entry in self.add_entries.items()}

        # Basic validation: ensure PR_NO and Serial No. are provided
        if not data["pr_no"] or not data["serial_no"]:
            print("PR_NO and Serial No. are required.")
            return

        conn = self.get_db_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            query = """
                INSERT INTO projector_reservation
                (PR_NO, SERIAL_NO, TIME, PROFESSOR, SECTION, REPRESENTATIVE, STATUS)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data["pr_no"],
                data["serial_no"],
        
            )
            cursor.execute(query, values)
            conn.commit()
            print("New reservation added:", data["pr_no"])
        except OSError as e:
            print(f"Error inserting new entry: {e}")
        finally:
            cursor.close()
            conn.close()


    #  RESERVATION BUTTON → PICK AN AVAILABLE PROJECTOR AND FILL DETAILS
   
    def open_reservation_window(self):
        res_window = ctk.CTkToplevel(self.root)
        res_window.title("Make a Reservation")
        res_window.geometry("400x450")
        res_window.configure(fg_color="white")

        ctk.CTkLabel(
            res_window,
            text="Make a Reservation",
            font=("Arial", 16, "bold"),
            text_color="black"
        ).pack(pady=10)

        # Fetch list of PR_NO for which status = 'Available'
        conn = self.get_db_connection()
        available_list = []
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT PR_NO FROM projector_reservation WHERE STATUS = 'Available'")
                available_list = [row[0] for row in cursor.fetchall()]
            except Error as e:
                print(f"Error fetching available projectors: {e}")
            finally:
                cursor.close()
                conn.close()

        ctk.CTkLabel(res_window, text="Select Projector (PR. NO.):", text_color="black", anchor="w", font=("Arial", 12)
                     ).pack(pady=(10, 0), padx=20, anchor="w")
        self.res_pr_dropdown = ctk.CTkOptionMenu(res_window, values=available_list, width=200)
        self.res_pr_dropdown.pack(pady=(5, 15))

        # Other fields: Time, Professor, Section, Representative
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
            command=self.submit_reservation
        ).pack(pady=20)

    def submit_reservation(self):
        pr_no = self.res_pr_dropdown.get()
        data = {key: entry.get().strip() for key, entry in self.res_entries.items()}

        if not pr_no:
            print("Please select a projector.")
            return
        if not data["time_slot"] or not data["professor"] or not data["section"] or not data["representative"]:
            print("All fields are required.")
            return

        conn = self.get_db_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            query = """
                UPDATE projector_reservation
                SET TIME = %s,
                    PROFESSOR = %s,
                    SECTION = %s,
                    REPRESENTATIVE = %s,
                    STATUS = 'Not Available'
                WHERE PR_NO = %s
            """
            values = (
                data["time_slot"],
                data["professor"],
                data["section"],
                data["representative"],
                pr_no
            )
            cursor.execute(query, values)
            conn.commit()
            print(f"Projector {pr_no} reserved successfully.")
        except OSError as e:
            print(f"Error updating reservation: {e}")
        finally:
            cursor.close()
            conn.close()

    #  CANCELLATION BUTTON → CHOOSE A RESERVED PROJECTOR TO CANCEL
 
    def open_cancellation_window(self):
        cancel_window = ctk.CTkToplevel(self.root)
        cancel_window.title("Cancel Reservation")
        cancel_window.geometry("350x250")
        cancel_window.configure(fg_color="white")

        ctk.CTkLabel(
            cancel_window,
            text="Cancel a Reservation",
            font=("Arial", 16, "bold"),
            text_color="black"
        ).pack(pady=10)

        # Fetch list of PR_NO where status = 'Not Available'
        conn = self.get_db_connection()
        reserved_list = []
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT PR_NO FROM projector_reservation WHERE STATUS = 'Not Available'")
                reserved_list = [row[0] for row in cursor.fetchall()]
            except Error as e:
                print(f"Error fetching reserved projectors: {e}")
            finally:
                cursor.close()
                conn.close()

        ctk.CTkLabel(cancel_window, text="Select Projector (PR. NO.):", text_color="black", anchor="w", font=("Arial", 12)
                     ).pack(pady=(10, 0), padx=20, anchor="w")
        self.cancel_pr_dropdown = ctk.CTkOptionMenu(cancel_window, values=reserved_list, width=200)
        self.cancel_pr_dropdown.pack(pady=(5, 15))

        ctk.CTkButton(
            cancel_window,
            text="Cancel Reservation",
            fg_color="#800000",
            text_color="white",
            command=self.submit_cancellation
        ).pack(pady=20)

    def submit_cancellation(self):
        pr_no = self.cancel_pr_dropdown.get()
        if not pr_no:
            print("Please select a projector to cancel.")
            return

        conn = self.get_db_connection()
        if conn is None:
            return

        try:
            cursor = conn.cursor()
            query = """
                UPDATE projector_reservation
                SET STATUS = 'Available',
                    PROFESSOR = '',
                    SECTION = '',
                    REPRESENTATIVE = '',
                    TIME = ''
                WHERE PR_NO = %s
            """
            cursor.execute(query, (pr_no,))
            conn.commit()
            print(f"Reservation for {pr_no} has been cancelled.")
        except OSError as e:
            print(f"Error cancelling reservation: {e}")
        finally:
            cursor.close()
            conn.close()

    #  VIEW BUTTON → SHOW ALL RESERVATIONS IN A TABLE

    def open_view_window(self):
        view_window = ctk.CTkToplevel(self.root)
        view_window.title("View Reservations")
        view_window.geometry("800x500")
        view_window.configure(fg_color="white")

        ctk.CTkLabel(
            view_window,
            text="All Projector Reservations",
            font=("Arial", 16, "bold"),
            text_color="black"
        ).pack(pady=10)

        # Frame to hold the data table
        table_container = ctk.CTkFrame(view_window, fg_color="white", border_width=1, corner_radius=10)
        table_container.pack(padx=20, pady=10, fill="both", expand=True)

        # Headers
        headers = ["PR. NO.", "SERIAL NO.", "TIME", "PROFESSOR", "SECTION", "REPRESENTATIVE", "STATUS"]
        for col_index, header in enumerate(headers):
            ctk.CTkLabel(
                table_container,
                text=header,
                font=("Arial", 14, "bold"),
                text_color="black",
                fg_color="#e6e6e6",
                width=110,
                height=30
            ).grid(row=0, column=col_index, padx=1, pady=1, sticky="nsew")

        # Fetch all records
        conn = self.get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT PR_NO, SERIAL_NO, TIME, PROFESSOR, SECTION, REPRESENTATIVE, STATUS FROM projector_reservation")
                rows = cursor.fetchall()
            except Error as e:
                print(f"Error fetching reservations: {e}")
                rows = []
            finally:
                cursor.close()
                conn.close()
        else:
            rows = []

        # Populate rows
        for row_index, row_data in enumerate(rows, start=1):
            for col_index, cell in enumerate(row_data):
                ctk.CTkLabel(
                    table_container,
                    text=str(cell),
                    font=("Arial", 13),
                    text_color="black",
                    fg_color="white",
                    width=110,
                    height=30
                ).grid(row=row_index, column=col_index, padx=1, pady=1, sticky="nsew")

        # Make columns expand evenly
        for col_index in range(len(headers)):
            table_container.grid_columnconfigure(col_index, weight=1)


if __name__ == "__main__":
    root = ctk.CTk()
    app = ProjectorReservationSystem(root)
    root.mainloop()
