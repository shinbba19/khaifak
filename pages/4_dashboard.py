import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import joblib
import os
from db_utils import run_query, reset_db

st.title("📊 Dashboard + AI Valuation")

# --- Reset Button ---
if st.sidebar.button("♻️ Reset Database"):
    reset_db()
    st.sidebar.success("Database ถูกรีเซ็ตเรียบร้อย ✅")

# โหลดโมเดล + features
model = joblib.load("price_model.pkl")
features = joblib.load("features.pkl")

# โหลด metrics แบบ fallback
if os.path.exists("metrics.pkl"):
    metrics = joblib.load("metrics.pkl")
else:
    metrics = {"MAE": 0, "R2": 0}
    st.warning("⚠️ ยังไม่มี metrics.pkl (กรุณา run train_model.py ใหม่เพื่อดูผลจริง)")

# 📌 แสดง Metrics ของโมเดล
st.subheader("📈 Model Performance (จากชุด Test ตอน Train)")
st.metric("MAE (บาท/ตร.ม.)", f"{metrics['MAE']:.2f}")
st.metric("R²", f"{metrics['R2']:.2f}")

st.markdown("---")

# ดึงข้อมูลจาก DB
rows = run_query("SELECT * FROM properties", fetch=True)

if rows:
    df = pd.DataFrame(rows)

    # --- มูลค่าทรัพย์ตามสถานะ ---
    if "status" in df.columns and "value" in df.columns:
        st.subheader("มูลค่าทรัพย์ตามสถานะ")
        chart = df.groupby("status")["value"].sum()
        st.bar_chart(chart)

    st.markdown("---")

    # --- AI Valuation ---
    st.subheader("AI Valuation: ราคาที่ระบบประเมิน")

    predictions = []
    debug_inputs = []

    for _, row in df.iterrows():
        input_dict = {f: 0 for f in features}

        if "district_type" in df.columns: input_dict["district_type"] = row.get("district_type", 1)
        if "nbr_floors" in df.columns: input_dict["nbr_floors"] = row.get("nbr_floors", 1)
        if "units" in df.columns: input_dict["units"] = row.get("units", 1)
        if "bld_age" in df.columns: input_dict["bld_age"] = row.get("bld_age", 0)
        if "room_size" in df.columns: input_dict["room_size"] = row.get("room_size", 30)

        X_input = pd.DataFrame([input_dict], columns=features).fillna(0)
        pred = model.predict(X_input)[0]
        predictions.append(pred)
        debug_inputs.append(input_dict)

    df["AI_Price_sqm"] = predictions

    # ✅ ใช้สูตรเดียวเท่านั้น: AI_Value = AI_Price_sqm × room_size
    if "room_size" in df.columns:
        df["AI_Value"] = df["AI_Price_sqm"] * df["room_size"]
    else:
        st.error("❌ ไม่พบคอลัมน์ room_size ในตาราง properties (กรุณา reset DB ใหม่)")

    st.dataframe(df)

    st.markdown("---")

    # --- กราฟ Owner vs AI ---
    if "value" in df.columns and "AI_Value" in df.columns:
        st.subheader("กราฟเปรียบเทียบ ราคาที่เจ้าของเสนอ vs AI ประเมิน")
        plt.figure(figsize=(6,4))
        plt.scatter(df["value"], df["AI_Value"], alpha=0.7)
        plt.xlabel("ราคาที่เจ้าของเสนอ (บาท)")
        plt.ylabel("ราคาที่ AI ประเมิน (บาท)")
        plt.title("Owner vs AI Price Comparison")
        st.pyplot(plt.gcf())

    st.markdown("---")

    # --- Debug Section ---
    st.subheader("🔍 Debug Section")
    st.write("🎯 Features used by model:", features)
    st.write("📥 Sample inputs to model:")
    st.json(debug_inputs[:5])  
    st.write("📊 Predictions (AI_Price_sqm):", predictions[:5])

else:
    st.info("ยังไม่มีข้อมูลทรัพย์")
