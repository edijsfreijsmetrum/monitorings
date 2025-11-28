
import streamlit as st
import os
import base64
import requests
import datetime
from zoneinfo import ZoneInfo

# Supabase konfigurācija
supabase_url = st.secrets["supabase_url"]
supabase_key = st.secrets["supabase_key"]

# Konstantas
APP_NAME = "Monitoringa atskaite"
APP_VERSION = "1.8"
APP_TYPE = "web"

# Iestatījumi ar "wide" izkārtojumu
st.set_page_config(page_title="Monitoringa atskaite", layout="wide")

def authenticate(username, password):
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json",
        }
        url = f"{supabase_url}/rest/v1/users"
        params = {
            "select": "*",
            "username": f"eq.{username}",
            "password": f"eq.{password}",
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            data = response.json()
            if data:
                return True
            else:
                return False
        else:
            st.error(f"Kļūda autentificējot lietotāju: {response.status_code}")
            return False
    except Exception as e:
        st.error(f"Kļūda: {str(e)}")
        return False

def log_user_login(username):
    try:
        # Iegūstiet aktuālo laiku Latvijas laika zonā
        riga_tz = ZoneInfo('Europe/Riga')
        current_time = datetime.datetime.now(riga_tz).isoformat()

        # Sagatavojiet datu vārdnīcu ar pareiziem kolonnu nosaukumiem
        data = {
            "username": username,
            "App": APP_NAME,
            "Ver": APP_VERSION,
            "app_type": APP_TYPE,
            "login_time": current_time
        }

        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        url = f"{supabase_url}/rest/v1/user_data"

        response = requests.post(url, json=data, headers=headers)

        if response.status_code not in [200, 201]:
            st.error(f"Kļūda ierakstot datus: {response.status_code}, {response.text}")
    except Exception as e:
        st.error(f"Kļūda: {str(e)}")

def login():
    username = st.session_state.get('username', '').strip()
    password = st.session_state.get('password', '').strip()
    if not username or not password:
        st.error("Lūdzu, ievadiet gan lietotājvārdu, gan paroli.")
    else:
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.session_state.username_logged = username
            log_user_login(username)
        else:
            st.error("Nepareizs lietotājvārds vai parole.")

def show_login():
    # Centrotu virsrakstu ar HTML
    st.markdown("<h1 style='text-align: center;'>Monitoringa atskaite v1.8</h1>", unsafe_allow_html=True)

    # Izmanto st.columns, lai centrētu formu un ierobežotu tās platumu
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        with st.form(key='login_form'):
            username = st.text_input("Lietotājvārds", key='username')
            password = st.text_input("Parole", type="password", key='password')
            submit_button = st.form_submit_button(label="Pieslēgties", on_click=login)

    st.markdown("<div style='text-align: center; margin-top: 20px; color: gray;'>© 2024 METRUM</div>", unsafe_allow_html=True)

def show_html_content():
    # Paslēpt Streamlit UI elementus ar CSS
    hide_streamlit_style = """
        <style>
        /* Paslēpt galveno izvēlni */
        #MainMenu {visibility: hidden;}
        /* Paslēpt virsrakstu */
        header {visibility: hidden;}
        /* Paslēpt kājeni */
        footer {visibility: hidden;}
        /* Nodrošina, ka stApp aizņem visu logu un izmanto Flexbox, lai centrētu saturu */
        .stApp {
            height: 100vh;
            width: 100vw;
            margin: 0;
            padding: 0;
            display: flex;
            justify-content: center;
            align-items: center;
            background-color: white; /* Opcijas fona krāsa */
        }
        /* Nodrošina, ka iframe aizņem visu stApp */
        .iframe-container {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # Izveidojiet iframe ar iebūvētu HTML saturu
    html_file_path = os.path.join("assets", "index.html")
    if os.path.exists(html_file_path):
        with open(html_file_path, 'rb') as HtmlFile:
            source_code = HtmlFile.read()
            # Encode the HTML content in base64
            encoded_html = base64.b64encode(source_code).decode()

        # Ievietojiet iframe ar base64 kodētu HTML saturu
        st.markdown(
            f'''
            <iframe src="data:text/html;base64,{encoded_html}" class="iframe-container"></iframe>
            ''',
            unsafe_allow_html=True
        )
    else:
        st.error("HTML fails nav atrasts `assets/index.html` ceļā.")

def main():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'username_logged' not in st.session_state:
        st.session_state.username_logged = ''

    if not st.session_state.logged_in:
        show_login()
    else:
        show_html_content()

if __name__ == "__main__":
    main()
