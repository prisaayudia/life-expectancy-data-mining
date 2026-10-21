app_code = r'''import streamlit as st
import pandas as pd
import numpy as np
import joblib

st.set_page_config(
    page_title="Life Expectancy Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

model = joblib.load("best_model.pkl")
feature_columns = joblib.load("feature_columns.pkl")
defaults = joblib.load("feature_defaults.pkl")
feature_ranges = joblib.load("feature_ranges.pkl")
model_name = joblib.load("model_name.pkl")

friendly_labels = {
    "Year": "Year",
    "Status": "Status",
    "Adult Mortality": "Adult Mortality",
    "infant deaths": "Infant deaths",
    "Alcohol": "Alcohol consumption",
    "percentage expenditure": "Percentage expenditure",
    "Hepatitis B": "Hepatitis B immunization",
    "Measles": "Measles cases",
    "BMI": "BMI",
    "under-five deaths": "Under-five deaths",
    "Polio": "Polio immunization",
    "Total expenditure": "Total health expenditure",
    "Diphtheria": "Diphtheria immunization",
    "HIV/AIDS": "HIV/AIDS",
    "GDP": "GDP",
    "Population": "Population",
    "thinness 1-19 years": "Thinness 1-19 years",
    "thinness 5-9 years": "Thinness 5-9 years",
    "Income composition of resources": "Income composition",
    "Schooling": "Schooling"
}

sections = {
    "Profil negara": ["Year", "Status", "Population", "GDP", "Schooling", "Income composition of resources"],
    "Kesehatan & imunisasi": ["Adult Mortality", "Alcohol", "Hepatitis B", "Polio", "Diphtheria", "Total expenditure"],
    "Penyakit & nutrisi": ["infant deaths", "under-five deaths", "Measles", "BMI", "HIV/AIDS", "thinness 1-19 years", "thinness 5-9 years", "percentage expenditure"]
}

st.markdown(
    """
    <style>
    .stApp {
        background: linear-gradient(180deg, #f7fbff 0%, #eef6ff 100%);
    }
    .hero {
        padding: 1.35rem 1.5rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #0f172a 0%, #1d4ed8 55%, #38bdf8 100%);
        color: white;
        box-shadow: 0 14px 32px rgba(37, 99, 235, 0.22);
        margin-bottom: 1rem;
    }
    .hero h1 {
        margin: 0;
        font-size: 2.2rem;
    }
    .hero p {
        margin: 0.45rem 0 0 0;
        font-size: 1rem;
        opacity: 0.95;
    }
    .mini-card {
        background: white;
        border-radius: 18px;
        padding: 1rem 1.1rem;
        box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
        border: 1px solid rgba(148, 163, 184, 0.18);
    }
    div[data-testid="stMetric"] {
        background: white;
        border: 1px solid rgba(148, 163, 184, 0.2);
        padding: 16px;
        border-radius: 18px;
        box-shadow: 0 8px 20px rgba(15, 23, 42, 0.06);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero">
        <h1>🌍 Life Expectancy Dashboard</h1>
        <p>Prediksi harapan hidup berdasarkan indikator kesehatan, ekonomi, dan nutrisi. Model aktif: <b>{model_name}</b>.</p>
    </div>
    """,
    unsafe_allow_html=True,
)


def safe_bounds(col):
    info = feature_ranges.get(col, {})
    mn = float(info.get("min", 0.0))
    mx = float(info.get("max", max(1.0, defaults.get(col, 1.0) * 2)))
    if not np.isfinite(mn) or not np.isfinite(mx) or mn == mx:
        mn, mx = 0.0, max(1.0, defaults.get(col, 1.0) * 2)
    return mn, mx


def render_input(col):
    label = friendly_labels.get(col, col)
    default_val = float(defaults.get(col, 0.0))
    mn, mx = safe_bounds(col)

    if col == "Status":
        return st.selectbox(
            label,
            options=[0, 1],
            index=1 if default_val >= 0.5 else 0,
            format_func=lambda x: "Developed" if x == 1 else "Developing"
        )

    if 0 <= mn and mx <= 100:
        return st.slider(label, min_value=float(mn), max_value=float(mx), value=float(np.clip(default_val, mn, mx)))

    step = max((mx - mn) / 200, 0.1)
    return st.number_input(
        label,
        min_value=float(mn),
        max_value=float(mx),
        value=float(np.clip(default_val, mn, mx)),
        step=float(step),
        format="%.4f"
    )

with st.sidebar:
    st.header("⚙️ Input fitur")
    st.caption("Ubah indikator negara lalu lihat perubahan prediksi secara real-time.")
    user_input = {}
    for section, cols in sections.items():
        with st.expander(section, expanded=(section == "Profil negara")):
            for col in cols:
                user_input[col] = render_input(col)

for col in feature_columns:
    if col not in user_input:
        user_input[col] = float(defaults.get(col, 0.0))

input_df = pd.DataFrame([user_input])[feature_columns]
prediction = float(model.predict(input_df)[0])
progress_value = max(0.0, min(prediction / 90.0, 1.0))

if prediction < 60:
    category = "Perlu perhatian"
    category_note = "Harapan hidup relatif rendah dibanding rata-rata global."
elif prediction < 75:
    category = "Menengah"
    category_note = "Harapan hidup berada di level menengah dan masih dapat ditingkatkan."
else:
    category = "Tinggi"
    category_note = "Harapan hidup termasuk tinggi dan menunjukkan profil kesehatan yang baik."

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Prediksi Life Expectancy", f"{prediction:.2f} tahun")
with c2:
    st.metric("Kategori", category)
with c3:
    status_label = "Developed" if input_df["Status"].iloc[0] == 1 else "Developing"
    st.metric("Status negara", status_label)

st.progress(progress_value, text=f"Posisi prediksi pada skala 0-90 tahun: {prediction:.2f}")

left, right = st.columns([1.2, 1])
with left:
    st.markdown('<div class="mini-card">', unsafe_allow_html=True)
    st.subheader("Ringkasan interpretasi")
    st.write(category_note)

    notes = []
    if input_df["Adult Mortality"].iloc[0] > defaults["Adult Mortality"]:
        notes.append("Adult Mortality di atas median dataset cenderung menekan life expectancy.")
    if input_df["Schooling"].iloc[0] > defaults["Schooling"]:
        notes.append("Schooling di atas median biasanya mendorong prediksi life expectancy lebih tinggi.")
    if input_df["Income composition of resources"].iloc[0] > defaults["Income composition of resources"]:
        notes.append("Income composition yang lebih baik berkorelasi positif dengan harapan hidup.")
    if input_df["HIV/AIDS"].iloc[0] > defaults["HIV/AIDS"]:
        notes.append("Nilai HIV/AIDS yang tinggi sering dikaitkan dengan penurunan harapan hidup.")
    if input_df["BMI"].iloc[0] < defaults["BMI"]:
        notes.append("BMI di bawah median dapat menjadi sinyal masalah gizi atau kesehatan populasi.")
    if not notes:
        notes.append("Kombinasi input saat ini cukup dekat dengan nilai tengah dataset.")

    for note in notes:
        st.write(f"- {note}")
    st.markdown('</div>', unsafe_allow_html=True)

with right:
    chart_features = [
        "Adult Mortality", "Schooling", "Income composition of resources",
        "BMI", "HIV/AIDS", "GDP"
    ]
    normalized = {}
    for col in chart_features:
        mn, mx = safe_bounds(col)
        normalized[friendly_labels[col]] = (float(input_df[col].iloc[0]) - mn) / (mx - mn + 1e-9)
    chart_df = pd.DataFrame({"Normalized value": normalized}).T
    st.subheader("Profil input (normalisasi 0-1)")
    st.bar_chart(chart_df)

tab1, tab2 = st.tabs(["📋 Detail Input", "ℹ️ Tentang Model"])
with tab1:
    show_df = input_df.rename(columns=friendly_labels).T
    show_df.columns = ["Nilai"]
    st.dataframe(show_df, use_container_width=True)

with tab2:
    st.write(f"Model terbaik yang disimpan: **{model_name}**")
    st.write("Fitur yang digunakan:")
    st.write(", ".join([friendly_labels.get(col, col) for col in feature_columns]))
    st.info("Aplikasi ini cocok untuk demo akademik atau portofolio data mining. Untuk produksi, tambahkan validasi input, logging, dan monitoring model.")
'''
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(app_code)

print('File app.py berhasil dibuat.')
