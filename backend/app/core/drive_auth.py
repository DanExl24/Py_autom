import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.config import TOKEN_JSON_PATH, CREDENTIALS_JSON_PATH

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

_drive_service = None
_sheets_service = None

def obtener_credenciales():
    creds = None
    token_str = str(TOKEN_JSON_PATH)
    credentials_str = str(CREDENTIALS_JSON_PATH)

    if os.path.exists(token_str):
        try:
            creds = Credentials.from_authorized_user_file(token_str, SCOPES)
        except Exception:
            creds = None

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if os.path.exists(credentials_str):
                flow = InstalledAppFlow.from_client_secrets_file(credentials_str, SCOPES)
                creds = flow.run_local_server(port=0)
            else:
                raise FileNotFoundError(f"No se encontró el archivo de credenciales en {credentials_str}")

        with open(token_str, "w", encoding="utf-8") as token_file:
            token_file.write(creds.to_json())

    return creds

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
