import os
import sys
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Agregar el directorio raíz al path de Python si es necesario
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from procesador_datos import ProcesadorDatos

# Importar matplotlib para los gráficos interactivos
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Definir la paleta de colores coherente con "Azul Rey Oscuro"
COLOR_AZUL_REY_SOPORTE = "#1E3A8A"  # Azul Rey Oscuro principal (branding/sidebar)
COLOR_AZUL_REY_LIGHT = "#2563EB"    # Azul Rey más vivo para elementos activos en modo claro
COLOR_AZUL_REY_DARK = "#3B82F6"     # Azul Rey brillante para destacar en modo oscuro
COLOR_ACCENT = "#0EA5E9"            # Cyan para acentos
COLOR_SUCCESS = "#10B981"           # Esmeralda para indicadores de éxito
COLOR_WARNING = "#F59E0B"           # Ámbar para alertas/observaciones

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configurar ventana principal
        self.title("Dashboard de Fichas y Estadísticas 2026")
        self.geometry("1200x750")
        self.minsize(1050, 650)

        # Cargar los datos
        self.procesador = ProcesadorDatos()

        # Establecer apariencia inicial
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        # Configurar Grid de la ventana principal (1 fila, 2 columnas)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Crear componentes
        self.crear_sidebar()
        self.crear_contenedor_principal()

        # Mostrar pestaña por defecto
        self.mostrar_pestaña("dashboard")

    def crear_sidebar(self):
        # Frame del Sidebar con color Azul Rey Oscuro
        self.sidebar_frame = ctk.CTkFrame(
            self, 
            width=220, 
            corner_radius=0,
            fg_color=(COLOR_AZUL_REY_SOPORTE, "#0B132B")  # Azul rey en claro, azul marino muy oscuro en oscuro
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)

        # Título del Sidebar
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="SENA\nFichas 2026", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFFFFF"
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 30))

        # Botón 1: Dashboard
        self.btn_dashboard = ctk.CTkButton(
            self.sidebar_frame,
            text="📊 Dashboard",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            height=40,
            fg_color="transparent",
            text_color="#E2E8F0",
            hover_color=("#3B82F6", "#1E293B"),
            command=lambda: self.mostrar_pestaña("dashboard")
        )
        self.btn_dashboard.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        # Botón 2: Estadísticas
        self.btn_stats = ctk.CTkButton(
            self.sidebar_frame,
            text="📈 Estadísticas",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            height=40,
            fg_color="transparent",
            text_color="#E2E8F0",
            hover_color=("#3B82F6", "#1E293B"),
            command=lambda: self.mostrar_pestaña("stats")
        )
        self.btn_stats.grid(row=2, column=0, padx=10, pady=5, sticky="ew")

        # Botón 3: Buscador
        self.btn_search = ctk.CTkButton(
            self.sidebar_frame,
            text="🔍 Buscador",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
            height=40,
            fg_color="transparent",
            text_color="#E2E8F0",
            hover_color=("#3B82F6", "#1E293B"),
            command=lambda: self.mostrar_pestaña("search")
        )
        self.btn_search.grid(row=3, column=0, padx=10, pady=5, sticky="ew")

        # Selector de Tema / Apariencia en la parte inferior
        self.appearance_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Tema Visual:", 
            text_color="#94A3B8",
            font=ctk.CTkFont(size=11)
        )
        self.appearance_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        
        self.appearance_optionemenu = ctk.CTkOptionMenu(
            self.sidebar_frame, 
            values=["System", "Light", "Dark"],
            command=self.cambiar_apariencia,
            fg_color=("#2563EB", "#1E293B"),
            button_color=("#1D4ED8", "#0F172A"),
            button_hover_color=("#1E40AF", "#1E293B"),
            text_color="#FFFFFF"
        )
        self.appearance_optionemenu.grid(row=6, column=0, padx=20, pady=(5, 20))

    def cambiar_apariencia(self, nuevo_tema):
        ctk.set_appearance_mode(nuevo_tema)
        # Re-renderizar gráficos con los nuevos colores de fondo
        self.after(200, self.actualizar_graficos)

    def crear_contenedor_principal(self):
        # Contenedor principal de contenidos (columna derecha)
        self.content_container = ctk.CTkFrame(
            self, 
            fg_color=("#F8FAFC", "#0F172A"),  # Gris pizarra muy claro en Light, azul muy oscuro en Dark
            corner_radius=0
        )
        self.content_container.grid(row=0, column=1, sticky="nsew", padx=0, pady=0)
        self.content_container.grid_rowconfigure(0, weight=1)
        self.content_container.grid_columnconfigure(0, weight=1)

        # Crear frames para cada pestaña
        self.frame_dashboard = DashboardFrame(self.content_container, self)
        self.frame_stats = StatsFrame(self.content_container, self)
        self.frame_search = SearchFrame(self.content_container, self)

    def mostrar_pestaña(self, pestaña):
        # Desactivar todos los botones
        self.btn_dashboard.configure(fg_color="transparent")
        self.btn_stats.configure(fg_color="transparent")
        self.btn_search.configure(fg_color="transparent")

        # Ocultar todos los frames
        self.frame_dashboard.grid_forget()
        self.frame_stats.grid_forget()
        self.frame_search.grid_forget()

        # Activar el seleccionado y mostrar su frame
        if pestaña == "dashboard":
            self.btn_dashboard.configure(fg_color=(COLOR_AZUL_REY_LIGHT, "#1E293B"))
            self.frame_dashboard.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.frame_dashboard.cargar_datos()
        elif pestaña == "stats":
            self.btn_stats.configure(fg_color=(COLOR_AZUL_REY_LIGHT, "#1E293B"))
            self.frame_stats.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
            self.frame_stats.cargar_datos()
        elif pestaña == "search":
            self.btn_search.configure(fg_color=(COLOR_AZUL_REY_LIGHT, "#1E293B"))
            self.frame_search.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)

    def actualizar_graficos(self):
        if self.frame_dashboard.winfo_ismapped():
            self.frame_dashboard.cargar_datos()

    def mostrar_detalle_ficha(self, ficha_info):
        # Ventana flotante de detalles
        detalle_win = DetailWindow(self, ficha_info)
        detalle_win.grab_set()


class DashboardFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid config
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Título superior
        self.title_label = ctk.CTkLabel(
            self, 
            text="📊 Resumen General de Formaciones", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1E293B", "#F8FAFC")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # Frame para KPIs
        self.kpi_container = ctk.CTkFrame(self, fg_color="transparent")
        self.kpi_container.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(30, 15))
        for i in range(4):
            self.kpi_container.grid_columnconfigure(i, weight=1)

        # Crear tarjetas KPI
        self.kpi_cards = []
        kpi_titles = ["Total Formaciones", "Total Aprendices", "Promedio Ficha", "Promedio Duración"]
        kpi_colors = [COLOR_AZUL_REY_DARK, COLOR_ACCENT, COLOR_SUCCESS, COLOR_WARNING]
        
        for i in range(4):
            card = ctk.CTkFrame(
                self.kpi_container, 
                fg_color=("#FFFFFF", "#1E293B"), 
                border_width=2,
                border_color=("#E2E8F0", "#334155")
            )
            card.grid(row=0, column=i, padx=8, sticky="ew")
            
            # Línea decorativa superior del color del KPI
            dec = ctk.CTkFrame(card, height=4, fg_color=kpi_colors[i])
            dec.pack(fill="x", side="top")

            lbl_title = ctk.CTkLabel(
                card, 
                text=kpi_titles[i].upper(), 
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color=("#64748B", "#94A3B8")
            )
            lbl_title.pack(anchor="w", padx=15, pady=(12, 2))

            lbl_val = ctk.CTkLabel(
                card, 
                text="0", 
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=("#0F172A", "#F8FAFC")
            )
            lbl_val.pack(anchor="w", padx=15, pady=(0, 12))
            
            self.kpi_cards.append(lbl_val)

        # Contenedor para Gráficos
        self.charts_container = ctk.CTkFrame(self, fg_color="transparent")
        self.charts_container.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        self.charts_container.grid_columnconfigure(0, weight=1)
        self.charts_container.grid_columnconfigure(1, weight=1)
        self.charts_container.grid_rowconfigure(0, weight=1)

        # Chart 1 Frame
        self.chart1_frame = ctk.CTkFrame(
            self.charts_container, 
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.chart1_frame.grid(row=0, column=0, padx=8, pady=5, sticky="nsew")
        self.chart1_title = ctk.CTkLabel(
            self.chart1_frame, 
            text="Aprendices por Red de Conocimiento (Top)",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.chart1_title.pack(anchor="w", padx=15, pady=8)

        # Chart 2 Frame
        self.chart2_frame = ctk.CTkFrame(
            self.charts_container, 
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.chart2_frame.grid(row=0, column=1, padx=8, pady=5, sticky="nsew")
        self.chart2_title = ctk.CTkLabel(
            self.chart2_frame, 
            text="Distribución de Oferta Abierta vs Cerrada",
            font=ctk.CTkFont(size=13, weight="bold")
        )
        self.chart2_title.pack(anchor="w", padx=15, pady=8)

        # Variables para almacenar lienzos
        self.canvas1 = None
        self.canvas2 = None

    def cargar_datos(self):
        kpis = self.controller.procesador.obtener_kpis()
        
        # Actualizar valores KPI
        self.kpi_cards[0].configure(text=f"{kpis['total_formaciones']}")
        self.kpi_cards[1].configure(text=f"{kpis['total_aprendices']:,}")
        self.kpi_cards[2].configure(text=f"{kpis['promedio_aprendices']}")
        self.kpi_cards[3].configure(text=f"{kpis['promedio_duracion']} meses")

        # Dibujar Gráficos
        self.dibujar_graficos()

    def dibujar_graficos(self):
        # Determinar colores basados en la apariencia
        modo_oscuro = ctk.get_appearance_mode() == "Dark"
        bg_color = "#1E293B" if modo_oscuro else "#FFFFFF"
        text_color = "#F8FAFC" if modo_oscuro else "#0F172A"
        grid_color = "#334155" if modo_oscuro else "#E2E8F0"

        # --- GRAFICO 1: Aprendices por Red de Conocimiento ---
        # Limpiar canvas anterior
        if self.canvas1:
            self.canvas1.get_tk_widget().destroy()

        datos_red = self.controller.procesador.obtener_aprendices_por_red()
        # Tomar top 5 y agrupar el resto en "Otros"
        items = list(datos_red.items())
        top_n = items[:5]
        resto = sum(val for key, val in items[5:])
        if resto > 0:
            top_n.append(("OTRAS REDES", resto))

        redes_nombres = [item[0] for item in top_n]
        # Recortar nombres largos para que quepan en el gráfico
        redes_recortadas = [r[:20] + "..." if len(r) > 22 else r for r in redes_nombres]
        redes_valores = [item[1] for item in top_n]

        fig1, ax1 = plt.subplots(figsize=(4.5, 3.2), dpi=100)
        fig1.patch.set_facecolor(bg_color)
        ax1.set_facecolor(bg_color)

        bars = ax1.barh(redes_recortadas[::-1], redes_valores[::-1], color=COLOR_AZUL_REY_DARK if modo_oscuro else COLOR_AZUL_REY_LIGHT)
        
        # Etiquetas del eje
        ax1.tick_params(colors=text_color, labelsize=8)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)
        ax1.spines['left'].set_color(grid_color)
        ax1.spines['bottom'].set_color(grid_color)
        ax1.grid(axis='x', linestyle='--', alpha=0.5, color=grid_color)

        # Añadir valores al final de las barras
        for bar in bars:
            width = bar.get_width()
            ax1.text(width + (width * 0.02), bar.get_y() + bar.get_height()/2, 
                     f'{int(width):,}', 
                     va='center', ha='left', color=text_color, fontsize=8, fontweight='bold')

        plt.tight_layout()

        self.canvas1 = FigureCanvasTkAgg(fig1, master=self.chart1_frame)
        self.canvas1.draw()
        self.canvas1.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig1)

        # --- GRAFICO 2: Distribución de Oferta ---
        if self.canvas2:
            self.canvas2.get_tk_widget().destroy()

        datos_oferta = self.controller.procesador.obtener_distribucion_oferta()
        oferta_labels = list(datos_oferta.keys())
        oferta_valores = list(datos_oferta.values())

        fig2, ax2 = plt.subplots(figsize=(4.5, 3.2), dpi=100)
        fig2.patch.set_facecolor(bg_color)
        ax2.set_facecolor(bg_color)

        # Colores coherentes con el azul rey y cyan
        colores_pie = [COLOR_AZUL_REY_DARK if modo_oscuro else COLOR_AZUL_REY_LIGHT, COLOR_ACCENT, COLOR_SUCCESS, COLOR_WARNING]
        
        wedges, texts, autotexts = ax2.pie(
            oferta_valores, 
            labels=oferta_labels, 
            autopct='%1.1f%%',
            startangle=90, 
            colors=colores_pie[:len(oferta_valores)],
            textprops=dict(color=text_color, fontsize=8),
            wedgeprops=dict(width=0.4, edgecolor=bg_color)  # Estilo Donut
        )

        for autotext in autotexts:
            autotext.set_color('#FFFFFF')
            autotext.set_fontsize(8)
            autotext.set_weight('bold')

        plt.tight_layout()

        self.canvas2 = FigureCanvasTkAgg(fig2, master=self.chart2_frame)
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
        plt.close(fig2)


class StatsFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid config
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Título superior
        self.title_label = ctk.CTkLabel(
            self, 
            text="📈 Rankings y Ocupación 2026", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1E293B", "#F8FAFC")
        )
        self.title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 15))

        # Panel Izquierdo: Instructores
        self.panel_inst = ctk.CTkFrame(
            self, 
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.panel_inst.grid(row=1, column=0, padx=8, pady=5, sticky="nsew")
        self.panel_inst.grid_rowconfigure(1, weight=1)
        self.panel_inst.grid_columnconfigure(0, weight=1)

        self.lbl_inst_title = ctk.CTkLabel(
            self.panel_inst, 
            text="🧑‍🏫 Instructores con Mayor Asignación (2026)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=(COLOR_AZUL_REY_LIGHT, COLOR_AZUL_REY_DARK)
        )
        self.lbl_inst_title.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.scroll_inst = ctk.CTkScrollableFrame(self.panel_inst, fg_color="transparent")
        self.scroll_inst.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Panel Derecho: Municipios y Fechas
        self.panel_right = ctk.CTkFrame(self, fg_color="transparent")
        self.panel_right.grid(row=1, column=1, padx=8, pady=5, sticky="nsew")
        self.panel_right.grid_rowconfigure(0, weight=1)
        self.panel_right.grid_rowconfigure(1, weight=1)
        self.panel_right.grid_columnconfigure(0, weight=1)

        # Municipios
        self.panel_muni = ctk.CTkFrame(
            self.panel_right,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.panel_muni.grid(row=0, column=0, pady=(0, 10), sticky="nsew")
        self.panel_muni.grid_rowconfigure(1, weight=1)
        self.panel_muni.grid_columnconfigure(0, weight=1)

        self.lbl_muni_title = ctk.CTkLabel(
            self.panel_muni, 
            text="🏙 Fichas por Municipio",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=(COLOR_AZUL_REY_LIGHT, COLOR_AZUL_REY_DARK)
        )
        self.lbl_muni_title.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.scroll_muni = ctk.CTkScrollableFrame(self.panel_muni, fg_color="transparent")
        self.scroll_muni.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        # Próximas a terminar
        self.panel_fin = ctk.CTkFrame(
            self.panel_right,
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.panel_fin.grid(row=1, column=0, pady=(10, 0), sticky="nsew")
        self.panel_fin.grid_rowconfigure(1, weight=1)
        self.panel_fin.grid_columnconfigure(0, weight=1)

        self.lbl_fin_title = ctk.CTkLabel(
            self.panel_fin, 
            text="📅 Fichas Próximas a Terminar etapa lectiva (2026/2027)",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color=(COLOR_AZUL_REY_LIGHT, COLOR_AZUL_REY_DARK)
        )
        self.lbl_fin_title.grid(row=0, column=0, padx=15, pady=10, sticky="w")

        self.scroll_fin = ctk.CTkScrollableFrame(self.panel_fin, fg_color="transparent")
        self.scroll_fin.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

    def cargar_datos(self):
        # 1. Limpiar paneles
        for widget in self.scroll_inst.winfo_children():
            widget.destroy()
        for widget in self.scroll_muni.winfo_children():
            widget.destroy()
        for widget in self.scroll_fin.winfo_children():
            widget.destroy()

        # 2. Cargar instructores
        ranking_inst = self.controller.procesador.obtener_ranking_instructores(2026, 12)
        for i, row in enumerate(ranking_inst):
            frame_row = ctk.CTkFrame(self.scroll_inst, fg_color="transparent")
            frame_row.pack(fill="x", pady=4, padx=5)
            
            lbl_pos = ctk.CTkLabel(frame_row, text=f"#{i+1}", font=ctk.CTkFont(weight="bold"), width=35, text_color=COLOR_AZUL_REY_DARK)
            lbl_pos.pack(side="left")
            
            lbl_name = ctk.CTkLabel(frame_row, text=row["instructor"].title(), anchor="w", font=ctk.CTkFont(size=12))
            lbl_name.pack(side="left", fill="x", expand=True, padx=5)
            
            lbl_stats = ctk.CTkLabel(
                frame_row, 
                text=f"{row['fichas']} fichas ({row['aprendices']} apr.)", 
                font=ctk.CTkFont(size=11, weight="bold"), 
                text_color=COLOR_ACCENT
            )
            lbl_stats.pack(side="right")

            # Separador
            sep = ctk.CTkFrame(self.scroll_inst, height=1, fg_color=("#F1F5F9", "#334155"))
            sep.pack(fill="x", padx=5)

        # 3. Cargar municipios
        ranking_muni = self.controller.procesador.obtener_fichas_por_municipio()
        for muni, count in list(ranking_muni.items())[:6]:
            frame_row = ctk.CTkFrame(self.scroll_muni, fg_color="transparent")
            frame_row.pack(fill="x", pady=4, padx=5)

            lbl_muni = ctk.CTkLabel(frame_row, text=muni.title(), anchor="w", font=ctk.CTkFont(size=12))
            lbl_muni.pack(side="left", fill="x", expand=True, padx=5)

            lbl_cnt = ctk.CTkLabel(
                frame_row, 
                text=f"{count} fichas", 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color=COLOR_SUCCESS
            )
            lbl_cnt.pack(side="right")

            sep = ctk.CTkFrame(self.scroll_muni, height=1, fg_color=("#F1F5F9", "#334155"))
            sep.pack(fill="x", padx=5)

        # 4. Cargar próximas a terminar
        proximas = self.controller.procesador.obtener_proximas_a_terminar(8)
        for row in proximas:
            frame_row = ctk.CTkFrame(self.scroll_fin, fg_color="transparent")
            frame_row.pack(fill="x", pady=4, padx=5)

            # Botón / enlace clickeable para abrir el detalle de ficha
            lbl_ficha = ctk.CTkLabel(
                frame_row, 
                text=row["ficha"], 
                font=ctk.CTkFont(weight="bold", underline=True), 
                text_color=COLOR_AZUL_REY_DARK,
                cursor="hand2"
            )
            lbl_ficha.pack(side="left", padx=(5, 10))
            
            # Encontrar los datos de la ficha correspondiente para hacerla clickeable
            f_info = next((f for f in self.controller.procesador.fichas if f["FICHA"] == row["ficha"]), None)
            if f_info:
                lbl_ficha.bind("<Button-1>", lambda e, info=f_info: self.controller.mostrar_detalle_ficha(info))

            prog_name = row["programa"]
            if len(prog_name) > 30:
                prog_name = prog_name[:28] + "..."
            lbl_prog = ctk.CTkLabel(frame_row, text=f"{prog_name.title()}", anchor="w", font=ctk.CTkFont(size=11))
            lbl_prog.pack(side="left", fill="x", expand=True)

            lbl_date = ctk.CTkLabel(
                frame_row, 
                text=f"{row['fecha_terminacion']}", 
                font=ctk.CTkFont(size=11, weight="bold"), 
                text_color=COLOR_WARNING
            )
            lbl_date.pack(side="right")

            sep = ctk.CTkFrame(self.scroll_fin, height=1, fg_color=("#F1F5F9", "#334155"))
            sep.pack(fill="x", padx=5)


class SearchFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent, fg_color="transparent")
        self.controller = controller

        # Grid config
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Título superior
        self.title_label = ctk.CTkLabel(
            self, 
            text="🔍 Buscador de Fichas", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=("#1E293B", "#F8FAFC")
        )
        self.title_label.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Panel de Filtros
        self.filters_panel = ctk.CTkFrame(
            self, 
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.filters_panel.grid(row=1, column=0, sticky="ew", pady=(0, 15), padx=2)
        
        # Configurar grid de filtros
        for i in range(5):
            self.filters_panel.grid_columnconfigure(i, weight=1)

        # Input de Búsqueda
        self.lbl_query = ctk.CTkLabel(self.filters_panel, text="Buscar ficha/programa/instructor:", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_query.grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
        
        self.entry_query = ctk.CTkEntry(self.filters_panel, placeholder_text="Ej: Oscar Yanguas, 2995479...")
        self.entry_query.grid(row=1, column=0, padx=10, pady=(0, 15), sticky="ew")
        self.entry_query.bind("<KeyRelease>", lambda e: self.realizar_busqueda())

        # Combobox Municipio
        opciones = self.controller.procesador.obtener_opciones_filtros()
        
        self.lbl_muni = ctk.CTkLabel(self.filters_panel, text="Municipio:", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_muni.grid(row=0, column=1, padx=10, pady=(10, 2), sticky="w")
        
        self.combo_muni = ctk.CTkOptionMenu(
            self.filters_panel, 
            values=opciones["municipios"], 
            command=lambda x: self.realizar_busqueda(),
            fg_color=("#F1F5F9", "#1E293B"),
            button_color=("#CBD5E1", "#334155"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.combo_muni.grid(row=1, column=1, padx=10, pady=(0, 15), sticky="ew")

        # Combobox Red
        self.lbl_red = ctk.CTkLabel(self.filters_panel, text="Red de Conocimiento:", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_red.grid(row=0, column=2, padx=10, pady=(10, 2), sticky="w")
        
        # Acortar textos largos en la lista de opciones para que el menú no se estire demasiado
        self.combo_red = ctk.CTkOptionMenu(
            self.filters_panel, 
            values=opciones["redes"], 
            command=lambda x: self.realizar_busqueda(),
            fg_color=("#F1F5F9", "#1E293B"),
            button_color=("#CBD5E1", "#334155"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.combo_red.grid(row=1, column=2, padx=10, pady=(0, 15), sticky="ew")

        # Combobox Nivel
        self.lbl_nivel = ctk.CTkLabel(self.filters_panel, text="Nivel:", font=ctk.CTkFont(size=11, weight="bold"))
        self.lbl_nivel.grid(row=0, column=3, padx=10, pady=(10, 2), sticky="w")
        
        self.combo_nivel = ctk.CTkOptionMenu(
            self.filters_panel, 
            values=opciones["niveles"], 
            command=lambda x: self.realizar_busqueda(),
            fg_color=("#F1F5F9", "#1E293B"),
            button_color=("#CBD5E1", "#334155"),
            text_color=("#0F172A", "#F8FAFC")
        )
        self.combo_nivel.grid(row=1, column=3, padx=10, pady=(0, 15), sticky="ew")

        # Botón de reinicio
        self.btn_reset = ctk.CTkButton(
            self.filters_panel,
            text="Limpiar Filtros",
            fg_color=("#E2E8F0", "#334155"),
            text_color=("#0F172A", "#F8FAFC"),
            hover_color=("#CBD5E1", "#475569"),
            command=self.reset_filtros
        )
        self.btn_reset.grid(row=1, column=4, padx=10, pady=(0, 15), sticky="ew")

        # Resultados Panel
        self.results_panel = ctk.CTkFrame(
            self, 
            fg_color=("#FFFFFF", "#1E293B"),
            border_width=1,
            border_color=("#E2E8F0", "#334155")
        )
        self.results_panel.grid(row=2, column=0, sticky="nsew", padx=2)
        self.results_panel.grid_rowconfigure(1, weight=1)
        self.results_panel.grid_columnconfigure(0, weight=1)

        # Header de la tabla
        self.header_frame = ctk.CTkFrame(self.results_panel, fg_color=("#F1F5F9", "#0B132B"), height=35, corner_radius=0)
        self.header_frame.grid(row=0, column=0, sticky="ew")
        
        lbl_h_ficha = ctk.CTkLabel(self.header_frame, text="FICHA", font=ctk.CTkFont(weight="bold", size=11), width=90, anchor="w")
        lbl_h_ficha.pack(side="left", padx=(15, 10))
        
        lbl_h_prog = ctk.CTkLabel(self.header_frame, text="PROGRAMA DE FORMACIÓN", font=ctk.CTkFont(weight="bold", size=11), anchor="w")
        lbl_h_prog.pack(side="left", fill="x", expand=True, padx=10)
        
        lbl_h_muni = ctk.CTkLabel(self.header_frame, text="MUNICIPIO", font=ctk.CTkFont(weight="bold", size=11), width=120, anchor="w")
        lbl_h_muni.pack(side="left", padx=10)

        lbl_h_apr = ctk.CTkLabel(self.header_frame, text="APR.", font=ctk.CTkFont(weight="bold", size=11), width=45, anchor="center")
        lbl_h_apr.pack(side="left", padx=10)
        
        lbl_h_inst = ctk.CTkLabel(self.header_frame, text="INSTRUCTOR 2026", font=ctk.CTkFont(weight="bold", size=11), width=180, anchor="w")
        lbl_h_inst.pack(side="left", padx=(10, 15))

        # Contenedor Scrollable para filas de datos
        self.scroll_results = ctk.CTkScrollableFrame(self.results_panel, fg_color="transparent", corner_radius=0)
        self.scroll_results.grid(row=1, column=0, sticky="nsew")

        # Mensaje de sin resultados
        self.no_results_lbl = ctk.CTkLabel(
            self.results_panel, 
            text="Ingresa filtros o búsqueda para ver las formaciones.",
            font=ctk.CTkFont(size=14, slant="italic"),
            text_color="#94A3B8"
        )
        self.no_results_lbl.grid(row=1, column=0)

        # Cargar tabla inicialmente
        self.realizar_busqueda()

    def reset_filtros(self):
        self.entry_query.delete(0, tk.END)
        self.combo_muni.set("Todos")
        self.combo_red.set("Todas")
        self.combo_nivel.set("Todos")
        self.realizar_busqueda()

    def realizar_busqueda(self):
        q = self.entry_query.get()
        m = self.combo_muni.get()
        r = self.combo_red.get()
        n = self.combo_nivel.get()

        fichas_filtradas = self.controller.procesador.buscar_fichas(q, m, r, n)

        # Limpiar tabla
        for widget in self.scroll_results.winfo_children():
            widget.destroy()

        if not fichas_filtradas:
            self.no_results_lbl.configure(text="No se encontraron formaciones con los filtros ingresados.")
            self.no_results_lbl.grid()
        else:
            self.no_results_lbl.grid_forget()
            
            # Dibujar filas
            for idx, f in enumerate(fichas_filtradas):
                # Color alterno de fila para mayor legibilidad
                bg_row = ("#FFFFFF", "#1E293B") if idx % 2 == 0 else ("#F8FAFC", "#1E293B")
                
                row_frame = ctk.CTkFrame(self.scroll_results, fg_color=bg_row, height=38, corner_radius=4, cursor="hand2")
                row_frame.pack(fill="x", pady=2, padx=5)
                
                # Ficha
                lbl_ficha = ctk.CTkLabel(row_frame, text=f.get("FICHA"), font=ctk.CTkFont(weight="bold"), width=90, anchor="w", text_color=COLOR_AZUL_REY_DARK)
                lbl_ficha.pack(side="left", padx=(10, 10), pady=6)
                
                # Programa
                prog_txt = f.get("NOMBRE DEL PROGRAMA") or "N/A"
                if len(prog_txt) > 55:
                    prog_txt = prog_txt[:52] + "..."
                lbl_prog = ctk.CTkLabel(row_frame, text=prog_txt.title(), font=ctk.CTkFont(size=12), anchor="w")
                lbl_prog.pack(side="left", fill="x", expand=True, padx=10)
                
                # Municipio
                lbl_muni = ctk.CTkLabel(row_frame, text=(f.get("MUNICIPIO") or "N/A").title(), font=ctk.CTkFont(size=11), width=120, anchor="w")
                lbl_muni.pack(side="left", padx=10)

                # Aprendices
                lbl_apr = ctk.CTkLabel(row_frame, text=f.get("APRENDICES MATRICULADOS"), font=ctk.CTkFont(size=11, weight="bold"), width=45, anchor="center")
                lbl_apr.pack(side="left", padx=10)
                
                # Instructor 2026
                inst_txt = f.get("INSTRUCTOR TÉCNICO 2026") or f.get("INSTRUCTOR TÉCNICO 2025") or "SIN ASIGNAR"
                if inst_txt == "None":
                    inst_txt = "SIN ASIGNAR"
                lbl_inst = ctk.CTkLabel(row_frame, text=inst_txt.title(), font=ctk.CTkFont(size=11), width=180, anchor="w")
                lbl_inst.pack(side="left", padx=(10, 10))

                # Vincular evento click en toda la fila para ver detalles
                for child in row_frame.winfo_children():
                    child.bind("<Button-1>", lambda e, info=f: self.controller.mostrar_detalle_ficha(info))
                row_frame.bind("<Button-1>", lambda e, info=f: self.controller.mostrar_detalle_ficha(info))


class DetailWindow(ctk.CTkToplevel):
    def __init__(self, parent, info):
        super().__init__(parent)
        
        self.title(f"Detalle de Ficha: {info.get('FICHA')}")
        self.geometry("680x560")
        self.resizable(False, False)
        
        # Color azul rey oscuro en encabezado
        self.header_panel = ctk.CTkFrame(self, fg_color=COLOR_AZUL_REY_SOPORTE, corner_radius=0, height=80)
        self.header_panel.pack(fill="x", side="top")
        
        lbl_head = ctk.CTkLabel(
            self.header_panel, 
            text=f"FICHA {info.get('FICHA')}", 
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color="#FFFFFF"
        )
        lbl_head.pack(anchor="w", padx=25, pady=(15, 2))
        
        lbl_sub = ctk.CTkLabel(
            self.header_panel, 
            text=f"Red de Conocimiento: {info.get('RED DE CONOCIMIENTO')}", 
            font=ctk.CTkFont(size=12), 
            text_color="#CBD5E1"
        )
        lbl_sub.pack(anchor="w", padx=25, pady=(0, 15))
        
        # Contenedor del formulario/detalles
        self.body_panel = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.body_panel.pack(fill="both", expand=True, padx=20, pady=15)
        
        # Mapear campos a mostrar en dos secciones
        secciones = [
            ("INFORMACIÓN DEL PROGRAMA", [
                ("Nombre del Programa", info.get("NOMBRE DEL PROGRAMA"), "text"),
                ("Código del Programa", info.get("CODIGO DE PROGRAMA"), "text"),
                ("Versión", info.get("VERSION"), "text"),
                ("Nivel de Formación", info.get("NIVEL"), "text"),
                ("Duración Estimada", f"{info.get('DURACION_CALCULADA')} meses", "accent"),
                ("Código de Proyecto", info.get("CÓDIGO PROYECTO"), "text"),
            ]),
            ("PLANIFICACIÓN Y LOGÍSTICA", [
                ("Municipio", info.get("MUNICIPIO"), "text"),
                ("Horario de Formación", info.get("HORARIO"), "text"),
                ("Ambiente de Formación", info.get("AMBIENTE"), "text"),
                ("Tipo de Oferta", info.get("TIPO DE OFERTA"), "text"),
                ("Aprendices Matriculados", info.get("APRENDICES MATRICULADOS"), "success"),
            ]),
            ("CALENDARIO Y ETAPAS", [
                ("Año/Trimestre Inicio", info.get("AÑO /TRIMESTRE DE INICIO"), "text"),
                ("Fecha de Inicio", info.get("FECHA INICIO"), "text"),
                ("Fin Etapa Lectiva", info.get("FECHA FINAL ETAPA LECTIVA"), "text"),
                ("Fecha de Terminación", info.get("FECHA TERMINACION"), "warning"),
            ]),
            ("ASIGNACIÓN Y APOYOS", [
                ("Instructor Técnico 2025", info.get("INSTRUCTOR TÉCNICO 2025"), "text"),
                ("Instructor Técnico 2026", info.get("INSTRUCTOR TÉCNICO 2026"), "text"),
                ("Apoyo Técnico Inglés", info.get("APOYO TÉCNICO INGLES"), "warning"),
                ("Apoyo Transversales", info.get("TRANSVERSALES") or "Ninguno registrado", "text"),
            ])
        ]
        
        for sec_name, campos in secciones:
            # Título de Sección
            sec_lbl = ctk.CTkLabel(
                self.body_panel, 
                text=sec_name, 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color=COLOR_AZUL_REY_DARK
            )
            sec_lbl.pack(anchor="w", pady=(15, 5))
            
            # Tarjeta de la sección
            sec_card = ctk.CTkFrame(
                self.body_panel, 
                fg_color=("#FFFFFF", "#1E293B"), 
                border_width=1,
                border_color=("#E2E8F0", "#334155")
            )
            sec_card.pack(fill="x", pady=(0, 5))
            
            # Agregar campos dentro de la tarjeta
            for name, val, val_type in campos:
                row_f = ctk.CTkFrame(sec_card, fg_color="transparent")
                row_f.pack(fill="x", padx=15, pady=6)
                
                lbl_n = ctk.CTkLabel(row_f, text=f"{name}:", font=ctk.CTkFont(size=11, weight="bold"), width=160, anchor="w", text_color=("#64748B", "#94A3B8"))
                lbl_n.pack(side="left")
                
                txt_color = ("#0F172A", "#F8FAFC")
                if val_type == "success":
                    txt_color = COLOR_SUCCESS
                elif val_type == "warning":
                    txt_color = COLOR_WARNING
                elif val_type == "accent":
                    txt_color = COLOR_ACCENT
                    
                val_str = str(val) if val is not None else "N/A"
                if val_str == "None" or val_str == "":
                    val_str = "N/A"
                    
                lbl_v = ctk.CTkLabel(
                    row_f, 
                    text=val_str.upper(), 
                    font=ctk.CTkFont(size=11, weight="bold" if val_type != "text" else "normal"),
                    text_color=txt_color, 
                    anchor="w",
                    wraplength=400,
                    justify="left"
                )
                lbl_v.pack(side="left", fill="x", expand=True)
                
                # Separador interno
                sep = ctk.CTkFrame(sec_card, height=1, fg_color=("#F1F5F9", "#334155"))
                sep.pack(fill="x", padx=10)

        # Botón Cerrar en el pie de la ventana
        btn_close = ctk.CTkButton(
            self, 
            text="Cerrar Detalles", 
            fg_color=COLOR_AZUL_REY_SOPORTE, 
            hover_color=COLOR_AZUL_REY_LIGHT,
            command=self.destroy
        )
        btn_close.pack(pady=15)


if __name__ == "__main__":
    app = App()
    app.mainloop()