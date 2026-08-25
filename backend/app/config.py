import os
from pathlib import Path

# Directorio raíz del proyecto
BACKEND_DIR = Path(__file__).resolve().parent.parent
BASE_DIR = BACKEND_DIR.parent

# Rutas de datos
OUTPUT_DIR = BASE_DIR / "output"
JSON_PATH = OUTPUT_DIR / "fichas.json"
FALLBACK_JSON_PATH = BASE_DIR / "fichas_test.json"
FICHAS_SIMPLE_PATH = BASE_DIR / "fichasSimple.json"

# Autenticación y Credenciales Google
AUTH_DIR = BASE_DIR / "auth"
TOKEN_JSON_PATH = AUTH_DIR / "json" / "token.json"
CREDENTIALS_JSON_PATH = AUTH_DIR / "json" / "credentials.json"
ROOT_AUTH_JSON = BASE_DIR / "auth.json"

# IDs de Google Drive
DRIVE_CARPETA_CONSOLIDADO = "1nc5qTNXcP05h4N8AMka-CODYrGTXk4rm"
DRIVE_CARPETA_PROGRAMACION = "1-pjnJ8jumWJXFzc3zONJXZ1KYLxC6Xjt"
DRIVE_NOMBRE_CARPETA_PROGRAMACION = "2. Programacion Formaciones"

# Ejecutable de Python (entorno virtual o fallback)
VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"
PYTHON_EXE = str(VENV_PYTHON) if VENV_PYTHON.exists() else "python"

# Frontend compilado
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"
