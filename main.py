import streamlit as st
import pandas as pd
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from db_utils import init_db, run_query, log_history

# ✅ Init DB
init_db()

# ---------- Helpers ----------
def status_badge(status: str) -> str:
    colors = {"pending": "🟡", "active": "🟢", "completed": "⚪", "approved": "✅", "rejected": "❌"}
    return f"{colors.get(status, '')} {status.capitalize()}"

def paid_status(paid: int) -> str:
    return "✅ Paid" if paid == 1 else "❌ Unpaid"

def require_login():
    if "username" not in st.session_state:
        st.warning("⚠️ Please login first!")
        st.stop()

# ---------- Sidebar ----------
st.sidebar.title("P2P ขายฝาก")

if "username" in st.session_state:
    st.sidebar.success(f"👤 {st.session_state['username']} ({st.session_state['role']})")
    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.experimental_rerun()

page = st.sidebar.radio("Go to", [
    "Register / Login",
    "Property Registration",
    "Contract Management",
    "Funding Slip Upload",
    "Repayment Slip Upload",
    "Installment Schedule",
    "Admin Dashboard"
])

if "page" in st.session_state:
    page = st.session_state["page"]
    del st.session_state["page"]

# ---------- Pages ----------
# 1. Register / Login
if page == "Register / Login":
    st.header("🔑 Register / Login")
    choice = st.radio("Choose an option", ["Register", "Login"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Register":
        full_name = st.text_input("Full Name")
        email = st.text_input("Email Address")
        role = st.selectbox("Role", ["owner", "investor", "admin"])
    else:
        full_name, email, role = None, None, None

    if st.button(choice):
        if choice == "Register":
            try:
                run_query("INSERT INTO users (full_name,email,username,password,role) VALUES (?,?,?,?,?)",
                          (full_name, email, username, password, role))
                st.session_state["username"] = username
                st.session_state["role"] = role
                st.success(f"Registration successful! Logged in as {full_name} ({role})")
            except Exception as e:
                st.error(f"Registration failed: {e}")
        else:
            user = run_query("SELECT * FROM users WHERE username=? AND password=?", (username, password))
            if user:
                st.session_state["username"] = user[0][3]
                st.session_state["role"] = user[0][5]
                st.success(f"Welcome back {user[0][1]} ({st.session_state['role']})")
            else:
                st.error("Invalid login.")

    # ---------- Mock P2P ขายฝาก Deals ----------
    st.markdown("---")
    st.subheader("📌 Example P2P ขายฝาก Deals")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
                 caption="The River Condo", use_column_width=True)
        st.markdown("💰 วงเงิน: 1,000,000 บาท")
        st.markdown("📈 ดอกเบี้ย: 12% ต่อปี")
        st.markdown("🕑 ระยะเวลา: 24 เดือน")
        st.progress(0.5)
        st.caption("Funding: 500k / 1M")
        if st.button("View Deal 1"):
            st.session_state["page"] = "Contract Management"
            st.experimental_rerun()

    with col2:
        st.image("https://images.unsplash.com/photo-1501183638710-841dd1904471",
                 caption="Sukhumvit Condo", use_column_width=True)
        st.markdown("💰 วงเงิน: 2,000,000 บาท")
        st.markdown("📈 ดอกเบี้ย: 10% ต่อปี")
        st.markdown("🕑 ระยะเวลา: 36 เดือน")
        st.progress(0.7)
        st.caption("Funding: 1.4M / 2M")
        if st.button("View Deal 2"):
            st.session_state["page"] = "Contract Management"
            st.experimental_rerun()

    with col3:
        st.image("https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
                 caption="บ้านเดี่ยว รามอินทรา", use_column_width=True)
        st.markdown("💰 วงเงิน: 3,500,000 บาท")
        st.markdown("📈 ดอกเบี้ย: 9% ต่อปี")
        st.markdown("🕑 ระยะเวลา: 48 เดือน")
        st.progress(0.3)
        st.caption("Funding: 1.05M / 3.5M")
        if st.button("View Deal 3"):
            st.session_state["page"] = "Contract Management"
            st.experimental_rerun()

    st.markdown("---")
    st.info("💡 ตัวอย่างดีลขายฝากแสดง วงเงิน ดอกเบี้ย ระยะเวลา และ Funding Progress เพื่อให้นักลงทุนตัดสินใจได้ง่าย")

# 2. Property Registration
elif page == "Property Registration":
    require_login()
    if st.session_state["role"] != "owner":
        st.error("Only property owners can register properties.")
    else:
        st.header("🏠 Property Registration")
        try:
            df_areas = pd.read_csv("areas.csv")
            area_options = df_areas["area"].tolist()
        except Exception:
            area_options = ["Other"]

        condo_name = st.text_input("Condo Name")
        area = st.selectbox("Area (เขตในกรุงเทพฯ)", area_options)
        floor = st.text_input("Floor")
        room_size = st.number_input("Room Size (sqm)", min_value=0.0, format="%.2f")
        location = st.text_input("Location (optional)")
        value = st.number_input("Estimated Value (THB)", min_value=0)
        doc = st.file_uploader("Upload Property Document", type=["pdf","jpg","png"])

        if st.button("Submit Property"):
            user = run_query("SELECT id FROM users WHERE username=?", (st.session_state["username"],))
            if user:
                user_id = user[0][0]
                doc_name = doc.name if doc else None
                prop_name = f"{condo_name}, Floor {floor}, {area}, {room_size} sqm"
                run_query(
                    "INSERT INTO properties (user_id,name,location,value,document_name,room_size) VALUES (?,?,?,?,?,?)",
                    (user_id, prop_name, location, value, doc_name, room_size)
                )
                st.success(f"Property '{prop_name}' registered!")
            else:
                st.error("User not found!")

# 3. Contract Management
elif page == "Contract Management":
    require_login()
    st.header("📜 Contract Management")

    props = run_query("SELECT id, name, location, value FROM properties")
    if props:
        prop_options = {f"{p[1]} ({p[2]}, {p[3]} THB)": p[0] for p in props}
        selected_prop = st.selectbox("Select Property", list(prop_options.keys()))
        property_id = prop_options[selected_prop]

        contracts = run_query("""
            SELECT id, terms, principal, interest_rate, duration_months,
                   signed_by_owner, signed_by_investor, status
            FROM contracts WHERE property_id=?
        """, (property_id,))

        if contracts:
            for c in contracts:
                st.write(f"Contract {c[0]} | {status_badge(c[7])}")
                st.write(f"Principal: {c[2]} | Interest: {c[3]}% | Duration: {c[4]} months")
                st.write(f"Terms: {c[1]}")

                if st.session_state["role"] == "investor" and not c[6]:
                    if st.button(f"💰 Join Deal (Contract {c[0]})"):
                        run_query("UPDATE contracts SET signed_by_investor=1, status='active' WHERE id=?", (c[0],))
                        log_history(c[0], "Investor joined contract", st.session_state["username"])
                        st.session_state["selected_contract_id"] = c[0]
                        st.session_state["page"] = "Funding Slip Upload"
                        st.experimental_rerun()

        if st.session_state["role"] == "owner":
            st.subheader("✍️ Create Contract")
            principal = st.number_input("Principal", min_value=0)
            interest_rate = st.number_input("Annual Interest Rate (%)", min_value=0.0)
            duration = st.number_input("Duration (months)", min_value=1)
            terms = st.text_area("Contract Terms")

            if st.button("Create Contract"):
                run_query("INSERT INTO contracts (property_id,terms,principal,interest_rate,duration_months,signed_by_owner) VALUES (?,?,?,?,?,1)",
                          (property_id, terms, principal, interest_rate, duration))
                new_id = run_query("SELECT last_insert_rowid()")[0][0]
                monthly_interest = (interest_rate/100) * principal / 12
                for i in range(1, duration+1):
                    due = (datetime.now() + timedelta(days=30*i)).strftime("%Y-%m-%d")
                    amount = monthly_interest if i < duration else monthly_interest + principal
                    run_query("INSERT INTO installments (contract_id,installment_no,due_date,amount,paid,slip_id) VALUES (?,?,?,?,0,NULL)",
                              (new_id, i, due, amount), fetch=False)
                log_history(new_id, "Owner created contract", st.session_state["username"])
                st.success("Contract + installments created!")
                st.experimental_rerun()
    else:
        st.warning("No properties available.")

# 4. Funding Slip Upload
elif page == "Funding Slip Upload":
    require_login()
    if st.session_state["role"] != "investor":
        st.error("Only investors can upload funding slips.")
    else:
        st.header("💵 Funding Slip Upload")
        contracts = run_query("SELECT id, property_id, status FROM contracts WHERE status='active'")
        if contracts:
            if "selected_contract_id" in st.session_state:
                contract_id = st.session_state["selected_contract_id"]
                del st.session_state["selected_contract_id"]
            else:
                contract_options = {f"Contract {c[0]} (Property {c[1]}) [{c[2]}]": c[0] for c in contracts}
                selected_contract = st.selectbox("Select Contract", list(contract_options.keys()))
                contract_id = contract_options[selected_contract]
            slip = st.file_uploader("Upload Funding Slip", type=["jpg","png","pdf"])
            if st.button("Submit Funding Slip"):
                user = run_query("SELECT id FROM users WHERE username=?", (st.session_state["username"],))
                if slip and user:
                    os.makedirs("uploads", exist_ok=True)
                    file_path = os.path.join("uploads", slip.name)
                    with open(file_path, "wb") as f:
                        f.write(slip.getbuffer())
                    run_query("INSERT INTO slips (contract_id, slip_type, file_name, uploaded_by, status) VALUES (?,?,?,?,?)",
                              (contract_id, "funding", file_path, user[0][0], "pending"))
                    st.success("Funding slip uploaded! Waiting for admin.")
        else:
            st.info("No active contracts.")

# 5. Repayment Slip Upload
elif page == "Repayment Slip Upload":
    require_login()
    if st.session_state["role"] != "owner":
        st.error("Only property owners can upload repayment slips.")
    else:
        st.header("💰 Repayment Slip Upload")
        contracts = run_query("SELECT id FROM contracts WHERE status='active'")
        if contracts:
            contract_ids = [str(c[0]) for c in contracts]
            contract_id = st.selectbox("Select Contract", contract_ids)

            installments = run_query("SELECT id, installment_no, due_date, amount, paid FROM installments WHERE contract_id=? ORDER BY installment_no", (contract_id,))
            if installments:
                df_inst = pd.DataFrame(installments, columns=["ID","No","Due Date","Amount","Paid"])
                df_inst["Paid"] = df_inst["Paid"].apply(paid_status)
                st.dataframe(df_inst)

                unpaid = [i for i in installments if i[4] == 0]
                if unpaid:
                    next_inst = unpaid[0]
                    st.info(f"Next installment to pay: No {next_inst[1]} | Due {next_inst[2]} | Amount {next_inst[3]}")
                    repayment_slip = st.file_uploader("Upload Repayment Slip", type=["jpg","png","pdf"])
                    if st.button("Submit Repayment Slip"):
                        user = run_query("SELECT id FROM users WHERE username=?", (st.session_state["username"],))
                        if repayment_slip and user:
                            os.makedirs("uploads", exist_ok=True)
                            file_path = os.path.join("uploads", repayment_slip.name)
                            with open(file_path, "wb") as f:
                                f.write(repayment_slip.getbuffer())
                            run_query("INSERT INTO slips (contract_id, slip_type, file_name, uploaded_by, status) VALUES (?,?,?,?,?)",
                                      (contract_id, "repayment", file_path, user[0][0], "pending"))
                            st.success(f"Repayment slip for installment {next_inst[1]} uploaded! Waiting for admin.")
                else:
                    st.success("🎉 All installments are paid!")
        else:
            st.info("No active contracts.")

# 6. Installment Schedule
elif page == "Installment Schedule":
    require_login()
    st.header("📅 Installment Schedule")

    if st.session_state["role"] == "owner":
        contracts = run_query("""
            SELECT c.id, c.principal, c.interest_rate, c.duration_months, c.status
            FROM contracts c
            JOIN properties p ON c.property_id = p.id
            JOIN users u ON p.user_id = u.id
            WHERE u.username = ?
        """, (st.session_state["username"],))
    elif st.session_state["role"] == "investor":
        contracts = run_query("""
            SELECT id, principal, interest_rate, duration_months, status
            FROM contracts
            WHERE signed_by_investor = 1
        """)
    else:
        contracts = run_query("SELECT id, principal, interest_rate, duration_months, status FROM contracts")

    if contracts:
        contract_options = {f"Contract {c[0]} ({status_badge(c[4])})": c[0] for c in contracts}
        selected_contract = st.selectbox("Select Contract", list(contract_options.keys()))
        contract_id = contract_options[selected_contract]

        installments = run_query("""
            SELECT installment_no, due_date, amount, paid, slip_id
            FROM installments
            WHERE contract_id=?
            ORDER BY installment_no
        """, (contract_id,))

        if installments:
            df_inst = pd.DataFrame(installments, columns=["No","Due Date","Amount","Paid","Slip_ID"])
            df_inst["Paid"] = df_inst["Paid"].apply(paid_status)

            slip_links = []
            for row in installments:
                if row[4]:
                    slip_file = run_query("SELECT file_name FROM slips WHERE id=?", (row[4],))
                    slip_links.append(slip_file[0][0] if slip_file else "")
                else:
                    slip_links.append("")
            df_inst["Slip_File"] = slip_links

            st.dataframe(df_inst)
        else:
            st.info("No installments found.")
    else:
        st.info("No contracts available.")

# 7. Admin Dashboard
elif page == "Admin Dashboard":
    require_login()
    if st.session_state["role"] != "admin":
        st.error("Only admins can view the dashboard.")
    else:
        st.header("📊 Admin Dashboard")

        st.subheader("Users")
        users = run_query("SELECT * FROM users")
        if users:
            df_users = pd.DataFrame(users, columns=["ID","Full_Name","Email","Username","Password","Role"])
            st.dataframe(df_users)

        st.subheader("Contracts")
        contracts = run_query("SELECT * FROM contracts")
        if contracts:
            df_contracts = pd.DataFrame(contracts, columns=["ID","Property_ID","Terms","Principal","Interest","Duration","Owner_Signed","Investor_Signed","Status"])
            st.dataframe(df_contracts)

        st.subheader("Installments")
        contract_ids = [str(c[0]) for c in contracts]
        filter_contract = st.selectbox("Filter by Contract ID", ["All"] + contract_ids)
        if filter_contract == "All":
            installments = run_query("SELECT * FROM installments")
        else:
            installments = run_query("SELECT * FROM installments WHERE contract_id=?", (filter_contract,))
        if installments:
            df_inst = pd.DataFrame(installments, columns=["ID","Contract_ID","No","Due_Date","Amount","Paid","Slip_ID"])
            df_inst["Paid"] = df_inst["Paid"].apply(paid_status)
            st.dataframe(df_inst)

        st.subheader("Slips (Pending Approval)")
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
