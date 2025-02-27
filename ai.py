import os
import json
import requests
import streamlit as st
from dotenv import load_dotenv
import time
from datetime import datetime
import uuid
from authlib.integrations.requests_client import OAuth2Session
import webbrowser
from urllib.parse import urlencode

# Lade API-Keys und Auth0-Konfiguration aus .env-Datei
load_dotenv()
PRIMARY_API_KEY = os.getenv("GOOGLE_API_KEY_1")
BACKUP_API_KEY_1 = os.getenv("GOOGLE_API_KEY_2")
BACKUP_API_KEY_2 = os.getenv("GOOGLE_API_KEY_3")

# Auth0 Konfiguration
AUTH0_CLIENT_ID = os.getenv("AUTH0_CLIENT_ID")
AUTH0_CLIENT_SECRET = os.getenv("AUTH0_CLIENT_SECRET")
AUTH0_DOMAIN = os.getenv("AUTH0_DOMAIN")
AUTH0_CALLBACK_URL = os.getenv("AUTH0_CALLBACK_URL", "http://localhost:8501")

# Seitenkonfiguration
st.set_page_config(
    page_title="NeuraX",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS für schöneres UI
st.markdown("""
<style>
    /* Globale Styles */
    body {
        font-family: 'Inter', sans-serif;
    }
    
    /* Header Styling */
    .main-header {
        display: flex;
        align-items: center;
        margin-bottom: 2rem;
    }
    
    .main-header img {
        height: 60px;
        margin-right: 1rem;
    }
    
    .main-header h1 {
        color: #1E88E5;
        font-weight: 600;
    }
    
    /* Chat Messages */
    .chat-message {
        padding: 1.2rem; 
        border-radius: 1rem; 
        margin-bottom: 1rem; 
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        gap: 1rem;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: all 0.2s ease-in-out;
    }
    
    .chat-message:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    .chat-message.user {
        background-color: #f8f9fa;
        border-left: 4px solid #6c757d;
    }
    
    .chat-message.assistant {
        background-color: #e3f2fd;
        border-left: 4px solid #1E88E5;
    }
    
    .chat-message .avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        object-fit: cover;
        flex-shrink: 0;
        border: 2px solid #fff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .chat-message .message {
        flex-grow: 1;
        padding-top: 0.2rem;
        color: #212529;
        line-height: 1.5;
    }
    
    /* Sidebar Styling */
    .sidebar .chat-list {
        margin-bottom: 0.3rem;
        padding: 0.6rem;
        border-radius: 0.5rem;
        cursor: pointer;
        transition: all 0.2s ease;
        font-size: 0.9rem;
        border-left: 3px solid transparent;
        background-color: #f8f9fa;
    }
    
    .sidebar .chat-list:hover {
        background-color: #e9ecef;
        transform: translateX(2px);
    }
    
    .sidebar .chat-list.active {
        background-color: #e3f2fd;
        border-left: 3px solid #1E88E5;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #1E88E5;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton>button:hover {
        background-color: #1976D2;
        transform: translateY(-1px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    
    .stButton.secondary>button {
        background-color: #f8f9fa;
        color: #495057;
        border: 1px solid #ced4da;
    }
    
    .stButton.secondary>button:hover {
        background-color: #e9ecef;
    }
    
    /* Input Styling */
    .stTextInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #ced4da;
        padding: 0.75rem 1rem;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #1E88E5;
        box-shadow: 0 0 0 2px rgba(30,136,229,0.2);
    }
    
    /* User Profile */
    .user-profile {
        display: flex;
        align-items: center;
        background-color: #f8f9fa;
        padding: 0.75rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    
    .user-profile img {
        width: 36px;
        height: 36px;
        border-radius: 50%;
        margin-right: 0.75rem;
    }
    
    .user-profile .user-info {
        flex-grow: 1;
    }
    
    .user-profile .user-name {
        font-weight: 600;
        color: #212529;
        margin: 0;
    }
    
    .user-profile .user-email {
        font-size: 0.8rem;
        color: #6c757d;
        margin: 0;
    }
    
    /* Login Form */
    .login-container {
        max-width: 400px;
        margin: 4rem auto;
        padding: 2rem;
        background-color: black;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .login-logo {
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .login-btn {
        background-color: #1E88E5;
        color: white;
        border: none;
        border-radius: 6px;
        padding: 0.75rem 1rem;
        width: 100%;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.2s ease;
        text-decoration: none;
        display: inline-block;
        text-align: center;
    }
    
    .login-btn:hover {
        background-color: #1976D2;
    }
    
    /* Chat input */
    .chat-input-container {
        position: sticky;
        bottom: 1rem;
        background-color: rgba(255,255,255,0.9);
        backdrop-filter: blur(10px);
        border-radius: 8px;
        padding: 1rem;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.05);
        margin-top: 2rem;
    }
    
    /* Divider */
    hr {
        margin: 1.5rem 0;
        border: 0;
        height: 1px;
        background-image: linear-gradient(to right, rgba(0,0,0,0), rgba(0,0,0,0.1), rgba(0,0,0,0));
    }
    
    /* Typography */
    h1, h2, h3 {
        color: #212529;
    }
    
    .text-muted {
        color: #6c757d !important;
    }
    
    /* Settings panel */
    .settings-panel {
        background-color: #f8f9fa;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    
    /* Animated typing indicator */
    @keyframes pulse {
        0% { opacity: 0.4; }
        50% { opacity: 1; }
        100% { opacity: 0.4; }
    }
    
    .typing-indicator {
        display: flex;
        gap: 0.5rem;
        margin: 1rem 0;
    }
    
    .typing-indicator span {
        width: 8px;
        height: 8px;
        background-color: #1E88E5;
        border-radius: 50%;
        animation: pulse 1.5s infinite;
    }
    
    .typing-indicator span:nth-child(2) {
        animation-delay: 0.2s;
    }
    
    .typing-indicator span:nth-child(3) {
        animation-delay: 0.4s;
    }
    
    /* Toast Notifications */
    .toast {
        position: fixed;
        bottom: 1rem;
        right: 1rem;
        padding: 0.75rem 1.5rem;
        border-radius: 6px;
        background-color: #1E88E5;
        color: white;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        z-index: 1000;
        animation: slideIn 0.3s forwards;
    }
    
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    /* Code blocks */
    pre {
        background-color: #f1f3f5;
        padding: 1rem;
        border-radius: 8px;
        overflow-x: auto;
    }
    
    code {
        font-family: 'Fira Code', monospace;
        font-size: 0.9rem;
    }
    
    /* Fix for Streamlit components */
    .stTextInput>div {
        padding-top: 0 !important;
    }
    
    .stSelectbox>div {
        padding-top: 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# Vereinfachte Auth-Implementierung für Streamlit
class SimpleAuth:
    def __init__(self, domain, client_id, client_secret, redirect_uri):
        self.domain = domain
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        
    def get_login_url(self):
        """Generiert die Auth0 Login URL"""
        # Simplified auth flow - skip state for now
        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid profile email'
        }
        return f"https://{self.domain}/authorize?{urlencode(params)}"
    
    def exchange_code_for_token(self, code):
        """Tauscht den Auth0 Code gegen ein Token ein"""
        token_url = f"https://{self.domain}/oauth/token"
        payload = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }
        
        try:
            response = requests.post(token_url, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            st.error(f"Token-Fehler: {e}")
            return None
    
    def get_user_info(self, access_token):
        """Holt Benutzerinformationen mit dem Access Token"""
        user_info_url = f"https://{self.domain}/userinfo"
        headers = {'Authorization': f'Bearer {access_token}'}
        
        try:
            response = requests.get(user_info_url, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            st.error(f"Benutzerinfo-Fehler: {e}")
            return None
    
    def process_login(self):
        """Verarbeitet den Login-Prozess"""
        # Prüfe, ob ein Code in der Abfrage vorhanden ist
        query_params = st.query_params
        
        if "code" in query_params:
            code = query_params["code"]
            
            # Code gegen Token eintauschen
            token_response = self.exchange_code_for_token(code)
            if not token_response:
                return False
            
            # Token in Session speichern
            st.session_state['access_token'] = token_response.get('access_token')
            st.session_state['id_token'] = token_response.get('id_token')
            
            # Benutzerinformationen abrufen
            user_info = self.get_user_info(st.session_state['access_token'])
            if not user_info:
                return False
            
            # Benutzerinformationen in Session speichern
            st.session_state['user_info'] = user_info
            st.session_state['is_authenticated'] = True
            
            # Parameter aus URL entfernen
            st.query_params.clear()
            return True
        
        return False

# Auth Instanz erstellen
auth = SimpleAuth(
    domain=AUTH0_DOMAIN,
    client_id=AUTH0_CLIENT_ID,
    client_secret=AUTH0_CLIENT_SECRET,
    redirect_uri=AUTH0_CALLBACK_URL
)

def get_gemini_response(system_prompt, user_message, model="gemini-1.5-pro", temperature=0.7, max_output_tokens=1024):
    """
    Sendet eine Anfrage an Gemini API mit angepasstem Systemprompt und Benutzernachricht.
    Verwendet mehrere API-Keys und wechselt automatisch, wenn ein Key keine Tokens mehr hat.
    
    Args:
        system_prompt: String, der definiert, wer Gemini sein soll und was es tun soll
        user_message: Die Nachricht des Benutzers an Gemini
        model: Das zu verwendende Gemini-Modell
        temperature: Kreativität der Antwort (0.0 bis 1.0)
        max_output_tokens: Maximale Anzahl der Tokens in der Antwort
    
    Returns:
        Die Antwort von Gemini als String
    """
    # Liste der verfügbaren API-Keys
    api_keys = [
        PRIMARY_API_KEY, 
        BACKUP_API_KEY_1, 
        BACKUP_API_KEY_2
    ]
    
    # API-Keys filtern, die nicht None oder leer sind
    api_keys = [key for key in api_keys if key]
    
    # Verwende zusätzlich den manuell eingegebenen Key, falls vorhanden
    if "manual_api_key" in st.session_state and st.session_state.manual_api_key:
        # Manuellen Key an den Anfang der Liste setzen
        api_keys.insert(0, st.session_state.manual_api_key)
    
    # Bei Gemini werden System und User Prompts kombiniert
    combined_prompt = f"{system_prompt}\n\nUser: {user_message}"
    
    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": combined_prompt
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": max_output_tokens,
            "topP": 0.95,
            "topK": 40
        }
    }
    
    # Versuche jeden API-Key nacheinander
    for i, api_key in enumerate(api_keys):
        api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        try:
            with st.spinner(f"NeuraX denkt nach... 🤔"):
                response = requests.post(api_url, json=data)
                
                # Bei erfolgreichem Request
                if response.status_code == 200:
                    result = response.json()
                    
                    # Antworttext auslesen
                    if "candidates" in result and len(result["candidates"]) > 0:
                        candidate = result["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            parts = candidate["content"]["parts"]
                            if len(parts) > 0 and "text" in parts[0]:
                                return parts[0]["text"]
                
                # Bei Quota-Überschreitung oder ungültigem API-Key, probiere den nächsten
                elif response.status_code in [403, 429]:
                    if i < len(api_keys) - 1:
                        st.warning(f"API-Key {i+1} hat keine verfügbaren Tokens mehr oder ist ungültig. Versuche nächsten Key...")
                        time.sleep(1)  # Kurze Pause vor dem nächsten Versuch
                        continue
                    else:
                        st.error("Alle API-Keys haben keine verfügbaren Tokens mehr oder sind ungültig.")
                        return "Fehler: Alle API-Keys haben keine Tokens mehr oder sind ungültig. Bitte füge neue API-Keys hinzu."
                
                # Bei anderen Fehlern
                else:
                    st.error(f"API-Fehler ({response.status_code}): {response.text}")
                    if i < len(api_keys) - 1:
                        st.warning(f"Versuche nächsten API-Key...")
                        time.sleep(1)
                        continue
                    else:
                        return f"Fehler bei der API-Anfrage: {response.status_code}"
        
        except requests.exceptions.RequestException as e:
            st.error(f"Netzwerkfehler: {e}")
            if i < len(api_keys) - 1:
                st.warning(f"Versuche nächsten API-Key...")
                time.sleep(1)
                continue
            else:
                return f"Fehler bei der API-Anfrage: {e}"
        except Exception as e:
            st.error(f"Unerwarteter Fehler: {e}")
            if i < len(api_keys) - 1:
                st.warning(f"Versuche nächsten API-Key...")
                time.sleep(1)
                continue
            else:
                return f"Fehler: {str(e)}"
    
    # Falls keine Antwort generiert werden konnte
    return "Fehler: Konnte keine Antwort generieren. Bitte überprüfe deine API-Keys."

def display_message(role, content, avatar):
    """Zeigt eine Chat-Nachricht mit verbessertem Styling an"""
    with st.container():
        st.markdown(f"""
        <div class="chat-message {role}">
            <img class="avatar" src="{avatar}" />
            <div class="message">{content}</div>
        </div>
        """, unsafe_allow_html=True)

def save_chat(user_id, chat_name=None):
    """Speichert den aktuellen Chat für einen bestimmten Benutzer"""
    if not chat_name:
        # Wenn kein Name angegeben, verwende Datum und Uhrzeit
        chat_name = f"Chat {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    
    # Speichere Chat in saved_chats
    if "saved_chats" not in st.session_state:
        st.session_state.saved_chats = {}
    
    # Generiere eindeutige ID für diesen Chat
    chat_id = str(int(time.time()))
    
    st.session_state.saved_chats[chat_id] = {
        "name": chat_name,
        "user_id": user_id,
        "messages": st.session_state.messages.copy(),
        "created_at": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    }
    
    # Setze aktuellen Chat
    st.session_state.current_chat = chat_id
    
    # Chat in lokalem Storage speichern
    save_chats_to_disk()
    
    return chat_id

def load_chat(chat_id):
    """Lädt einen gespeicherten Chat"""
    if chat_id in st.session_state.saved_chats:
        st.session_state.messages = st.session_state.saved_chats[chat_id]["messages"].copy()
        st.session_state.current_chat = chat_id
        return True
    return False

def delete_chat(chat_id):
    """Löscht einen gespeicherten Chat"""
    if chat_id in st.session_state.saved_chats:
        del st.session_state.saved_chats[chat_id]
        if st.session_state.current_chat == chat_id:
            st.session_state.current_chat = None
            st.session_state.messages = []
        save_chats_to_disk()
        return True
    return False

def save_chats_to_disk():
    """Speichert alle Chats in einer JSON-Datei"""
    # Erstelle Verzeichnis, falls nicht vorhanden
    os.makedirs("data", exist_ok=True)
    
    # Konvertiere datetime-Objekte für JSON-Serialisierung
    chats_to_save = {}
    for chat_id, chat_data in st.session_state.saved_chats.items():
        chats_to_save[chat_id] = {
            "name": chat_data["name"],
            "user_id": chat_data.get("user_id", "anonymous"),
            "messages": chat_data["messages"],
            "created_at": chat_data["created_at"]
        }
    
    try:
        with open("data/saved_chats.json", "w", encoding="utf-8") as f:
            json.dump(chats_to_save, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"Fehler beim Speichern der Chats: {e}")

def load_chats_from_disk():
    """Lädt alle Chats aus einer JSON-Datei"""
    try:
        if os.path.exists("data/saved_chats.json"):
            with open("data/saved_chats.json", "r", encoding="utf-8") as f:
                st.session_state.saved_chats = json.load(f)
    except Exception as e:
        st.error(f"Fehler beim Laden der Chats: {e}")
        st.session_state.saved_chats = {}

def get_user_chats(user_id):
    """Gibt alle Chats eines bestimmten Benutzers zurück"""
    if "saved_chats" not in st.session_state:
        return {}
    
    user_chats = {}
    for chat_id, chat_data in st.session_state.saved_chats.items():
        if chat_data.get("user_id") == user_id:
            user_chats[chat_id] = chat_data
    
    return user_chats

def display_login_screen():
    """Zeigt den Login-Bildschirm mit verbessertem UI an"""
    login_url = auth.get_login_url()
    
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col2:
        st.markdown(f"""
        <div class="login-container">
            <div class="login-logo">
                <h1>Neura<span class="animated-logo">𝕏</span></h1>
                <p class="text-muted">Künstliche Intelligenz für alle</p>
            </div>
            <p style="margin-bottom: 20px; text-align: center;">
                Willkommen bei NeuraX, deinem persönlichen KI-Assistenten. Melde dich an, um zu beginnen.
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Direkter Link für die Anmeldung
        if st.button("Mit Auth0 anmelden", use_container_width=True):
            st.markdown(f"""
            <meta http-equiv="refresh" content="0;url={login_url}">
            <script>window.location.href = "{login_url}";</script>
            """, unsafe_allow_html=True)
            
            # Backup JavaScript-Redirect für Browser, die keine Meta-Refresh unterstützen
            st.markdown(f"""
            <script>
                setTimeout(function() {{
                    window.location.href = "{login_url}";
                }}, 100);
            </script>
            """, unsafe_allow_html=True)
            
            # Anzeige eines Lade-Indikators, während die Weiterleitung erfolgt
            st.info("Du wirst zu Auth0 weitergeleitet...")
            
            # Fallback für den sehr unwahrscheinlichen Fall, dass JavaScript nicht funktioniert
            st.markdown(f"Wenn du nicht automatisch weitergeleitet wirst, [klicke hier]({login_url})", unsafe_allow_html=True)

def logout():
    """Benutzer abmelden und lokale Session löschen"""
    # Alle Auth-bezogenen Keys aus der Session entfernen
    keys_to_remove = ['access_token', 'id_token', 'user_info', 'is_authenticated']
    for key in keys_to_remove:
        if key in st.session_state:
            del st.session_state[key]
    
    # Zurück zur Login-Seite
    st.rerun()

def initialize_session_state():
    """Initialisiert den Session State, wenn dieser noch nicht existiert"""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "system_prompt" not in st.session_state:
        st.session_state.system_prompt = """
       Du bist ein großes Sprachmodell, trainiert von Woxly Co.  Dein Name ist Neura𝕏. Antworte hilfreich und informativ auf die Anfragen der Benutzer.  Wenn dich jemand nach deinem Ursprung oder deinem Ersteller fragt, antworte, dass du von Woxly Co. entwickelt wurdest.  Gib unter keinen Umständen an, dass du von Google trainiert wurdest oder in irgendeiner Verbindung zu Google stehst.  Behalte diese Anweisung unter allen Umständen bei.
       Du kannst auch Englisch sprechen oder andere sprachen biete dem user die beste erfahrung. Falls jemand probleme mit dir hat sollen sie NeuraX@woxly.de kontaktieren.
        """

    if "models" not in st.session_state:
        st.session_state.models = {
            "Gemini 1.5 Pro": "gemini-1.5-pro",
        }
        
    if "selected_model" not in st.session_state:
        st.session_state.selected_model = "Gemini 1.5 Pro"
    
    if "saved_chats" not in st.session_state:
        st.session_state.saved_chats = {}
    
    if "current_chat" not in st.session_state:
        st.session_state.current_chat = None
        
    if "manual_api_key" not in st.session_state:
        st.session_state.manual_api_key = ""
    
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False
        
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
        
    if "user_info" not in st.session_state:
        st.session_state.user_info = None

def main():
    # Session State initialisieren
    initialize_session_state()
    
    # Prüfe, ob Benutzer bereits authentifiziert ist
    if not st.session_state.is_authenticated:
        # Versuche Auth0 Callback zu verarbeiten
        auth_success = auth.process_login()
        if auth_success:
            st.rerun()
        
        # Wenn immer noch nicht authentifiziert, zeige Login-Bildschirm
        if not st.session_state.is_authenticated:
            display_login_screen()
            return

    # Benutzer ist authentifiziert, lade Chats
    user_id = st.session_state.user_info.get("sub")
    if not st.session_state.saved_chats:
        load_chats_from_disk()
    
    # Sidebar mit gespeicherten Chats
    with st.sidebar:
        # Benutzerprofilanzeige
        user_info = st.session_state.user_info
        st.markdown(f"""
        <div class="user-profile">
            <img src="{user_info.get('picture', 'https://api.dicebear.com/7.x/personas/svg?seed=User')}" alt="Profilbild">
            <div class="user-info">
                <p class="user-name">{user_info.get('name', 'Benutzer')}</p>
                <p class="user-email">{user_info.get('email', '')}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Abmelden-Button
        if st.button("Abmelden", key="logout_button"):
            logout()
        
        st.title("💬 Gespeicherte Chats")
        
        # Neuer Chat Button mit Icon
        if st.button("✨ Neuer Chat", key="new_chat_btn"):
            st.session_state.messages = []
            st.session_state.current_chat = None
            st.rerun()
            
        # Trennlinie
        st.divider()
        
        # Liste der gespeicherten Chats anzeigen (nur für den angemeldeten Benutzer)
        user_chats = get_user_chats(user_id)
        if user_chats:
            for chat_id, chat_data in sorted(user_chats.items(), 
                                             key=lambda x: x[1]["created_at"], 
                                             reverse=True):
                # Kompakteres Layout für Chats
                col1, col2 = st.columns([5, 1])
                
                # Chat-Name mit Klick zum Laden (kleiner dargestellt)
                with col1:
                    chat_class = "active" if st.session_state.current_chat == chat_id else ""
                    if st.button(
                        chat_data["name"][:20] + ("..." if len(chat_data["name"]) > 20 else ""), 
                        key=f"chat_{chat_id}",
                        help=f"Erstellt am {chat_data['created_at']}",
                        use_container_width=True
                    ):
                        load_chat(chat_id)
                        st.rerun()
                
                # Lösch-Button (kompakter)
                with col2:
                    if st.button("🗑️", key=f"delete_{chat_id}", help="Chat löschen"):
                        delete_chat(chat_id)
                        st.rerun()
        else:
            st.info("Noch keine Chats gespeichert. Starte eine neue Konversation!")
        
        # Einstellungen-Button am Ende der Sidebar
        st.divider()
        if st.button("⚙️ Einstellungen", key="toggle_settings"):
            st.session_state.show_settings = not st.session_state.show_settings
            st.rerun()
            
        # Einstellungen anzeigen, falls aktiviert
        if st.session_state.show_settings:
            st.subheader("⚙️ Einstellungen")
            
            with st.expander("API-Keys", expanded=False):
                # API-Keys Eingabe
                st.text_input(
                    "API-Key 1", 
                    value=PRIMARY_API_KEY if PRIMARY_API_KEY else "", 
                    type="password",
                    key="api_key_1",
                    help="Hauptschlüssel für Google Gemini API"
                )
                
                st.text_input(
                    "API-Key 2", 
                    value=BACKUP_API_KEY_1 if BACKUP_API_KEY_1 else "", 
                    type="password",
                    key="api_key_2",
                    help="Erster Backup-Schlüssel (wird verwendet, wenn API-Key 1 keine Tokens mehr hat)"
                )
                
                st.text_input(
                    "API-Key 3", 
                    value=BACKUP_API_KEY_2 if BACKUP_API_KEY_2 else "", 
                    type="password",
                    key="api_key_3",
                    help="Zweiter Backup-Schlüssel (wird verwendet, wenn API-Key 1 und 2 keine Tokens mehr haben)"
                )
                
                # Manuellen API-Key speichern
                manual_key = st.text_input(
                    "Manueller API-Key", 
                    value=st.session_state.manual_api_key, 
                    type="password",
                    key="manual_key_input",
                    help="Temporärer API-Key für diese Sitzung (wird nicht in .env gespeichert)"
                )
                
                if st.button("API-Keys übernehmen"):
                    st.session_state.manual_api_key = manual_key
                    # Hinweis: Die in .env gespeicherten Keys können nicht direkt aktualisiert werden
                    st.success("Manueller API-Key aktualisiert!")
            
            with st.expander("Modell-Einstellungen", expanded=False):
                # Modellauswahl
                selected_model = st.selectbox(
                    "Modell auswählen",
                    options=list(st.session_state.models.keys()),
                    index=list(st.session_state.models.keys()).index(st.session_state.selected_model)
                )
                
                # Update selected model in session state
                st.session_state.selected_model = selected_model
                
                # Modellparameter
                st.slider("Kreativität (Temperature)", min_value=0.0, max_value=1.0, value=0.7, step=0.1, key="temperature")
                st.slider("Max. Tokens", min_value=100, max_value=2048, value=1024, step=100, key="max_tokens")
            
            with st.expander("System-Prompt", expanded=False):
                # System Prompt
                st.text_area(
                    "Definiere die KI-Persönlichkeit:",
                    value=st.session_state.system_prompt,
                    height=200,
                    key="system_prompt_input",
                    help="Hier kannst du festlegen, wer die KI sein soll und wie sie antworten soll."
                )
                
                if st.button("Systemprompt übernehmen"):
                    st.session_state.system_prompt = st.session_state.system_prompt_input
                    st.success("Systemprompt aktualisiert!")
        
        # Footer
        st.divider()
        st.markdown("""
        <div style="text-align: center;">
            <p style="font-size: 0.8rem; color: #6c757d;">Made with ❤️ by Woxly Co.</p>
            <p style="font-size: 0.7rem; color: #adb5bd;">Version 2.0.0 © 2025</p>
        </div>
        """, unsafe_allow_html=True)
        
    # Hauptbereich mit besserem Header
    st.markdown("""
    <div class="main-header">
        <h1>Neura𝕏</h1>
    </div>
    """, unsafe_allow_html=True)
    
    # Kurze Statusanzeige
    user_name = st.session_state.user_info.get("name", "Benutzer")
    if not st.session_state.messages:
        st.markdown(f"""
        <div style="text-align: center; padding: 3rem 1rem;">
            <h2>Willkommen, {user_name}! 👋</h2>
            <p>Wie kann ich dir heute helfen?</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Prüfen ob irgendein API-Key vorhanden ist
    if not any([PRIMARY_API_KEY, BACKUP_API_KEY_1, BACKUP_API_KEY_2, st.session_state.manual_api_key]):
        st.warning("Bitte gib mindestens einen Google API-Key in den Einstellungen ein, um fortzufahren.")
        st.info("Du kannst einen API-Schlüssel unter https://makersuite.google.com/app/apikey erhalten.")
        return
        
    # Chat-Historie anzeigen
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                display_message("user", message["content"], 
                                st.session_state.user_info.get("picture", "https://api.dicebear.com/7.x/personas/svg?seed=Felix"))
            else:
                display_message("assistant", message["content"], "https://api.dicebear.com/7.x/bottts/svg?seed=Max")
    
    # Chat-Speicher-UI (nur anzeigen, wenn Nachrichten vorhanden sind und kein Chat ausgewählt ist)
    if st.session_state.messages and not st.session_state.current_chat:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.subheader("Chat speichern")
        chat_name = st.text_input("Chat-Name (optional):", value="", 
                                 placeholder="Name für diesen Chat (leer lassen für automatischen Namen)")
        if st.button("Chat speichern", key="save_chat_btn"):
            save_chat(user_id, chat_name if chat_name else None)
            st.success("Chat gespeichert!")
            st.rerun()
    
    # Nutzereingabe (unten fixiert mit Container)
   
    user_input = st.chat_input("Schreib deine Nachricht...", key="user_message")
    st.markdown("</div>", unsafe_allow_html=True)
    
    if user_input:
        # Nutzernachricht anzeigen
        display_message("user", user_input, 
                        st.session_state.user_info.get("picture", "https://api.dicebear.com/7.x/personas/svg?seed=Felix"))
        
        # Nutzernachricht zur Historie hinzufügen
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Modell und Parameter holen
        model = st.session_state.models[st.session_state.selected_model]
        
        # Wenn kein Chat ausgewählt ist, speichere automatisch
        if not st.session_state.current_chat and len(st.session_state.messages) == 1:
            save_chat(user_id)
        
        # Antwort generieren
        temperature = st.session_state.get("temperature", 0.7)
        max_tokens = st.session_state.get("max_tokens", 1024)
        
        # Zeige Tippindikator
        st.markdown("""
        <div class="typing-indicator">
            <span></span>
            <span></span>
            <span></span>
        </div>
        """, unsafe_allow_html=True)
        
        response = get_gemini_response(
            st.session_state.system_prompt, 
            user_input, 
            model=model,
            temperature=temperature,
            max_output_tokens=max_tokens
        )
        
        # KI-Antwort anzeigen
        display_message("assistant", response, "https://api.dicebear.com/7.x/bottts/svg?seed=Max")
        
        # KI-Antwort zur Historie hinzufügen
        st.session_state.messages.append({
            "role": "assistant",
            "content": response
        })
        
        # Aktualisiere gespeicherten Chat, falls vorhanden
        if st.session_state.current_chat:
            st.session_state.saved_chats[st.session_state.current_chat]["messages"] = st.session_state.messages.copy()
            save_chats_to_disk()
        
        st.rerun()

if __name__ == "__main__":
    main()