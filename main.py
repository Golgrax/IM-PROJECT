import customtkinter as ctk
from PIL import Image
import mysql.connector
from mysql.connector import Error
from db_connector import connect_db
import admin_dashboard
import student_dashboard
import os

class ProjectorReservationSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("Projector Reservation System")
        self.root.geometry("900x550")
        self.root.configure(bg="#800000")
        self.root.resizable(True, True)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        # Load background image
        # Assuming IMAGE folder is sibling to main.py
        base_path = os.path.dirname(os.path.abspath(__file__))
        self.logo_path = os.path.join(base_path, "IMAGE", "PUP_LOGO.png")
        self.bg_path = os.path.join(base_path, "IMAGE", "background.png") # Changed to a generic background image

        try:
            self.original_bg_image = Image.open(self.bg_path)
            self.bg_label = ctk.CTkLabel(root, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
            self.root.after(100, self.update_background)
            self.root.bind("<Configure>", self.on_resize)
        except FileNotFoundError:
            print(f"Error: Background image not found at {self.bg_path}. Please check the path.")
            self.bg_label = ctk.CTkLabel(root, text="Background Image Missing", fg_color="#800000")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.create_login_frame()

    def on_resize(self, event):
        if event.width > 1 and event.height > 1:
            self.update_background()

    def update_background(self):
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        if width > 1 and height > 1 and hasattr(self, 'original_bg_image'):
            resized_image = self.original_bg_image.resize((width, height), Image.LANCZOS)
            self.bg_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(width, height))
            self.bg_label.configure(image=self.bg_image)

    def create_login_frame(self):
        for widget in self.root.winfo_children():
            if widget != self.bg_label and hasattr(self, 'bg_label'):
                widget.destroy()

        self.login_frame = ctk.CTkFrame(self.root,
                                        fg_color="#800000",
                                        border_width=2,
                                        corner_radius=15,
                                        width=380,
                                        height=320)
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        try:
            logo_image = Image.open(self.logo_path)
            logo_image = logo_image.resize((80, 80), Image.LANCZOS)
            self.logo_ctk_image = ctk.CTkImage(light_image=logo_image, dark_image=logo_image, size=(80, 80))
            ctk.CTkLabel(self.login_frame, image=self.logo_ctk_image, text="").pack(pady=(15, 5))
        except FileNotFoundError:
            print(f"Error: Logo image not found at {self.logo_path}.")
            ctk.CTkLabel(self.login_frame, text="PUP Logo", font=("Arial", 16, "bold"), text_color="white").pack(pady=(15, 5))


        ctk.CTkLabel(
            self.login_frame,
            text="Projector Reservation System",
            font=("Arial", 18, "bold"),
            text_color="white"
        ).pack(pady=5)

        ctk.CTkLabel(self.login_frame, text="Username:", text_color="white", font=("Arial", 12)).pack(pady=(10, 0))
        self.username_entry = ctk.CTkEntry(self.login_frame, font=("Arial", 12), width=250, placeholder_text="Enter username")
        self.username_entry.pack(pady=5)

        ctk.CTkLabel(self.login_frame, text="Password:", text_color="white", font=("Arial", 12)).pack(pady=(10, 0))
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", font=("Arial", 12), width=250, placeholder_text="Enter password")
        self.password_entry.pack(pady=5)

        self.error_label = ctk.CTkLabel(self.login_frame, text="", text_color="yellow", font=("Arial", 10, "bold"))
        self.error_label.pack(pady=(5, 0))

        login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            font=("Arial", 14, "bold"),
            fg_color="#FFD700", # Gold color for button
            text_color="black",
            hover_color="#DAA520",
            command=self.login
        )
        login_button.pack(pady=10)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "admin" and password == "admin":
            self.login_frame.destroy()
            self.root.withdraw() # Hide main window
            admin_dashboard.open_admin_dashboard("Admin")
            self.root.deiconify() # Show main window again when dashboard closes
            self.create_login_frame() # Re-show login frame
        else:
            conn = connect_db()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("SELECT name FROM students WHERE name = %s AND password = %s", (username, password))
                    student_data = cursor.fetchone()
                    if student_data:
                        student_name = student_data[0]
                        self.login_frame.destroy()
                        self.root.withdraw()
                        student_dashboard.open_student_dashboard(student_name)
                        self.root.deiconify()
                        self.create_login_frame()
                    else:
                        self.error_label.configure(text="Invalid username or password.")
                except Error as e:
                    self.error_label.configure(text=f"Database error: {e}")
                finally:
                    cursor.close()
                    conn.close()
            else:
                self.error_label.configure(text="Could not connect to database.")

if __name__ == "__main__":
    root = ctk.CTk()
    app = ProjectorReservationSystem(root)
    root.mainloop()