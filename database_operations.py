import sqlite3

DATABASE_FILE = "appointments.db"


def initialize_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            appointment_time TEXT NOT NULL
        )
    """
    )
    conn.commit()
    conn.close()


# Uncomment to initialize the database
# initialize_database()


def save_appointment(name, phone_number, appointment_time):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (name, phone_number, appointment_time) VALUES (?, ?, ?)",
        (name, phone_number, appointment_time),
    )
    conn.commit()
    conn.close()


def update_appointment(name, phone_number, appointment_time):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE appointments SET appointment_time=? WHERE name=? AND phone_number=?",
        (appointment_time, name, phone_number),
    )
    conn.commit()
    conn.close()


def cancel_appointment(name, phone_number):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "DELETE FROM appointments WHERE name=? AND phone_number=?", (name, phone_number)
    )
    conn.commit()
    conn.close()


def check_existing_appointment(name, phone_number):
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT appointment_time FROM appointments WHERE name=? AND phone_number=?",
        (name, phone_number),
    )
    appointment = cursor.fetchone()
    conn.close()
    if appointment:
        return appointment[0]  # Return the appointment time if found
    else:
        return None  # Return None if no appointment is found
