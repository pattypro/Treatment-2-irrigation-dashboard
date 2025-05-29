
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# --- Dashboard Title ---
st.title("T2 Smart Irrigation Scheduler Dashboard")
st.markdown("""
This tool calculates daily irrigation recommendations for T2 treatment based on:
- **Soil Moisture at 15cm**
- **Evapotranspiration (ET0)**
- **Rain Forecast (next 6-12 hrs)**
""")

# --- Upload CSV ---
uploaded_file = st.file_uploader("Upload your sensor & weather data (.csv)", type="csv")

# --- Parameters ---
st.sidebar.header("Irrigation Parameters")
fc = st.sidebar.number_input("Field Capacity (FC) [%]", value=38.0)
trigger_threshold = 0.70 * fc
kc = st.sidebar.number_input("Crop Coefficient (Kc)", value=1.15)
forecast_rain_threshold = st.sidebar.number_input("Rain Threshold (mm)", value=2.0)

# --- Main Logic ---
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, parse_dates=['timestamp'])

    def irrigation_decision(row):
        if row['soil_moisture'] < trigger_threshold:
            if row['forecast_rain'] < forecast_rain_threshold:
                etc = row['ET0'] * kc
                irrigation = max(0, etc - row['forecast_rain'])
                return pd.Series([True, etc, irrigation])
            else:
                return pd.Series([False, 0, 0])
        else:
            return pd.Series([False, 0, 0])

    df[['irrigate', 'ETc', 'irrigation_mm']] = df.apply(irrigation_decision, axis=1)

    # Show Results
    st.success("Irrigation schedule generated successfully!")
    st.dataframe(df[['timestamp', 'soil_moisture', 'ET0', 'forecast_rain', 'irrigate', 'ETc', 'irrigation_mm']])

    # --- Visualization ---
    st.subheader("📊 Data Visualization")

    fig, ax = plt.subplots(figsize=(12, 6))
    sns.lineplot(data=df, x='timestamp', y='soil_moisture', label='Soil Moisture', marker='o', ax=ax)
    sns.lineplot(data=df, x='timestamp', y='ET0', label='ET0', marker='s', ax=ax)
    sns.lineplot(data=df, x='timestamp', y='forecast_rain', label='Rain Forecast', marker='^', ax=ax)
    sns.lineplot(data=df, x='timestamp', y='irrigation_mm', label='Irrigation (mm)', marker='D', ax=ax)
    ax.set_title("Soil Moisture, ET0, Rain Forecast, and Irrigation Over Time")
    ax.set_ylabel("Values")
    ax.set_xlabel("Date")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # Download option
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Irrigation Schedule", csv, "T2_irrigation_schedule.csv", "text/csv")

else:
    st.warning("Please upload your sensor and weather data file to proceed.")

# --- Sample CSV format hint ---
st.markdown("""
#### 📄 Sample CSV Format:
| timestamp | soil_moisture | ET0 | forecast_rain |
|-----------|----------------|------|----------------|
| 2025-06-01 06:00 | 25 | 4.2 | 0.5 |
| 2025-06-02 06:00 | 27 | 3.9 | 3.0 |
| 2025-06-03 06:00 | 24 | 4.0 | 1.5 |
""")
