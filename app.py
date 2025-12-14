import streamlit as st
import pandas as pd

# =====================
# KONFIGURASI HALAMAN
# =====================
st.set_page_config(
    page_title="Dashboard Analitik Brazilian E-Commerce",
    layout="wide"
)

st.title("Dashboard Analitik Brazilian E-Commerce")
st.caption("Sumber data: Tabel Fakta hasil ETL Pentaho Data Integration")

# =====================
# LOAD DATA
# =====================
@st.cache_data
def load_data():
    df = pd.read_csv(
        "fact_olist.csv",
        engine="python"
    )
    df.columns = df.columns.str.strip()
    df['purchase_date'] = pd.to_datetime(
        df['purchase_date'], errors="coerce"
    )
    return df

df = load_data()

# =====================
# SIDEBAR FILTER
# =====================
st.sidebar.subheader("🔎 Filter Data")

# kategori
kategori_list = ["All"] + sorted(df['category'].dropna().unique().tolist())
kategori = st.sidebar.selectbox("Kategori Produk", kategori_list)

# state
state_list = sorted(df['customer_state'].dropna().unique().tolist())
state = st.sidebar.multiselect("State Pelanggan", state_list)

# =====================
# TERAPKAN FILTER (INI YANG SEBELUMNYA KURANG)
# =====================
df_f = df.copy()

# Filter state
if len(state) > 0:
    df_f = df_f[df_f['customer_state'].isin(state)]

# Filter kategori
if kategori != "All":
    df_f = df_f[df_f['category'] == kategori]

# =====================
# KPI
# =====================
st.subheader("📌 Key Performance Indicator (KPI)")

col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "💰 Total Revenue",
    f"{df_f['total_revenue'].sum():,.0f}"
)

col2.metric(
    "🧾 Jumlah Order",
    df_f['order_id'].nunique()
)

col3.metric(
    "🚚 Rata-rata Delivery Duration (hari)",
    round(df_f['delivery_duration'].mean(), 2)
)

# KPI Rating + Bintang
avg_rating = df_f['customer_rating'].mean()
stars = "⭐" * int(round(avg_rating)) if not pd.isna(avg_rating) else ""

col4.metric(
    "⭐ Rata-rata Customer Rating",
    f"{avg_rating:.2f} {stars}"
)

# =====================
# GRAFIK
# =====================

# 1. Tren Revenue
st.subheader("Tren Revenue per Waktu")
trend = df_f.groupby(df_f['purchase_date'].dt.to_period('M'))['total_revenue'].sum()
st.line_chart(trend)

# 2. Revenue per Kategori
st.subheader("Penjualan per Kategori Produk")
rev_kat = df_f.groupby('category')['total_revenue'].sum().sort_values(ascending=False)
st.bar_chart(rev_kat)

# 3. Revenue per State
st.subheader("Penjualan per State")
rev_state = df_f.groupby('customer_state')['total_revenue'].sum().sort_values(ascending=False)
st.bar_chart(rev_state)

# 4. Status Pengiriman
st.subheader("Distribusi Status Pengiriman")
status = df_f['order_status'].value_counts()
st.bar_chart(status)

# 5. Metode Pembayaran
st.subheader("Metode Pembayaran")
payment = df_f.groupby('payment_type')['payment_amount'].sum()
st.bar_chart(payment)

# =====================
# TABEL FAKTA
# =====================
st.subheader("Tabel Fakta (Detail Data)")
st.dataframe(df_f)


