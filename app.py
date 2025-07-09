
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import xlsxwriter

# ========================
# KONFIGURASI USER & ROLE
# ========================
USERS = {
    "admin": {"password": "admin123", "role": "admin", "nmppk": None},
    "kikikusumawati": {"password": "mekongga123", "role": "user", "nmppk": "MEKONGGA"},
    "rahmawati": {"password": "ppkm123", "role": "user", "nmppk": "PPKM"},
}

# ========================
# INISIALISASI STATE
# ========================
if "notifications" not in st.session_state:
    st.session_state["notifications"] = {}

# ========================
# LOGIN
# ========================
def login():
    st.title("🔐 Login Dashboard SRK")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    login_button = st.button("Login")

    if login_button:
        if username in USERS and USERS[username]["password"] == password:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.experimental_rerun()
        else:
            st.error("Username atau password salah")

# ========================
# LOAD DATA GOOGLE SHEET
# ========================
def load_data():
    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["google"], scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open("SRK BOMBANA").sheet1
    records = sheet.get_all_records()
    return pd.DataFrame(records)

# ========================
# RESET PASSWORD
# ========================
def reset_password():
    st.subheader("🔁 Ganti Password")
    current_user = st.session_state["username"]
    role = USERS[current_user]["role"]

    if role == "admin":
        selected_user = st.selectbox("Pilih User", list(USERS.keys()))
        new_pw = st.text_input("Password Baru", type="password")
        if st.button("Reset Password"):
            USERS[selected_user]["password"] = new_pw
            st.success(f"Password untuk {selected_user} berhasil diubah.")
    else:
        old_pw = st.text_input("Password Lama", type="password")
        new_pw = st.text_input("Password Baru", type="password")
        if st.button("Ubah Password"):
            if old_pw == USERS[current_user]["password"]:
                USERS[current_user]["password"] = new_pw
                st.success("Password berhasil diubah.")
            else:
                st.error("Password lama salah.")

# ========================
# KIRIM NOTIFIKASI ADMIN
# ========================
def send_notification():
    st.subheader("📣 Kirim Notifikasi ke User")
    target_user = st.selectbox("Pilih User", [u for u in USERS if USERS[u]["role"] == "user"])
    message = st.text_area("Isi Notifikasi")

    if st.button("Kirim Notifikasi"):
        notif_dict = st.session_state["notifications"]
        if target_user not in notif_dict:
            notif_dict[target_user] = []
        notif_dict[target_user].append(message)
        st.success(f"Notifikasi berhasil dikirim ke {target_user}")

# ========================
# GENERATE EXCEL
# ========================
def generate_excel_download(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Data')
        writer.save()
    output.seek(0)
    return output

# ========================
# GENERATE GAMBAR GRAFIK
# ========================
def generate_chart_image(df_grouped):
    fig, ax = plt.subplots()
    df_grouped.plot(kind='bar', x='NMPPK', y='Capaian', ax=ax)
    ax.set_title("Diagram Capaian per NMPPK")
    ax.set_ylabel("Capaian")
    fig.tight_layout()
    img_bytes = BytesIO()
    fig.savefig(img_bytes, format='png')
    img_bytes.seek(0)
    return img_bytes

# ========================
# DASHBOARD UTAMA
# ========================
def show_dashboard():
    df = load_data()
    user_info = USERS[st.session_state["username"]]
    role = user_info["role"]
    nmppk_user = user_info["nmppk"]

    # Logo dan Judul
    st.image("logo.png", width=120)
    st.markdown("<h1 style='color:#0a8754;'>Dashboard SRK BOMBANA</h1>", unsafe_allow_html=True)

    # Filter bulan
    if role == "admin":
        df_filtered = df
    else:
        df_filtered = df[df["NMPPK"] == nmppk_user]

    if "Bulan" in df_filtered.columns:
        bulan_terpilih = st.selectbox("📆 Pilih Bulan", sorted(df_filtered["Bulan"].unique()))
        df_filtered = df_filtered[df_filtered["Bulan"] == bulan_terpilih]

    st.dataframe(df_filtered)

    if "NMPPK" in df_filtered.columns and "Capaian" in df_filtered.columns:
        chart_data = df_filtered.groupby("NMPPK")["Capaian"].sum().reset_index()
        st.subheader("📌 Diagram Batang Capaian")
        st.bar_chart(chart_data.set_index("NMPPK"))

        st.subheader("📆 Grafik Gabungan Beberapa Bulan")
        df_month = df_filtered.groupby(["Bulan", "NMPPK"])["Capaian"].sum().reset_index()
        df_pivot = df_month.pivot(index="Bulan", columns="NMPPK", values="Capaian").fillna(0)
        st.line_chart(df_pivot)

        st.subheader("⬇️ Ekspor Data ke Excel")
        excel_data = generate_excel_download(df_filtered)
        st.download_button("Download Excel", data=excel_data, file_name="data_srkkonsel.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        st.subheader("🖼️ Unduh Grafik sebagai Gambar PNG")
        chart_image = generate_chart_image(chart_data)
        st.download_button("Download Grafik PNG", data=chart_image, file_name="grafik_capaian.png", mime="image/png")

    menu = st.sidebar.radio("Menu", ["Dashboard", "Reset Password", "Notifikasi", "Generate Akun User"] + (["Upload Data (Admin Only)"] if role == "admin" else []))
    if menu == "Reset Password":
        reset_password()
    elif menu == "Notifikasi":
        if role == "admin":
            send_notification()
        else:
            st.subheader("📬 Notifikasi Anda")
            messages = st.session_state["notifications"].get(st.session_state["username"], [])
            if messages:
                for msg in messages[::-1]:
                    st.info(msg)
            else:
                st.write("Belum ada notifikasi.")
    elif menu == "Upload Data (Admin Only)":
        if role != "admin":
            st.warning("Hanya admin yang bisa mengakses menu ini.")
        else:
            st.subheader("📤 Upload Data ke Google Sheet")
            uploaded = st.file_uploader("Upload file Excel", type=["xlsx"])
            if uploaded:
                df_new = pd.read_excel(uploaded)
                st.dataframe(df_new)
                if st.button("Upload ke Google Sheet"):
                    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
                    creds = Credentials.from_service_account_info(st.secrets["google"], scopes=scope)
                    client = gspread.authorize(creds)
                    sheet = client.open("SRK BOMBANA").sheet1
                    sheet.clear()
                    sheet.update([df_new.columns.values.tolist()] + df_new.values.tolist())
                    st.success("Data berhasil diunggah ke Google Sheet.")

    if st.button("Logout"):
        st.session_state.clear()
        st.experimental_rerun()

# ========================
# MAIN
# ========================
if "logged_in" not in st.session_state:
    login()
else:
    show_dashboard()


def generate_user_password_from_sheet():
    st.subheader("🔐 Generate Akun User dari Google Sheet")

    scope = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(st.secrets["google"], scopes=scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key("11O5e0klK3Giry-uXwoXS2zmUl5L7rpl-Yl-KXNROFoo").sheet1
    data = sheet.get_all_records()
    df = pd.DataFrame(data)

    if "NMPPK" not in df.columns:
        st.error("Kolom 'NMPPK' tidak ditemukan.")
        return

    nmppk_list = df["NMPPK"].dropna().unique().tolist()

    df_users = pd.DataFrame({
        "Username": [n.lower().replace(" ", "") for n in nmppk_list],
        "Password": [n.lower().replace(" ", "") + "123" for n in nmppk_list],
        "NMPPK": nmppk_list,
        "Role": ["user"] * len(nmppk_list)
    })

    df_users = pd.concat([pd.DataFrame({
        "Username": ["admin"],
        "Password": ["admin123"],
        "NMPPK": [None],
        "Role": ["admin"]
    }), df_users], ignore_index=True)

    st.dataframe(df_users)

    from io import BytesIO
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_users.to_excel(writer, index=False, sheet_name='UserLogin')
    output.seek(0)

    st.download_button("📥 Download Akun User Excel", data=output, file_name="akun_user_dari_google_sheet.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")


if menu == "Generate Akun User":
    if role == "admin":
        generate_user_password_from_sheet()
    else:
        st.warning("Menu ini hanya untuk admin.")