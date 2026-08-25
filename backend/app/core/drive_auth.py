import os
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from app.config import (
    TOKEN_JSON_PATH, 
    CREDENTIALS_JSON_PATH, 
    AUTH_DIR, 
    BASE_DIR
)

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

_drive_service = None
_sheets_service = None

SERVICE_ACCOUNT_CANDIDATES = [
    AUTH_DIR / "json" / "service_account.json",
    AUTH_DIR / "service_account.json",
    BASE_DIR / "service_account.json"
]

def obtener_credenciales():
    # 1. Prioridad: Verificar Service Account para VPS/Docker
    for sa_path in SERVICE_ACCOUNT_CANDIDATES:
        if sa_path.exists():
            try:
                print(f"[AUTH] Usando Google Service Account desde: {sa_path}")
                return service_account.Credentials.from_service_account_file(str(sa_path), scopes=SCOPES)
            except Exception as e:
                print(f"[AUTH] Error al cargar Service Account en {sa_path}: {e}")

    # Verificar si credentials.json es de tipo Service Account
    if CREDENTIALS_JSON_PATH.exists():
        try:
            with open(CREDENTIALS_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if data.get("type") == "service_account":
                    print("[AUTH] Usando Service Account detectado en credentials.json")
                    return service_account.Credentials.from_service_account_file(str(CREDENTIALS_JSON_PATH), scopes=SCOPES)
        except Exception:
            pass

    # 2. Fallback: Token de usuario OAuth 2.0
    creds = None
    if TOKEN_JSON_PATH.exists():
        try:
            creds = Credentials.from_authorized_user_file(str(TOKEN_JSON_PATH), SCOPES)
        except Exception as e:
            print(f"[AUTH] Error al leer token OAuth: {e}")

    if creds and creds.valid:
        return creds

    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            with open(str(TOKEN_JSON_PATH), "w", encoding="utf-8") as token_file:
                token_file.write(creds.to_json())
            return creds
        except Exception as e:
            print(f"[AUTH] Error al refrescar token OAuth ({e}).")

    raise RuntimeError(
        "No se pudo autenticar con Google Drive. "
        "En entornos de servidor (VPS/Docker), se recomienda colocar la llave 'service_account.json' en la carpeta 'auth/json/service_account.json' "
        "y compartir la carpeta de Drive con el correo de la cuenta de servicio."
    )

def obtener_servicio_drive():
    global _drive_service
    if _drive_service is None:
        _drive_service = build("drive", "v3", credentials=obtener_credenciales())
    return _drive_service

def obtener_servicio_sheets():
    global _sheets_service
    if _sheets_service is None:
        _sheets_service = build("sheets", "v4", credentials=obtener_credenciales())
    return _sheets_service
