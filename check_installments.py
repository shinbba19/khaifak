import sqlite3

# เปลี่ยนชื่อ database.db ให้ตรงกับที่ใช้ใน db_utils.py
conn = sqlite3.connect("database.db")
c = conn.cursor()

# ดูว่า schema มีอะไรบ้าง
print("Schema installments:")
for row in c.execute("PRAGMA table_info(installments);"):
    print(row)

# ดูข้อมูล installments
print("\nData in installments:")
for row in c.execute("SELECT * FROM installments;"):
    print(row)

conn.close()
