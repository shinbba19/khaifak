import streamlit as st
from datetime import datetime, timedelta
from db_utils import run_query, reset_db

st.title("🏡 เจ้าของทรัพย์")

# --- Reset Button ---
if st.sidebar.button("♻️ Reset Database"):
    reset_db()
    st.sidebar.success("Database ถูกรีเซ็ตเรียบร้อย ✅")

# --- Add Owner ---
st.subheader("เพิ่มข้อมูลเจ้าของ")
name = st.text_input("ชื่อเจ้าของ")
contact = st.text_input("เบอร์ติดต่อ")
if st.button("บันทึกเจ้าของ"):
    if name.strip() == "" or contact.strip() == "":
        st.error("❌ ต้องกรอกชื่อและเบอร์ติดต่อ")
    else:
        run_query("INSERT INTO owners (name, contact) VALUES (?,?)", (name, contact))
        st.success("บันทึกเจ้าของเรียบร้อย ✅")

st.markdown("---")

# --- Add Property ---
st.subheader("เพิ่มข้อมูลทรัพย์")
owner_id = st.number_input("Owner ID", min_value=1)
location = st.text_input("ทำเล")
district_type = st.selectbox("ประเภททำเล", [1, 2, 3])
nbr_floors = st.number_input("จำนวนชั้นของตึก", min_value=1, value=8)
units = st.number_input("จำนวนยูนิต", min_value=1, value=200)
bld_age = st.number_input("อายุอาคาร (ปี)", min_value=0, value=5)
room_size = st.number_input("ขนาดห้อง (ตร.ม.)", min_value=10.0, value=30.0, step=1.0)
value = st.number_input("ราคาที่เจ้าของเสนอ (บาท)", min_value=100000.0, value=1000000.0, step=50000.0)
redemption_days = st.number_input("ระยะเวลาไถ่ถอน (วัน)", min_value=30, value=180)

if st.button("บันทึกทรัพย์"):
    # ✅ Validation
    if location.strip() == "":
        st.error("❌ ต้องกรอกทำเล")
    elif room_size <= 0:
        st.error("❌ ขนาดห้องต้องมากกว่า 0")
    elif value <= 0:
        st.error("❌ ราคาที่เจ้าของเสนอต้องมากกว่า 0")
    elif units <= 0 or nbr_floors <= 0:
        st.error("❌ จำนวนยูนิตและจำนวนชั้นต้องมากกว่า 0")
    else:
        start = datetime.today().strftime("%Y-%m-%d")
        end = (datetime.today() + timedelta(days=redemption_days)).strftime("%Y-%m-%d")

        # ✅ ตรวจสอบ schema
        cols = [c[1] for c in run_query("PRAGMA table_info(properties);", fetch=True)]

        if all(col in cols for col in ["district_type", "nbr_floors", "units", "bld_age", "room_size"]):
            run_query("""INSERT INTO properties 
                         (owner_id, location, district_type, nbr_floors, units, bld_age, room_size, value, start_date, end_date, status) 
                         VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
                      (owner_id, location, district_type, nbr_floors, units, bld_age, room_size, value, start, end, "รอการลงทุน"))
        elif all(col in cols for col in ["district_type", "nbr_floors", "units", "bld_age"]):
            run_query("""INSERT INTO properties 
                         (owner_id, location, district_type, nbr_floors, units, bld_age, value, start_date, end_date, status) 
                         VALUES (?,?,?,?,?,?,?,?,?,?)""",
                      (owner_id, location, district_type, nbr_floors, units, bld_age, value, start, end, "รอการลงทุน"))
        else:
            run_query("""INSERT INTO properties 
                         (owner_id, location, value, start_date, end_date, status) 
                         VALUES (?,?,?,?,?,?)""",
                      (owner_id, location, value, start, end, "รอการลงทุน"))

        st.success("บันทึกทรัพย์เรียบร้อย ✅")
