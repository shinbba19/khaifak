import streamlit as st
from db_utils import run_query, init_db

# ✅ Init database
init_db()

# -------------------------
# Title
# -------------------------
st.title("🏦 Propflex – โปร่งใส ยืดหยุ่น มั่นใจทุกการลงทุน")
st.write("ยินดีต้อนรับเข้าสู่ระบบ **Propflex**")

# -------------------------
# Register / Login Section
# -------------------------
st.header("🔑 Register / Login")

choice = st.radio("เลือกการทำงาน", ["Register", "Login"], key="auth_choice")
username = st.text_input("Username")
password = st.text_input("Password", type="password")

if choice == "Register":
    full_name = st.text_input("Full Name")
    email = st.text_input("Email Address")
    role = st.selectbox("Role", ["owner", "investor", "admin"])
else:
    full_name, email, role = None, None, None

if st.button(choice, key="auth_button"):
    if choice == "Register":
        try:
            run_query(
                "INSERT INTO users (full_name,email,username,password,role) VALUES (?,?,?,?,?)",
                (full_name, email, username, password, role)
            )
            st.session_state["username"] = username
            st.session_state["role"] = role
            st.success(f"✅ Registration successful! Logged in as {full_name} ({role})")
        except Exception as e:
            st.error(f"❌ Registration failed: {e}")
    else:  # Login
        user = run_query(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password)
        )
        if user:
            st.session_state["username"] = user[0][3]  # username
            st.session_state["role"] = user[0][5]      # role
            st.success(f"👋 Welcome back {user[0][1]} ({st.session_state['role']})")
        else:
            st.error("⚠️ Invalid login.")

# -------------------------
# Mock Example Deals
# -------------------------
st.markdown("---")
st.subheader("📌 Example P2P ขายฝาก Deals")

col1, col2, col3 = st.columns(3)

with col1:
    st.image("https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
             caption="The River Condo")
    st.markdown("💰 วงเงิน: 1,000,000 บาท")
    st.markdown("📈 ดอกเบี้ย: 12% ต่อปี")
    st.markdown("🕑 ระยะเวลา: 24 เดือน")
    st.progress(0.5)
    st.caption("Funding: 500k / 1M")
    st.button("ดูรายละเอียด Deal 1", key="deal1")

with col2:
    st.image("https://images.unsplash.com/photo-1501183638710-841dd1904471",
             caption="Sukhumvit Condo")
    st.markdown("💰 วงเงิน: 2,000,000 บาท")
    st.markdown("📈 ดอกเบี้ย: 10% ต่อปี")
    st.markdown("🕑 ระยะเวลา: 36 เดือน")
    st.progress(0.7)
    st.caption("Funding: 1.4M / 2M")
    st.button("ดูรายละเอียด Deal 2", key="deal2")

with col3:
    st.image("https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
             caption="บ้านเดี่ยว รามอินทรา")
    st.markdown("💰 วงเงิน: 3,500,000 บาท")
    st.markdown("📈 ดอกเบี้ย: 9% ต่อปี")
    st.markdown("🕑 ระยะเวลา: 48 เดือน")
    st.progress(0.3)
    st.caption("Funding: 1.05M / 3.5M")
    st.button("ดูรายละเอียด Deal 3", key="deal3")

st.markdown("---")
st.info("💡 ตัวอย่างดีลขายฝากแสดง วงเงิน ดอกเบี้ย ระยะเวลา และ Funding Progress เพื่อให้นักลงทุนตัดสินใจได้ง่าย")
