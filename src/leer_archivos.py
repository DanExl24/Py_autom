import sys
import os
import io
import json
import datetime
from googleapiclient.http import MediaIoBaseDownload
from openpyxl import load_workbook

# Añadir el directorio raíz al path para permitir importar módulos hermanos (como 'auth')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth.servicio_general import obtener_servicio_drive

# ID de la carpeta principal en Google Drive
CARPETA_PRINCIPAL = "1nc5qTNXcP05h4N8AMka-CODYrGTXk4rm"

def descargar_excel_desde_drive():
    """Conecta a Google Drive, busca el archivo consolidado y lo descarga en memoria RAM."""
    print("Conectando con Google Drive...")
    drive = obtener_servicio_drive()
    
    print("Buscando el archivo Excel consolidado...")
    resultado = drive.files().list(  # type: ignore
        q=f"'{CARPETA_PRINCIPAL}' in parents",
        fields="files(id,name,mimeType)"
    ).execute()
    
    archivos = resultado.get("files", [])
    consolidado = None
    for archivo in archivos:
        if archivo['name'] == 'CONSOLIDADO PROGRAMAS REGULAR - 2026.xlsx':
            consolidado = archivo
            break
            
    if not consolidado:
        raise FileNotFoundError("No se encontró el archivo 'CONSOLIDADO PROGRAMAS REGULAR - 2026.xlsx' en Google Drive.")
        
    print(f"Descargando '{consolidado['name']}'...")
    request = drive.files().get_media(fileId=consolidado['id'])  # type: ignore
    excel_memoria = io.BytesIO()
    downloader = MediaIoBaseDownload(excel_memoria, request)
    
    descargado = False
    while not descargado:
        _, descargado = downloader.next_chunk()
        
    excel_memoria.seek(0)
    print("Descarga finalizada con éxito.")
    return excel_memoria

def sanitizar_texto(texto):
    """Corrige codificaciones rotas (ej. tildes y eñes) y normaliza espacios y saltos de línea."""
    if not isinstance(texto, str):
        return texto
    
    # Lista de reemplazos para caracteres con problemas de codificación comunes en Excel
    reemplazos_encoding = {
        'AO': 'AÑO',
        'DISEO': 'DISEÑO',
        'MONTAI': 'MONTAÑI',
        'CDIGO': 'CÓDIGO',
        'GESTIN': 'GESTIÓN',
        'CONSTRUCCIN': 'CONSTRUCCIÓN',
        'ANIMACIN': 'ANIMACIÓN',
        'INFORMTIC': 'INFORMÁTIC',
        'UNIN': 'UNIÓN',
        'INICI0': 'INICIO',
        'ASIGNACIN': 'ASIGNACIÓN',
        'RESOLUCIN': 'RESOLUCIÓN',
        'VALORACIN': 'VALORACIÓN',
        'TECNOLOGO': 'TECNÓLOGO',
        'TECNICO': 'TÉCNICO',
    }
    
    # Primero limpiar caracteres rotos representados como caracteres de reemplazo
    for bad_char in ('\ufffd', ''):
        texto = texto.replace(f'A{bad_char}O', 'AÑO')
        texto = texto.replace(f'DISE{bad_char}O', 'DISEÑO')
        texto = texto.replace(f'MONTA{bad_char}I', 'MONTAÑI')
        texto = texto.replace(f'C{bad_char}DIGO', 'CÓDIGO')
        texto = texto.replace(f'GESTI{bad_char}N', 'GESTIÓN')
        texto = texto.replace(f'CONSTRUCCI{bad_char}N', 'CONSTRUCCIÓN')
        texto = texto.replace(f'ANIMACI{bad_char}N', 'ANIMACIÓN')
        texto = texto.replace(f'UNI{bad_char}N', 'UNIÓN')
        texto = texto.replace(f'T{bad_char}CNICO', 'TÉCNICO')
        texto = texto.replace(f'TECN{bad_char}LOGO', 'TECNÓLOGO')
        
    for buscar, reemplazar in reemplazos_encoding.items():
        texto = texto.replace(buscar, reemplazar)
        
    # Reemplazar saltos de línea y múltiples espacios por un espacio simple
    texto = texto.replace('\n', ' ')
    while '  ' in texto:
        texto = texto.replace('  ', ' ')
        
    return texto.strip()

def limpiar_valor(valor):
    """Limpia los tipos de datos de Excel (None, fechas, flotantes con .0)."""
    if valor is None:
        return None
        
    # Si es una cadena, verificar si representa un valor nulo y sanitizarla
    if isinstance(valor, str):
        valor_limpio = valor.strip()
        if valor_limpio.upper() in ('NONE', 'NAN', ''):
            return None
        return sanitizar_texto(valor_limpio)
        
    # Si es fecha/tiempo de python, formatear a string estándar 'YYYY-MM-DD'
    if isinstance(valor, (datetime.datetime, datetime.date)):
        return valor.strftime('%Y-%m-%d')
        
    # Si es un número float que representa un entero, convertir a int
    if isinstance(valor, float):
        if valor.is_integer():
            return int(valor)
        return valor
        
    return valor

def normalizar_trimestre(valor):
    if not isinstance(valor, str):
        return valor
    # Limpiar espacios múltiples y pasar a mayúsculas
    s = valor.strip().upper()
    
    # Buscar patrón: T-[espacio]?[romano][separador][año]
    # Ej: T-III-2024, T-III 2024, T- IV 2025, T- II-2025
    import re
    match = re.search(r'T\s*-\s*(I{1,3}|IV|V)\s*[-/ ]\s*(\d{4})', s)
    if match:
        romano = match.group(1).upper()
        anio = match.group(2)
        return f"T-{romano}-{anio}"
        
    return s

def obtener_valor_celda(hoja, fila, columna):
    """Resuelve celdas combinadas (merged cells) en openpyxl para obtener el valor correcto."""
    for rango in hoja.merged_cells.ranges:
        if fila >= rango.min_row and fila <= rango.max_row and columna >= rango.min_col and columna <= rango.max_col:
            # Retorna el valor de la celda superior izquierda del rango combinado
            return hoja.cell(row=rango.min_row, column=rango.min_col).value
    return hoja.cell(row=fila, column=columna).value

def extraer_fichas(excel_stream):
    """Extrae las fichas de la hoja del Excel de forma dinámica y limpia."""
    print("Cargando el libro de Excel con openpyxl...")
    # data_only=True permite leer los valores calculados de las fórmulas, no las fórmulas en sí
    wb = load_workbook(excel_stream, data_only=True)
    
    # Intentar buscar la hoja (manejando posibles nombres)
    sheet_name = "PASAN 2026 - TI-TII-TIII"
    if sheet_name not in wb.sheetnames:
        sheet_name = "PASAN 2026 "
        if sheet_name not in wb.sheetnames:
            sheet_name = "PASAN 2026"
    hoja = wb[sheet_name]
    print(f"Procesando hoja: '{sheet_name}'")
    
    # 1. Buscar la fila y columna cabecera "RED DE CONOCIMIENTO"
    header_row = None
    red_col = None
    for fila in range(1, 20):  # Usualmente las cabeceras están al principio
        for col in range(1, hoja.max_column + 1):
            val = hoja.cell(row=fila, column=col).value
            if val and sanitizar_texto(str(val)).upper() == "RED DE CONOCIMIENTO":
                header_row = fila
                red_col = col
                break
        if header_row:
            break
            
    if not header_row or not red_col:
        raise ValueError("No se pudo localizar el encabezado 'RED DE CONOCIMIENTO' en la hoja.")
        
    print(f"Cabecera detectada en Fila {header_row}, Columna {red_col}")
    
    # 2. Leer dinámicamente todos los encabezados hacia la derecha
    encabezados = []
    for col in range(red_col, hoja.max_column + 1):
        h_val = hoja.cell(row=header_row, column=col).value
        if h_val is not None:
            nombre_cabecera = sanitizar_texto(str(h_val))
            encabezados.append((col, nombre_cabecera))
            
    print(f"Se encontraron {len(encabezados)} columnas de datos.")
    
    # 3. Leer las filas de datos desde la siguiente fila de la cabecera
    fichas_estructuradas = {}
    
    for fila in range(header_row + 1, hoja.max_row + 1):
        # Determinar la red de conocimiento (resolviendo si está en celda combinada)
        red_valor = obtener_valor_celda(hoja, fila, red_col)
        red_limpia = limpiar_valor(red_valor)
        
        if not red_limpia:
            continue
            
        # Construir el registro de la ficha con todas las columnas
        registro = {}
        for col, nombre_cabecera in encabezados:
            val_celda = obtener_valor_celda(hoja, fila, col)
            val_limpio = limpiar_valor(val_celda)
            
            # Normalizar el campo del Año / Trimestre de Inicio si es string
            if nombre_cabecera == "AÑO /TRIMESTRE DE INICIO" and isinstance(val_limpio, str):
                val_limpio = normalizar_trimestre(val_limpio)
                
            registro[nombre_cabecera] = val_limpio
            
        ficha_id = registro.get("FICHA")
        
        # Ignorar filas de encabezados repetidos (donde la ficha dice 'FICHA') o filas vacías
        if not ficha_id or str(ficha_id).strip().upper() == "FICHA":
            continue
            
        # Asegurarse de que la red de conocimiento esté grabada limpia
        registro["RED DE CONOCIMIENTO"] = red_limpia
        
        # Inicializar el nodo de la red si es nuevo
        if red_limpia not in fichas_estructuradas:
            fichas_estructuradas[red_limpia] = {}
            
        # Guardar la ficha indexada por su número de ficha convertido a string
        fichas_estructuradas[red_limpia][str(ficha_id)] = registro
        
    print(f"Extracción completada. {len(fichas_estructuradas)} Redes de Conocimiento procesadas.")
    for red, fichas in fichas_estructuradas.items():
        print(f" - {red}: {len(fichas)} fichas")
        
    return fichas_estructuradas

def ejecutar_extraccion():
    """Función principal que descarga, procesa y guarda las fichas limpias."""
    try:
        # Descargar Excel
        excel_memoria = descargar_excel_desde_drive()
        
        # Extraer datos
        datos_fichas = extraer_fichas(excel_memoria)
        
        # Resolver rutas relativas para guardar en la carpeta output/
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_file = os.path.join(base_dir, "output", "fichas.json")
        
        # Asegurar que el directorio de salida existe
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Guardar en JSON codificado en UTF-8 estándar
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(datos_fichas, f, ensure_ascii=False, indent=2)
            
        print(f"Archivo JSON guardado con éxito en: {output_file}")
        
    except Exception as e:
        print(f"Error al procesar el archivo Excel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    ejecutar_extraccion()
