import os
import subprocess
from typing import Generator
from app.config import BASE_DIR, PYTHON_EXE

class SyncService:
    @staticmethod
    def ejecutar_sincronizacion_stream() -> Generator[str, None, None]:
        script_path = os.path.join(BASE_DIR, "src", "antiguo_lector.py")
        
        process = subprocess.Popen(
            [PYTHON_EXE, script_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            cwd=str(BASE_DIR),
            bufsize=1
        )

        if process.stdout:
            for line in iter(process.stdout.readline, ""):
                yield line

        process.wait()
        if process.returncode != 0:
            yield f"\n[ERROR] El script de sincronización falló con código {process.returncode}\n"
        else:
            yield "\n[COMPLETADO] Base de datos actualizada con éxito en caliente.\n"
