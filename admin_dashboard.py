import tkinter as tk
from tkinter import messagebox, ttk
from db_connector import connect_db

def open_admin_dashboard(admin_name):
    admin_win = tk.Tk()
    admin_win.title("Admin Dashboard")
    admin_win.state('zoomed')
    admin_win.configure(bg="#F0F0F0")

    style = ttk.Style()
    style.theme_use('clam')
    style.configure("TFrame", background="#F0F0F0")
    style.configure("TLabel", background="#F0F0F0", font=("Arial", 10))
    style.configure("TLabelFrame", background="#F0F0F0", font=("Arial", 12, "bold"))
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background="#D0D0D0", foreground="black")
    style.configure("Treeview", font=("Arial", 10), rowheight=25)
    style.map("Treeview", background=[('selected', '#B0E0E6')])

    main_frame = ttk.Frame(admin_win, padding="20")
    main_frame.pack(fill='both', expand=True)

    ttk.Label(main_frame, text=f"Welcome, {admin_name}!", font=("Arial", 18, "bold")).pack(pady=20)

    # Add Projector Section
    add_frame = ttk.LabelFrame(main_frame, text="Add New Projector", padding="10")
    add_frame.pack(fill="x", pady=10)

    ttk.Label(add_frame, text="Projector Name:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
    proj_name_entry = ttk.Entry(add_frame, width=40)
    proj_name_entry.grid(row=0, column=1, pady=5, padx=5)

    ttk.Label(add_frame, text="Model:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
    model_entry = ttk.Entry(add_frame, width=40)
    model_entry.grid(row=1, column=1, pady=5, padx=5)

    def add_projector():
        proj_name = proj_name_entry.get().strip()
        model = model_entry.get().strip()

        if not proj_name or not model:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
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

    ttk.Button(add_frame, text="Add Projector", command=add_projector, style="Accent.TButton").grid(row=2, column=0, columnspan=2, pady=10)
    style.configure("Accent.TButton", background="#4CAF50", foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Accent.TButton", background=[('active', '#5CB85C')])


    # Reservation Section
    pending_frame = ttk.LabelFrame(main_frame, text="Pending & Approved Reservations", padding="10")
    pending_frame.pack(fill="both", expand=True, pady=10)

    cols = ("Reservation ID", "Student Name", "Projector", "Professor", "Date", "Start", "End", "Purpose", "Status")
    tree = ttk.Treeview(pending_frame, columns=cols, show='headings')
    for col in cols:
        tree.heading(col, text=col)
        tree.column(col, width=100 if col != "Purpose" else 200, anchor='center')
    tree.pack(fill="both", expand=True)

    def load_pending_reservations():
        for i in tree.get_children():
            tree.delete(i)
        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
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
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    # Approve / Reject Buttons
    btn_frame = ttk.Frame(main_frame, padding="5")
    btn_frame.pack(pady=5)

    def update_reservation_status(new_status):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a reservation to update.")
            return

        res_id = tree.item(selected[0])['values'][0]
        current_status_in_tree = tree.item(selected[0])['values'][8]

        confirm = messagebox.askyesno(f"{new_status} Reservation", f"Are you sure you want to mark this reservation as {new_status}?")
        if not confirm:
            return

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("SELECT projector_id, status FROM reservations WHERE reservation_id = %s", (res_id,))
            res_info = cursor.fetchone()
            if not res_info:
                messagebox.showerror("Error", "Reservation not found.")
                return

            proj_id = res_info[0]
            old_reservation_status = res_info[1]

            cursor.execute("UPDATE reservations SET status = %s WHERE reservation_id = %s", (new_status, res_id))

            # Logic to update projector status
            if new_status == 'Approved' and old_reservation_status != 'Approved':
                cursor.execute("UPDATE projectors SET status = 'Reserved' WHERE projector_id = %s", (proj_id,))
            elif new_status in ('Cancelled', 'Rejected') and old_reservation_status == 'Approved':
                # Only free up projector if it was previously approved and now cancelled/rejected
                cursor.execute("UPDATE projectors SET status = 'Available' WHERE projector_id = %s", (proj_id,))

            db.commit()
            messagebox.showinfo("Success", f"Reservation marked as {new_status}.")
            load_pending_reservations()
            load_projectors()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    ttk.Button(btn_frame, text="Approve", command=lambda: update_reservation_status("Approved"), style="Accent.TButton", width=15).pack(side="left", padx=10)
    ttk.Button(btn_frame, text="Reject", command=lambda: update_reservation_status("Rejected"), style="Danger.TButton", width=15).pack(side="left", padx=10)
    style.configure("Danger.TButton", background="#F44336", foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Danger.TButton", background=[('active', '#D32F2F')])

    # Projector List Section
    projector_frame = ttk.LabelFrame(main_frame, text="Projector List", padding="10")
    projector_frame.pack(fill="both", expand=True, pady=10)

    proj_cols = ("Projector ID", "Name", "Model", "Status")
    proj_tree = ttk.Treeview(projector_frame, columns=proj_cols, show='headings')
    for col in proj_cols:
        proj_tree.heading(col, text=col)
        proj_tree.column(col, width=150, anchor='center')
    proj_tree.pack(fill="both", expand=True)

    def load_projectors():
        for i in proj_tree.get_children():
            proj_tree.delete(i)
        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("SELECT projector_id, projector_name, model, status FROM projectors")
            records = cursor.fetchall()
            for r in records:
                proj_tree.insert('', 'end', values=r)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    logout_frame = ttk.Frame(admin_win, padding="10")
    logout_frame.pack(side="bottom", fill="x")
    ttk.Button(logout_frame, text="Logout", command=admin_win.destroy, style="Dark.TButton", width=20).pack(pady=5)
    style.configure("Dark.TButton", background="#555555", foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Dark.TButton", background=[('active', '#777777')])

    load_pending_reservations()
    load_projectors()

    admin_win.mainloop()