import tkinter as tk
from tkinter import messagebox, ttk
from db_connector import connect_db
from datetime import date, datetime, time # Import time as well
from PIL import Image, ImageTk
import os
import mysql.connector

# Added parent_window parameter for Toplevel
def open_student_dashboard(parent_window, student_name):
    student_win = tk.Toplevel(parent_window) # Changed to Toplevel
    student_win.title("Student Dashboard")
    student_win.geometry("1000x650") # Initial size
    student_win.minsize(900, 550)
    student_win.state('zoomed') # Maximize the window

    # --- Background Image Management ---
    base_path = os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_path, "IMAGE", "background.png")

    bg_label = None
    try:
        student_win.original_bg_image = Image.open(bg_image_path)
        bg_label = tk.Label(student_win)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        student_win.bg_photo_ref = None # Initialize a persistent reference 
    except FileNotFoundError:
        student_win.configure(bg="#800000") # Fallback to PUP maroon

    def update_background_image(event=None):
        if hasattr(student_win, 'original_bg_image') and bg_label:
            width = student_win.winfo_width()
            height = student_win.winfo_height()
            if width > 0 and height > 0:
                resized_image = student_win.original_bg_image.resize((width, height), Image.LANCZOS)
                temp_photo_image = ImageTk.PhotoImage(resized_image)
                bg_label.configure(image=temp_photo_image)
                student_win.bg_photo_ref = temp_photo_image # CRUCIAL: Store a persistent reference 

    student_win.bind('<Configure>', update_background_image)
    student_win.after_idle(update_background_image) # Initial call with slight delay

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

    # --- Main UI Element Placement (Directly in student_win) ---
    # Removed main_layout_frame, main_canvas, scrollable_content_frame

    welcome_label = ttk.Label(student_win, text=f"Welcome, {student_name}!", font=("Arial", 18, "bold"), background=root_bg_color)
    welcome_label.pack(pady=(15, 10), padx=20, fill='x')

    notebook = ttk.Notebook(student_win)
    notebook.pack(expand=True, fill='both', padx=15, pady=10)

    # Mouse wheel scrolling (bind to the Toplevel window)
    def _on_mouse_wheel(event):
        # Determine whether to scroll up or down based on event.delta or event.num
        if event.num == 4 or event.delta > 0: # Scroll up
            notebook.yview_scroll(-1, "units") # Scroll the notebook content
        elif event.num == 5 or event.delta < 0: # Scroll down
            notebook.yview_scroll(1, "units") # Scroll the notebook content
    # Note: notebook.yview_scroll might not work directly if notebook is not a canvas.
    # For a general solution without a canvas, this binding is tricky for complex layouts.
    # If content in tabs overflows, vertical scrollbars within the *tabs* are better.
    # Removing direct mouse wheel scroll for now, unless specific scrollable areas are added.
    # student_win.bind_all("<Button-4>", _on_mouse_wheel) 
    # student_win.bind_all("<Button-5>", _on_mouse_wheel)
    # student_win.bind_all("<MouseWheel>", _on_mouse_wheel)


    # --- Tab 1: Make a Reservation ---
    tab_reserve = ttk.Frame(notebook, padding="15")
    notebook.add(tab_reserve, text=" Make a Reservation ")

    reserve_frame = ttk.LabelFrame(tab_reserve, text="Reservation Form", padding="15")
    reserve_frame.pack(padx=20, pady=20, fill="x")

    form_entries = {}

    ttk.Label(reserve_frame, text="Select Projector:").pack(anchor="w", padx=10, pady=(10, 0))
    projector_combo = ttk.Combobox(reserve_frame, state="readonly", width=42, font=("Arial", 10))
    projector_combo.pack(padx=10, pady=5)
    form_entries["projector_combo"] = projector_combo

    # Initial load of projectors for the combobox
    def load_projectors_for_combo():
        db = connect_db()
        if db:
            cursor = db.cursor()
            try:
                cursor.execute("SELECT projector_id, projector_name FROM projectors WHERE status = 'Available'")
                projectors = cursor.fetchall()
                projector_combo['values'] = [f"{p[0]} - {p[1]}" for p in projectors]
            except mysql.connector.Error as err:
                messagebox.showerror("Database Error", str(err))
            finally:
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if 'db' in locals() and db:
                    db.close()
    load_projectors_for_combo()

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
            start_time = datetime.strptime(time_start_str, '%H:%M').time()
            end_time = datetime.strptime(time_end_str, '%H:%M').time()
            res_date = datetime.strptime(date_str, '%Y-%m-%d').date()

            # Basic time validation
            if start_time >= end_time:
                messagebox.showerror("Input Error", "Start time must be before end time.")
                return
            if res_date < date.today():
                messagebox.showerror("Input Error", "Reservation date cannot be in the past.")
                return
            if res_date == date.today() and start_time < datetime.now().time():
                messagebox.showerror("Input Error", "Start time for today cannot be in the past.")
                return

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

            # Check for availability and conflicts before inserting
            cursor.execute("""
                SELECT status FROM projectors WHERE projector_id = %s
            """, (proj_id,))
            proj_status = cursor.fetchone()
            if not proj_status or proj_status[0] != 'Available':
                messagebox.showwarning("Availability", f"Projector ID {proj_id} is currently '{proj_status[0]}'. Cannot reserve.")
                return
            
            # Check for overlapping 'Approved' reservations for the same projector
            cursor.execute("""
                SELECT COUNT(*) FROM reservations
                WHERE projector_id = %s AND date_reserved = %s AND status = 'Approved'
                AND (
                    (time_start < %s AND time_end > %s) 
                    OR (%s < time_end AND %s > time_start) 
                    OR (time_start = %s AND time_end = %s) 
                )
            """, (proj_id, res_date, end_time, start_time, 
                  start_time, end_time, start_time, end_time))
            conflict_count = cursor.fetchone()[0]
            if conflict_count > 0:
                messagebox.showwarning("Conflict", "This projector has an overlapping approved reservation for the selected date/time.")
                return

            cursor.execute("""
            INSERT INTO reservations (..., time_start, time_end, ...)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
            """, (student_id, proj_id, professor_name, date_str,
                start_time, end_time, purpose))

            db.commit()

            messagebox.showinfo("Success", "Reservation submitted! Awaiting admin approval.")
            for key in entry_fields:
                if key != "date_reserved":
                    form_entries[key].delete(0, tk.END)
            form_entries["projector_combo"].set('')
            load_reservations() # Refresh student's reservation history
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    ttk.Button(reserve_frame, text="Submit Reservation", command=submit_reservation, style="Accent.TButton").pack(pady=15)

    # --- Tab 2: My Reservations ---
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
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    def cancel_reservation():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a reservation to cancel.")
            return

        res_values = tree.item(selected[0])['values']
        res_id = res_values[0]
        current_status = res_values[7] # Status column
        
        if current_status in ('Rejected', 'Cancelled'):
            messagebox.showinfo("Already Processed", f"This reservation is already {current_status} and cannot be cancelled further.")
            return
        
        # Prevent cancelling past approved/pending reservations directly
        res_date_str = res_values[3] # Date column
        res_end_time_str = res_values[5] # End time column

        try:
            res_datetime = datetime.combine(datetime.strptime(res_date_str, '%Y-%m-%d').date(), 
                                            datetime.strptime(res_end_time_str, '%H:%M:%S').time())
        except ValueError: # Handle potential HH:MM if not HH:MM:SS
             res_datetime = datetime.combine(datetime.strptime(res_date_str, '%Y-%m-%d').date(), 
                                            datetime.strptime(res_end_time_str, '%H:%M').time())

        if res_datetime < datetime.now() and current_status == 'Approved':
            messagebox.showwarning("Cannot Cancel", "This reservation is already completed and cannot be cancelled.")
            return

        confirm = messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this reservation?")
        if not confirm:
            return

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            # Get projector_id before updating reservation status
            cursor.execute("SELECT projector_id FROM reservations WHERE reservation_id = %s", (res_id,))
            proj_id_result = cursor.fetchone()
            
            # Update reservation status to 'Cancelled' instead of deleting
            cursor.execute("UPDATE reservations SET status = 'Cancelled' WHERE reservation_id = %s", (res_id,))

            # If it was an 'Approved' reservation, set projector status back to 'Available'
            if current_status == 'Approved' and proj_id_result:
                proj_id = proj_id_result[0]
                cursor.execute("UPDATE projectors SET status = 'Available' WHERE projector_id = %s", (proj_id,))

            db.commit()
            messagebox.showinfo("Cancelled", "Reservation cancelled successfully.")
            load_reservations()
            # Update projector combo values after cancellation as a projector might become available
            load_projectors_for_combo()

        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'db' in locals() and db:
                db.close()

    ttk.Button(view_frame, text="Cancel Selected Reservation", command=cancel_reservation, style="Danger.TButton").pack(pady=15)

    # --- Bottom Controls (Logout Button) ---
    bottom_controls_frame = ttk.Frame(student_win, padding="10", style="TFrame") # Explicitly apply TFrame style
    bottom_controls_frame.pack(side="bottom", fill="x")

    ttk.Button(bottom_controls_frame, text="Logout", command=student_win.destroy, style="Dark.TButton").pack(side="right", padx=10)

    # Initial data load
    load_reservations()

    student_win.mainloop()