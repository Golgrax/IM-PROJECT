import mysql.connector
from mysql.connector import Error

class DBManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None

    def connect(self):
        """Establishes a database connection if not already connected."""
        if self.connection is None or not self.connection.is_connected():
            try:
                self.connection = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database
                )
                print("Database connection successful.")
            except Error as e:
                print(f"Error connecting to MySQL database: {e}")
                self.connection = None
        return self.connection

    def close(self):
        """Closes the database connection if it's open."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed.")

    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """
        Executes a database query.
        Returns:
            - True for successful DML (INSERT, UPDATE, DELETE)
            - Fetched data for SELECT queries
            - False if an error occurs
        """
        conn = self.connect()
        if not conn:
            return False

        cursor = None
        try:
            cursor = conn.cursor()
            cursor.execute(query, params or ()) # Ensure params is iterable
            if query.strip().upper().startswith(("INSERT", "UPDATE", "DELETE")):
                conn.commit()
                return True # Successful DML operation
            else: # SELECT query
                if fetch_one:
                    return cursor.fetchone()
                if fetch_all:
                    return cursor.fetchall()
                return None
        except Error as e:
            print(f"Database query error: {e}")
            conn.rollback() # Rollback changes on error
            return False
        finally:
            if cursor:
                cursor.close()

    # --- Student related operations ---
    def get_student_credentials(self, username):
        """Fetches student password for login verification."""
        query = "SELECT password FROM students WHERE name = %s"
        result = self.execute_query(query, (username,), fetch_one=True)
        return result[0] if result else None

    def get_student_id_by_name(self, student_name):
        """Fetches student_id by name."""
        query = "SELECT student_id FROM students WHERE name = %s"
        result = self.execute_query(query, (student_name,), fetch_one=True)
        return result[0] if result else None

    # --- Projector related operations ---
    def add_projector(self, projector_name, model):
        """Adds a new projector record."""
        query = "INSERT INTO projectors (projector_name, model, status) VALUES (%s, %s, 'Available')"
        return self.execute_query(query, (projector_name, model))

    def get_all_projectors(self):
        """Fetches all projector records."""
        query = "SELECT projector_id, projector_name, model, status FROM projectors"
        return self.execute_query(query, fetch_all=True)

    def get_available_projectors_for_student_combo(self):
        """Fetches projector_id and name for available projectors."""
        query = "SELECT projector_id, projector_name FROM projectors WHERE status = 'Available'"
        return self.execute_query(query, fetch_all=True)

    def update_projector_status(self, projector_id, new_status):
        """Updates a projector's status."""
        query = "UPDATE projectors SET status = %s WHERE projector_id = %s"
        return self.execute_query(query, (new_status, projector_id))

    # --- Reservation related operations ---
    def add_reservation(self, student_id, projector_id, professor_name, date_reserved, time_start, time_end, purpose):
        """Adds a new reservation record."""
        query = """
            INSERT INTO reservations (student_id, projector_id, professor_name, date_reserved,
            time_start, time_end, purpose, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'Pending')
        """
        return self.execute_query(query, (student_id, projector_id, professor_name, date_reserved, time_start, time_end, purpose))

    def get_student_reservations(self, student_id):
        """Fetches all reservations for a specific student."""
        query = """
            SELECT r.reservation_id, p.projector_name, r.professor_name, r.date_reserved,
                   r.time_start, r.time_end, COALESCE(r.purpose, 'No Purpose'), r.status
            FROM reservations r
            JOIN projectors p ON r.projector_id = p.projector_id
            WHERE r.student_id = %s
        """
        return self.execute_query(query, (student_id,), fetch_all=True)

    def cancel_student_reservation(self, reservation_id):
        """Cancels a student's reservation and updates projector status if necessary."""
        # Get projector_id and current reservation status
        query_info = "SELECT projector_id, status FROM reservations WHERE reservation_id = %s"
        result_info = self.execute_query(query_info, (reservation_id,), fetch_one=True)

        if not result_info:
            return False

        proj_id, res_status = result_info

        # Delete the reservation
        delete_query = "DELETE FROM reservations WHERE reservation_id = %s"
        delete_success = self.execute_query(delete_query, (reservation_id,))

        if delete_success and res_status == 'Approved':
            # If the reservation was approved, mark the projector as available again
            self.update_projector_status(proj_id, 'Available')
        return delete_success

    def get_admin_dashboard_reservations(self):
        """Fetches pending/approved reservations for the admin dashboard."""
        query = """
            SELECT r.reservation_id, s.name, p.projector_name, r.professor_name, r.date_reserved, r.time_start, r.time_end,
                   COALESCE(r.purpose, 'No Purpose'), r.status
            FROM reservations r
            JOIN students s ON r.student_id = s.student_id
            JOIN projectors p ON r.projector_id = p.projector_id
            ORDER BY r.date_reserved, r.time_start
        """
        return self.execute_query(query, fetch_all=True)

    def update_reservation_status(self, reservation_id, new_status, projector_id):
        """Updates a reservation's status and the associated projector's status."""
        update_res_query = "UPDATE reservations SET status = %s WHERE reservation_id = %s"
        res_success = self.execute_query(update_res_query, (new_status, reservation_id))

        if res_success:
            if new_status == 'Approved':
                self.update_projector_status(projector_id, 'Reserved')
            elif new_status in ('Rejected', 'Cancelled'): # If rejected/cancelled, free up projector
                self.update_projector_status(projector_id, 'Available')
        return res_success

    def get_projector_id_from_reservation(self, reservation_id):
        """Gets projector_id from a reservation_id."""
        query = "SELECT projector_id FROM reservations WHERE reservation_id = %s"
        result = self.execute_query(query, (reservation_id,), fetch_one=True)
        return result[0] if result else None