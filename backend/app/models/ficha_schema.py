from typing import Optional
from pydantic import BaseModel, Field

class FichaDetalleSchema(BaseModel):
    RED_DE_CONOCIMIENTO: Optional[str] = Field(None, alias="RED DE CONOCIMIENTO")
    NIVEL: Optional[str] = None
    NOMBRE_DEL_PROGRAMA: Optional[str] = Field(None, alias="NOMBRE DEL PROGRAMA")
    CODIGO_DE_PROGRAMA: Optional[int] = Field(None, alias="CODIGO DE PROGRAMA")
    VERSION: Optional[int] = 1
    FICHA: Optional[str] = None
    APRENDICES_MATRICULADOS: Optional[int] = Field(0, alias="APRENDICES MATRICULADOS")
    TIPO_DE_OFERTA: Optional[str] = Field(None, alias="TIPO DE OFERTA")
    CODIGO_PROYECTO: Optional[int] = Field(0, alias="CÓDIGO PROYECTO")
    MUNICIPIO: Optional[str] = None
    HORARIO: Optional[str] = None
    AMBIENTE: Optional[str] = None
    DURACION: Optional[int] = None
    FECHA_INICIO: Optional[str] = Field(None, alias="FECHA INICIO")
    FECHA_FINAL_ETAPA_LECTIVA: Optional[str] = Field(None, alias="FECHA FINAL ETAPA LECTIVA")
    FECHA_TERMINACION: Optional[str] = Field(None, alias="FECHA TERMINACION")
    INSTRUCTOR_TECNICO_2025: Optional[str] = Field(None, alias="INSTRUCTOR TÉCNICO 2025")
    INSTRUCTOR_TECNICO_2026: Optional[str] = Field(None, alias="INSTRUCTOR TÉCNICO 2026")
    APOYO_TECNICO_INGLES: Optional[str] = Field(None, alias="APOYO TÉCNICO INGLES")
    TRANSVERSALES: Optional[str] = None

    class Config:
        populate_by_name = True

class StandardResponse(BaseModel):
    status: str
    message: Optional[str] = None
    data: Optional[dict] = None
