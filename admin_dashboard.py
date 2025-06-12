import customtkinter as ctk
from tkinter import messagebox
from datetime import date # Keep for date.today()

class AdminDashboard:
    def __init__(self, master, admin_name, db_manager):
        self.master = master
        self.db = db_manager # Use the passed DBManager instance
        self.master.title("Admin Dashboard")
        self.master.geometry("1200x700") # Increased size for better layout
        self.master.configure(fg_color="#f4f4f4") # Light background for CTk
        self.master.resizable(True, True)

        self.master.grab_set() # Make the dashboard modal
        self.master.transient(master.winfo_toplevel()) # Link to parent window

        ctk.set_appearance_mode("light") # Set light mode for this window

        # Root frame with grid layout
        root_frame = ctk.CTkFrame(self.master, fg_color="#f4f4f4")
        root_frame.pack(fill='both', expand=True, padx=20, pady=20) # Added padding

        # Configure grid rows and columns
        root_frame.grid_rowconfigure(1, weight=1) # Reservation treeview
        root_frame.grid_rowconfigure(3, weight=1) # Projector treeview
        root_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(root_frame, text=f"Welcome, {admin_name}!", font=("Arial", 22, "bold"), text_color="#333333", fg_color="transparent").grid(row=0, column=0, pady=20, sticky="ew")

        # --- Add Projector Section ---
        add_frame = ctk.CTkFrame(root_frame, fg_color="white", corner_radius=10)
        add_frame.grid(row=1, column=0, pady=10, padx=10, sticky="ew") # Adjusted row, column

        ctk.CTkLabel(add_frame, text="Add New Projector", font=("Arial", 16, "bold"), text_color="#333333", fg_color="transparent").grid(row=0, column=0, columnspan=2, pady=(15, 10))

        ctk.CTkLabel(add_frame, text="Projector Name:", text_color="#333333", fg_color="transparent").grid(row=1, column=0, sticky="w", padx=20, pady=5)
        self.proj_name_entry = ctk.CTkEntry(add_frame, width=250)
        self.proj_name_entry.grid(row=1, column=1, pady=5, padx=20, sticky="ew")

        ctk.CTkLabel(add_frame, text="Model:", text_color="#333333", fg_color="transparent").grid(row=2, column=0, sticky="w", padx=20, pady=5)
        self.model_entry = ctk.CTkEntry(add_frame, width=250)
        self.model_entry.grid(row=2, column=1, pady=5, padx=20, sticky="ew")

        ctk.CTkButton(add_frame, text="Add Projector", command=self.add_projector, fg_color="#4CAF50", hover_color="#45a049", text_color="white", font=("Arial", 14, "bold")).grid(row=3, column=0, columnspan=2, pady=15)

        add_frame.grid_columnconfigure(1, weight=1) # Make entry column expandable


        # --- Reservation Section ---
        pending_frame = ctk.CTkFrame(root_frame, fg_color="white", corner_radius=10)
        pending_frame.grid(row=2, column=0, pady=10, padx=10, sticky="nsew") # Adjusted row, column

        ctk.CTkLabel(pending_frame, text="Pending & Approved Reservations", font=("Arial", 16, "bold"), text_color="#333333", fg_color="transparent").pack(pady=10)

        # Using ttk.Treeview still, as CustomTkinter doesn't have a direct replacement
        self.cols = ("Reservation ID", "Student Name", "Projector", "Professor", "Date", "Start", "End", "Purpose", "Status")
        self.tree = ctk.CTkTreeview(pending_frame, columns=self.cols, show='headings') # Using CTkTreeview for better theming
        for col in self.cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100 if col != "Purpose" else 200, anchor="center") # Anchor for centering text
        self.tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Approve / Reject Buttons ---
        btn_frame = ctk.CTkFrame(root_frame, fg_color="transparent")
        btn_frame.grid(row=3, column=0, pady=5, sticky="ew")

        ctk.CTkButton(btn_frame, text="Approve", command=lambda: self.update_reservation_status("Approved"), fg_color="#4CAF50", hover_color="#45a049", text_color="white", font=("Arial", 14, "bold")).pack(side="left", padx=10, expand=True)
        ctk.CTkButton(btn_frame, text="Reject", command=lambda: self.update_reservation_status("Rejected"), fg_color="#f44336", hover_color="#da3a3a", text_color="white", font=("Arial", 14, "bold")).pack(side="left", padx=10, expand=True)

        # --- Projector List Section ---
        projector_frame = ctk.CTkFrame(root_frame, fg_color="white", corner_radius=10)
        projector_frame.grid(row=4, column=0, pady=10, padx=10, sticky="nsew") # Adjusted row, column

        ctk.CTkLabel(projector_frame, text="Projector List", font=("Arial", 16, "bold"), text_color="#333333", fg_color="transparent").pack(pady=10)

        self.proj_cols = ("Projector ID", "Name", "Model", "Status")
        self.proj_tree = ctk.CTkTreeview(projector_frame, columns=self.proj_cols, show='headings') # Using CTkTreeview
        for col in self.proj_cols:
            self.proj_tree.heading(col, text=col)
            self.proj_tree.column(col, width=150, anchor="center")
        self.proj_tree.pack(fill="both", expand=True, padx=10, pady=10)

        # --- Logout button frame pinned at the bottom ---
        logout_frame = ctk.CTkFrame(root_frame, fg_color="transparent")
        logout_frame.grid(row=5, column=0, pady=(0, 10), sticky="ew")
        ctk.CTkButton(logout_frame, text="Logout", command=self.master.destroy, fg_color="#555555", hover_color="#444444", text_color="white", font=("Arial", 14, "bold")).pack(pady=10)

        # Load data when window opens
        self.load_pending_reservations()
        self.load_projectors()

    def add_projector(self):
        proj_name = self.proj_name_entry.get().strip()
        model = self.model_entry.get().strip()

        if not proj_name or not model:
            messagebox.showwarning("Input Error", "Please fill in all fields.")
            return

        if self.db.add_projector(proj_name, model):
            messagebox.showinfo("Success", f"Projector '{proj_name}' added.")
            self.proj_name_entry.delete(0, ctk.END)
            self.model_entry.delete(0, ctk.END)
            self.load_projectors()
        else:
            messagebox.showerror("Database Error", "Failed to add projector. Check database connection or if projector name already exists.")

    def load_pending_reservations(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        records = self.db.get_admin_dashboard_reservations()
        if records:
            for r in records:
                self.tree.insert('', 'end', values=r)
        else:
            print("No pending/approved reservations found.") # For debugging

    def update_reservation_status(self, new_status):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Selection Error", "Please select a reservation to update.")
            return

        res_id = self.tree.item(selected[0])['values'][0]
        current_status = self.tree.item(selected[0])['values'][-1] # Get current status from treeview

        if current_status == new_status:
            messagebox.showinfo("Status Unchanged", f"Reservation is already {new_status}.")
            return

        confirm = messagebox.askyesno(f"{new_status} Reservation", f"Are you sure you want to mark Reservation ID {res_id} as {new_status}?")
        if not confirm:
            return

        proj_id = self.db.get_projector_id_from_reservation(res_id)
        if proj_id is None:
            messagebox.showerror("Error", "Could not find associated projector for this reservation.")
            return

        if self.db.update_reservation_status(res_id, new_status, proj_id):
            messagebox.showinfo("Success", f"Reservation marked as {new_status}.")
            self.load_pending_reservations()
            self.load_projectors() # Refresh projector list as its status might change
        else:
            messagebox.showerror("Database Error", "Failed to update reservation status.")

    def load_projectors(self):
        for i in self.proj_tree.get_children():
            self.proj_tree.delete(i)
        records = self.db.get_all_projectors()
        if records:
            for r in records:
                self.proj_tree.insert('', 'end', values=r)
        else:
            print("No projectors found.") # For debugging
