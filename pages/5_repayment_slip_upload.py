import streamlit as st
import pandas as pd
import os
from db_utils import run_query

def repayment_page():
    st.header("💰 Repayment Management (Interest Only + Balloon Principal)")

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

    if role != "owner":
        st.error("❌ Only property owners can upload repayment slips.")
        st.stop()

    # -------------------
    # Owner ID
    # -------------------
    owner = run_query("SELECT id FROM users WHERE username=?", (username,))
    if not owner:
        st.error("❌ Owner not found in DB")
        st.stop()
    owner_id = owner[0][0]

    # -------------------
    # Load active contracts
    # -------------------
    contracts = run_query(
        "SELECT id, principal, interest_rate, duration_months, status "
        "FROM contracts WHERE owner_id=? AND status='active'",
        (owner_id,)
    )

    if not contracts:
        st.info("📭 No active contracts found.")
        st.stop()

    contract_options = {
        f"Contract {c[0]} | {c[1]} THB | {c[2]}% | {c[3]} mo": c[0] for c in contracts
    }
    selected_contract = st.selectbox("Select Contract", list(contract_options.keys()))
    contract_id = contract_options[selected_contract]

    # -------------------
    # Fetch installments
    # -------------------
    installments = run_query(
        "SELECT id, installment_no, due_date, amount, paid, slip_id "
        "FROM installments WHERE contract_id=? ORDER BY installment_no",
        (contract_id,)
    )

    # -------------------
    # Auto-generate if not exists
    # -------------------
    if not installments:
        st.warning("⚠️ No installments found. Generating schedule...")

        contract = run_query(
            "SELECT principal, interest_rate, duration_months FROM contracts WHERE id=?",
            (contract_id,)
        )
        if not contract:
            st.error("❌ Contract not found in DB")
            st.stop()

        principal, interest_rate, duration_months = contract[0]
        monthly_interest = principal * (interest_rate/100) / 12

        today = pd.Timestamp.today()
        inserted = 0

        for i in range(1, duration_months + 1):
            due = (today + pd.DateOffset(months=i)).date().isoformat()

            if i < duration_months:
                principal_payment = 0
                interest_payment = monthly_interest
            else:
                principal_payment = principal
                interest_payment = monthly_interest

            total_payment = principal_payment + interest_payment

            try:
                run_query(
                    "INSERT INTO installments (contract_id, installment_no, due_date, amount, paid, slip_id) VALUES (?,?,?,?,?,?)",
                    (contract_id, i, due, total_payment, 0, None)
                )
                inserted += 1
            except Exception as e:
                st.write("Error inserting installment", i, ":", e)

        st.success(f"✅ Generated and inserted {inserted} installments into DB.")

        installments = run_query(
            "SELECT id, installment_no, due_date, amount, paid, slip_id "
            "FROM installments WHERE contract_id=? ORDER BY installment_no",
            (contract_id,)
        )

    # -------------------
    # Build DataFrame with Interest & Principal columns
    # -------------------
    contract = run_query(
        "SELECT principal, interest_rate, duration_months FROM contracts WHERE id=?",
        (contract_id,)
    )
    principal, interest_rate, duration_months = contract[0]
    monthly_interest = principal * (interest_rate/100) / 12

    rows = []
    today = pd.Timestamp.today()

    for i in range(1, duration_months + 1):
        due = (today + pd.DateOffset(months=i)).date().isoformat()
        if i < duration_months:
            pmt_principal = 0
            pmt_interest = monthly_interest
        else:
            pmt_principal = principal
            pmt_interest = monthly_interest
        total = pmt_principal + pmt_interest
        rows.append([i, due, round(pmt_interest,2), round(pmt_principal,2), round(total,2)])

    df_inst = pd.DataFrame(rows, columns=["No","Due Date","Interest","Principal","Total"])
    df_inst["Paid"] = ["❌ Unpaid"] * len(df_inst)

    st.subheader("📅 Installment Schedule (Interest Only + Balloon Principal)")
    st.dataframe(df_inst)

    # -------------------
    # Upload repayment slip
    # -------------------
    unpaid = [i for i in installments if (i[4] == 0 or str(i[4]) == "0")]
    if unpaid:
        next_inst = unpaid[0]
        st.info(f"👉 Next installment: No {next_inst[1]} | Due {next_inst[2]} | Amount {next_inst[3]} THB")

        repayment_slip = st.file_uploader("Upload Repayment Slip", type=["jpg","png","pdf"])
        if st.button("Submit Repayment Slip"):
            if repayment_slip:
                os.makedirs("uploads", exist_ok=True)
                file_path = os.path.join("uploads", repayment_slip.name)
                with open(file_path, "wb") as f:
                    f.write(repayment_slip.getbuffer())

                run_query(
                    "INSERT INTO slips (contract_id, slip_type, file_name, uploaded_by, status) VALUES (?,?,?,?,?)",
                    (contract_id, "repayment", file_path, owner_id, "pending")
                )
                st.success(f"✅ Slip for installment {next_inst[1]} uploaded! Waiting for admin approval.")
            else:
                st.error("⚠️ Please upload a file before submitting.")
    else:
        st.success("🎉 All installments are fully paid!")

# -------------------
# Run page
# -------------------
repayment_page()
