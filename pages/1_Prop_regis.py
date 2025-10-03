import streamlit as st
import pandas as pd
import os
from db_utils import run_query, log_history, get_last_id   # ✅ import get_last_id

st.title("🏠 Property Registration")

# Require login
if "username" not in st.session_state:
    st.warning("⚠️ You must login first (go to Register/Login page)")
    st.stop()

username = st.session_state.get("username")
role = st.session_state.get("role")

# -------------------
# Sidebar user info
# -------------------
with st.sidebar:
    st.markdown("### 👤 User Info")
    st.write(f"**Name:** {username}")
    st.write(f"**Role:** {role.capitalize() if role else 'N/A'}")

# Role check
if role != "owner":
    st.error("Only property owners can register properties.")
    st.stop()

# --- UI Form ---
condo_name = st.text_input("Condo Name")
area = st.text_input("Area (เขตในกรุงเทพฯ)")
floor = st.text_input("Floor")
room_size = st.number_input("Room Size (sqm)", min_value=0.0, format="%.2f")
location = st.text_input("Location (optional)")
value = st.number_input("Estimated Value (THB)", min_value=0)
doc = st.file_uploader("Upload Property Document", type=["pdf", "jpg", "png"])

if st.button("Submit Property"):
    try:
        user = run_query("SELECT id FROM users WHERE username=?", (username,))
        if user:
            user_id = user[0][0]
            doc_name = doc.name if doc else None
            prop_name = f"{condo_name}, Floor {floor}, {area}, {room_size} sqm"

            run_query(
                "INSERT INTO properties (user_id,name,location,value,document_name,room_size) VALUES (?,?,?,?,?,?)",
                (user_id, prop_name, location, value, doc_name, room_size)
            )

            # ✅ get last inserted property_id
            new_property_id = get_last_id()

            # ✅ log history (include property_id)
            log_history(new_property_id, f"Owner registered new property: {prop_name}", username)

            st.success(f"✅ Property '{prop_name}' registered! (ID: {new_property_id})")
        else:
            st.error("User not found in DB")
    except Exception as e:
        st.error(f"❌ Error while saving property: {e}")
