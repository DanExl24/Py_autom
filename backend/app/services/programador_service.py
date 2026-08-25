import json
import os
import re
import webbrowser
from app.config import (
    FICHAS_SIMPLE_PATH,
    DRIVE_CARPETA_PROGRAMACION,
    DRIVE_NOMBRE_CARPETA_PROGRAMACION
)
from app.core.drive_auth import obtener_servicio_drive

class ProgramadorService:
    @staticmethod
    def _res_carpeta(folder_id: str):
        drive = obtener_servicio_drive()
        resultado = (
            drive.files()  # type: ignore
            .list(
                q=f"'{folder_id}' in parents",
                fields="files(id,name,mimeType,webViewLink)"
            )
            .execute()
        )
        return resultado.get("files", [])

    @classmethod
    def indexar_programadores(cls) -> dict:
        print("Consultando Google Drive para indexar carpetas de programadores...")
        items = cls._res_carpeta(DRIVE_CARPETA_PROGRAMACION)
        indice = {}

        for item in items:
            if item.get('name') == DRIVE_NOMBRE_CARPETA_PROGRAMACION:
                programadores = cls._res_carpeta(item['id'])
                for programador in programadores:
                    redes = cls._res_carpeta(programador['id'])
                    for red in redes:
                        fichas = cls._res_carpeta(red['id'])
                        for ficha in fichas:
                            coincidencia = re.search(r"\d{7}", ficha["name"])
                            if coincidencia:
                                numero = coincidencia.group()
                                indice[numero] = {
                                    "nombre": ficha["name"],
                                    "id": ficha["id"],
                                    "programador": programador["name"],
                                    "red": red["name"],
                                    "mimetype": ficha.get("mimeType", ""),
                                    "url": ficha.get("webViewLink", "")
                                }

        with open(FICHAS_SIMPLE_PATH, "w", encoding="utf-8") as f:
            json.dump(indice, f, ensure_ascii=False, indent=2)

        return indice

    @classmethod
    def buscar_url_ficha(cls, ficha_num: str, abrir_navegador: bool = False) -> str | None:
        if not FICHAS_SIMPLE_PATH.exists():
            cls.indexar_programadores()

        try:
            with open(FICHAS_SIMPLE_PATH, "r", encoding="utf-8") as f:
                fichas = json.load(f)
        except Exception as e:
            print(f"Error al leer {FICHAS_SIMPLE_PATH}: {e}")
            return None

        ficha = fichas.get(str(ficha_num))
        if ficha and ficha.get("url"):
            url = ficha["url"]
            if abrir_navegador:
                webbrowser.open(url)
            return url
        return None
