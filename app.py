
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from io import BytesIO

st.set_page_config(page_title="Dashboard SRK Konsel - Google Sheet", layout="wide")
st.markdown("<h1 style='text-align: center; color: #006400;'>📊 Dashboard SRK Konsel - Google Sheet</h1>", unsafe_allow_html=True)
st.markdown("---")

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("client_secret.json", scope)
client = gspread.authorize(creds)

sheet_name = "SRK Konsel Data"
sheet = client.open(sheet_name).sheet1
data = sheet.get_all_records()
df = pd.DataFrame(data)
df = df.rename(columns={df.columns[0]: "NMPPK"})

bulan_kolom = ['January', 'February', 'March', 'April', 'May', 'June', 'July']
for col in bulan_kolom:
    df[col] = pd.to_numeric(df[col], errors='coerce')

user_list = df["NMPPK"].dropna().unique()
username = st.sidebar.selectbox("Pilih NMPPK", user_list)
selected_data = df[df["NMPPK"] == username].iloc[0]
selected_months = st.multiselect("Pilih Bulan", bulan_kolom, default=bulan_kolom)
data_bulan = selected_data[selected_months]

st.subheader(f"Grafik Klaim Bulanan - {username}")
fig, ax = plt.subplots()
data_bulan.plot(kind='bar', ax=ax)
ax.set_ylabel("Jumlah Klaim")
ax.set_xlabel("Bulan")
st.pyplot(fig)

if "% capaian" in selected_data:
    try:
        capaian = float(selected_data["% capaian"])
        st.info(f"**% Capaian: {capaian:.2%}**")
    except:
        st.warning("Tidak dapat membaca nilai % capaian")

excel_output = BytesIO()
data_bulan.to_frame().reset_index().rename(columns={"index": "Bulan", 0: "Jumlah"}).to_excel(excel_output, index=False)
st.download_button("📥 Download Data Excel", data=excel_output.getvalue(), file_name=f"data_{username}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

img_output = BytesIO()
fig.savefig(img_output, format='png')
st.download_button("🖼️ Download Grafik PNG", data=img_output.getvalue(), file_name=f"grafik_{username}.png", mime="image/png")
