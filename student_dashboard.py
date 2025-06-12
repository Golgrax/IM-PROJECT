import tkinter as tk
from tkinter import messagebox, ttk
from db_connector import connect_db
from datetime import date, datetime
from PIL import Image, ImageTk
import os
import mysql.connector

def open_student_dashboard(student_name):
    student_win = tk.Tk()
    student_win.title("Student Dashboard")
    student_win.geometry("1000x650")
    student_win.minsize(900, 550)

    # --- Background Image Management ---
    base_path = os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_path, "IMAGE", "background.png")

    bg_label = None # Declare bg_label here
    try:
        student_win.original_bg_image = Image.open(bg_image_path) # Store original image on window
        bg_label = tk.Label(student_win)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except FileNotFoundError:
        student_win.configure(bg="#800000") # Fallback to PUP maroon

    def update_background_image(event=None):
        if hasattr(student_win, 'original_bg_image') and bg_label:
            width = student_win.winfo_width()
            height = student_win.winfo_height()
            if width > 0 and height > 0:
                resized_image = student_win.original_bg_image.resize((width, height), Image.LANCZOS)
                student_win.bg_photo_image = ImageTk.PhotoImage(resized_image) # Strong reference
                bg_label.configure(image=student_win.bg_photo_image)

    student_win.bind('<Configure>', update_background_image)
    student_win.after(100, update_background_image) # Initial call

    # --- Scrollable Content Setup ---
    main_canvas = tk.Canvas(student_win, highlightthickness=0)
    main_canvas.pack(side="top", fill="both", expand=True, padx=0, pady=0)

    v_scrollbar = ttk.Scrollbar(student_win, orient="vertical", command=main_canvas.yview)
    h_scrollbar = ttk.Scrollbar(student_win, orient="horizontal", command=main_canvas.xview)
    v_scrollbar.pack(side="right", fill="y")
    h_scrollbar.pack(side="bottom", fill="x")

    main_canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)

    scrollable_content_frame = ttk.Frame(main_canvas, padding="20")
    main_canvas.create_window((0, 0), window=scrollable_content_frame, anchor="nw")

    def on_frame_configure(event):
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    scrollable_content_frame.bind("<Configure>", on_frame_configure)

    def _on_mouse_wheel(event):
        if event.num == 4 or event.delta > 0:
            main_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            main_canvas.yview_scroll(1, "units")
    main_canvas.bind_all("<Button-4>", _on_mouse_wheel)
    main_canvas.bind_all("<Button-5>", _on_mouse_wheel)
    main_canvas.bind_all("<MouseWheel>", _on_mouse_wheel)


    # --- UI Element Definitions (All elements go into scrollable_content_frame) ---
    welcome_label = ttk.Label(scrollable_content_frame, text=f"Welcome, {student_name}!", font=("Arial", 18, "bold"))
    welcome_label.pack(pady=(15, 10))

    notebook = ttk.Notebook(scrollable_content_frame)
    notebook.pack(expand=True, fill='both', padx=15, pady=10)

    tab_reserve = ttk.Frame(notebook, padding="15")
    notebook.add(tab_reserve, text=" Make a Reservation ")

    reserve_frame = ttk.LabelFrame(tab_reserve, text="Reservation Form", padding="15")
    reserve_frame.pack(padx=20, pady=20, fill="x")

    form_entries = {}

    ttk.Label(reserve_frame, text="Select Projector:").pack(anchor="w", padx=10, pady=(10, 0))
    projector_combo = ttk.Combobox(reserve_frame, state="readonly", width=42, font=("Arial", 10))
    projector_combo.pack(padx=10, pady=5)
    form_entries["projector_combo"] = projector_combo

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
            cursor.close()
            db.close()

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
            db_conn_for_combo = connect_db()
            if db_conn_for_combo:
                cursor_for_combo = db_conn_for_combo.cursor()
                try:
                    cursor_for_combo.execute("SELECT projector_id, projector_name FROM projectors WHERE status = 'Available'")
                    projectors = cursor_for_combo.fetchall()
                    projector_combo['values'] = [f"{p[0]} - {p[1]}" for p in projectors]
                except mysql.connector.Error:
                    pass
                finally:
                    cursor_for_combo.close()
                    db_conn_for_combo.close()


        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    ttk.Button(view_frame, text="Cancel Selected Reservation", command=cancel_reservation, style="Danger.TButton").pack(pady=15)

    bottom_controls_frame = ttk.Frame(student_win, padding="10")
    bottom_controls_frame.pack(side="bottom", fill="x")

    is_dark_mode = False # Keep this outside apply_theme for persistent state

    # --- Theme Configuration (Light and Dark Modes - Defined after frames are created) ---
    def apply_theme(mode):
        nonlocal is_dark_mode
        is_dark_mode = (mode == 'dark')

        # PUP Theme Colors
        if mode == 'dark':
            bg_color = "#333333"
            fg_color = "white"
            frame_bg_color = "#4C0000"
            label_frame_bg_color = "#555555" # Use slightly different for contrast
            heading_bg = "#800000"
            treeview_bg = "#555555"
            treeview_fg = "white"
            treeview_selected = "#DAA520"
            accent_button_bg = "#FFD700"
            accent_button_fg = "black"
            danger_button_bg = "#dc3545"
            dark_button_bg = "#6c757d"
        else: # Light mode (PUP inspired)
            bg_color = "#F0F0F0"
            fg_color = "black"
            frame_bg_color = "white"
            label_frame_bg_color = "#F0F0F0"
            heading_bg = "#E0E0E0"
            treeview_bg = "white"
            treeview_fg = "black"
            treeview_selected = "#ADD8E6"
            accent_button_bg = "#800000"
            accent_button_fg = "white"
            danger_button_bg = "#f44336"
            dark_button_bg = "#555555"

        if not hasattr(student_win, 'original_bg_image'):
            student_win.configure(bg=bg_color)

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
        style.configure("TCombobox.readonly", fieldbackground=frame_bg_color, foreground=fg_color)

        style.configure("Accent.TButton", background=accent_button_bg, foreground=accent_button_fg, font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Accent.TButton", background=[('active', "#A52A2A" if not is_dark_mode else "#218838")]) # Brown or darker green
        style.configure("Danger.TButton", background=danger_button_bg, foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Danger.TButton", background=[('active', "#D32F2F" if not is_dark_mode else "#c82333")])
        style.configure("Dark.TButton", background=dark_button_bg, foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Dark.TButton", background=[('active', "#777777" if not is_dark_mode else "#5a6268")])

        # Manually update specific labels and canvas
        welcome_label.configure(background=frame_bg_color, foreground=fg_color)
        main_canvas.configure(background=frame_bg_color)
        main_canvas.update_idletasks() # Ensure canvas redraws

        # Reload projector combo values to update style and availability
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
                cursor.close()
                db.close()

    def toggle_theme():
        if is_dark_mode:
            apply_theme('light')
        else:
            apply_theme('dark')

    ttk.Button(bottom_controls_frame, text="Toggle Theme", command=toggle_theme, style="Dark.TButton").pack(side="left", padx=10)
    ttk.Button(bottom_controls_frame, text="Logout", command=student_win.destroy, style="Dark.TButton").pack(side="right", padx=10)

    # Initial data load and theme application
    load_reservations()
    student_win.after(10, lambda: apply_theme('light'))

    student_win.mainloop()