# app.py
import customtkinter as ctk
from PIL import Image
from db_connector import DBManager
from admin_dashboard import AdminDashboard # Import your new dashboard classes
from student_dashboard import StudentDashboard

class ProjectorReservationSystem:
    def __init__(self, root, db_manager):
        self.root = root
        self.db = db_manager # Store the DBManager instance

        self.root.title("Projector Reservation System")
        self.root.geometry("1000x600")
        self.root.configure(bg="#800000") # Maroon background for main window
        self.root.resizable(True, True)

        ctk.set_appearance_mode("dark") # Default appearance for the main app

        # Load background image
        # IMPORTANT: Adjust this path relative to where main.py is run.
        # If your 'IMAGE' folder is directly in 'IM-PROJECT', './IMAGE/PUP_LOGO.png' is correct.
        image_path = "./IMAGE/PUP_LOGO.png"
        self.original_image = None
        try:
            self.original_image = Image.open(image_path)
            print(f"Background image loaded from: {image_path}")
        except FileNotFoundError:
            print(f"Warning: Background image not found at {image_path}. Displaying without image.")
        except Exception as e:
            print(f"Error loading image: {e}")
            self.original_image = None # Ensure it's None if any error occurs

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
        if width > 1 and height > 1 and self.original_image:
            resized_image = self.original_image.resize((width, height), Image.LANCZOS)
            self.bg_image = ctk.CTkImage(light_image=resized_image, dark_image=resized_image, size=(width, height))
            self.bg_label.configure(image=self.bg_image)
        elif not self.original_image:
            # If image failed to load, clear background or set a solid color
            self.bg_label.configure(fg_color="#800000") # Maroon background if no image

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
                                        height=280) # Increased height slightly
        self.login_frame.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            self.login_frame,
            text="Projector Reservation System",
            font=("Arial", 18, "bold"), # Increased font size
            text_color="white"
        ).place(relx=0.5, rely=0.15, anchor="center")

        ctk.CTkLabel(self.login_frame,
                     text="Username:",
                     text_color="white",
                     font=("Arial", 14) # Increased font size
                     ).place(x=30, y=80) # Adjusted y
        self.username_entry = ctk.CTkEntry(self.login_frame, font=("Arial", 14), width=200)
        self.username_entry.place(x=120, y=80)

        ctk.CTkLabel(self.login_frame,
                     text="Password:",
                     text_color="white",
                     font=("Arial", 14) # Increased font size
                     ).place(x=30, y=130) # Adjusted y
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", font=("Arial", 14), width=200)
        self.password_entry.place(x=120, y=130)

        self.error_label = ctk.CTkLabel(self.login_frame, text="", text_color="red", font=("Arial", 12))
        self.error_label.place(relx=0.5, rely=0.88, anchor="center") # Adjusted y

        login_button = ctk.CTkButton(
            self.login_frame,
            text="Login",
            font=("Arial", 14, "bold"),
            fg_color="yellow",
            text_color="black",
            command=self.login
        )
        login_button.place(relx=0.5, rely=0.75, anchor="center")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "admin" and password == "admin":
            # Admin login
            self.login_frame.destroy()
            self.open_admin_dashboard(username)
        else:
            # Try student login
            stored_password = self.db.get_student_credentials(username)
            if stored_password and stored_password == password:
                self.login_frame.destroy()
                self.open_student_dashboard(username)
            else:
                self.error_label.configure(text="Invalid credentials!")

    def open_admin_dashboard(self, admin_name):
        # Create a new Toplevel window for the admin dashboard
        admin_win = ctk.CTkToplevel(self.root)
        # Pass the DBManager instance to the dashboard
        AdminDashboard(admin_win, admin_name, self.db)
        # Hide the main window if you want the dashboard to be the only visible window
        # self.root.withdraw()
        # To show main window again when dashboard closes:
        admin_win.protocol("WM_DELETE_WINDOW", lambda: self.on_dashboard_close(admin_win))

    def open_student_dashboard(self, student_name):
        # Create a new Toplevel window for the student dashboard
        student_win = ctk.CTkToplevel(self.root)
        # Pass the DBManager instance and student name to the dashboard
        StudentDashboard(student_win, student_name, self.db)
        # Hide the main window if you want the dashboard to be the only visible window
        # self.root.withdraw()
        # To show main window again when dashboard closes:
        student_win.protocol("WM_DELETE_WINDOW", lambda: self.on_dashboard_close(student_win))

    def on_dashboard_close(self, dashboard_window):
        # This function is called when a dashboard window is closed
        dashboard_window.destroy()
        # Bring the main login window back to the foreground and clear entries
        self.create_login_frame() # Recreate login frame
        self.root.deiconify() # Show the main window if it was hidden
        self.username_entry.delete(0, ctk.END)
        self.password_entry.delete(0, ctk.END)
        self.error_label.configure(text="") # Clear any previous error