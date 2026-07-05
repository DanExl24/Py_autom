import json
import os
from datetime import datetime

class ProcesadorDatos:
    def __init__(self, json_path=None):
        if json_path is None:
            # Intentar encontrar fichas.json en la ruta estándar
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            json_path = os.path.join(base_dir, "output", "fichas.json")
            if not os.path.exists(json_path):
                # Fallback al archivo en la raíz
                json_path = os.path.join(base_dir, "fichas_test.json")
        
        self.json_path = json_path
        self.fichas = []
        self.cargar_datos()

    def parse_date(self, date_str):
        if not date_str or date_str == "None" or date_str == "nan" or str(date_str).strip() == "":
            return None
        try:
            # Formato estándar es YYYY-MM-DD
            return datetime.strptime(str(date_str).strip()[:10], "%Y-%m-%d")
        except Exception:
            return None

    def cargar_datos(self):
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            self.fichas = []
            
            # El JSON está estructurado por Red de Conocimiento -> Ficha -> Datos Ficha
            for red_nombre, fichas_dict in data.items():
                for ficha_num, info in fichas_dict.items():
                    # Normalizar nulos
                    ficha_info = {}
                    for k, v in info.items():
                        if v == "None" or v == "nan" or v == "null":
                            ficha_info[k] = None
                        else:
                            ficha_info[k] = v
                    
                    # Asegurar campos requeridos
                    ficha_info["FICHA"] = str(ficha_num)
                    ficha_info["RED DE CONOCIMIENTO"] = red_nombre
                    
                    # Convertir número de aprendices a int
                    try:
                        ficha_info["APRENDICES MATRICULADOS"] = int(float(ficha_info.get("APRENDICES MATRICULADOS") or 0))
                    except Exception:
                        ficha_info["APRENDICES MATRICULADOS"] = 0
                        
                    # Calcular duración si es nula
                    duracion = ficha_info.get("DURACION")
                    if duracion is None or duracion == "":
                        inicio = self.parse_date(ficha_info.get("FECHA INICIO"))
                        fin = self.parse_date(ficha_info.get("FECHA TERMINACION"))
                        if inicio and fin:
                            ficha_info["DURACION_CALCULADA"] = round((fin - inicio).days / 30.44)
                        else:
                            ficha_info["DURACION_CALCULADA"] = 0
                    else:
                        try:
                            ficha_info["DURACION_CALCULADA"] = int(float(duracion))
                        except Exception:
                            ficha_info["DURACION_CALCULADA"] = 0
                            
                    self.fichas.append(ficha_info)
        except Exception as e:
            print(f"Error al cargar fichas.json: {e}")
            self.fichas = []

    # --- KPIs ---
    def obtener_kpis(self):
        if not self.fichas:
            return {
                "total_formaciones": 0,
                "total_aprendices": 0,
                "promedio_aprendices": 0.0,
                "total_redes": 0,
                "total_municipios": 0,
                "total_instructores": 0,
                "promedio_duracion": 0.0
            }
        
        total_formaciones = len(self.fichas)
        total_aprendices = sum(f["APRENDICES MATRICULADOS"] for f in self.fichas)
        promedio_aprendices = round(total_aprendices / total_formaciones, 1) if total_formaciones else 0
        
        redes = set(f.get("RED DE CONOCIMIENTO") for f in self.fichas if f.get("RED DE CONOCIMIENTO"))
        municipios = set(f.get("MUNICIPIO") for f in self.fichas if f.get("MUNICIPIO"))
        
        instructores = set()
        for f in self.fichas:
            i25 = f.get("INSTRUCTOR TÉCNICO 2025")
            i26 = f.get("INSTRUCTOR TÉCNICO 2026")
            if i25 and i25 != "None": instructores.add(i25.strip().upper())
            if i26 and i26 != "None": instructores.add(i26.strip().upper())
            
        duraciones = [f["DURACION_CALCULADA"] for f in self.fichas if f.get("DURACION_CALCULADA")]
        promedio_duracion = round(sum(duraciones) / len(duraciones), 1) if duraciones else 0.0
        
        return {
            "total_formaciones": total_formaciones,
            "total_aprendices": total_aprendices,
            "promedio_aprendices": promedio_aprendices,
            "total_redes": len(redes),
            "total_municipios": len(municipios),
            "total_instructores": len(instructores),
            "promedio_duracion": promedio_duracion
        }

    # --- Datos de Gráficos ---
    def obtener_aprendices_por_red(self):
        resultado = {}
        for f in self.fichas:
            red = f.get("RED DE CONOCIMIENTO") or "DESCONOCIDA"
            resultado[red] = resultado.get(red, 0) + f["APRENDICES MATRICULADOS"]
        # Ordenar por cantidad
        return dict(sorted(resultado.items(), key=lambda item: item[1], reverse=True))

    def obtener_fichas_por_municipio(self):
        resultado = {}
        for f in self.fichas:
            muni = f.get("MUNICIPIO") or "DESCONOCIDO"
            resultado[muni] = resultado.get(muni, 0) + 1
        return dict(sorted(resultado.items(), key=lambda item: item[1], reverse=True))

    def obtener_distribucion_oferta(self):
        resultado = {}
        for f in self.fichas:
            oferta = str(f.get("TIPO DE OFERTA") or "DESCONOCIDO").strip().upper()
            if "ABIERTA" in oferta:
                oferta_key = "ABIERTA"
            elif "CERRADA" in oferta:
                oferta_key = "CERRADA"
            else:
                oferta_key = oferta
            resultado[oferta_key] = resultado.get(oferta_key, 0) + 1
        return resultado

    def obtener_distribucion_nivel(self):
        resultado = {}
        for f in self.fichas:
            nivel = str(f.get("NIVEL") or "DESCONOCIDO").strip().upper()
            resultado[nivel] = resultado.get(nivel, 0) + 1
        return resultado

    # --- Rankings y Listados ---
    def obtener_ranking_instructores(self, año=2026, limit=10):
        inst_key = f"INSTRUCTOR TÉCNICO {año}"
        fichas_por_inst = {}
        aprendices_por_inst = {}
        
        for f in self.fichas:
            inst = f.get(inst_key)
            if inst and inst != "None" and str(inst).strip() != "":
                inst = inst.strip().upper()
                fichas_por_inst[inst] = fichas_por_inst.get(inst, 0) + 1
                aprendices_por_inst[inst] = aprendices_por_inst.get(inst, 0) + f["APRENDICES MATRICULADOS"]
                
        ranking = []
        for inst, cant_fichas in fichas_por_inst.items():
            ranking.append({
                "instructor": inst,
                "fichas": cant_fichas,
                "aprendices": aprendices_por_inst.get(inst, 0)
            })
            
        ranking.sort(key=lambda x: (x["fichas"], x["aprendices"]), reverse=True)
        return ranking[:limit]

    def obtener_proximas_a_terminar(self, limit=10):
        validas = []
        for f in self.fichas:
            fecha_fin = self.parse_date(f.get("FECHA TERMINACION"))
            if fecha_fin:
                validas.append((f, fecha_fin))
                
        validas.sort(key=lambda x: x[1])
        
        resultado = []
        for f, fecha in validas[:limit]:
            resultado.append({
                "ficha": f.get("FICHA"),
                "programa": f.get("NOMBRE DEL PROGRAMA"),
                "municipio": f.get("MUNICIPIO"),
                "fecha_terminacion": f.get("FECHA TERMINACION"),
                "instructor_2026": f.get("INSTRUCTOR TÉCNICO 2026")
            })
        return resultado

    def obtener_opciones_filtros(self):
        municipios = sorted(list(set(f.get("MUNICIPIO") for f in self.fichas if f.get("MUNICIPIO"))))
        redes = sorted(list(set(f.get("RED DE CONOCIMIENTO") for f in self.fichas if f.get("RED DE CONOCIMIENTO"))))
        niveles = sorted(list(set(f.get("NIVEL") for f in self.fichas if f.get("NIVEL"))))
        return {
            "municipios": ["Todos"] + municipios,
            "redes": ["Todas"] + redes,
            "niveles": ["Todos"] + niveles
        }

    # --- Filtrado y Búsqueda ---
    def buscar_fichas(self, query="", municipio="Todos", red="Todas", nivel="Todos"):
        resultado = []
        query = query.lower().strip()
        
        for f in self.fichas:
            if municipio != "Todos" and f.get("MUNICIPIO") != municipio:
                continue
            if red != "Todas" and f.get("RED DE CONOCIMIENTO") != red:
                continue
            if nivel != "Todos" and f.get("NIVEL") != nivel:
                continue
                
            if query:
                valores_buscar = [
                    f.get("FICHA") or "",
                    f.get("NOMBRE DEL PROGRAMA") or "",
                    f.get("CODIGO DE PROGRAMA") or "",
                    f.get("INSTRUCTOR TÉCNICO 2025") or "",
                    f.get("INSTRUCTOR TÉCNICO 2026") or "",
                    f.get("AMBIENTE") or "",
                    f.get("TIPO DE OFERTA") or "",
                    f.get("CÓDIGO PROYECTO") or ""
                ]
                match = False
                for val in valores_buscar:
                    if query in str(val).lower():
                        match = True
                        break
                if not match:
                    continue
                    
            resultado.append(f)
            
        return resultado
