import customtkinter as ctk
from tkinter import messagebox
from datetime import date, datetime

class StudentDashboard:
    def __init__(self, master, student_name, db_manager):
        self.master = master
        self.student_name = student_name
        self.db = db_manager # Use the passed DBManager instance
        self.student_id = self.db.get_student_id_by_name(self.student_name) # Get student ID

        if self.student_id is None:
            messagebox.showerror("Error", "Student not found in database. Please contact admin.")
            master.destroy()
            return

        self.master.title("Student Dashboard")
        self.master.geometry("1000x600")
        self.master.configure(fg_color="#f4f4f4") # Light background
        self.master.resizable(True, True)

        self.master.grab_set() # Make the dashboard modal
        self.master.transient(master.winfo_toplevel()) # Link to parent window

        ctk.set_appearance_mode("light") # Set light mode for this window

        ctk.CTkLabel(self.master, text=f"Welcome, {self.student_name}!", font=("Arial", 22, "bold"), text_color="#333333", fg_color="transparent").pack(pady=(15, 10))

        self.notebook = ctk.CTkTabview(self.master, fg_color="transparent")
        self.notebook.pack(expand=True, fill='both', padx=15, pady=10)

        # --- TAB 1: Make a Reservation ---
        tab_reserve = self.notebook.add("Make a Reservation")
        tab_reserve.grid_columnconfigure(0, weight=1) # Make column expandable for centering

        reserve_frame = ctk.CTkFrame(tab_reserve, fg_color="white", corner_radius=10)
        reserve_frame.pack(padx=20, pady=20, fill="x", anchor="center")

        ctk.CTkLabel(reserve_frame, text="Reservation Form", font=("Arial", 16, "bold"), text_color="#333333", fg_color="transparent").pack(pady=(10, 15))


        ctk.CTkLabel(reserve_frame, text="Select Projector:", text_color="#333333", fg_color="transparent").pack(anchor="w", padx=20)
        self.projector_combo = ctk.CTkOptionMenu(reserve_frame, width=250, values=[])
        self.projector_combo.pack(padx=20, pady=5)
        self.load_projectors_for_reservation()

        ctk.CTkLabel(reserve_frame, text="Professor Name:", text_color="#333333", fg_color="transparent").pack(anchor="w", padx=20)
        self.prof_entry = ctk.CTkEntry(reserve_frame, width=250)
        self.prof_entry.pack(padx=20, pady=5)

        ctk.CTkLabel(reserve_frame, text="Date (YYYY-MM-DD):", text_color="#333333", fg_color="transparent").pack(anchor="w", padx=20)
        self.date_entry = ctk.CTkEntry(reserve_frame, width=250)
        self.date_entry.insert(0, str(date.today()))
        self.date_entry.pack(padx=20, pady=5)

        ctk.CTkLabel(reserve_frame, text="Start Time (HH:MM):", text_color="#333333", fg_color="transparent").pack(anchor="w", padx=20)
        self.start_entry = ctk.CTkEntry(reserve_frame, width=250)
        self.start_entry.pack(padx=20, pady=5)

        ctk.CTkLabel(reserve_frame, text="End Time (HH:MM):", text_color="#333333", fg_color="transparent").pack(anchor="w", padx=20)
        self.end_entry = ctk.CTkEntry(reserve_frame, width=250)
        self.end_entry.pack(padx=20, pady=5)

        ctk.CTkLabel(reserve_frame, text="Purpose:", text_color="#333333", fg_color="transparent").pack(anchor="w", padx=20)
        self.purpose_entry = ctk.CTkEntry(reserve_frame, width=250)
        self.purpose_entry.pack(padx=20, pady=5)

        ctk.CTkButton(reserve_frame, text="Submit Reservation", command=self.submit_reservation,
                      fg_color="#4CAF50", hover_color="#45a049", text_color="white", font=("Arial", 14, "bold")).pack(pady=15)

        # --- TAB 2: View My Reservations ---
        tab_view = self.notebook.add("My Reservations")
        tab_view.grid_columnconfigure(0, weight=1)

        view_frame = ctk.CTkFrame(tab_view, fg_color="white", corner_radius=10)
        view_frame.pack(padx=20, pady=20, expand=True, fill="both")

        ctk.CTkLabel(view_frame, text="Your Reservation Records", font=("Arial", 16, "bold"), text_color="#333333", fg_color="transparent").pack(pady=(10, 15))

        self.columns = ("ID", "Projector", "Professor", "Date", "Start", "End", "Purpose", "Status")
        self.tree = ctk.CTkTreeview(view_frame, columns=self.columns, show='headings')
        for col in self.columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=110 if col != "Purpose" else 200, anchor="center")
        self.tree.pack(expand=True, fill='both', padx=10, pady=10)

        ctk.CTkButton(view_frame, text="Cancel Selected Reservation", command=self.cancel_reservation,
                      fg_color="#f44336", hover_color="#da3a3a", text_color="white", font=("Arial", 14, "bold")).pack(pady=15)

        # --- Logout Button ---
        ctk.CTkButton(self.master, text="Logout", command=self.logout,
                      fg_color="#333", hover_color="#222", text_color="white", font=("Arial", 14, "bold")).pack(pady=10)

        self.load_reservations()

    def load_projectors_for_reservation(self):
        projectors = self.db.get_available_projectors_for_student_combo()
        if projectors:
            self.projector_combo.configure(values=[f"{p[0]} - {p[1]}" for p in projectors])
            self.projector_combo.set(f"{projectors[0][0]} - {projectors[0][1]}") # Set default value
        else:
            self.projector_combo.configure(values=["No projectors available"])
            self.projector_combo.set("No projectors available")
            self.projector_combo.configure(state="disabled") # Disable if no projectors

    def submit_reservation(self):
        proj_selection = self.projector_combo.get()
        prof_name = self.prof_entry.get().strip()
        date_str = self.date_entry.get().strip()
        start_time_str = self.start_entry.get().strip()
        end_time_str = self.end_entry.get().strip()
        purpose = self.purpose_entry.get().strip()

        if proj_selection == "No projectors available" or not all([proj_selection, prof_name, date_str, start_time_str, end_time_str, purpose]):
            messagebox.showwarning("Input Error", "Please complete all fields and ensure a projector is selected.")
            return

        try:
            proj_id = int(proj_selection.split(" - ")[0])
            datetime.strptime(date_str, '%Y-%m-%d')
            datetime.strptime(start_time_str, '%H:%M')
            datetime.strptime(end_time_str, '%H:%M')
        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid date or time format. Use YYYY-MM-DD and HH:MM. Error: {e}")
            return

        if self.db.add_reservation(self.student_id, proj_id, prof_name, date_str, start_time_str, end_time_str, purpose):
            messagebox.showinfo("Success", "Reservation submitted! Awaiting admin approval.")
            # Clear fields
            self.prof_entry.delete(0, ctk.END)
            self.date_entry.delete(0, ctk.END)
            self.date_entry.insert(0, str(date.today()))
            self.start_entry.delete(0, ctk.END)
            self.end_entry.delete(0, ctk.END)
            self.purpose_entry.delete(0, ctk.END)
            self.load_projectors_for_reservation() # Refresh available projectors
            self.load_reservations() # Refresh my reservations tab
        else:
            messagebox.showerror("Database Error", "Failed to submit reservation.")

    def load_reservations(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        records = self.db.get_student_reservations(self.student_id)
        if records:
            for row in records:
                self.tree.insert('', 'end', values=row)
        else:
            print("No reservations found for this student.") # For debugging

    def cancel_reservation(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Select a reservation to cancel.")
            return

        res_id = self.tree.item(selected[0])['values'][0]
        current_status = self.tree.item(selected[0])['values'][-1]

        if current_status not in ('Pending', 'Approved'):
            messagebox.showinfo("Cannot Cancel", f"Reservation is already '{current_status}' and cannot be cancelled.")
            return


        confirm = messagebox.askyesno("Confirm Cancellation", "Are you sure you want to cancel this reservation?")
        if not confirm:
            return

        if self.db.cancel_student_reservation(res_id):
            messagebox.showinfo("Cancelled", "Reservation cancelled successfully.")
            self.load_reservations() # Refresh my reservations
            self.load_projectors_for_reservation() # Refresh available projectors
        else:
            messagebox.showerror("Database Error", "Failed to cancel reservation.")

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.master.destroy()