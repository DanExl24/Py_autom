export interface Ficha {
  "RED DE CONOCIMIENTO": string;
  "NIVEL": string;
  "NOMBRE DEL PROGRAMA": string;
  "CODIGO DE PROGRAMA": number;
  "VERSION": number;
  "FICHA": string;
  "APRENDICES MATRICULADOS": number;
  "TIPO DE OFERTA": string;
  "CÓDIGO PROYECTO": number;
  "MUNICIPIO": string;
  "HORARIO": string;
  "AMBIENTE": string | number;
  "DURACION": number | null;
  "DURACION_CALCULADA": number;
  "AÑO /TRIMESTRE DE INICIO": string;
  "FECHA INICIO": string;
  "FECHA FINAL ETAPA LECTIVA": string;
  "FECHA TERMINACION": string;
  "INSTRUCTOR TÉCNICO 2025": string | null;
  "INSTRUCTOR TÉCNICO 2026": string | null;
  "APOYO TÉCNICO INGLES": string | null;
  "TRANSVERSALES": string | null;
}

export interface Kpis {
  totalFormaciones: number;
  totalAprendices: number;
  promedioAprendices: number;
  promedioDuracion: number;
  totalRedes: number;
  totalMunicipios: number;
  totalInstructores: number;
}
