import joblib
import pandas as pd

# โหลดโมเดลครั้งเดียว
model = joblib.load("condo_price_model.pkl")

# ตัวอย่าง feature mapping (คุณอาจต้องปรับให้ตรง dataset)
def predict_price(input_dict):
    # แปลง dict → DataFrame
    df = pd.DataFrame([input_dict])

    # TODO: ต้อง map area → dummy variables หรือ numerical
    # ตอนนี้ mock ให้ area ถูก drop ไป (เฉพาะ numeric)
    df = df.drop(columns=["area"], errors="ignore")

    # Predict
    pred = model.predict(df)[0]
    return pred
