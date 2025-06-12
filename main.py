import tkinter as tk
from tkinter import messagebox
import mysql.connector
from admin_dashboard import open_admin_dashboard  # your admin dashboard function
from student_dashboard import open_student_dashboard  # your student dashboard function

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1019",
        database="projector_management_db"
    )

def login():
    username = entry_username.get().strip()
    password = entry_password.get().strip()

    if not username or not password:
        messagebox.showwarning("Input Error", "Please enter both username and password.")
        return

    try:
        db = connect_db()
        cursor = db.cursor()

        # Check admins first
        cursor.execute("SELECT password, name FROM admins WHERE LOWER(username) = LOWER(%s)", (username,))
        admin = cursor.fetchone()

        if admin:
            db_password, admin_name = admin
            if password == db_password:
                cursor.close()
                db.close()
                root.destroy()  # Close login window
                open_admin_dashboard(admin_name)  # Open admin dashboard directly
                return
            else:
                messagebox.showerror("Login Failed", "Incorrect password for admin.")
                cursor.close()
                db.close()
                return

        # Check students
        cursor.execute("SELECT password, name FROM students WHERE LOWER(username) = LOWER(%s)", (username,))
        student = cursor.fetchone()

        if student:
            db_password, student_name = student
            if password == db_password:
                cursor.close()
                db.close()
                root.destroy()  # Close login window
                open_student_dashboard(student_name)  # Open student dashboard directly
                return
            else:
                messagebox.showerror("Login Failed", "Incorrect password for student.")
                cursor.close()
                db.close()
                return

        messagebox.showerror("Login Failed", "Username not found.")
        cursor.close()
        db.close()

    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")

root = tk.Tk()
root.title("Login Form")
root.geometry("300x250")

tk.Label(root, text="Username").pack(pady=5)
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Password").pack(pady=5)
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="Login", command=login).pack(pady=20)

root.mainloop()
