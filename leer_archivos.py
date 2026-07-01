from servicio_general import obtener_servicio_drive
import io
import json
from googleapiclient.http import MediaIoBaseDownload
from openpyxl import load_workbook

drive = obtener_servicio_drive()
PASAN2026 = {}
hoja_min_row = 0
hoja_max_row = 0
hoja_min_col = 0
hoja_max_col = 0
CARPETA_PRINCIPAL = "1nc5qTNXcP05h4N8AMka-CODYrGTXk4rm"

def carpeta_principal(ID):
    resultado = (
    drive.files()
    .list(
        q=f"'{ID}' in parents",
        fields="files(id,name,mimeType,webViewLink)"
    )
    .execute()
    )
    return resultado

# Obtener archivos dentro de la carpeta principal
oferta = carpeta_principal(CARPETA_PRINCIPAL).get("files",[])
programas_regulares = {}
for archivo in oferta:
    if (archivo['name']=='CONSOLIDADO PROGRAMAS REGULAR - 2026.xlsx'):
        programas_regulares = archivo

# Hacer la peticion aq google drive al archivo de programas regulares por medio de la ID del archivo
request = drive.files().get_media(fileId=programas_regulares['id'])

# crear un archivo en memoria RAM
excel = io.BytesIO()

# Descargar el archivo de drive y escribir sus datos dentro de la variable excel, asi se genera el archivo en memoria
downloader = MediaIoBaseDownload(excel, request)

# Variable para saber cuando termina la descarga
done = False
# Descargar el archivo
while not done:
    _, done = downloader.next_chunk() #Descargar por pedazos (chuncks)

excel.seek(0) #Leer desde el comienzo del cursor

wb = load_workbook(excel)

# print(wb.sheetnames)

def leer_hoja ():
    hoja = wb["PASAN 2026 "]
    # print(f"Hoja: {hoja}")
    # print(f"Filas de la hoja: {hoja.max_row}")
    # print(f"Columnas de la hoja: {hoja.max_column}")
    # print(f"Dimensiones calculadas: {hoja.calculate_dimension()}")
    return hoja

def debug_celdas():
    hoja = leer_hoja()

    with open("celdas.txt", "w", encoding="utf-8") as archivo:
        for fila in hoja.iter_rows():
            for celda in fila:
                if celda.value is not None:
                    archivo.write(f"Coordenada: {celda.coordinate}, valor: {celda.value}\n")

# leer_hoja('PASAN 2026 ')

def obtener_rango(nombre):
    hoja = leer_hoja()
    for fila in hoja.iter_rows():
        for celda in fila:
            if celda.value is not None:
                if(celda.value == nombre):
                    for rango in hoja.merged_cells.ranges:
                        if celda.coordinate in rango:
                            print(f"Rango: {rango}")
                            return {"Rango": {rango}}
                        else:
                            print(f"Celda: {celda.coordinate}")
                    return {"Celda" : {celda.coordinate}}
                
def obtener_rango_hoja(nombre):
    hoja = leer_hoja()
    rg = {}
    for fila in hoja.iter_rows():
        for celda in fila:
            if celda.value is not None:
                if(celda.value == nombre):
                    for rango in hoja.merged_cells.ranges:
                        if celda.coordinate in rango:
                            PASAN2026[nombre] = {
                                "nombre" : nombre,
                                "coordenadas" : f"{rango}",
                                "min_row" : f"{rango.min_row}",
                                "max_row" : f"{rango.max_row}",
                                "min_col" : f"{rango.min_col}",
                                "max_col" : f"{rango.max_col}",
                            }
                            return PASAN2026
                        else:
                            print(f"No hay rango")
                        

#with open("Red_conocimiento.json", "w") as seed_redes:
#    json.dump(obtener_rango_hoja("FORMACIONES TITULADA REGULAR MODALIDAD PRESENCIAL Y VIRTUAL 2026"),seed_redes,ensure_ascii=False,indent=1)

# Funcion para obtener las redes de conocimiento
def obtener_redes():
    hoja = leer_hoja()
    #print(type(json))
    for fila in hoja.iter_rows():
        for celda in fila:
            if celda.value is not None:
                if(celda.value == "RED DE CONOCIMIENTO"):
                    # Recorrer todas las redes sumando el valor de las filas
                    FilaRedes = celda.row+1
                    CeldaRedes = hoja.cell(FilaRedes,celda.column)
                    print(CeldaRedes.value)
                    for rango in hoja.merged_cells.ranges:
                        if CeldaRedes.coordinate in rango:
                            print(rango)
                            PASAN2026[CeldaRedes.value] = {
                                "nombre" : CeldaRedes.value,
                                "coordenadas" : f"{rango}",
                                "min_row" : f"{rango.min_row}",
                                "max_row" : f"{rango.max_row}",
                                "min_col" : f"{rango.min_col}",
                                "max_col" : f"{rango.max_col}",
                            }
    return PASAN2026
                    #print(celda.row)
                    #print(celda.column)

#with open("Red_conocimiento.json", "w") as seed_redes:
#    json.dump(obtener_redes(),seed_redes,ensure_ascii=False,indent=1)

with open("Red_conocimiento.json") as archivo:
    ars = json.load(archivo)
    ar = ars.get("FORMACIONES TITULADA REGULAR MODALIDAD PRESENCIAL Y VIRTUAL 2026")
    if(ar):
        hoja_min_row = ar['min_row']
        hoja_max_row = ar['max_row']
        hoja_min_col = ar['min_col']
        hoja_max_col = ar['max_col']


                        
def consultar_valor(rango):
    hoja = leer_hoja()
    for fila in hoja.iter_rows():
        for celda in fila:
            if celda.value is not None:
                if celda.coordinate in rango:
                    print(f"Valor: {celda.value}")




def obtener_encabezados():
    hoja = leer_hoja()
    encabezado = {}
    for fila in hoja.iter_rows():
        for celda in fila:
            if celda.value is not None:
                if(celda.value == "RED DE CONOCIMIENTO"):
                    print(celda.coordinate)
                    ColInicioFila = celda.row
                    ColInicio = celda.column
                    print("ColInicio:", ColInicio)
                    print("hoja_max_col:", hoja_max_col)
                    for rangoEncabezado in range(ColInicio,int(hoja_max_col) +1):
                        encabezados = hoja.cell(row=ColInicioFila,column=rangoEncabezado) 
                        encabezado[encabezados.value] = {
                            "nombre" : encabezados.value,
                            "coordenadas" : encabezados.coordinate,
                            "row" : encabezados.row,
                            "col" : encabezados.column
                        }
                    return encabezado
#with open("Encabezados.json", "w") as encabezados:
#    json.dump(obtener_encabezados(),encabezados,ensure_ascii=False,indent=1)



def ficha_por_red():
    hoja = leer_hoja()
    redes = {}
    fichas = {}
    encabezado = {}
    with open("Red_conocimiento.json") as redes_json:
        redes = json.load(redes_json)
    with open("Encabezados.json") as encabezados:
        encabezado = json.load(encabezados)
    for nombre_red, valores_red in redes.items():
        fichas_red = {}
        coordenadas = valores_red
        for filas in range(int(coordenadas["min_row"]),int(coordenadas["max_row"]) + 1):
            registro = {}
            for nombre_encabezado,valores_encabezado in encabezado.items():
                columna = valores_encabezado["col"]
                registro[nombre_encabezado.strip()] = str(hoja.cell(row=filas,column=columna).value).strip()
                if nombre_encabezado.strip() == "RED DE CONOCIMIENTO":
                    registro["RED DE CONOCIMIENTO"] = nombre_red
            numero_ficha = registro["FICHA"]
            fichas_red[numero_ficha] = registro
        fichas[nombre_red] = fichas_red
    return fichas
#with open("fichas.json","w") as fichas:
#    json.dump(ficha_por_red(),fichas,ensure_ascii=False,indent=1)

