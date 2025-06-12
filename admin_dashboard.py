import tkinter as tk
from tkinter import messagebox, ttk
from db_connector import connect_db
from datetime import date, datetime, time # Import time as well
from PIL import Image, ImageTk
import os
import mysql.connector

# Added parent_window parameter for Toplevel
def open_admin_dashboard(parent_window, admin_name):
    admin_win = tk.Toplevel(parent_window) # Changed to Toplevel
    admin_win.title("Admin Dashboard")
    admin_win.geometry("1000x650") # Initial size
    admin_win.minsize(900, 550)
    admin_win.state('zoomed') # Maximize the window

    # --- Background Image Management ---
    base_path = os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_path, "IMAGE", "background.png")

    bg_label = None
    try:
        admin_win.original_bg_image = Image.open(bg_image_path)
        bg_label = tk.Label(admin_win)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        admin_win.bg_photo_ref = None # Initialize a persistent reference
    except FileNotFoundError:
        admin_win.configure(bg="#800000") # Fallback to PUP maroon

    def update_background_image(event=None):
        if hasattr(admin_win, 'original_bg_image') and bg_label:
            width = admin_win.winfo_width()
            height = admin_win.winfo_height()
            if width > 0 and height > 0:
                resized_image = admin_win.original_bg_image.resize((width, height), Image.LANCZOS)
                temp_photo_image = ImageTk.PhotoImage(resized_image)
                bg_label.configure(image=temp_photo_image)
                admin_win.bg_photo_ref = temp_photo_image # Store persistent reference

    admin_win.after_idle(update_background_image) # Use after_idle for initial call
    admin_win.bind('<Configure>', update_background_image) # Bind to window resize

    # --- Define Fixed PUP Theme Colors ---
    root_bg_color = "#800000"  # PUP Maroon
    frame_bg_color = "#3A3A3A"  # Dark grey for main content frames
    label_frame_bg_color = "#555555" # Medium dark grey
    fg_color = "white"
    heading_bg = "#666666"
    treeview_bg = "#555555"
    treeview_fg = "white"
    treeview_selected = "#DAA520" # Gold
    accent_button_bg = "#FFD700"  # Gold
    accent_button_fg = "black"
    danger_button_bg = "#dc3545"  # Red
    dark_button_bg = "#6c757d"   # Grey, for logout button

    # --- Apply Fixed PUP Theme Styles ---
    style = ttk.Style()
    style.theme_use('clam')

    style.configure("TFrame", background=frame_bg_color)
    style.configure("TLabel", background=frame_bg_color, foreground=fg_color, font=("Arial", 10))
    style.configure("TLabelFrame", background=label_frame_bg_color, foreground=fg_color, font=("Arial", 12, "bold"))
    style.configure("TLabelframe.Label", background=label_frame_bg_color, foreground=fg_color)
    style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background=heading_bg, foreground=fg_color)
    style.configure("Treeview", font=("Arial", 10), rowheight=25, background=treeview_bg, foreground=treeview_fg, fieldbackground=treeview_bg)
    style.map("Treeview", background=[('selected', treeview_selected)])

    style.configure("TEntry", fieldbackground=frame_bg_color, foreground=fg_color)
    style.configure("TCombobox", fieldbackground=frame_bg_color, foreground=fg_color)
    style.configure("TCombobox.readonly", fieldbackground=frame_bg_color, foreground=fg_color, selectbackground=treeview_selected, selectforeground="black")
    style.configure("TNotebook", background=frame_bg_color)
    style.configure("TNotebook.Tab", background=label_frame_bg_color, foreground=fg_color)
    style.map("TNotebook.Tab", background=[('selected', frame_bg_color)], foreground=[('selected', fg_color)])

    style.configure("Accent.TButton", background=accent_button_bg, foreground=accent_button_fg, font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Accent.TButton", background=[('active', "#DAA520")])
    style.configure("Danger.TButton", background=danger_button_bg, foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Danger.TButton", background=[('active', "#c82333")])
    style.configure("Dark.TButton", background=dark_button_bg, foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Dark.TButton", background=[('active', "#5a6268")])
    style.configure("Info.TButton", background="#2196F3", foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
    style.map("Info.TButton", background=[('active', '#1976D2')])


    # --- Main UI Element Placement (Directly in admin_win) ---
    # Removed main_layout_frame, main_canvas, scrollable_content_frame

    welcome_label = ttk.Label(admin_win, text=f"Welcome, {admin_name}!", font=("Arial", 18, "bold"), background=root_bg_color)
    welcome_label.pack(pady=(15, 10), padx=20, fill='x')

    notebook = ttk.Notebook(admin_win)
    notebook.pack(expand=True, fill='both', padx=15, pady=10)

    # --- Tab 1: Manage Reservations ---
    tab_admin_manage_reservations = ttk.Frame(notebook, padding="15")
    notebook.add(tab_admin_manage_reservations, text="Manage Reservations")

    admin_reservations_frame = ttk.LabelFrame(tab_admin_manage_reservations, text="All Reservation Requests", padding="15")
    admin_reservations_frame.pack(padx=20, pady=20, expand=True, fill="both")

    admin_tree_columns = ("ID", "Student", "Projector", "Professor", "Date", "Start", "End", "Purpose", "Status")
    admin_tree = ttk.Treeview(admin_reservations_frame, columns=admin_tree_columns, show='headings')
    for col in admin_tree_columns:
        admin_tree.heading(col, text=col)
        admin_tree.column(col, width=100 if col not in ["Purpose", "Projector", "Student"] else 150, anchor="center")
    admin_tree.pack(expand=True, fill='both', padx=10, pady=10)

    def load_all_reservations():
        for i in admin_tree.get_children():
            admin_tree.delete(i)
        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("""
                SELECT r.reservation_id, s.name AS student_name, p.projector_name, r.professor_name,
                       r.date_reserved, r.time_start, r.time_end, COALESCE(r.purpose, 'No Purpose'), r.status
                FROM reservations r
                JOIN students s ON r.student_id = s.student_id
                JOIN projectors p ON r.projector_id = p.projector_id
                ORDER BY r.date_reserved DESC, r.time_start DESC
            """)
            for row in cursor.fetchall():
                admin_tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    def update_reservation_status(status):
        selected = admin_tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a reservation to update.")
            return

        res_values = admin_tree.item(selected[0])['values']
        res_id = res_values[0]
        projector_name = res_values[2]
        current_status = res_values[8]
        res_date = res_values[4]
        res_start_time = res_values[5]
        res_end_time = res_values[6]

        if current_status == status:
            messagebox.showinfo("Status Unchanged", f"Reservation is already '{status}'.")
            return
        
        # Prevent changing status of a reservation that is already in the past
        reservation_date = datetime.strptime(str(res_date), '%Y-%m-%d').date()
        
        # Ensure time format is consistent (HH:MM or HH:MM:SS)
        try:
            reservation_end_time = datetime.strptime(str(res_end_time), '%H:%M:%S').time()
        except ValueError:
            reservation_end_time = datetime.strptime(str(res_end_time), '%H:%M').time()
        
        try:
            reservation_start_time = datetime.strptime(str(res_start_time), '%H:%M:%S').time()
        except ValueError:
            reservation_start_time = datetime.strptime(str(res_start_time), '%H:%M').time()


        reservation_end_datetime = datetime.combine(reservation_date, reservation_end_time)

        if reservation_end_datetime < datetime.now() and current_status in ('Pending', 'Approved'):
             if not messagebox.askyesno("Confirm Past Reservation Update", 
                                        "This reservation is in the past. Are you sure you want to change its status?"):
                 return
             
        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            # Get projector_id for status updates
            cursor.execute("SELECT projector_id FROM projectors WHERE projector_name = %s", (projector_name,))
            proj_id_result = cursor.fetchone()
            if not proj_id_result:
                messagebox.showerror("Error", "Projector not found.")
                return
            proj_id = proj_id_result[0]

            if status == 'Approved':
                # Check for conflicts (same projector, overlapping time, same date)
                cursor.execute("""
                    SELECT COUNT(*) FROM reservations
                    WHERE projector_id = %s AND date_reserved = %s
                    AND reservation_id != %s AND status = 'Approved'
                    AND (
                        (time_start < %s AND time_end > %s) 
                        OR (%s < time_end AND %s > time_start) 
                        OR (time_start = %s AND time_end = %s) 
                    )
                """, (proj_id, res_date, res_id, reservation_end_time, reservation_start_time, 
                      reservation_start_time, reservation_end_time, reservation_start_time, reservation_end_time))
                conflict_count = cursor.fetchone()[0]
                if conflict_count > 0:
                    messagebox.showerror("Conflict", "This projector has an overlapping approved reservation on this date/time.")
                    return

                cursor.execute("UPDATE projectors SET status = 'Reserved' WHERE projector_id = %s", (proj_id,))
                cursor.execute("UPDATE reservations SET status = %s WHERE reservation_id = %s", (status, res_id))
                db.commit()
                messagebox.showinfo("Success", f"Reservation {res_id} Approved. Projector {projector_name} status set to Reserved.")
            elif status in ('Rejected', 'Cancelled'):
                cursor.execute("UPDATE reservations SET status = %s WHERE reservation_id = %s", (status, res_id))
                if current_status == 'Approved': # If it was approved, make projector available again
                    cursor.execute("UPDATE projectors SET status = 'Available' WHERE projector_id = %s", (proj_id,))
                db.commit()
                messagebox.showinfo("Success", f"Reservation {res_id} set to {status}.")
            else:
                 messagebox.showerror("Error", "Invalid status action.")
                 return

            load_all_reservations()
            # Refresh projector management tab treeview
            load_projectors_for_management()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    button_frame = ttk.Frame(admin_reservations_frame)
    button_frame.pack(pady=10)
    ttk.Button(button_frame, text="Approve", command=lambda: update_reservation_status('Approved'), style="Accent.TButton").pack(side="left", padx=5)
    ttk.Button(button_frame, text="Reject", command=lambda: update_reservation_status('Rejected'), style="Danger.TButton").pack(side="left", padx=5)
    ttk.Button(button_frame, text="Cancel", command=lambda: update_reservation_status('Cancelled'), style="Dark.TButton").pack(side="left", padx=5)


    # --- Tab 2: Manage Projectors ---
    tab_admin_manage_projectors = ttk.Frame(notebook, padding="15")
    notebook.add(tab_admin_manage_projectors, text="Manage Projectors")

    # Add New Projector section
    projector_manage_frame = ttk.LabelFrame(tab_admin_manage_projectors, text="Add New Projector", padding="15")
    projector_manage_frame.pack(padx=20, pady=20, fill="x")

    ttk.Label(projector_manage_frame, text="Projector Name:").pack(anchor="w", padx=10, pady=(10,0))
    proj_name_entry = ttk.Entry(projector_manage_frame, width=45, font=("Arial", 10))
    proj_name_entry.pack(padx=10, pady=5)

    ttk.Label(projector_manage_frame, text="Model:").pack(anchor="w", padx=10, pady=(10,0))
    proj_model_entry = ttk.Entry(projector_manage_frame, width=45, font=("Arial", 10))
    proj_model_entry.pack(padx=10, pady=5)

    def add_projector():
        name = proj_name_entry.get().strip()
        model = proj_model_entry.get().strip()
        if not name:
            messagebox.showwarning("Input Error", "Projector name cannot be empty.")
            return

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("INSERT INTO projectors (projector_name, model, status) VALUES (%s, %s, 'Available')", (name, model))
            db.commit()
            messagebox.showinfo("Success", "Projector added successfully.")
            proj_name_entry.delete(0, tk.END)
            proj_model_entry.delete(0, tk.END)
            load_projectors_for_management()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    ttk.Button(projector_manage_frame, text="Add Projector", command=add_projector, style="Accent.TButton").pack(pady=10)

    # Existing Projectors List
    proj_list_frame = ttk.LabelFrame(tab_admin_manage_projectors, text="Existing Projectors", padding="15")
    proj_list_frame.pack(padx=20, pady=20, expand=True, fill="both")

    proj_columns = ("ID", "Name", "Model", "Status")
    proj_tree = ttk.Treeview(proj_list_frame, columns=proj_columns, show='headings')
    for col in proj_columns:
        proj_tree.heading(col, text=col)
        proj_tree.column(col, width=150, anchor="center")
    proj_tree.pack(expand=True, fill='both', padx=10, pady=10)

    def load_projectors_for_management():
        for i in proj_tree.get_children():
            proj_tree.delete(i)
        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("SELECT projector_id, projector_name, model, status FROM projectors")
            for row in cursor.fetchall():
                proj_tree.insert('', 'end', values=row)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    # Manage Projector Status section (from your "working fine" example)
    manage_proj_status_frame = ttk.LabelFrame(tab_admin_manage_projectors, text="Update Selected Projector Status", padding="15")
    manage_proj_status_frame.pack(padx=20, pady=20, fill="x")

    ttk.Label(manage_proj_status_frame, text="Select new status:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
    proj_status_combo = ttk.Combobox(manage_proj_status_frame, state="readonly", width=20, font=("Arial", 10))
    proj_status_combo['values'] = ('Available', 'Under Maintenance')
    proj_status_combo.grid(row=0, column=1, pady=5, padx=5)

    def update_projector_status():
        selected = proj_tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a projector from the list above to update its status.")
            return

        proj_id = proj_tree.item(selected[0])['values'][0]
        new_status = proj_status_combo.get()

        if not new_status:
            messagebox.showwarning("Input Error", "Please select a new status.")
            return

        current_proj_status = proj_tree.item(selected[0])['values'][3]

        if new_status == current_proj_status:
            messagebox.showinfo("No Change", f"Projector is already '{new_status}'.")
            return

        confirm = messagebox.askyesno("Confirm Status Update", f"Are you sure you want to change status of Projector ID {proj_id} to '{new_status}'?")
        if not confirm:
            return

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            # Check if projector is 'Reserved' and trying to set to 'Under Maintenance'
            if current_proj_status == 'Reserved' and new_status == 'Under Maintenance':
                # Check for active future approved reservations
                cursor.execute("""
                    SELECT COUNT(*) FROM reservations
                    WHERE projector_id = %s AND status = 'Approved'
                    AND date_reserved >= CURDATE()
                    AND (date_reserved > CURDATE() OR time_end > CURTIME())
                """, (proj_id,))
                active_reservations = cursor.fetchone()[0]
                if active_reservations > 0:
                    response = messagebox.askyesno(
                        "Projector is Reserved",
                        f"This projector has {active_reservations} active approved reservations. Changing its status to '{new_status}' will make it unavailable. Do you want to proceed? (Active reservations will remain 'Approved' until manually changed.)"
                    )
                    if not response:
                        return

            cursor.execute("UPDATE projectors SET status = %s WHERE projector_id = %s", (new_status, proj_id))
            db.commit()
            messagebox.showinfo("Success", f"Projector ID {proj_id} status updated to '{new_status}'.")
            load_projectors_for_management() # Refresh the projector list
            load_all_reservations() # Refresh reservations just in case (e.g., if a new reservation was made for it immediately after freeing it up)
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    ttk.Button(manage_proj_status_frame, text="Update Projector Status", command=update_projector_status, style="Info.TButton").grid(row=0, column=2, pady=5, padx=10)


    # --- Bottom Controls (Logout Button) ---
    bottom_controls_frame = ttk.Frame(admin_win, padding="10", style="TFrame") # Explicitly apply TFrame style
    bottom_controls_frame.pack(side="bottom", fill="x")

    ttk.Button(bottom_controls_frame, text="Logout", command=admin_win.destroy, style="Dark.TButton").pack(side="right", padx=10)

    # Initial data load for admin dashboard
    load_all_reservations()
    load_projectors_for_management()

    admin_win.mainloop()