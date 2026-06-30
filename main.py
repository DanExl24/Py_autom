from servicio_general import obtener_servicio_drive,obtener_servicio_sheets
import webbrowser
import json
import re
drive = obtener_servicio_drive()
sheets = obtener_servicio_sheets()
FOLDER_ID = "1-pjnJ8jumWJXFzc3zONJXZ1KYLxC6Xjt"
SELECT_FOLDER = '2. Programacion Formaciones'
SF_FOLDERS = []

fd=[]

def res_carpeta(ID):
    resultado = (
    drive.files()
    .list(
        q=f"'{ID}' in parents",
        fields="files(id,name,mimeType,webViewLink)"
    )
    .execute()
    )
    return resultado

def get_carpeta(item):
    folder_id = item['id']
    SF_FOLDERS =  res_carpeta(folder_id).get("files",[])
    return SF_FOLDERS


items = res_carpeta(FOLDER_ID).get("files", [])

def constructor():
    def construir_fichas():
        for item in items:
            if item['name'] == SELECT_FOLDER:
                programadores = get_carpeta(item)
                print(programadores)
                indice = {}
                for programador in programadores:
                    redes = get_carpeta(programador)
                    for red in redes:
                        fichas = get_carpeta(red)
                        for ficha in fichas:
                            coincidencia = re.search(r"\d{7}", ficha["name"])

                            if coincidencia:

                                numero = coincidencia.group()

                                indice[numero] = {
                                    "nombre": ficha["name"],
                                    "id": ficha["id"],
                                    "programador": programador["name"],
                                    "red": red["name"],
                                    "mimetype" : ficha["mimeType"],
                                    "url": ficha["webViewLink"]
                                }


                return indice
    indice = construir_fichas()
    with open("fichas.json", "w") as archivo:
        json.dump(indice, archivo)


def buscar_ficha(FICHA):
    with open("fichas.json") as archivo:
        fichas = json.load(archivo)
    ficha = fichas.get((f"{FICHA}"))
    if(ficha['url']):
        print(f"Abriendo {ficha["nombre"]}...\nmimeType:{ficha["mimetype"]}")
        webbrowser.open(ficha["url"])
        
    else:
        print(f"No existe esta ficha")
