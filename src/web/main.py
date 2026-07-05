from fastapi import FastAPI, HTTPException, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
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
    # Ejecuta antiguo_lector.py en segundo plano y transmite la salida (stdout) en tiempo real
    script_path = os.path.join(BASE_DIR, "src", "antiguo_lector.py")
    python_exe = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = "python"
        
    def stream_process_output():
        # Usar Popen con line buffering para capturar e imprimir logs de inmediato
        process = subprocess.Popen(
            [python_exe, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=BASE_DIR,
            bufsize=1
        )
        
        # Leer línea por línea
        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                yield line
                
        process.wait()
        if process.returncode != 0:
            yield f"\n[ERROR] El script de sincronización falló con código {process.returncode}\n"
        else:
            yield "\n[COMPLETADO] Base de datos actualizada con éxito en caliente.\n"

    return StreamingResponse(stream_process_output(), media_type="text/plain")

@app.get("/api/abrir-programador/{ficha}")
def abrir_programador(ficha: str):
    try:
        from constructor import buscar_ficha
        url = buscar_ficha(ficha, abrir_navegador=False)
        if not url:
            raise HTTPException(status_code=404, detail=f"No se encontró el programador de Drive para la ficha {ficha}")
        return {"status": "ok", "url": url}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al abrir programador de Drive: {str(e)}"
        )
@app.post("/api/abrir-buscador-gui")
def abrir_buscador_gui():
    script_path = os.path.join(BASE_DIR, "src", "buscador_fichas.py")
    python_exe = os.path.join(BASE_DIR, "venv", "Scripts", "python.exe")
    if not os.path.exists(python_exe):
        python_exe = "python"
        
    try:
        # Popen lanza en segundo plano sin esperar al término de la aplicación GUI
        subprocess.Popen(
            [python_exe, script_path],
            cwd=BASE_DIR,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        return {"status": "ok", "message": "Buscador CustomTkinter GUI iniciado"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo iniciar el buscador CustomTkinter: {str(e)}"
        )




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
