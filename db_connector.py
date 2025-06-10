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
            cursor.execute(query, params or ())
            conn.commit()

            if fetch_one:
                return cursor.fetchone()
            if fetch_all:
                return cursor.fetchall()
            return True
        except Error as e:
            print(f"Database query error: {e}")
            conn.rollback()
            return False
        finally:
            if cursor:
                cursor.close()


    def add_projector_entry(self, pr_no, serial_no):
        """Adds a new projector record, initially setting it as 'Available'."""
        query = """
            INSERT INTO projector_reservation
            (PR_NO, SERIAL_NO, TIME, PROFESSOR, SECTION, REPRESENTATIVE, STATUS)
            VALUES (%s, %s, '', '', '', '', 'Available')
        """
        return self.execute_query(query, (pr_no, serial_no))

    def update_reservation_details(self, pr_no, time_slot, professor, section, representative):
        """Updates an existing projector's details for reservation."""
        query = """
            UPDATE projector_reservation
            SET TIME = %s,
                PROFESSOR = %s,
                SECTION = %s,
                REPRESENTATIVE = %s,
                STATUS = 'Not Available'
            WHERE PR_NO = %s
        """
        return self.execute_query(query, (time_slot, professor, section, representative, pr_no))

    def cancel_projector_reservation(self, pr_no):
        """Resets a reserved projector's status to 'Available' and clears details."""
        query = """
            UPDATE projector_reservation
            SET STATUS = 'Available',
                PROFESSOR = '',
                SECTION = '',
                REPRESENTATIVE = '',
                TIME = ''
            WHERE PR_NO = %s
        """
        return self.execute_query(query, (pr_no,))

    def get_all_reservations(self):
        """Fetches all projector reservation records."""
        return self.execute_query(
            "SELECT PR_NO, SERIAL_NO, TIME, PROFESSOR, SECTION, REPRESENTATIVE, STATUS FROM projector_reservation",
            fetch_all=True
        )

    def get_available_projector_nos(self):
        """Fetches PR_NO of projectors with 'Available' status."""
        result = self.execute_query("SELECT PR_NO FROM projector_reservation WHERE STATUS = 'Available'", fetch_all=True)
        return [row[0] for row in result] if result else []

    def get_reserved_projector_nos(self):
        """Fetches PR_NO of projectors with 'Not Available' status."""
        result = self.execute_query("SELECT PR_NO FROM projector_reservation WHERE STATUS = 'Not Available'", fetch_all=True)
        return [row[0] for row in result] if result else []