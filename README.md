<div align="center">
  <img src="IMAGE/PUP_LOGO.png" alt="PUP Logo" width="150"/>
  <h1>Projector Reservation System</h1>
</div>

<p align="center">
  Hello tropa! ito'y simpleng desktop application para sa managing projector reservations na ginawa namin with Python (CustomTkinter & Tkinter) and MySQL. Plz subcribe Uwu
</p>

<p align="center">
  <a href="https://replit.com/github/Golgrax/IM-PROJECT" target="_blank">
    <img src="https://replit.com/badge/github/Golgrax/IM-PROJECT" alt="Run on Replit">
  </a>
</p>

---

## ✨ Features

*   **User Authentication:** Separate logins para sa Admin at Students. (E.g. sir Nand and Lennon)
*   **Admin Dashboard:**
    *   Add new projectors.
    *   Mag view, approve, or reject ng pending reservations.
    *   Monitor projector availability status.
*   **Student Dashboard:**
    *   Submit ng new projector reservation requests.
    *   View ng personal reservation history.
    *   Cancel ng pending reservations.
*   **Database Integration:** Gumagamit MySQL para ma-store user, projector, at reservation data.
*   **Modern UI:** Built with CustomTkinter for a sleek login screen and Tkinter with `ttk` for dashboards.

## 🛠️ Prerequisites

HOY! bago ka nga pala mag-start, ensure mo muna na you have the following installed jaan sa PC mo:

*   **Git:** For cloning the repository.
*   **Python 3.9+:** The programming language.
*   **MySQL Server:** The database backend.
*   **MySQL Workbench (Recommended):** A graphical tool for database management.

---

## 🚀 Getting Started

### 1. Clone the Repository

Open your terminal (or command prompt, IDK kasi sa OS niyo so it  depends what it calls) and clone the project:

```bash
git clone https://github.com/Golgrax/IM-PROJECT.git
cd IM-PROJECT
```

### 2. Database Setup

**a. Install MySQL Server & Workbench (ONLY IF WLA PA):**

*   **Windows:** Download installers from [MySQL Downloads](https://dev.mysql.com/downloads/installer/).
*   **macOS:** Download installers from [MySQL Downloads](https://dev.mysql.com/downloads/mysql/). Use Homebrew: `brew install mysql`.
*   **Linux (Debian/Ubuntu):**
    ```bash
    sudo apt update
    sudo apt install mysql-server mysql-workbench
    ```
    **Remember your MySQL `root` password** during installation. If you leave it blank, set `password=""` in `db_connector.py`.

**b. Create niyo yung DB niyo if it doesnt Exist yet so I can't help for that kasi inyo yan**



**c. Configure ng `db_connector.py`:**

*   Open `db_connector.py` sa `IM-PROJECT` folder.
*   Pag nag set ka ng MySQL `root` password, update `password=""` to `password="password_mo"`.

### 3. Install Python Dependencies

**a. Create & Activate Virtual Environment:**

It's good practice to isolate project dependencies.

*   **Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```
*   **macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
    (Your terminal prompt will change to `(venv)...` once activated.)

**b. Install Packages:**

```bash
pip install -r requirements.txt
```

### 4. Run the Application

With the virtual environment active:

```bash
python3 main.py
```

---

## 🔑 Usage

The application will launch with a login screen.

*   **Admin Login:**
    *   **Username:** `admin`
    *   **Password:** `admin`

*   **Student Login:**
    *   **Username:** `AliasKulay` (or `John lemon`)
    *   **Password:** `studentpass` (or `johnpass`)

### THAT'S ALL!!!