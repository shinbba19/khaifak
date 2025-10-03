import sqlite3

DB_FILE = "database.db"   # 👈 แก้ชื่อไฟล์ db ของพี่

def migrate():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # เพิ่ม owner_id
    try:
        c.execute("ALTER TABLE contracts ADD COLUMN owner_id INTEGER")
        print("✅ Added owner_id column")
    except Exception as e:
        print(f"⚠️ Skipping owner_id: {e}")

    # เพิ่ม investor_id
    try:
        c.execute("ALTER TABLE contracts ADD COLUMN investor_id INTEGER")
        print("✅ Added investor_id column")
    except Exception as e:
        print(f"⚠️ Skipping investor_id: {e}")

    conn.commit()
    conn.close()
    print("🎉 Migration completed.")

if __name__ == "__main__":
    migrate()
