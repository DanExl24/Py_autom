import os
import sys
from google_auth_oauthlib.flow import InstalledAppFlow

# Añadir directorio raíz al path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTH_JSON_DIR = os.path.join(BASE_DIR, "auth", "json")
CREDENTIALS_PATH = os.path.join(AUTH_JSON_DIR, "credentials.json")
TOKEN_PATH = os.path.join(AUTH_JSON_DIR, "token.json")

SCOPES = [
    "https://www.googleapis.com/auth/drive.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]

def generar_token():
    print("=========================================================")
    print(" 🔑 Generador de Token OAuth 2.0 para Google Drive")
    print("=========================================================")
    
    if not os.path.exists(CREDENTIALS_PATH):
        print(f"❌ Error: No se encontró {CREDENTIALS_PATH}")
        print("Por favor coloca tu archivo credentials.json de Google Cloud en auth/json/credentials.json")
        return

    print("Abriendo el navegador para iniciar sesión con tu cuenta de Google...")
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
    creds = flow.run_local_server(port=8080)

    os.makedirs(AUTH_JSON_DIR, exist_ok=True)
    token_json_str = creds.to_json()
    with open(TOKEN_PATH, "w", encoding="utf-8") as f:
        f.write(token_json_str)

    print("\n✅ ¡Token generado y guardado con éxito localmente en:")
    print(f"   {TOKEN_PATH}")
    print("\n---------------------------------------------------------")
    print("📋 CONTENIDO PARA COPIAR AL VPS (auth/json/token.json):")
    print("---------------------------------------------------------")
    print(token_json_str)
    print("---------------------------------------------------------\n")

if __name__ == "__main__":
    generar_token()
