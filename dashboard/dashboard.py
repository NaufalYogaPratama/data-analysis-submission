import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from babel.numbers import format_currency

sns.set(style='darkgrid')

# Fungsi pembantu yang dibutuhkan untuk menyiapkan berbagai dataframe
def create_daily_rentals_df(day_df):
    daily_rentals_df = day_df.groupby("dteday").agg({
        "casual": "sum",
        "registered": "sum",
        "cnt": "sum"
    }).reset_index()
    daily_rentals_df.rename(columns={"dteday": "date"}, inplace=True)
    return daily_rentals_df

def create_seasonal_rental_df(day_df):
    seasonal_rental_df = day_df.groupby('season')['cnt'].sum().reset_index()
    seasonal_rental_df.rename(columns={'cnt': 'total_rental'}, inplace=True)
    return seasonal_rental_df

def create_workingday_rental_df(day_df):
    workingday_rental_df = day_df.groupby('workingday')['cnt'].sum().reset_index()
    workingday_rental_df.rename(columns={'cnt': 'total_rental'}, inplace=True)
    return workingday_rental_df

def create_weather_rental_df(day_df):
    weather_rental_df = day_df.groupby('weathersit')['cnt'].sum().reset_index()
    weather_rental_df.rename(columns={'cnt': 'total_rental'}, inplace=True)
    return weather_rental_df

def create_daily_trend_df(day_df):
    daily_trend_df = pd.DataFrame(day_df.set_index('dteday')['cnt'])
    daily_trend_df.rename(columns={'cnt': 'total_rental'}, inplace=True)
    return daily_trend_df

def create_hourly_rentals_df(hour_df):
    hourly_rentals_df = hour_df.groupby('hr')['cnt'].sum().reset_index()
    hourly_rentals_df.rename(columns={'cnt': 'total_rental'}, inplace=True)
    return hourly_rentals_df

# Load data bersih
try:
    day_df = pd.read_csv("dashboard/day_data_clean.csv")
    hour_df = pd.read_csv("dashboard/hour_data_clean.csv")
    day_df["dteday"] = pd.to_datetime(day_df["dteday"])
    
    # Periksa apakah kolom 'hr' ada di hour_df
    if 'hr' not in hour_df.columns:
        st.error("Kolom 'hr' tidak ditemukan dalam file 'hour.csv'.")
        st.stop()
except FileNotFoundError:
    st.error("File 'day.csv' atau 'hour.csv' tidak ditemukan.")
    st.stop()
    
# Sidebar untuk pemfilteran tanggal
st.sidebar.image("https://www.pngplay.com/wp-content/uploads/7/Downhill-Mountain-Bike-Transparent-Background.png")
st.sidebar.title("Bike Sharing Dashboard")
start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Tanggal",
    [day_df["dteday"].min(), day_df["dteday"].max()]
)

if start_date > end_date:
    st.sidebar.error("Tanggal mulai tidak boleh lebih besar dari tanggal akhir.")
    st.stop()
    
filtered_df = day_df[(day_df["dteday"] >= pd.Timestamp(start_date)) & (day_df["dteday"] <= pd.Timestamp(end_date))]

# Siapkan subset data
daily_rentals_df = create_daily_rentals_df(filtered_df)
seasonal_rentals_df = create_seasonal_rental_df(filtered_df)
workingday_rentals_df = create_workingday_rental_df(filtered_df)
weather_rentals_df = create_weather_rental_df(filtered_df)
daily_trend_df = create_daily_trend_df(filtered_df)
hourly_rentals_df = create_hourly_rentals_df(hour_df)

# Konten utama dashboard
st.header("Bike Sharing Data Analysis")
st.subheader("Summary Metrics")

col1, col2, col3 = st.columns(3)
with col1:
    total_rentals = daily_rentals_df["cnt"].sum()
    st.metric("Total Penyewaan", f"{total_rentals:,}")

with col2:
    casual_rentals = daily_rentals_df["casual"].sum()
    st.metric("Penyewaan Kasual", f"{casual_rentals:,}")

with col3:
    registered_rentals = daily_rentals_df["registered"].sum()
    st.metric("Penyewaan Terdaftar", f"{registered_rentals:,}")
    
# Plot rata-rata penyewaan berdasarkan musim
st.header("Rata-rata Penyewaan Berdasarkan Musim")
fig1, ax1 = plt.subplots(figsize=(8, 5))
sns.barplot(x=day_df['season'], y=day_df['cnt'], errorbar=None, estimator='mean', hue=day_df['season'], palette=["#B3D7AE", "#B3D7AE", "#44935B", "#B3D7AE"], legend=False, ax=ax1)
ax1.set_xlabel("Musim")
ax1.set_ylabel("Jumlah Penyewaan")
ax1.set_xticks([0, 1, 2, 3])
ax1.set_xticklabels(['Semi', 'Panas', 'Gugur', 'Salju'])
st.pyplot(fig1)

# Plot rata-rata penyewaan berdasarkan hari kerja
st.header("Rata-rata Penyewaan Berdasarkan Hari Kerja")
fig2, ax2 = plt.subplots(figsize=(8, 5))
sns.barplot(x=day_df['workingday'], y=day_df['cnt'], errorbar=None, estimator='mean', hue=day_df['workingday'], palette='Greens', legend=False, ax=ax2)
ax2.set_xlabel("Hari")
ax2.set_ylabel("Jumlah Penyewaan")
ax2.set_xticks([0, 1])
ax2.set_xticklabels(['Libur', 'Kerja'])
st.pyplot(fig2)

# Plot penyewaan berdasarkan kondisi cuaca
st.header("Penyewaan Berdasarkan Kondisi Cuaca")
fig3, ax3 = plt.subplots(figsize=(8, 5))
sns.barplot(x=day_df['weathersit'], y=day_df['cnt'], errorbar=None, estimator='mean', hue=day_df['weathersit'], palette=["#44935B", "#B3D7AE", "#B3D7AE"], legend=False, ax=ax3)
ax3.set_xlabel("Kondisi Cuaca")
ax3.set_ylabel("Jumlah Penyewaan")
ax3.set_xticks([0, 1, 2, 3])
ax3.set_xticklabels(['Cerah', 'Kabut', 'Hujan Ringan', 'Hujan Deras/Snow'])
st.pyplot(fig3)

# Plot tren penyewaan sepeda harian
st.header("Tren Penyewaan Sepeda (2011-2012)")
fig4, ax4 = plt.subplots(figsize=(15, 6))
ax4.plot(day_df['dteday'], day_df['cnt'], color='#44935B', label='Jumlah Penyewaan Harian')
ax4.set_xlabel("Tanggal")
ax4.set_ylabel("Jumlah Penyewaan")
ax4.legend()
ax4.grid()
st.pyplot(fig4)

# Plot rata-rata penyewaan berdasarkan jam
st.header("Rata-rata Penyewaan Berdasarkan Jam")
fig5, ax5 = plt.subplots(figsize=(10, 6))
sns.lineplot(x=hour_df['hr'], y=hour_df['cnt'], estimator='mean', errorbar=None, color='#44935B', ax=ax5)
ax5.set_xlabel("Jam")
ax5.set_ylabel("Jumlah Penyewaan")
ax5.grid()
st.pyplot(fig5)