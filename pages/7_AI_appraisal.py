import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error

st.title("🌲 AI Condo Price Appraisal (Random Forest)")

# --- Load Data ---
DATA_PATH = "Price per sqm_cleaned_data_selection3.csv"
df = pd.read_csv(DATA_PATH)

# --- Define Target & Features ---
target = "price_sqm"
features = ["bld_age", "nbr_floors", "units", "district_type"]

# Clean data
df = df.dropna(subset=features + [target])
X, y = df[features], df[target]

# --- Train Model ---
model = RandomForestRegressor(n_estimators=200, max_depth=10, random_state=42)
model.fit(X, y)

# --- Section 2: Evaluation ---
st.header("📈 Model Evaluation")
y_pred = model.predict(X)

col1, col2 = st.columns(2)
with col1:
    st.metric("R² Score", f"{r2_score(y, y_pred):.4f}")
with col2:
    st.metric("MAE (THB/sqm)", f"{mean_absolute_error(y, y_pred):,.2f}")


# --- Section 3: Prediction ---
st.header("📝 Condo Price Prediction")

inputs = {}
inputs["bld_age"] = st.number_input("Building Age (years)", min_value=0, value=10)
inputs["nbr_floors"] = st.number_input("Floor", min_value=1, value=5)
inputs["units"] = st.number_input("Total Units in Project", min_value=10, value=200)
inputs["district_type"] = st.selectbox("District Type", df["district_type"].unique())
room_size = st.number_input("Room Size (sqm)", min_value=10.0, value=30.0, step=1.0)

if st.button("Predict Price"):
    input_df = pd.DataFrame([inputs])
    predicted_ppsqm = model.predict(input_df)[0]
    st.success(f"🏷️ Predicted Price per sqm: {predicted_ppsqm:,.2f} THB")
    st.info(f"💰 Estimated Total Price: {predicted_ppsqm * room_size:,.2f} THB")
