from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
import sys
import json
import io
import subprocess

app = FastAPI(title="SENA Fichas API")

# Configurar CORS para permitir que el frontend de desarrollo (Vite en puerto 5173 o similar) acceda a la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JSON_PATH = os.path.join(BASE_DIR, "output", "fichas.json")
FALLBACK_JSON_PATH = os.path.join(BASE_DIR, "fichas_test.json")

# Agregar src al path de python para poder importar el módulo de extracción
sys.path.append(os.path.join(BASE_DIR, "src"))
from leer_archivos import extraer_fichas

@app.get("/api/fichas")
def get_fichas():
    path = JSON_PATH if os.path.exists(JSON_PATH) else FALLBACK_JSON_PATH
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Archivo de fichas no encontrado")
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer datos: {str(e)}")

@app.post("/api/actualizar")
def actualizar_datos():
    # Ejecuta leer_archivos.py para sincronizar con Google Drive o archivos locales de Excel
    script_path = os.path.join(BASE_DIR, "src", "leer_archivos.py")
    python_exe = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = "python"
        
    try:
        result = subprocess.run(
            [python_exe, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR
        )
        return {"status": "ok", "message": "Datos actualizados correctamente", "output": result.stdout}
    except subprocess.CalledProcessError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al ejecutar actualización: {e.stderr or e.stdout or str(e)}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")

@app.post("/api/sincronizar")
async def sincronizar_excel(file: UploadFile = File(...)):
    # Validar formato de archivo
    if not (file.filename.endswith('.xlsx') or file.filename.endswith('.xls')):
        raise HTTPException(status_code=400, detail="Formato de archivo inválido. Debe ser un archivo Excel (.xlsx o .xls)")

    try:
        # Cargar los datos actuales antes de actualizar para comparar
        antiguo_path = JSON_PATH if os.path.exists(JSON_PATH) else FALLBACK_JSON_PATH
        antiguos_programas = set()
        antiguos_instructores = set()
        if os.path.exists(antiguo_path):
            try:
                with open(antiguo_path, "r", encoding="utf-8") as f:
                    antiguos_datos = json.load(f)
                    for red_name, fichas_dict in antiguos_datos.items():
                        for info in fichas_dict.values():
                            prog = info.get("NOMBRE DEL PROGRAMA")
                            if prog: antiguos_programas.add(prog.strip().upper())
                            inst = info.get("INSTRUCTOR TÉCNICO 2026") or info.get("INSTRUCTOR TÉCNICO 2025")
                            if inst and inst != "None" and inst != "":
                                antiguos_instructores.add(inst.strip().upper())
            except Exception:
                pass

        # Leer archivo subido a memoria
        contents = await file.read()
        excel_stream = io.BytesIO(contents)

        # Extraer fichas usando el script existente
        datos_fichas = extraer_fichas(excel_stream)

        # Validaciones de consistencia
        if not datos_fichas:
            raise ValueError("No se encontraron redes de conocimiento ni fichas estructuradas en el archivo.")

        # Calcular métricas e instructores/programas nuevos
        total_registros = 0
        total_columnas = 0
        nuevos_programas = set()
        nuevos_instructores = set()

        for red, fichas_dict in datos_fichas.items():
            for info in fichas_dict.values():
                total_registros += 1
                if not total_columnas:
                    total_columnas = len(info)
                prog = info.get("NOMBRE DEL PROGRAMA")
                if prog: nuevos_programas.add(prog.strip().upper())
                inst = info.get("INSTRUCTOR TÉCNICO 2026") or info.get("INSTRUCTOR TÉCNICO 2025")
                if inst and inst != "None" and inst != "":
                    nuevos_instructores.add(inst.strip().upper())

        programas_nuevos_cnt = len(nuevos_programas - antiguos_programas)
        instructores_nuevos_cnt = len(nuevos_instructores - antiguos_instructores)

        # Guardar la nueva base de datos JSON
        os.makedirs(os.path.dirname(JSON_PATH), exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(datos_fichas, f, ensure_ascii=False, indent=2)

        return {
            "status": "ok",
            "registros": total_registros,
            "columnas": total_columnas,
            "programas_nuevos": programas_nuevos_cnt,
            "instructores_nuevos": instructores_nuevos_cnt
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Fallo en la validación o estructura del Excel: {str(e)}"
        )
@app.get("/api/abrir-programador/{ficha}")
def abrir_programador(ficha: str):
    # Buscar fichasSimple.json en la raíz del proyecto o en el directorio actual
    json_path = os.path.join(BASE_DIR, "fichasSimple.json")
    if not os.path.exists(json_path):
        json_path = os.path.join(BASE_DIR, "src", "fichasSimple.json")
        
    if not os.path.exists(json_path):
        # Intentar ejecutar constructor() para generarlo si no existe
        try:
            sys.path.append(os.path.join(BASE_DIR, "src"))
            from constructor import constructor
            constructor()
            json_path = os.path.join(BASE_DIR, "fichasSimple.json")
            if not os.path.exists(json_path):
                json_path = os.path.join(os.getcwd(), "fichasSimple.json")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"No se encontró el índice de programadores y falló la generación: {str(e)}")
            
    if not os.path.exists(json_path):
        raise HTTPException(status_code=404, detail="Índice de programadores (fichasSimple.json) no encontrado.")
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            fichas_simple = json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer índice de programadores: {str(e)}")

    ficha_data = fichas_simple.get(str(ficha))
    if not ficha_data or not ficha_data.get("url"):
        raise HTTPException(status_code=404, detail=f"No se encontró el programador de Drive para la ficha {ficha}")

    url = ficha_data["url"]
    
    # Abrir en el navegador local de la máquina
    try:
        import webbrowser
        webbrowser.open(url)
    except Exception:
        pass
        
    return {"status": "ok", "url": url, "nombre": ficha_data.get("nombre")}



# Servir archivos estáticos del frontend si existe la compilación (producción)
frontend_dist = os.path.join(BASE_DIR, "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="static")
else:
    @app.get("/")
    def index():
        return {
            "message": "Servidor API funcionando. Desarrolla el frontend en el puerto de Vite y compílalo para servirlo desde aquí."
        }
