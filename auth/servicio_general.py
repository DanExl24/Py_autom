import os.path
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

# Rutas de credenciales
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

TOKEN_PATH = os.path.join(BASE_DIR, "json", "token.json")
CREDENTIALS_PATH = os.path.join(BASE_DIR, "json", "credentials.json")
SERVICE_ACCOUNT_PATHS = [
    os.path.join(BASE_DIR, "json", "service_account.json"),
    os.path.join(ROOT_DIR, "service_account.json"),
    os.path.join(ROOT_DIR, "auth", "service_account.json")
]

def obtener_credenciales():
    # 0. Prioridad Web: Token de acceso directo emitido desde Google Identity Services en el navegador
    direct_token = os.environ.get("GOOGLE_ACCESS_TOKEN")
    if direct_token:
        print("[AUTH] Usando token de acceso temporal provisto directamente desde la interfaz web...")
        return Credentials(token=direct_token)

    # 1. Verificar si existe Cuenta de Servicio (Service Account para Servidor/VPS)
    for sa_path in SERVICE_ACCOUNT_PATHS:
        if os.path.exists(sa_path):
            try:
                print(f"[AUTH] Usando Google Service Account desde: {sa_path}")
                return service_account.Credentials.from_service_account_file(sa_path, scopes=SCOPES)
            except Exception as e:
                print(f"[AUTH] Error al cargar Service Account en {sa_path}: {e}")

    # Verificar si credentials.json es de tipo Service Account
    if os.path.exists(CREDENTIALS_PATH):
        try:
            with open(CREDENTIALS_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("type") == "service_account":
                    print("[AUTH] Usando Service Account detectado en credentials.json")
                    return service_account.Credentials.from_service_account_file(CREDENTIALS_PATH, scopes=SCOPES)
        except Exception:
            pass

    # 2. Fallback: Token de usuario OAuth 2.0
    creds = None
    if os.path.exists(TOKEN_PATH):
        try:
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
        except Exception as e:
            print(f"[AUTH] Advertencia al leer token OAuth con refresh_token: {e}")
            try:
                with open(TOKEN_PATH, "r", encoding="utf-8") as f:
                    token_data = json.load(f)
                    if token_data.get("token"):
                        creds = Credentials(token=token_data["token"], scopes=SCOPES)
            except Exception as e_inner:
                print(f"[AUTH] Error al cargar token directo: {e_inner}")

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(TOKEN_PATH, "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
            return creds
        except Exception as e:
            print(f"[AUTH] Error al refrescar token OAuth ({e}).")

    # Si el token no es válido ni se pudo refrescar
    raise RuntimeError(
        "No se pudo autenticar con Google Drive (token expirado o inválido). "
        "Para renovar el token: ejecuta 'python auth/generar_token.py' en tu PC local e ingresa con tu cuenta de Google. "
        "Luego copia el contenido generado en 'auth/json/token.json' dentro del VPS."
    )

def obtener_servicio_drive():
    return build(
        "drive",
        "v3",
        credentials=obtener_credenciales()
    )

def obtener_servicio_sheets():
    return build(
        "sheets",
        "v4",
        credentials=obtener_credenciales()
    )
