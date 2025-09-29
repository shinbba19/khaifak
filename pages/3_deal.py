import streamlit as st
import pandas as pd
import joblib
from db_utils import run_query, reset_db

st.title("📑 ดีลสรุป")

# --- Reset Button ---
if st.sidebar.button("♻️ Reset Database"):
    reset_db()
    st.sidebar.success("Database ถูกรีเซ็ตเรียบร้อย ✅")

# โหลดโมเดล + features
model = joblib.load("price_model.pkl")
features = joblib.load("features.pkl")

# --- Properties ---
rows_prop = run_query("SELECT * FROM properties", fetch=True)
st.subheader("ทรัพย์ทั้งหมด")

if rows_prop:
    df_prop = pd.DataFrame(rows_prop)

    # ✅ คำนวณ AI_Price_sqm และ AI_Value
    predictions = []
    for _, row in df_prop.iterrows():
        input_dict = {f: 0 for f in features}
        if "district_type" in df_prop.columns: input_dict["district_type"] = row.get("district_type", 1)
        if "nbr_floors" in df_prop.columns: input_dict["nbr_floors"] = row.get("nbr_floors", 1)
        if "units" in df_prop.columns: input_dict["units"] = row.get("units", 1)
        if "bld_age" in df_prop.columns: input_dict["bld_age"] = row.get("bld_age", 0)
        if "room_size" in df_prop.columns: input_dict["room_size"] = row.get("room_size", 30)

        X_input = pd.DataFrame([input_dict], columns=features).fillna(0)
        pred = model.predict(X_input)[0]
        predictions.append(pred)

    df_prop["AI_Price_sqm"] = predictions

    if "room_size" in df_prop.columns:
        df_prop["AI_Value"] = df_prop["AI_Price_sqm"] * df_prop["room_size"]
    else:
        df_prop["AI_Value"] = None
        st.warning("⚠️ room_size ไม่มีในตาราง properties (ลอง Reset Database)")

    st.dataframe(df_prop)
else:
    st.info("ยังไม่มีข้อมูลทรัพย์")

st.markdown("---")

# --- Investments ---
rows_invest = run_query("SELECT * FROM investments", fetch=True)
st.subheader("การลงทุนทั้งหมด")
if rows_invest:
    df_invest = pd.DataFrame(rows_invest)
    st.dataframe(df_invest)
else:
    st.info("ยังไม่มีข้อมูลการลงทุน")
