import tkinter as tk
from tkinter import messagebox, ttk
from db_connector import connect_db
from datetime import date, datetime
import mysql.connector

def open_student_dashboard(student_name, login_window):
    student_win = tk.Toplevel(login_window)
    student_win.title("Student Dashboard")
    student_win.geometry("1000x650")
    student_win.configure(bg="#F0F0F0")
    student_win.minsize(900, 550)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background="#F0F0F0")
    style.configure("TLabel", background="#F0F0F0", font=("Arial", 10))
    style.configure("TLabelFrame", background="#F0F0F0", font=("Arial", 12, "bold"))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#D0D0D0", foreground="black")
    style.configure("Treeview", font=("Arial", 10), rowheight=25)
    style.map("Treeview", background=[('selected', '#B0E0E6')])
    style.configure("Accent.TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Accent.TButton", background=[('active', '#5CB85C')])
    style.configure("Danger.TButton", background="#F44336", foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Danger.TButton", background=[('active', '#D32F2F')])
    style.configure("Dark.TButton", background="#555555", foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Dark.TButton", background=[('active', '#777777')])

    ttk.Label(student_win, text=f"Welcome, {student_name}!", font=("Arial", 18, "bold")).pack(pady=(15, 10))

    notebook = ttk.Notebook(student_win)
    notebook.pack(expand=True, fill='both', padx=15, pady=10)

    tab_reserve = ttk.Frame(notebook, padding="15")
    notebook.add(tab_reserve, text=" Make a Reservation ")

    reserve_frame = ttk.LabelFrame(tab_reserve, text="Reservation Form", padding="15")
    reserve_frame.pack(padx=20, pady=20, fill="x")

    form_labels = ["Select Projector", "Professor Name", "Date (YYYY-MM-DD)", "Start Time (HH:MM)", "End Time (HH:MM)", "Purpose"]
    form_entries = {}

    ttk.Label(reserve_frame, text="Select Projector:").pack(anchor="w", padx=10, pady=(10, 0))
    projector_combo = ttk.Combobox(reserve_frame, state="readonly", width=42, font=("Arial", 10))
    project_options = []
    db = connect_db()
    if db:
        cursor = db.cursor()
        try:
            cursor.execute("SELECT projector_id, projector_name FROM projectors WHERE status = 'Available'")
            projectors = cursor.fetchall()
            projector_combo['values'] = [f"{p[0]} - {p[1]}" for p in projectors]
            project_options = projectors
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()
    projector_combo.pack(padx=10, pady=5)
    form_entries["projector_combo"] = projector_combo

    entry_fields = {
        "professor_name": "Professor Name",
        "date_reserved": "Date (YYYY-MM-DD)",
        "time_start": "Start Time (HH:MM)",
        "time_end": "End Time (HH:MM)",
        "purpose": "Purpose"
    }

    for key, label_text in entry_fields.items():
        ttk.Label(reserve_frame, text=f"{label_text}:").pack(anchor="w", padx=10, pady=(10, 0))
        entry = ttk.Entry(reserve_frame, width=45, font=("Arial", 10))
        entry.pack(padx=10, pady=5)
        form_entries[key] = entry
    form_entries["date_reserved"].insert(0, str(date.today()))

    def submit_reservation():
        proj_selection = form_entries["projector_combo"].get()
        professor_name = form_entries["professor_name"].get().strip()
        date_str = form_entries["date_reserved"].get().strip()
        time_start_str = form_entries["time_start"].get().strip()
        time_end_str = form_entries["time_end"].get().strip()
        purpose = form_entries["purpose"].get().strip()

        if not all([proj_selection, professor_name, date_str, time_start_str, time_end_str, purpose]):
            messagebox.showwarning("Input Error", "Please complete all fields.")
            return

        try:
            proj_id = int(proj_selection.split(" - ")[0])
            datetime.strptime(date_str, '%Y-%m-%d')
            datetime.strptime(time_start_str, '%H:%M')
            datetime.strptime(time_end_str, '%H:%M')
        except ValueError:
            messagebox.showerror("Input Error", "Invalid date or time format. Use YYYY-MM-DD and HH:MM.")
            return
        except Exception as e:
            messagebox.showerror("Input Error", f"An unexpected error occurred with inputs: {e}")
            return

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("SELECT student_id FROM students WHERE name = %s", (student_name,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Student not found in database.")
                return
            student_id = result[0]

            cursor.execute("""
                INSERT INTO reservations (student_id, projector_id, professor_name, date_reserved,
                time_start, time_end, purpose, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
            """, (student_id, proj_id, professor_name, date_str,
                  time_start_str, time_end_str, purpose))
            db.commit()

            messagebox.showinfo("Success", "Reservation submitted! Awaiting admin approval.")
            for key in entry_fields:
                if key != "date_reserved":
                    form_entries[key].delete(0, tk.END)
            form_entries["projector_combo"].set('')
            load_reservations()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    ttk.Button(reserve_frame, text="Submit Reservation", command=submit_reservation, style="Accent.TButton").pack(pady=15)

    tab_view = ttk.Frame(notebook, padding="15")
    notebook.add(tab_view, text="My Reservations")

    view_frame = ttk.LabelFrame(tab_view, text="Your Reservation Records", padding="15")
    view_frame.pack(padx=20, pady=20, expand=True, fill="both")

    columns = ("ID", "Projector", "Professor", "Date", "Start", "End", "Purpose", "Status")
    tree = ttk.Treeview(view_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100 if col not in ["Purpose", "Projector"] else 150, anchor="center")
    tree.pack(expand=True, fill='both', padx=10, pady=10)

    def load_reservations():
        for i in tree.get_children():
            tree.delete(i)

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("SELECT student_id FROM students WHERE name = %s", (student_name,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Student not found in database.")
                return
            student_id = result[0]

            cursor.execute("""
                SELECT r.reservation_id, p.projector_name, r.professor_name, r.date_reserved,
                       r.time_start, r.time_end, COALESCE(r.purpose, 'No Purpose'), r.status
                FROM reservations r
                JOIN projectors p ON r.projector_id = p.projector_id
                WHERE r.student_id = %s
                ORDER BY r.date_reserved DESC, r.time_start DESC
            """, (student_id,))
            for row in cursor.fetchall():
                tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    def cancel_reservation():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a reservation to cancel.")
            return

        res_id = tree.item(selected[0])['values'][0]
        current_status = tree.item(selected[0])['values'][7]

        if current_status in ('Rejected', 'Cancelled'):
            messagebox.showinfo("Already Processed", f"This reservation is already {current_status} and cannot be cancelled further.")
            return

        confirm = messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this reservation?")
        if not confirm:
            return

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("SELECT projector_id FROM reservations WHERE reservation_id = %s", (res_id,))
            proj_id_result = cursor.fetchone()

            cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", (res_id,))

            if current_status == 'Approved' and proj_id_result:
                proj_id = proj_id_result[0]
                cursor.execute("UPDATE projectors SET status = 'Available' WHERE projector_id = %s", (proj_id,))

            db.commit()
            messagebox.showinfo("Cancelled", "Reservation cancelled successfully.")
            load_reservations()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    ttk.Button(view_frame, text="Cancel Selected Reservation", command=cancel_reservation, style="Danger.TButton").pack(pady=15)

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            student_win.destroy()
            login_window.deiconify()

    ttk.Button(student_win, text="Logout", command=logout, style="Dark.TButton").pack(pady=10)

    load_reservations()
