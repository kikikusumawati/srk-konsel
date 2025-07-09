
import streamlit as st

# Fungsi untuk generate akun
def generate_user_password_from_sheet():
    st.title("Generate Akun User")
    st.write("Fitur ini akan menarik NMPPK dari Google Sheet dan membuat username + password.")
    st.success("Fitur aktif. (Simulasi)")

# Fungsi utama dashboard
def show_dashboard(role):
    menu = st.sidebar.radio("Menu", ["Dashboard", "Generate Akun User", "Pengaturan"])

    if menu == "Dashboard":
        st.title("📊 Dashboard Utama")
        st.write("Selamat datang di Dashboard SRK.")
    elif menu == "Generate Akun User":
        if role == "admin":
            generate_user_password_from_sheet()
        else:
            st.warning("Menu ini hanya untuk admin.")
    else:
        st.info("Pengaturan lainnya.")

# Halaman login
def main():
    st.set_page_config(page_title="Dashboard SRK", page_icon="📊", layout="wide")
    st.title("🔐 Login Dashboard SRK")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            show_dashboard("admin")
        else:
            st.error("Login gagal.")

if __name__ == "__main__":
    main()
