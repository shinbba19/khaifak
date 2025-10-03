import sqlite3
from datetime import datetime

DB_FILE = "p2p_khaifak.db"

def run_query(query, params=(), fetch=True):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(query, params)
    data = None
    if fetch:
        data = c.fetchall()
    conn.commit()
    conn.close()
    return data

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        email TEXT UNIQUE,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )''')

    # Properties
    c.execute('''CREATE TABLE IF NOT EXISTS properties (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        location TEXT,
        value REAL,
        document_name TEXT,
        room_size REAL,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')

    # Contracts
    c.execute('''CREATE TABLE IF NOT EXISTS contracts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        property_id INTEGER,
        owner_id INTEGER,
        investor_id INTEGER,
        terms TEXT,
        principal REAL,
        interest_rate REAL,
        duration_months INTEGER,
        signed_by_owner INTEGER DEFAULT 0,
        signed_by_investor INTEGER DEFAULT 0,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (property_id) REFERENCES properties(id)
    )''')

    # Installments
    c.execute('''CREATE TABLE IF NOT EXISTS installments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        installment_no INTEGER,
        due_date TEXT,
        amount REAL,
        paid INTEGER DEFAULT 0,
        slip_id INTEGER,
        FOREIGN KEY (contract_id) REFERENCES contracts(id)
    )''')

    # Slips
    c.execute('''CREATE TABLE IF NOT EXISTS slips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        slip_type TEXT,
        file_name TEXT,
        uploaded_by INTEGER,
        status TEXT DEFAULT 'pending',
        FOREIGN KEY (contract_id) REFERENCES contracts(id),
        FOREIGN KEY (uploaded_by) REFERENCES users(id)
    )''')

    # History
    c.execute('''CREATE TABLE IF NOT EXISTS history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contract_id INTEGER,
        action TEXT,
        user TEXT,
        timestamp TEXT
    )''')

    conn.commit()
    conn.close()

def log_history(contract_id, action, user):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history (contract_id, action, user, timestamp) VALUES (?,?,?,?)",
        (contract_id, action, user, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()

def get_last_id():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT last_insert_rowid()")
    last_id = c.fetchone()[0]
    conn.close()
    return last_id
