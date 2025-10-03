import streamlit as st
import pandas as pd
from db_utils import run_query

def installment_schedule_page():
    st.header("📅 Installment Schedule")

    # -------------------
    # Check login
    # -------------------
    if "username" not in st.session_state:
        st.warning("⚠️ Please login first!")
        st.stop()

    username = st.session_state.get("username")
    role = st.session_state.get("role", "")

    # -------------------
    # Sidebar user info
    # -------------------
    with st.sidebar:
        st.markdown("### 👤 User Info")
        st.write(f"**Name:** {username}")
        st.write(f"**Role:** {role.capitalize() if role else 'N/A'}")

    # -------------------
    # Load contracts by role
    # -------------------
    if role == "owner":
        contracts = run_query("""
            SELECT c.id, c.principal, c.interest_rate, c.duration_months, c.status
            FROM contracts c
            JOIN users u ON c.owner_id = u.id
            WHERE u.username=?
        """, (username,))

    elif role == "investor":
        contracts = run_query("""
            SELECT c.id, c.principal, c.interest_rate, c.duration_months, c.status
            FROM contracts c
            JOIN users u ON c.investor_id = u.id
            WHERE u.username=?
        """, (username,))

    else:  # admin
        contracts = run_query("SELECT id, principal, interest_rate, duration_months, status FROM contracts")

    if not contracts:
        st.info("📭 No contracts found.")
        st.stop()

    # -------------------
    # Select Contract
    # -------------------
    contract_options = {
        f"Contract {c[0]} | {c[1]} THB | {c[2]}% | {c[3]} mo | {c[4]}": c[0] 
        for c in contracts
    }
    selected_contract = st.selectbox("Select Contract", list(contract_options.keys()))
    contract_id = contract_options[selected_contract]

    # -------------------
    # Get contract details (for interest calculation)
    # -------------------
    contract = run_query(
        "SELECT principal, interest_rate, duration_months FROM contracts WHERE id=?",
        (contract_id,)
    )
    if not contract:
        st.error("❌ Contract not found in DB")
        st.stop()
    principal, interest_rate, duration_months = contract[0]
    monthly_interest = principal * (interest_rate/100) / 12

    # -------------------
    # Show Installments
    # -------------------
    installments = run_query(
        "SELECT id, installment_no, due_date, amount, paid, slip_id "
        "FROM installments WHERE contract_id=? ORDER BY installment_no",
        (contract_id,)
    )

    if installments:
        rows = []
        for row in installments:
            inst_id, no, due, amount, paid, slip_id = row

            # คำนวณ Interest & Principal (interest only + balloon)
            if no < duration_months:
                inst_interest = monthly_interest
                inst_principal = 0
            else:
                inst_interest = monthly_interest
                inst_principal = principal

            inst_total = inst_interest + inst_principal
            paid_status = "✅ Paid" if str(paid) == "1" else "❌ Unpaid"

            slip_file = ""
            if slip_id:
                slip = run_query("SELECT file_name FROM slips WHERE id=?", (slip_id,))
                slip_file = slip[0][0] if slip else ""

            rows.append([no, due, round(inst_interest,2), round(inst_principal,2),
                         round(inst_total,2), paid_status, slip_file])

        df_inst = pd.DataFrame(rows, columns=["No","Due Date","Interest","Principal","Total","Paid","Slip_File"])

        st.subheader("📊 Installment Table")
        st.dataframe(df_inst)
    else:
        st.warning("⚠️ No installments found for this contract.")

# Run page
installment_schedule_page()
