import sqlite3
import os

DB_FILE = "database.db"

# Run query helper
def run_query(query, params=(), fetch=True):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    if fetch:
        rows = c.fetchall()
    else:
        rows = None
    conn.commit()
    conn.close()
    return rows

# Initialize DB
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Users table
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            email TEXT UNIQUE,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
    """)

    # Properties table
    c.execute("""
        CREATE TABLE IF NOT EXISTS properties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT,
            location TEXT,
            value REAL,
            document_name TEXT,
            room_size REAL,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)

    # Contracts table
    c.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            property_id INTEGER,
            terms TEXT,
            principal REAL,
            interest_rate REAL,
            duration_months INTEGER,
            signed_by_owner INTEGER DEFAULT 0,
            signed_by_investor INTEGER DEFAULT 0,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(property_id) REFERENCES properties(id)
        )
    """)

    # Installments table
    c.execute("""
        CREATE TABLE IF NOT EXISTS installments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            installment_no INTEGER,
            due_date TEXT,
            amount REAL,
            paid INTEGER DEFAULT 0,
            slip_id INTEGER,
            FOREIGN KEY(contract_id) REFERENCES contracts(id),
            FOREIGN KEY(slip_id) REFERENCES slips(id)
        )
    """)

    # Slips table
    c.execute("""
        CREATE TABLE IF NOT EXISTS slips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            slip_type TEXT,
            file_name TEXT,
            uploaded_by INTEGER,
            status TEXT DEFAULT 'pending',
            FOREIGN KEY(contract_id) REFERENCES contracts(id),
            FOREIGN KEY(uploaded_by) REFERENCES users(id)
        )
    """)

    # History table
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            contract_id INTEGER,
            action TEXT,
            actor TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(contract_id) REFERENCES contracts(id)
        )
    """)

    conn.commit()
    conn.close()

# Log history
def log_history(contract_id, action, actor):
    run_query(
        "INSERT INTO history (contract_id, action, actor) VALUES (?,?,?)",
        (contract_id, action, actor),
        fetch=False
    )
