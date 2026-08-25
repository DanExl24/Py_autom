import os
import subprocess
from app.config import BASE_DIR, PYTHON_EXE

def lanzar_buscador_gui():
    script_path = os.path.join(BASE_DIR, "src", "buscador_fichas.py")
    subprocess.Popen(
        [PYTHON_EXE, script_path],
        cwd=str(BASE_DIR),
        creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
    )
