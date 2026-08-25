from typing import Optional
from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from app.services.sync_service import SyncService
from app.core.gui_launcher import lanzar_buscador_gui

router = APIRouter(prefix="/api", tags=["Sincronización"])

@router.post("/actualizar")
def actualizar_datos(
    x_google_access_token: Optional[str] = Header(None, alias="X-Google-Access-Token")
):
    return StreamingResponse(
        SyncService.ejecutar_sincronizacion_stream(access_token=x_google_access_token), 
        media_type="text/plain"
    )

@router.post("/abrir-buscador-gui")
def abrir_buscador_gui():
    try:
        lanzar_buscador_gui()
        return {"status": "ok", "message": "Buscador CustomTkinter GUI iniciado"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"No se pudo iniciar el buscador CustomTkinter: {str(e)}"
        )
