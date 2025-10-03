import streamlit as st
import pandas as pd
from db_utils import run_query, log_history

def admin_dashboard_page():
    st.header("📊 Admin Dashboard")

    if "username" not in st.session_state or st.session_state.get("role") != "admin":
        st.error("❌ Only admins can view this page.")
        st.stop()

    # -------------------------
    # Users Table
    # -------------------------
    st.subheader("👥 Users")
    users = run_query("SELECT * FROM users")
    if users:
        df_users = pd.DataFrame(
            users,
            columns=["ID","Full_Name","Email","Username","Password","Role"]
        )
        st.dataframe(df_users)

    # -------------------------
    # Properties Table
    # -------------------------
    st.subheader("🏠 Properties")
    properties = run_query("SELECT * FROM properties")
    if properties:
        df_props = pd.DataFrame(
            properties,
            columns=["ID","User_ID","Name","Location","Value","Document_Name","Room_Size"]
        )
        st.dataframe(df_props)

    # -------------------------
    # Contracts Table
    # -------------------------
    st.subheader("📜 Contracts")
    contracts = run_query("SELECT * FROM contracts")
    if contracts:
        df_contracts = pd.DataFrame(
            contracts,
            columns=[
                "ID","Property_ID","Owner_ID","Investor_ID","Terms",
                "Principal","Interest_Rate","Duration_Months",
                "Owner_Signed","Investor_Signed","Status"
            ]
        )
        st.dataframe(df_contracts)

    # -------------------------
    # Installments Table
    # -------------------------
    st.subheader("💰 Installments")
    contract_ids = [str(c[0]) for c in contracts] if contracts else []
    filter_contract = st.selectbox("Filter by Contract ID", ["All"] + contract_ids)

    if filter_contract == "All":
        installments = run_query("SELECT * FROM installments")
    else:
        installments = run_query("SELECT * FROM installments WHERE contract_id=?", (filter_contract,))
    
    if installments:
        df_inst = pd.DataFrame(
            installments,
            columns=["ID","Contract_ID","No","Due_Date","Amount","Paid","Slip_ID"]
        )
        df_inst["Paid"] = df_inst["Paid"].apply(lambda x: "✅ Paid" if x == 1 else "❌ Unpaid")
        st.dataframe(df_inst)

    # -------------------------
    # Slips Approval
    # -------------------------
    st.subheader("📂 Slips (Pending Approval)")
    slips = run_query("SELECT * FROM slips WHERE status='pending'")
    if slips:
        for slip in slips:
            slip_id, contract_id, slip_type, file_name, uploaded_by, status = slip
            st.write(f"📄 Slip {slip_id} | Contract {contract_id} | Type: {slip_type} | File: {file_name}")

            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"✅ Approve {slip_id}"):
                    run_query("UPDATE slips SET status='approved' WHERE id=?", (slip_id,))
                    log_history(contract_id, f"Admin approved {slip_type} slip {slip_id}", "admin")

                    if slip_type == "repayment":
                        inst = run_query(
                            "SELECT id FROM installments WHERE contract_id=? AND paid=0 ORDER BY installment_no ASC LIMIT 1",
                            (contract_id,)
                        )
                        if inst:
                            inst_id = inst[0][0]
                            run_query("UPDATE installments SET paid=1, slip_id=? WHERE id=?", (slip_id, inst_id), fetch=False)
                    st.success(f"Slip {slip_id} approved.")
                    st.experimental_rerun()

            with col2:
                if st.button(f"❌ Reject {slip_id}"):
                    run_query("UPDATE slips SET status='rejected' WHERE id=?", (slip_id,))
                    log_history(contract_id, f"Admin rejected {slip_type} slip {slip_id}", "admin")
                    st.error(f"Slip {slip_id} rejected.")
                    st.experimental_rerun()

    # -------------------------
    # History Table
    # -------------------------
    st.subheader("📜 Action History")
    history = run_query("SELECT * FROM history ORDER BY timestamp DESC")
    if history:
        df_hist = pd.DataFrame(
            history,
            columns=["ID","Contract_ID","Action","User","Timestamp"]
        )
        st.dataframe(df_hist)

# เรียกใช้งานฟังก์ชัน
admin_dashboard_page()
