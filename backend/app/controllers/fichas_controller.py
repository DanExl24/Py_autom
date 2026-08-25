from fastapi import APIRouter, HTTPException
from app.services.fichas_service import FichasService
from app.services.programador_service import ProgramadorService

router = APIRouter(prefix="/api", tags=["Fichas"])

@router.get("/fichas")
def get_fichas():
    try:
        return FichasService.obtener_fichas()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al leer datos de fichas: {str(e)}")

@router.get("/abrir-programador/{ficha}")
def abrir_programador(ficha: str):
    try:
        url = ProgramadorService.buscar_url_ficha(ficha, abrir_navegador=False)
        if not url:
            raise HTTPException(
                status_code=404, 
                detail=f"No se encontró el programador de Drive para la ficha {ficha}"
            )
        return {"status": "ok", "url": url}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al abrir programador de Drive: {str(e)}"
        )
