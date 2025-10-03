import streamlit as st
from db_utils import run_query, log_history, get_last_id
from datetime import datetime, timedelta

st.header("📜 Contract Management")

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
# Load properties
# -------------------
props = run_query("SELECT id, name, location, value FROM properties")

if props:
    prop_options = {f"{p[1]} ({p[2]}, {p[3]} THB)": p[0] for p in props}
    selected_prop = st.selectbox("Select Property", list(prop_options.keys()))
    property_id = prop_options[selected_prop]

    # -------------------
    # Show contracts
    # -------------------
    contracts = run_query("""
        SELECT id, terms, principal, interest_rate, duration_months,
               signed_by_owner, signed_by_investor, status
        FROM contracts
        WHERE property_id=?
    """, (property_id,))

    if contracts:
        for c in contracts:
            st.markdown(f"### Contract {c[0]} | Status: **{c[7]}**")
            st.write(f"💰 Principal: {c[2]} THB")
            st.write(f"📈 Interest: {c[3]}% ต่อปี")
            st.write(f"⏳ Duration: {c[4]} เดือน")
            st.write(f"📝 Terms: {c[1]}")

            # Investor join deal
            if role == "investor" and not c[6]:
                if st.button(f"💰 Join Deal (Contract {c[0]})", key=f"join_{c[0]}"):
                    run_query(
                        """
                        UPDATE contracts 
                        SET signed_by_investor=1, 
                            investor_id=(SELECT id FROM users WHERE username=?), 
                            status='active'
                        WHERE id=?
                        """,
                        (username, c[0])
                    )
                    log_history(c[0], "Investor joined contract", username)
                    st.success(f"✅ You joined Contract {c[0]} successfully!")
                    st.experimental_rerun()

    # -------------------
    # Owner create contract
    # -------------------
    if role == "owner":
        st.subheader("✍️ Create New Contract")

        principal = st.number_input("Principal (THB)", min_value=0)
        interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0)
        duration = st.number_input("Duration (months)", min_value=1)
        terms = st.text_area("Contract Terms")

        if st.button("Create Contract"):
            owner = run_query("SELECT id FROM users WHERE username=?", (username,))
            if not owner:
                st.error("❌ Owner not found!")
            else:
                owner_id = owner[0][0]
                run_query(
                    """INSERT INTO contracts 
                       (property_id, owner_id, terms, principal, interest_rate, duration_months, signed_by_owner, status) 
                       VALUES (?,?,?,?,?,?,1,'pending')""",
                    (property_id, owner_id, terms, principal, interest_rate, duration)
                )

                new_contract_id = get_last_id()

                # Create installments (interest-only + principal balloon)
                monthly_interest = (interest_rate / 100) * principal / 12
                for i in range(1, duration + 1):
                    due_date = (datetime.now() + timedelta(days=30 * i)).strftime("%Y-%m-%d")
                    amount = monthly_interest if i < duration else monthly_interest + principal
                    run_query(
                        "INSERT INTO installments (contract_id, installment_no, due_date, amount, paid, slip_id) VALUES (?,?,?,?,0,NULL)",
                        (new_contract_id, i, due_date, amount),
                        fetch=False
                    )

                log_history(new_contract_id, "Owner created contract", username)
                st.success(f"✅ Contract {new_contract_id} created with {duration} installments!")
                st.experimental_rerun()

else:
    st.warning("⚠️ No properties available. Please register property first.")
