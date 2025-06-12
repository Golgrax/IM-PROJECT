import tkinter as tk
from tkinter import messagebox, ttk
from db_connector import connect_db
from PIL import Image, ImageTk
import os
import mysql.connector

def open_admin_dashboard(admin_name):
    admin_win = tk.Tk()
    admin_win.title("Admin Dashboard")
    admin_win.geometry("1200x700")
    admin_win.minsize(900, 600)

    # --- Background Image Management ---
    base_path = os.path.dirname(os.path.abspath(__file__))
    bg_image_path = os.path.join(base_path, "IMAGE", "background.png")

    bg_label = None # Initialize to None for error handling
    try:
        admin_win.original_bg_image = Image.open(bg_image_path) # Store original image on window
        bg_label = tk.Label(admin_win)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except FileNotFoundError:
        admin_win.configure(bg="#800000") # Fallback to PUP maroon if image missing

    def update_background_image(event=None):
        if hasattr(admin_win, 'original_bg_image') and bg_label:
            width = admin_win.winfo_width()
            height = admin_win.winfo_height()
            if width > 0 and height > 0:
                resized_image = admin_win.original_bg_image.resize((width, height), Image.LANCZOS)
                temp_photo_image = ImageTk.PhotoImage(resized_image)
                bg_label.configure(image=temp_photo_image)
                bg_label.image = temp_photo_image # Crucial for persistent reference
                # No need for admin_win.bg_photo_image = temp_photo_image if bg_label.image is enough

    admin_win.bind('<Configure>', update_background_image)
    admin_win.after(50, update_background_image) # Initial call with slight delay


    # --- Main Layout Frame (tk.Frame - sits over the background image) ---
    main_layout_frame = tk.Frame(admin_win, bg="#F0F0F0") # Default light background
    main_layout_frame.pack(fill='both', expand=True, padx=20, pady=20) # Padding from window edges
    main_layout_frame.grid_rowconfigure(0, weight=1) # Canvas row expands vertically
    main_layout_frame.grid_columnconfigure(0, weight=1) # Canvas column expands horizontally

    # --- Scrollable Content Setup ---
    main_canvas = tk.Canvas(main_layout_frame, highlightthickness=0, bg="#F0F0F0") # Default light background
    main_canvas.grid(row=0, column=0, sticky="nsew")

    v_scrollbar = ttk.Scrollbar(main_layout_frame, orient="vertical", command=main_canvas.yview)
    v_scrollbar.grid(row=0, column=1, sticky="ns") # Vertical scrollbar always present

    # Horizontal scrollbar removed/disabled by default
    # If horizontal scrolling is truly needed for tables etc., you'd bind main_canvas.xview
    # and use h_scrollbar.grid, but often it's better to make content fit or resize tables.
    main_canvas.configure(yscrollcommand=v_scrollbar.set) # Only vertical scroll

    # Create a tk.Frame inside the canvas for all content
    # It must have a fixed width for horizontal centering
    SCROLL_CONTENT_WIDTH = 1000 # Define a fixed width for the scrollable content area
    scrollable_content_frame = tk.Frame(main_canvas, bg="white", width=SCROLL_CONTENT_WIDTH)
    scrollable_content_frame.pack_propagate(False) # Prevent frame from resizing to content
    scrollable_content_frame.bind("<Configure>", lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))) # Update scrollregion

    # Create window in canvas for the content frame, centered horizontally
    # Anchor 'n' (north) aligns top-center of the window to the canvas position
    main_canvas.create_window((main_canvas.winfo_width() / 2, 0), window=scrollable_content_frame, anchor="n")

    # Function to reposition content frame if canvas width changes
    def center_scrollable_content(event=None):
        main_canvas.coords(scrollable_content_frame, main_canvas.winfo_width() / 2, 0)
        main_canvas.configure(scrollregion=main_canvas.bbox("all"))

    main_canvas.bind('<Configure>', center_scrollable_content) # Bind to canvas resize


    # Mouse wheel scrolling
    def _on_mouse_wheel(event):
        if event.num == 4 or event.delta > 0:
            main_canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            main_canvas.yview_scroll(1, "units")
    admin_win.bind_all("<Button-4>", _on_mouse_wheel) # Linux wheel up
    admin_win.bind_all("<Button-5>", _on_mouse_wheel) # Linux wheel down
    admin_win.bind_all("<MouseWheel>", _on_mouse_wheel) # Windows/macOS


    # --- UI Element Definitions (All elements go into scrollable_content_frame) ---
    # Add padding to elements packed within scrollable_content_frame to create internal spacing
    welcome_label = ttk.Label(scrollable_content_frame, text=f"Welcome, {admin_name}!", font=("Arial", 18, "bold"))
    welcome_label.pack(pady=20, padx=20) # Added padx

    add_frame = ttk.LabelFrame(scrollable_content_frame, text="Add New Projector", padding="10")
    add_frame.pack(fill="x", pady=10, padx=20) # Added padx

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

    pending_frame = ttk.LabelFrame(scrollable_content_frame, text="Pending & Approved Reservations", padding="10")
    pending_frame.pack(fill="both", expand=True, pady=10, padx=20) # Added padx

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

    btn_frame = ttk.Frame(scrollable_content_frame, padding="5")
    btn_frame.pack(pady=5, padx=20) # Added padx

    def update_reservation_status(new_status):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a reservation to update.")
            return

        res_id = tree.item(selected[0])['values'][0]
        current_reservation_status = tree.item(selected[0])['values'][8] 

        confirm = messagebox.askyesno(f"{new_status} Reservation", f"Are you sure you want to mark this reservation as {new_status}?")
        if not confirm:
            return

        db = connect_db()
        if not db: return
        cursor = db.cursor()
        try:
            cursor.execute("SELECT projector_id FROM reservations WHERE reservation_id = %s", (res_id,))
            proj_id_result = cursor.fetchone()
            if not proj_id_result:
                messagebox.showerror("Error", "Reservation not found in database.")
                return
            proj_id = proj_id_result[0]

            cursor.execute("UPDATE reservations SET status = %s WHERE reservation_id = %s", (new_status, res_id))

            if new_status == 'Approved' and current_reservation_status != 'Approved':
                cursor.execute("UPDATE projectors SET status = 'Reserved' WHERE projector_id = %s", (proj_id,))
            elif new_status in ('Cancelled', 'Rejected') and current_reservation_status == 'Approved':
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

    projector_frame = ttk.LabelFrame(scrollable_content_frame, text="Projector List", padding="10")
    projector_frame.pack(fill="both", expand=True, pady=10, padx=20) # Added padx

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

    manage_proj_status_frame = ttk.LabelFrame(scrollable_content_frame, text="Manage Projector Status", padding="10")
    manage_proj_status_frame.pack(fill="x", pady=10, padx=20) # Added padx

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
            if current_proj_status == 'Reserved' and new_status == 'Under Maintenance':
                response = messagebox.askyesno(
                    "Projector is Reserved",
                    "This projector is currently reserved. Changing its status to 'Under Maintenance' might affect an active reservation. Do you want to proceed and effectively make it unavailable for its current reservation?"
                )
                if not response:
                    return

            cursor.execute("UPDATE projectors SET status = %s WHERE projector_id = %s", (new_status, proj_id))
            db.commit()
            messagebox.showinfo("Success", f"Projector ID {proj_id} status updated to '{new_status}'.")
            load_projectors()
            load_pending_reservations()
        except mysql.connector.Error as err:
            messagebox.showerror("Database Error", str(err))
        finally:
            cursor.close()
            db.close()

    ttk.Button(manage_proj_status_frame, text="Update Projector Status", command=update_projector_status, style="Info.TButton").grid(row=0, column=2, pady=5, padx=10)

    # --- Bottom Controls (Logout & Theme Toggle - fixed at bottom) ---
    bottom_controls_frame = ttk.Frame(main_layout_frame, padding="10")
    bottom_controls_frame.grid(row=2, column=0, columnspan=2, sticky="ew")

    is_dark_mode = False

    def apply_theme(mode):
        nonlocal is_dark_mode
        is_dark_mode = (mode == 'dark')

        # PUP Theme Colors
        if mode == 'dark':
            root_bg = "#333333" # General dark background for window if no image
            frame_bg = "#3A3A3A" # Dark grey for main content frames (simulates slight transparency)
            label_frame_bg = "#555555" # Darker grey for labelframes
            fg_color = "white"
            heading_bg = "#666666" # Dark grey for treeview headers
            treeview_bg = "#555555"
            treeview_fg = "white"
            treeview_selected = "#DAA520" # PUP Yellow for selection (gold)
            accent_button_bg = "#FFD700" # Bright yellow for accents
            accent_button_fg = "black"
            danger_button_bg = "#dc3545" # Red
            dark_button_bg = "#6c757d" # Grey
            info_button_bg = "#007bff" # Blue
        else: # Light mode (PUP inspired)
            root_bg = "#F0F0F0"
            frame_bg = "white"
            label_frame_bg = "#E0E0E0"
            fg_color = "black"
            heading_bg = "#D0D0D0"
            treeview_bg = "white"
            treeview_fg = "black"
            treeview_selected = "#ADD8E6"
            accent_button_bg = "#800000" # PUP Maroon for accents
            accent_button_fg = "white"
            danger_button_bg = "#f44336"
            dark_button_bg = "#555555"
            info_button_bg = "#2196F3"

        # Update backgrounds for Tkinter widgets (non-ttk)
        main_layout_frame.configure(bg=root_bg)
        scrollable_content_frame.configure(bg=frame_bg)
        main_canvas.configure(background=frame_bg)

        # Configure ttk styles
        style = ttk.Style()
        style.theme_use('clam')

        style.configure("TFrame", background=frame_bg)
        style.configure("TLabel", background=frame_bg, foreground=fg_color, font=("Arial", 10))
        style.configure("TLabelFrame", background=label_frame_bg, foreground=fg_color, font=("Arial", 12, "bold"))
        style.configure("TLabelframe.Label", background=label_frame_bg, foreground=fg_color)
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"), background=heading_bg, foreground=fg_color)
        style.configure("Treeview", font=("Arial", 10), rowheight=25, background=treeview_bg, foreground=treeview_fg, fieldbackground=treeview_bg)
        style.map("Treeview", background=[('selected', treeview_selected)])

        style.configure("TEntry", fieldbackground=frame_bg, foreground=fg_color)
        style.configure("TCombobox", fieldbackground=frame_bg, foreground=fg_color)
        style.configure("TCombobox.readonly", fieldbackground=frame_bg, foreground=fg_color)
        style.configure("TNotebook", background=frame_bg)
        style.configure("TNotebook.Tab", background=label_frame_bg, foreground=fg_color)
        style.map("TNotebook.Tab", background=[('selected', frame_bg)], foreground=[('selected', fg_color)])

        style.configure("Accent.TButton", background=accent_button_bg, foreground=accent_button_fg, font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Accent.TButton", background=[('active', "#A52A2A" if not is_dark_mode else "#218838")])
        style.configure("Danger.TButton", background=danger_button_bg, foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Danger.TButton", background=[('active', "#D32F2F" if not is_dark_mode else "#c82333")])
        style.configure("Dark.TButton", background=dark_button_bg, foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Dark.TButton", background=[('active', "#777777" if not is_dark_mode else "#5a6268")])
        style.configure("Info.TButton", background=info_button_bg, foreground="white", font=("Arial", 10, "bold"), borderwidth=0)
        style.map("Info.TButton", background=[('active', "#1976D2" if not is_dark_mode else "#0069d9")])

        # Manually update specific non-ttk labels
        welcome_label.configure(background=frame_bg, foreground=fg_color)


    # --- Theme Controls (created here as well) ---
    def toggle_theme():
        if is_dark_mode:
            apply_theme('light')
        else:
            apply_theme('dark')

    ttk.Button(bottom_controls_frame, text="Toggle Theme", command=toggle_theme, style="Dark.TButton").pack(side="left", padx=10)
    ttk.Button(bottom_controls_frame, text="Logout", command=admin_win.destroy, style="Dark.TButton").pack(side="right", padx=10)

    # Initial Theme Application
    admin_win.after(10, lambda: apply_theme('light'))

    # Initial data loads
    load_pending_reservations()
    load_projectors()

    admin_win.mainloop()