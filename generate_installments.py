import sqlite3
from datetime import datetime, timedelta

DB_FILE = "database.db"

def generate_installments_for_existing_contracts():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # หา contracts ที่ยังไม่มี installment
    c.execute("""
        SELECT c.id, c.principal, c.interest_rate, c.duration_months
        FROM contracts c
        WHERE NOT EXISTS (SELECT 1 FROM installments i WHERE i.contract_id = c.id)
    """)
    contracts = c.fetchall()

    if not contracts:
        print("✅ No contracts found that need installments.")
    else:
        for contract in contracts:
            contract_id, principal, interest_rate, duration = contract
            print(f"🔧 Generating installments for Contract {contract_id} (P={principal}, r={interest_rate}, n={duration})")

            if not principal or not duration:
                print(f"⚠️ Skipped Contract {contract_id} (missing principal or duration)")
                continue

            monthly_interest = (interest_rate/100) * principal / 12
            for i in range(1, duration+1):
                due = (datetime.now() + timedelta(days=30*i)).strftime("%Y-%m-%d")
                if i < duration:
                    amount = monthly_interest
                else:
                    amount = monthly_interest + principal
                c.execute("""
                    INSERT INTO installments (contract_id, installment_no, due_date, amount, paid, slip_id)
                    VALUES (?,?,?,?,0,NULL)
                """, (contract_id, i, due, amount))

            print(f"✅ Created {duration} installments for Contract {contract_id}")

    conn.commit()
    conn.close()

if __name__ == "__main__":
    generate_installments_for_existing_contracts()
