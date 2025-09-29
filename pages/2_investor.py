import streamlit as st
import pandas as pd
from db_utils import run_query, reset_db

st.title("💰 นักลงทุน")

# --- Reset Button ---
if st.sidebar.button("♻️ Reset Database"):
    reset_db()
    st.sidebar.success("Database ถูกรีเซ็ตเรียบร้อย ✅")

# --- Add Investor ---
st.subheader("เพิ่มข้อมูลนักลงทุน")
name = st.text_input("ชื่อ")
contact = st.text_input("เบอร์ติดต่อ")
if st.button("บันทึกนักลงทุน"):
    run_query("INSERT INTO investors (name, contact) VALUES (?,?)", (name, contact))
    st.success("บันทึกนักลงทุนเรียบร้อย ✅")

st.markdown("---")

# --- Show Properties ---
st.subheader("เลือกดีลลงทุน")

rows = run_query("SELECT * FROM properties", fetch=True)
if rows:
    df = pd.DataFrame(rows)
    st.dataframe(df)
    investor_id = st.number_input("Investor ID", min_value=1)
    property_id = st.number_input("Property ID", min_value=1)
    amount = st.number_input("จำนวนเงินลงทุน (บาท)", min_value=10000.0, step=10000.0)
    slip = st.text_input("หลักฐานการโอน (ลิงก์/ไฟล์)")
    if st.button("ยืนยันการลงทุน"):
        run_query("INSERT INTO investments (investor_id, property_id, amount, slip) VALUES (?,?,?,?)",
                  (investor_id, property_id, amount, slip))
        run_query("UPDATE properties SET status = ? WHERE id = ?",
                  (f"ลงทุนแล้ว {amount} บาท", property_id))
        st.success("ลงทุนเรียบร้อย 🎉")
else:
    st.warning("ยังไม่มีทรัพย์")
