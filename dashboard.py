import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    # Load dataset bike sharing dengan jalur absolut
    hour_df = pd.read_csv('D:/Dicoding/Dashboard/dashboard/hour.csv')  # Ubah dengan jalur absolut Anda
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
    return hour_df

# Memuat data
hour_df = load_data()

st.title("Bike Sharing Dashboard")

# Pilihan untuk menampilkan data
st.sidebar.header("Filter Data")
date_range = st.sidebar.date_input("Pilih Rentang Tanggal", [hour_df['dteday'].min(), hour_df['dteday'].max()])

# Filter data berdasarkan rentang tanggal
filtered_df = hour_df[(hour_df['dteday'] >= pd.to_datetime(date_range[0])) & (hour_df['dteday'] <= pd.to_datetime(date_range[1]))]

st.subheader("Data Bike Sharing")
st.write(filtered_df.head())

# Agregasi data untuk analisis RFM
reference_date = filtered_df['dteday'].max()

rfm_df = filtered_df.groupby(filtered_df['dteday'].dt.to_period('M')).agg({
    'dteday': 'max',
    'casual': 'sum',
    'registered': 'sum',
    'cnt': 'sum'
}).reset_index()

rfm_df['Recency'] = (reference_date - rfm_df['dteday']).dt.days
rfm_df['Frequency_Casual'] = rfm_df['casual']
rfm_df['Frequency_Registered'] = rfm_df['registered']
rfm_df['Monetary_Casual'] = rfm_df['casual']
rfm_df['Monetary_Registered'] = rfm_df['registered']

rfm_df['Recency_Score'] = pd.qcut(rfm_df['Recency'], 5, labels=[5, 4, 3, 2, 1])
rfm_df['Frequency_Score'] = pd.qcut(rfm_df['Frequency_Casual'] + rfm_df['Frequency_Registered'], 5, labels=[1, 2, 3, 4, 5])
rfm_df['Monetary_Score'] = pd.qcut(rfm_df['Monetary_Casual'] + rfm_df['Monetary_Registered'], 5, labels=[1, 2, 3, 4, 5])

rfm_df['RFM_score'] = (rfm_df['Recency_Score'].astype(int) + 
                       rfm_df['Frequency_Score'].astype(int) + 
                       rfm_df['Monetary_Score'].astype(int)) / 3

rfm_df["customer_segment"] = np.where(
    rfm_df['RFM_score'] > 4.5, "Top customers", 
    np.where(rfm_df['RFM_score'] > 4, "High value customers",
             np.where(rfm_df['RFM_score'] > 3, "Medium value customers", 
                      np.where(rfm_df['RFM_score'] > 1.6, 'Low value customers', 'Lost customers'))))

rfm_df['Month'] = rfm_df['dteday'].dt.strftime('%b %Y')

st.subheader("Customer Segmentation Based on RFM Analysis")
st.write(rfm_df[['Month', 'RFM_score', 'customer_segment']].head(20))

# Visualisasi
fig, ax = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))
colors = ["#72BCD4"] * 5

sns.barplot(y="Recency", x="Month", data=rfm_df.sort_values(by="Recency", ascending=True).head(5), palette=colors, ax=ax[0])
ax[0].set_ylabel(None)
ax[0].set_xlabel("Month")
ax[0].set_title("By Recency (days)", loc="center", fontsize=12)
ax[0].tick_params(axis='x', labelsize=10, rotation=45)

sns.barplot(y="Frequency_Casual", x="Month", data=rfm_df.sort_values(by="Frequency_Casual", ascending=False).head(5), palette=colors, ax=ax[1])
ax[1].set_ylabel(None)
ax[1].set_xlabel("Month")
ax[1].set_title("By Frequency (Casual Users)", loc="center", fontsize=12)
ax[1].tick_params(axis='x', labelsize=10, rotation=45)

sns.barplot(y="Monetary_Registered", x="Month", data=rfm_df.sort_values(by="Monetary_Registered", ascending=False).head(5), palette=colors, ax=ax[2])
ax[2].set_ylabel(None)
ax[2].set_xlabel("Month")
ax[2].set_title("By Monetary (Registered Users)", loc="center", fontsize=12)
ax[2].tick_params(axis='x', labelsize=10, rotation=45)

plt.suptitle("Top Months Based on RFM Parameters", fontsize=16)
st.pyplot(fig)
