import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector
from datetime import date, datetime

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="host",
        password="1019",
        database="projector_reservation_db"
    )

def open_student_dashboard(student_name):
    student_win = tk.Tk()
    student_win.title("Student Dashboard")
    student_win.geometry("1000x600")
    student_win.configure(bg="#f4f4f4")

    # Add minsize so window is resizable but not too small
    student_win.minsize(900, 500)

    tk.Label(student_win, text=f"Welcome, {student_name}!", font=("Arial", 18, "bold"), bg="#f4f4f4").pack(pady=(15, 10))

    notebook = ttk.Notebook(student_win)
    notebook.pack(expand=True, fill='both', padx=15, pady=10)

    # --- TAB 1: Make a Reservation ---
    tab_reserve = tk.Frame(notebook, bg="white")
    notebook.add(tab_reserve, text=" Make a Reservation")

    reserve_frame = tk.LabelFrame(tab_reserve, text="Reservation Form", bg="white", font=("Arial", 12, "bold"))
    reserve_frame.pack(padx=20, pady=20, fill="x")

    def add_labeled_entry(label, parent):
        tk.Label(parent, text=label, bg="white").pack(anchor="w", padx=10)
        entry = tk.Entry(parent, width=45)
        entry.pack(padx=10, pady=5)
        return entry

    tk.Label(reserve_frame, text="Select Projector", bg="white").pack(anchor="w", padx=10)
    projector_combo = ttk.Combobox(reserve_frame, state="readonly", width=42)
    projector_combo.pack(padx=10, pady=5)

    try:
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT projector_id, projector_name FROM projectors WHERE status = 'Available'")
        projectors = cursor.fetchall()
        projector_combo['values'] = [f"{p[0]} - {p[1]}" for p in projectors]
        cursor.close()
        db.close()
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", str(err))
        student_win.destroy()
        return

    prof_entry = add_labeled_entry("Professor Name", reserve_frame)
    date_entry = add_labeled_entry("Date (YYYY-MM-DD)", reserve_frame)
    date_entry.insert(0, str(date.today()))
    start_entry = add_labeled_entry("Start Time (HH:MM)", reserve_frame)
    end_entry = add_labeled_entry("End Time (HH:MM)", reserve_frame)
    purpose_entry = add_labeled_entry("Purpose", reserve_frame)

    def submit_reservation():
        if not all([projector_combo.get(), prof_entry.get(), date_entry.get(),
                    start_entry.get(), end_entry.get(), purpose_entry.get()]):
            messagebox.showwarning("Input Error", "Please complete all fields.")
            return

        try:
            proj_id = int(projector_combo.get().split(" - ")[0])
            datetime.strptime(date_entry.get(), '%Y-%m-%d')
            datetime.strptime(start_entry.get(), '%H:%M')
            datetime.strptime(end_entry.get(), '%H:%M')
        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input format: {e}")
            return

        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT student_id FROM students WHERE name = %s", (student_name,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Student not found.")
                return

            student_id = result[0]
            cursor.execute("""
                INSERT INTO reservations (student_id, projector_id, professor_name, date_reserved,
                time_start, time_end, purpose, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
            """, (student_id, proj_id, prof_entry.get(), date_entry.get(),
                  start_entry.get(), end_entry.get(), purpose_entry.get()))
            db.commit()

            messagebox.showinfo("Success", "Reservation submitted!")
            load_reservations()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    tk.Button(reserve_frame, text="Submit Reservation", command=submit_reservation,
              bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

    # --- TAB 2: View My Reservations ---
    tab_view = tk.Frame(notebook, bg="white")
    notebook.add(tab_view, text="My Reservations")

    view_frame = tk.LabelFrame(tab_view, text="Your Reservation Records", bg="white", font=("Arial", 12, "bold"))
    view_frame.pack(padx=20, pady=20, expand=True, fill="both")

    columns = ("ID", "Projector", "Professor", "Date", "Start", "End", "Purpose", "Status")
    tree = ttk.Treeview(view_frame, columns=columns, show='headings')
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=110 if col != "Purpose" else 200, anchor="center")
    tree.pack(expand=True, fill='both', padx=10, pady=10)

    def load_reservations():
        for i in tree.get_children():
            tree.delete(i)

        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT student_id FROM students WHERE name = %s", (student_name,))
            result = cursor.fetchone()
            if not result:
                messagebox.showerror("Error", "Student not found.")
                return
            student_id = result[0]

            cursor.execute("""
                SELECT r.reservation_id, p.projector_name, r.professor_name, r.date_reserved,
                       r.time_start, r.time_end, COALESCE(r.purpose, 'No Purpose'), r.status
                FROM reservations r
                JOIN projectors p ON r.projector_id = p.projector_id
                WHERE r.student_id = %s
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
        confirm = messagebox.askyesno("Confirm", "Are you sure you want to cancel this reservation?")
        if not confirm:
            return

        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("DELETE FROM reservations WHERE reservation_id = %s", (res_id,))
            db.commit()
            messagebox.showinfo("Cancelled", "Reservation cancelled successfully.")
            load_reservations()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    tk.Button(view_frame, text="Cancel Selected Reservation", command=cancel_reservation,
              bg="#f44336", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

    # --- Logout Button ---
    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            student_win.destroy()

    tk.Button(student_win, text="Logout", command=logout,
              bg="#333", fg="white", font=("Arial", 10, "bold")).pack(pady=10)

    load_reservations()
    student_win.mainloop()
