import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.servicio_general import obtener_servicio_drive
import webbrowser
import json
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, "fichasSimple.json")

# Variable global para cachear el cliente de Drive
_drive_service = None

def obtener_drive():
    global _drive_service
    if _drive_service is None:
        _drive_service = obtener_servicio_drive()
    return _drive_service

def res_carpeta(ID):
    drive = obtener_drive()
    resultado = (
        drive.files() # type: ignore
        .list(
            q=f"'{ID}' in parents",
            fields="files(id,name,mimeType,webViewLink)"
        )
        .execute()
    )
    return resultado

def get_carpeta(item):
    folder_id = item['id']
    SF_FOLDERS = res_carpeta(folder_id).get("files", [])
    return SF_FOLDERS

def constructor():
    FOLDER_ID = "1-pjnJ8jumWJXFzc3zONJXZ1KYLxC6Xjt"
    SELECT_FOLDER = '2. Programacion Formaciones'
    
    print("Conectando y consultando Google Drive para indexar programadores...")
    items = res_carpeta(FOLDER_ID).get("files", [])
    
    def construir_fichas():
        indice = {}
        for item in items:
            if item['name'] == SELECT_FOLDER:
                programadores = get_carpeta(item)
                print(programadores)
                for programador in programadores:
                    redes = get_carpeta(programador)
                    for red in redes:
                        fichas = get_carpeta(red)
                        for ficha in fichas:
                            coincidencia = re.search(r"\d{7}", ficha["name"])
                            if coincidencia:
                                numero = coincidencia.group()
                                indice[numero] = {
                                    "nombre": ficha["name"],
                                    "id": ficha["id"],
                                    "programador": programador["name"],
                                    "red": red["name"],
                                    "mimetype" : ficha["mimeType"],
                                    "url": ficha["webViewLink"]
                                }
        return indice

    indice = construir_fichas()
    
    # Asegurar que se escribe en la ruta absoluta
    with open(JSON_PATH, "w", encoding="utf-8") as archivo:
        json.dump(indice, archivo, ensure_ascii=False, indent=2)
    print(f"Indexación finalizada. Archivo creado en: {JSON_PATH}")

def buscar_ficha(FICHA, abrir_navegador=True):
    # Generar el archivo si no existe
    if not os.path.exists(JSON_PATH):
        constructor()
        
    try:
        with open(JSON_PATH, "r", encoding="utf-8") as archivo:
            fichas = json.load(archivo)
    except Exception as e:
        print(f"Error al leer {JSON_PATH}: {e}")
        return None
        
    ficha = fichas.get(str(FICHA))
    if ficha and ficha.get('url'):
        url = ficha['url']
        if abrir_navegador:
            print(f"Abriendo {ficha['nombre']}...\nmimeType:{ficha['mimetype']}")
            webbrowser.open(url)
        return url
    else:
        print(f"No existe esta ficha: {FICHA}")
        return None
