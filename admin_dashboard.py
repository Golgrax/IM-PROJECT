import tkinter as tk
from tkinter import messagebox, ttk
import mysql.connector

def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="host",
        password="1019",
        database="projector_reservation_db"
    )

def open_admin_dashboard(admin_name):
    admin_win = tk.Tk()
    admin_win.title("Admin Dashboard")
    admin_win.state('zoomed')  # Maximize window
    admin_win.configure(bg="#f4f4f4")

    # Root frame with grid layout
    root_frame = tk.Frame(admin_win, bg="#f4f4f4")
    root_frame.pack(fill='both', expand=True)

    # Configure grid rows and columns
    root_frame.rowconfigure(0, weight=1)  # main content expands
    root_frame.columnconfigure(0, weight=1)

    # Main content frame (all widgets go here)
    main_frame = tk.Frame(root_frame, bg="#f4f4f4")
    main_frame.grid(row=0, column=0, sticky='nsew', padx=20, pady=20)

    tk.Label(main_frame, text=f"Welcome, {admin_name}!", font=("Arial", 18, "bold"), bg="#f4f4f4").pack(pady=20)

    # --- Add Projector Section ---
    add_frame = tk.LabelFrame(main_frame, text="Add New Projector", padx=10, pady=10, bg="#f4f4f4")
    add_frame.pack(fill="x", pady=10)

    tk.Label(add_frame, text="Projector Name:", bg="#f4f4f4").grid(row=0, column=0, sticky="w")
    proj_name_entry = tk.Entry(add_frame, width=30)
    proj_name_entry.grid(row=0, column=1, pady=5, padx=5)

    tk.Label(add_frame, text="Model:", bg="#f4f4f4").grid(row=1, column=0, sticky="w")
    model_entry = tk.Entry(add_frame, width=30)
    model_entry.grid(row=1, column=1, pady=5, padx=5)

    def add_projector():
        proj_name = proj_name_entry.get().strip()
        model = model_entry.get().strip()

        if not proj_name or not model:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute(
                "INSERT INTO projectors (projector_name, model, status) VALUES (%s, %s, 'Available')",
                (proj_name, model)
            )
            db.commit()
            messagebox.showinfo("Success", f"Projector '{proj_name}' added.")
            proj_name_entry.delete(0, tk.END)
            model_entry.delete(0, tk.END)
            load_projectors()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    tk.Button(add_frame, text="Add Projector", command=add_projector, bg="#4CAF50", fg="white").grid(row=2, column=0, columnspan=2, pady=10)

    # --- Reservation Section ---
    pending_frame = tk.LabelFrame(main_frame, text="Pending & Approved Reservations", padx=10, pady=10, bg="#f4f4f4")
    pending_frame.pack(fill="both", expand=True, pady=10)

    cols = ("Reservation ID", "Student Name", "Projector", "Professor", "Date", "Start", "End", "Purpose", "Status")
    tree = ttk.Treeview(pending_frame, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100 if col != "Purpose" else 200)
    tree.pack(fill="both", expand=True)

    def load_pending_reservations():
        for i in tree.get_children():
            tree.delete(i)
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("""
                SELECT r.reservation_id, s.name, p.projector_name, r.professor_name, r.date_reserved, r.time_start, r.time_end, 
                       COALESCE(r.purpose, 'No Purpose'), r.status
                FROM reservations r
                JOIN students s ON r.student_id = s.student_id
                JOIN projectors p ON r.projector_id = p.projector_id
                WHERE r.status IN ('Pending', 'Approved')
                ORDER BY r.date_reserved, r.time_start
            """)
            records = cursor.fetchall()
            for r in records:
                tree.insert('', 'end', values=r)
            cursor.close()
            db.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    # --- Approve / Reject Buttons ---
    btn_frame = tk.Frame(main_frame, bg="#f4f4f4")
    btn_frame.pack(pady=5)

    def update_reservation_status(new_status):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a reservation to update.")
            return

        res_id = tree.item(selected[0])['values'][0]

        confirm = messagebox.askyesno(f"{new_status} Reservation", f"Are you sure you want to mark this reservation as {new_status}?")
        if not confirm:
            return

        try:
            db = connect_db()
            cursor = db.cursor()

            # Update reservation status
            cursor.execute("UPDATE reservations SET status = %s WHERE reservation_id = %s", (new_status, res_id))

            # Update projector status
            cursor.execute("SELECT projector_id FROM reservations WHERE reservation_id = %s", (res_id,))
            proj_id = cursor.fetchone()[0]

            if new_status == 'Approved':
                cursor.execute("UPDATE projectors SET status = 'Reserved' WHERE projector_id = %s", (proj_id,))
            elif new_status in ('Cancelled', 'Rejected'):
                cursor.execute("UPDATE projectors SET status = 'Available' WHERE projector_id = %s", (proj_id,))

            db.commit()
            messagebox.showinfo("Success", f"Reservation marked as {new_status}.")
            load_pending_reservations()
            load_projectors()

            cursor.close()
            db.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    tk.Button(btn_frame, text="Approve", command=lambda: update_reservation_status("Approved"), bg="#4CAF50", fg="white", width=15).pack(side="left", padx=10)
    tk.Button(btn_frame, text="Reject", command=lambda: update_reservation_status("Rejected"), bg="#f44336", fg="white", width=15).pack(side="left", padx=10)

    # --- Projector List Section ---
    projector_frame = tk.LabelFrame(main_frame, text="Projector List", padx=10, pady=10, bg="#f4f4f4")
    projector_frame.pack(fill="both", expand=True, pady=10)

    proj_cols = ("Projector ID", "Name", "Model", "Status")
    proj_tree = ttk.Treeview(projector_frame, columns=proj_cols, show='headings')
    for col in proj_cols:
        proj_tree.heading(col, text=col)
        proj_tree.column(col, width=150)
    proj_tree.pack(fill="both", expand=True)

    def load_projectors():
        for i in proj_tree.get_children():
            proj_tree.delete(i)
        try:
            db = connect_db()
            cursor = db.cursor()
            cursor.execute("SELECT projector_id, projector_name, model, status FROM projectors")
            records = cursor.fetchall()
            for r in records:
                proj_tree.insert('', 'end', values=r)
            cursor.close()
            db.close()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))

    # --- Logout button frame pinned at the bottom ---
    logout_frame = tk.Frame(root_frame, bg="#f4f4f4")
    logout_frame.grid(row=1, column=0, sticky='ew', pady=(0,10))
    tk.Button(logout_frame, text="Logout", command=admin_win.destroy, bg="#555555", fg="white", width=20).pack()

    # Load data when window opens
    load_pending_reservations()
    load_projectors()

    admin_win.mainloop()
