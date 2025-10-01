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
    "Admin Dashboard",
    "AI Appraisal"   # ✅ เพิ่มเมนูใหม่
], key="main_menu")

if "page" in st.session_state:
    page = st.session_state["page"]
    del st.session_state["page"]

# ---------- Pages ----------
# 1. Register / Login
if page == "Register / Login":
    st.header("🔑 Register / Login")
    choice = st.radio("Choose an option", ["Register", "Login"], key="auth_choice")
    username = st.text_input("Username", key="auth_username")
    password = st.text_input("Password", type="password", key="auth_password")

    if choice == "Register":
        full_name = st.text_input("Full Name", key="reg_fullname")
        email = st.text_input("Email Address", key="reg_email")
        role = st.selectbox("Role", ["owner", "investor", "admin"], key="reg_role")
    else:
        full_name, email, role = None, None, None

    if st.button(choice, key="auth_button"):
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
                 caption="The River Condo")
        st.markdown("💰 วงเงิน: 1,000,000 บาท")
        st.markdown("📈 ดอกเบี้ย: 12% ต่อปี")
        st.markdown("🕑 ระยะเวลา: 24 เดือน")
        st.progress(0.5)
        st.caption("Funding: 500k / 1M")
        if st.button("View Deal 1", key="deal1"):
            st.session_state["page"] = "Contract Management"
            st.experimental_rerun()

    with col2:
        st.image("https://images.unsplash.com/photo-1501183638710-841dd1904471",
                 caption="Sukhumvit Condo")
        st.markdown("💰 วงเงิน: 2,000,000 บาท")
        st.markdown("📈 ดอกเบี้ย: 10% ต่อปี")
        st.markdown("🕑 ระยะเวลา: 36 เดือน")
        st.progress(0.7)
        st.caption("Funding: 1.4M / 2M")
        if st.button("View Deal 2", key="deal2"):
            st.session_state["page"] = "Contract Management"
            st.experimental_rerun()

    with col3:
        st.image("https://images.unsplash.com/photo-1564013799919-ab600027ffc6",
                 caption="บ้านเดี่ยว รามอินทรา")
        st.markdown("💰 วงเงิน: 3,500,000 บาท")
        st.markdown("📈 ดอกเบี้ย: 9% ต่อปี")
        st.markdown("🕑 ระยะเวลา: 48 เดือน")
        st.progress(0.3)
        st.caption("Funding: 1.05M / 3.5M")
        if st.button("View Deal 3", key="deal3"):
            st.session_state["page"] = "Contract Management"
            st.experimental_rerun()

# (2 → 7 หน้าอื่น ๆ คงเดิม ไม่แก้ ไว้ตรงนี้เพื่อความย่อ)

# 8. AI Appraisal
elif page == "AI Appraisal":
    st.header("🤖 AI Condo Price Appraisal")

    try:
        df_ai = pd.read_csv("Price per sqm_cleaned_data_selection3.csv")
    except Exception as e:
        st.error(f"ไม่พบไฟล์ dataset: {e}")
        st.stop()

    features = ["district_type", "nbr_floors", "units", "bld_age"]
    target = "price_sqm"

    df_ai = df_ai.dropna(subset=features + [target])
    X = df_ai[features]
    y = df_ai[target]

    from sklearn.model_selection import train_test_split
    from sklearn.ensemble import RandomForestRegressor

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestRegressor(n_estimators=200, max_depth=12, random_state=42)
    model.fit(X_train, y_train)

    col1, col2 = st.columns(2)
    with col1:
        district_type = st.number_input("District Type (รหัสทำเล)", min_value=1, max_value=10, value=2)
        nbr_floors = st.number_input("จำนวนชั้นของโครงการ", min_value=1, max_value=80, value=20)
    with col2:
        units = st.number_input("จำนวนยูนิตในโครงการ", min_value=10, max_value=2000, value=300)
        bld_age = st.number_input("อายุอาคาร (ปี)", min_value=0, max_value=50, value=10)

    room_size = st.number_input("ขนาดห้อง (ตร.ม.)", min_value=20, max_value=500, value=35)

    input_dict = {
        "district_type": district_type,
        "nbr_floors": nbr_floors,
        "units": units,
        "bld_age": bld_age
    }
    input_df = pd.DataFrame([input_dict])

    if st.button("📊 ประเมินราคา", key="ai_button"):
        pred_price_per_sqm = model.predict(input_df)[0]
        estimated_value = pred_price_per_sqm * room_size

        st.success(f"💰 ราคาประเมินต่อตารางเมตร: **{pred_price_per_sqm:,.0f} บาท/ตร.ม.**")
        st.info(f"🏷️ มูลค่าห้อง (ประมาณ): **{estimated_value:,.0f} บาท**")

        st.markdown("### 📊 ปัจจัยที่มีผลต่อราคา")
        feature_imp = pd.DataFrame({
            "Feature": X.columns,
            "Importance": model.feature_importances_
        }).sort_values(by="Importance", ascending=False)
        st.bar_chart(feature_imp.set_index("Feature"))
