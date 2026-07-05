import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from constructor import buscar_ficha

ctk.set_appearance_mode("System")      # System, Light o Dark
ctk.set_default_color_theme("blue")

def ejecutar():
    ficha = entrada.get()
    buscar_ficha(ficha)

app = ctk.CTk()
app.title("Busqueda de Programadores")
app.geometry("400x180")
app.attributes("-topmost", True)

titulo = ctk.CTkLabel(app, text="Ingrese la ficha")
titulo.pack(pady=(20,5))

entrada = ctk.CTkEntry(app, width=250)
entrada.pack()

boton = ctk.CTkButton(app, text="Buscar", command=ejecutar)
boton.pack(pady=20)

app.mainloop()