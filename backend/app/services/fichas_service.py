import json
import os
from app.config import JSON_PATH, FALLBACK_JSON_PATH, OUTPUT_DIR

class FichasService:
    @staticmethod
    def obtener_fichas() -> dict:
        path = JSON_PATH if JSON_PATH.exists() else FALLBACK_JSON_PATH
        if not path.exists():
            raise FileNotFoundError(f"Archivo de fichas no encontrado en {JSON_PATH} ni {FALLBACK_JSON_PATH}")
        
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def guardar_fichas(data: dict) -> None:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
