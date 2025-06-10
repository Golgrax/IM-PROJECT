import customtkinter as ctk
from app import ProjectorReservationSystem
from db_connector import DBManager
### GUYS PAKI CHANGE CONFIGURATION KUNG ANO ASA LAPTOP OR DESKTOP NIYO KASI MAGIIBA LALO'T WALA TAYO SERVER AND USING CLIENT LANG
DB_CONFIG = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "12345678",
    "database": "reservationprojector"
}

if __name__ == "__main__":
    db_manager = DBManager(**DB_CONFIG)
    root = ctk.CTk()
    app = ProjectorReservationSystem(root, db_manager)
    try:
        root.mainloop()
    finally:
        db_manager.close()