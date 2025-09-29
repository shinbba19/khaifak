import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score

# โหลด dataset (เช่นที่ชินอัปมา)
df = pd.read_csv("Price per sqm_cleaned_data_selection3.csv")

# ✅ features และ target
features = ["district_type", "nbr_floors", "units", "bld_age", "room_size"]
target = "price_sqm"   # ต้องมีใน dataset

X = df[features]
y = df[target]

# แบ่ง train/test
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# เทรนโมเดล
model = RandomForestRegressor(n_estimators=200, random_state=42)
model.fit(X_train, y_train)

# ประเมินผล
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print(f"MAE: {mae:.2f}, R²: {r2:.2f}")

# ✅ เซฟโมเดล + features + metrics
joblib.dump(model, "price_model.pkl")
joblib.dump(features, "features.pkl")
joblib.dump({"MAE": mae, "R2": r2}, "metrics.pkl")

print("✅ Model saved as price_model.pkl, features.pkl, metrics.pkl")
