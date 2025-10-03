import streamlit as st
import os
from db_utils import run_query

def funding_upload_page():
    st.header("💵 Funding Slip Upload")

    # -------------------
    # Check login
    # -------------------
    if "username" not in st.session_state:
        st.warning("⚠️ Please login first!")
        st.stop()

    username = st.session_state.get("username")
    role = st.session_state.get("role", "")

    if role != "investor":
        st.error("❌ Only investors can upload funding slips.")
        st.stop()

    # -------------------
    # Sidebar user info
    # -------------------
    with st.sidebar:
        st.markdown("### 👤 User Info")
        st.write(f"**Name:** {username}")
        st.write(f"**Role:** {role.capitalize()}")

    # -------------------
    # Load contracts available for funding
    # -------------------
    contracts = run_query(
        "SELECT id, property_id, principal, interest_rate, duration_months, status "
        "FROM contracts WHERE signed_by_investor=1 AND status='active'"
    )

    if not contracts:
        st.info("📭 No active contracts available for funding.")
        st.stop()

    # -------------------
    # Select contract
    # -------------------
    contract_options = {
        f"Contract {c[0]} | Property {c[1]} | {c[2]} THB | {c[3]}% | {c[4]} mo | {c[5]}": c[0] 
        for c in contracts
    }
    selected_contract = st.selectbox("Select Contract", list(contract_options.keys()))
    contract_id = contract_options[selected_contract]

    # -------------------
    # Upload Slip
    # -------------------
    slip = st.file_uploader("Upload Funding Slip", type=["jpg","png","pdf"])
    if st.button("Submit Funding Slip"):
        investor = run_query("SELECT id FROM users WHERE username=?", (username,))
        if not investor:
            st.error("❌ Investor not found in DB.")
        elif not slip:
            st.error("⚠️ Please upload a file before submitting.")
        else:
            os.makedirs("uploads", exist_ok=True)
            file_path = os.path.join("uploads", slip.name)
            with open(file_path, "wb") as f:
                f.write(slip.getbuffer())

            run_query(
                "INSERT INTO slips (contract_id, slip_type, file_name, uploaded_by, status) VALUES (?,?,?,?,?)",
                (contract_id, "funding", file_path, investor[0][0], "pending")
            )
            st.success(f"✅ Funding slip uploaded for Contract {contract_id}! Waiting for admin approval.")

# Run page
funding_upload_page()
