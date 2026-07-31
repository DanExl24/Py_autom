# Consolidado General de Estadísticas, Módulos, Filtros e Indicadores del Sistema

Este documento es la **guía maestra consolidada** del **Sistema de Gestión de Formaciones SENA (Caquetá 2026)**. Resume y detalla técnicamente todos los módulos, la arquitectura de datos, los algoritmos de inferencia, indicadores clave (KPIs), alertas automáticas, gráficos interactivos, filtros de búsqueda, vistas de detalle y opciones de exportación del sistema.

---

## 💾 1. Arquitectura y Mini Base de Datos (`fichas.json`)

La mini base de datos está almacenada en `output/fichas.json` (con fallback a `fichas_test.json`). Posee una estructura jerárquica indexada por **Red de Conocimiento** $\rightarrow$ **Número de Ficha**:

```json
{
  "INFORMATICA, DISEÑO Y DESARROLLO DE SOFTWARE": {
    "2995479": {
      "RED DE CONOCIMIENTO": "INFORMATICA, DISEÑO Y DESARROLLO DE SOFTWARE",
      "NIVEL": "TECNÓLOGO",
      "NOMBRE DEL PROGRAMA": "ANALISIS Y DESARROLLO DE SOFTWARE",
      "CODIGO DE PROGRAMA": 228118,
      "VERSION": 1,
      "FICHA": 2995479,
      "APRENDICES MATRICULADOS": 23,
      "TIPO DE OFERTA": "ABIERTA",
      "CÓDIGO PROYECTO": 2480542,
      "MUNICIPIO": "FLORENCIA",
      "HORARIO": "LUNES A SABADO 6:00 AM - 14:00 PM",
      "AMBIENTE": 202,
      "DURACION": null,
      "AÑO /TRIMESTRE DE INICIO": "T-III-2024",
      "FECHA INICIO": "2024-07-08",
      "FECHA FINAL ETAPA LECTIVA": "2026-04-11",
      "FECHA TERMINACION": "2026-10-07",
      "INSTRUCTOR TÉCNICO 2025": "OSCAR YANGUAS",
      "INSTRUCTOR TÉCNICO 2026": "YUDY CONSTANZA GARCIA",
      "APOYO TÉCNICO INGLES": "SE REQUIERE AMPLIAR",
      "TRANSVERSALES": null
    }
  }
}
```

### Esquema del Modelo `Ficha` (TypeScript interface)

| Campo | Tipo | Descripción |
| :--- | :--- | :--- |
| `RED DE CONOCIMIENTO` | `string` | Red académica asignada (ej. Informática, Agropecuaria, etc.) |
| `FICHA` | `string` | Identificador único de la ficha de formación |
| `NOMBRE DEL PROGRAMA` | `string` | Nombre del programa académico |
| `CODIGO DE PROGRAMA` | `number` | Código oficial de la titulación |
| `VERSION` | `number` | Versión del diseño curricular |
| `NIVEL` | `string` | Nivel educativo (`TECNÓLOGO`, `TÉCNICO`, `OPERARIO`, etc.) |
| `APRENDICES MATRICULADOS`| `number` | Cantidad total de aprendices activos |
| `TIPO DE OFERTA` | `string` | Tipo de oferta (`ABIERTA`, `ABIERTA DE FORMACION`, `ESPECIAL`) |
| `CÓDIGO PROYECTO` | `number` | Código del proyecto formativo |
| `MUNICIPIO` | `string` | Municipio donde se imparte (ej. `FLORENCIA`, `VALPARAISO`) |
| `HORARIO` | `string` | Registro en texto plano del horario asignado |
| `AMBIENTE` | `string \| number` | Salón, taller o ambiente de formación |
| `DURACION` | `number \| null` | Duración formal registrada en meses |
| `DURACION_CALCULADA` | `number` | Duración calculada en meses entre `FECHA INICIO` y `FECHA TERMINACION` |
| `AÑO /TRIMESTRE DE INICIO`| `string` | Identificador del trimestre inicial (`T-I-2025`, `T-III-2024`) |
| `FECHA INICIO` | `string` | Fecha de inicio lectivo (`YYYY-MM-DD`) |
| `FECHA FINAL ETAPA LECTIVA`| `string` | Fecha estimada de cierre lectivo |
| `FECHA TERMINACION` | `string` | Fecha de terminación de la ficha |
| `INSTRUCTOR TÉCNICO 2025`| `string \| null` | Nombre del instructor técnico asignado en 2025 |
| `INSTRUCTOR TÉCNICO 2026`| `string \| null` | Nombre del instructor técnico asignado en 2026 |
| `APOYO TÉCNICO INGLES` | `string \| null` | Estado u observaciones del instructor de Inglés |
| `TRANSVERSALES` | `string \| null` | Estado u observaciones de instructores transversales |

---

## ⚙️ 2. Algoritmo de Inferencia de Jornadas y Horarios Compuestos (`horario.ts`)

La jornada de cada ficha se infiere automáticamente aplicando la siguiente jerarquía de reglas:

1. **Horarios Compuestos (Especiales)**:
   - Se evalúa si el texto incluye múltiples rangos horarios (ej. `14:00 A 22:00` y `07:00 A 12:00`), palabras como `" Y "`, saltos de línea o varios bloques de días distintos (ej. `"MIERCOLES A VIERNES 14:00 A 22:00 SÁBADO 07:00 A 12:00"`).
   - **Resultado**: `"Horario Compuesto"`.

2. **Palabras Clave Explícitas**:
   - `MAÑANA` o `DIURNA` $\rightarrow$ `"Mañana"`
   - `TARDE` $\rightarrow$ `"Tarde"`
   - `MIXTA` $\rightarrow$ `"Mixta"`
   - `NOCHE` o `NOCTURNA` $\rightarrow$ `"Noche"`

3. **Inferencia por Rango de Horas Numéricas**:
   Extrae la hora de inicio y fin (convertidas a formato 24h):
   - **Mañana**: 06:00 - 14:00 (Hora inicio $\ge$ 06:00 y Hora fin $\le$ 14:00)
   - **Tarde**: 12:00 - 20:00 (Hora inicio $\ge$ 12:00 y Hora fin $\le$ 20:00)
   - **Mixta**: 16:00 - 23:59 (Hora inicio entre 16:00 y 17:59)
   - **Noche**: 18:00 - 23:59 (Hora inicio $\ge$ 18:00)
   - **Fallback**: En caso de rangos no estándar, se clasifica por la hora de inicio (06:00-11:59 Mañana, 12:00-15:59 Tarde, 16:00-17:59 Mixta, $\ge$18:00 Noche).

---

## 📊 3. Módulo 1: Dashboard Principal

Proporciona una vista ejecutiva del estado general del centro de formación.

### A. Indicadores Clave (8 KPIs Principales)

- **Total Formaciones:** Conteo total de fichas activas ($N$).
- **Total Aprendices:** Suma total de aprendices matriculados ($\sum \text{Aprendices}$).
- **Total Instructores:** Cantidad de instructores únicos asignados en 2025/2026.
- **Redes de Conocimiento:** Número de redes de conocimiento con oferta activa.
- **Municipios Cubiertos:** Número de municipios con formaciones en desarrollo.
- **Promedio por Ficha:** Ocupación media por grupo ($\frac{\text{Total Aprendices}}{\text{Total Formaciones}}$).
- **Promedio Duración:** Duración media en meses ($\frac{\sum \text{DURACION\_CALCULADA}}{N}$).
- **Próximo Inicio / Terminación:** Próximos hitos del calendario.

### B. Bandeja de Alertas Críticas (Automatizadas)

- ⚠️ **Alerta de Baja Matrícula:** Fichas con menos de 15 aprendices (umbral crítico administrativo).
- ⏱️ **Alerta de Plazos Lectivos:** Fichas con terminación a menos de 30 días del día actual.
- 📁 **Alerta de Asignación de Proyectos:** Fichas activas sin código de proyecto asignado (`CÓDIGO PROYECTO` = 0 o nulo).

### C. Visualizaciones Gráficas Interactivas

1. **Aprendices por Red:** Barras horizontales con las 5 redes con más aprendices y agrupación de restantes.
2. **Distribución de Oferta:** Gráfico de dona (Oferta Abierta vs. Oferta Especial/Cerrada).
3. **Nivel de Formación:** Gráfico de dona (Tecnólogo vs. Técnico).
4. **Top 10 Programas:** Barras horizontales con los programas de mayor volumen.
5. **Ranking de Municipios:** Barras verticales por municipio.
6. **Timeline de Aperturas:** Gráfico de líneas que muestra aperturas mes a mes.

---

## 🔍 4. Módulo 2: Buscador Avanzado e Inteligente (`BuscadorFichas.vue`)

Permite búsquedas cruzadas y filtración contextual instantánea.

### Filtros Disponibles

1. **Texto Libre (`query`)**: Busca en Ficha, Programa, Código Programa, Código Proyecto, Instructores, Municipio, Ambiente, Horario y Jornada.
2. **Jornada**: `Todas`, `Mañana`, `Tarde`, `Mixta`, `Noche`, `Horario Compuesto`, `Sin especificar`.
3. **Horario Específico**: Dropdown con todos los horarios únicos ordenados.
4. **Municipio**: Selecciona municipio específico.
5. **Red de Conocimiento**: Selecciona red específica.
6. **Nivel**: Selecciona nivel específico (`TECNÓLOGO`, `TÉCNICO`, etc.).
7. **Año/Trimestre de Inicio**: Dropdown ordenado cronológicamente (`T-I-2024`, `T-I-2025`, etc.).
8. **Rango de Fechas**:
   - `Inicio Desde` (`FECHA INICIO` $\ge$ fecha elegida)
   - `Terminación Hasta` (`FECHA TERMINACION` $\le$ fecha elegida)

### KPIs Auto-Adaptativos del Buscador
Se recalculan automáticamente sobre los resultados filtrados:
- **Fichas Filtradas**
- **Aprendices Filtrados**
- **Promedio Ficha Filtrada**
- **Instructores Activos Filtrados**

### Panel Desplegable: Horarios Más Repetidos
Agrupa y lista los horarios más frecuentes con la cantidad de fichas, aprendices acumulados y botón directo para abrir el `QuickDetailModal`.

---

## 📈 5. Módulo 3: Estadísticas Avanzadas y Rankings Especializados (`EstadisticasDetalle.vue`)

Organizado en 9 subpestañas especializadas.

> 🔒 **Filtro Exclusivo de Horarios**: En la parte superior de este módulo existe un panel de filtros (**Jornada, Horario Completo y Rango de Fechas**) que **únicamente se muestra cuando la pestaña "Horarios" está seleccionada**, manteniéndose oculto en el resto de vistas.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                 ESTADÍSTICAS Y RANKINGS ESPECIALIZADOS                      │
├──────────┬───────────┬────────────┬──────────────┬───────────┬──────────────┤
│ Horarios │ Programas │ Aprendices │ Instructores │ Fechas... │     ...      │
└──────────┴───────────┴────────────┴──────────────┴───────────┴──────────────┘
```

### Detalle de las 9 Subpestañas de Estadísticas

#### 1. 🕒 Horarios
- **Resumen por Jornada**: 6 Tarjetas con conteo de fichas y aprendices en: *Mañana, Tarde, Mixta, Noche, Horario Compuesto y Sin Especificar*.
- **Ranking de Horarios Frecuentes**: Ránking completo ordenado por número de fichas con aprendices acumulados y botón "Ver Fichas".

#### 2. 📖 Programas
- **Programas con Más Aprendices**: Top 10 programas con mayor cantidad de estudiantes.
- **Programas con Más Fichas**: Top 10 programas con mayor número de fichas.
- **Programas con Múltiples Versiones**: Identifica programas con más de una versión activa en simultáneo (ej. `v1, v2`).

#### 3. 🎓 Aprendices
- **Matrícula por Red de Conocimiento**: Matrícula total agrupada por Red.
- **Matrícula por Municipio**: Matrícula total agrupada por Municipio.
- **Fichas con Baja Matrícula**: Listado interactivo de fichas con menos de 15 aprendices.

#### 4. 👥 Instructores
- **Instructores con Más Aprendices**: Ranking Top 10 de instructores por volumen de alumnos a cargo.
- **Mayor Variedad de Programas**: Instructores con mayor diversidad curricular (imparten más programas distintos).
- **Instructores Nuevos en 2026**: Instructores que imparten en 2026 pero no tenían fichas en 2025.
- **Instructores Salientes**: Instructores de 2025 que no tienen asignación en 2026.

#### 5. 📅 Fechas y Plazos
- **Formaciones que Inician este Mes**: Fichas cuyo inicio coincide con el mes actual.
- **Formaciones que Finalizan este Mes**: Fichas cuya terminación coincide con el mes actual.

#### 6. 📍 Municipios y Oferta
- **Municipios con un Solo Programa**: Identifica municipios con oferta limitada (1 solo programa activo).
- **Identificación de Cobertura**: Relación entre la sede principal (Florencia) y las sub-sedes impactadas.

#### 7. 📑 Proyectos y Ambientes
- **Proyectos con Más Fichas**: Códigos de proyecto del SENA que concentran la mayor cantidad de fichas y aprendices.
- **Ambientes Multificha (Compartidos)**: Ambientes pedagógicos asignados a 2 o más fichas activas en simultáneo.

#### 8. ⚡ Indicadores Pro
- **Densidad Aprendices / Instructor**: $\frac{\text{Total Aprendices}}{\text{Instructores Únicos}}$.
- **Municipio Mayor Variedad**: Municipio no-sede con mayor número de programas únicos.
- **Tamaño Promedio de Ficha**: Ocupación media de aprendices por grupo.

#### 9. 🗓️ Años-Trimestres
- **Distribución por Trimestres**: Conteo de fichas y aprendices por cada trimestre de inicio (`T-I-2024`, `T-III-2024`, `T-I-2025`, etc.).
- **Desglose Tabular**: Al hacer clic en un trimestre, despliega la tabla detallada de todas sus formaciones.

---

## 🪟 6. Módulo 4: Modal de Vista Rápida de Registros (`QuickDetailModal.vue`)

Al hacer clic sobre cualquier tarjeta, fila o elemento interactivo en las vistas de estadísticas, se abre una ventana modal flotante que permite a los funcionarios inspeccionar el registro a profundidad.

### Características del Modal
1. **Encabezado Contextual**: Indica el título y subtítulo del registro seleccionado (ej. *"Programa: ANÁLISIS Y DESARROLLO DE SOFTWARE"*, *"Horario: LUNES A SABADO 06:00 - 14:00"*, *"Instructor: OSCAR YANGUAS"*).
2. **Métricas de Resumen**: Muestra el total de fichas enlazadas, el total de aprendices y métricas específicas.
3. **Buscador Interno**: Permite realizar búsquedas por texto dentro de las fichas del modal.
4. **Filtro de Jornada**: Selector para filtrar las fichas del modal por su jornada inferida.
5. **Tarjetas de Fichas Enlazadas**: Lista interactiva con número de ficha, programa, municipio, horario, instructor y aprendices. Incluye botón para abrir el **Programador en Google Drive** (`/api/abrir-programador/{ficha}`) y opción para abrir la **Ficha Técnica** completa.

---

## 🔄 7. Módulo 5: Sincronización, Reportes y Exportación

### Sincronización y Validación (`SincronizarExcel.vue`)
- **Streaming de Sincronización**: Llama a `/api/actualizar` para re-ejecutar `antiguo_lector.py` en segundo plano con logs en tiempo real.
- **Validación de Columnas y Registros**: Sanitización de nombres de cabecera, fechas ISO, números enteros y limpieza de nulos (`None`/`nan`).

### Exportación y Reportes
- **Exportar CSV**: Genera archivo CSV estructurado con codificación UTF-8 BOM.
- **Exportar JSON**: Descarga la base estructurada completa de fichas.
- **Imprimir / Guardar en PDF**: Reglas CSS `@media print` que formatean las vistas y tablas eliminando barras de navegación para generar reportes oficiales en PDF.

---

## 🌐 8. Endpoints de la API Backend (`main.py`)

| Método | Endpoint | Descripción |
| :--- | :--- | :--- |
| `GET` | `/api/fichas` | Retorna la base de datos completa JSON (`output/fichas.json`) |
| `POST`| `/api/actualizar` | Ejecuta la re-lectura del Excel en caliente vía `StreamingResponse` |
| `GET` | `/api/abrir-programador/{ficha}` | Retorna la URL oficial del programador en Google Drive mediante `constructor.py` |
| `POST`| `/api/abrir-buscador-gui` | Inicia la interfaz GUI de escritorio nativa en Python (`buscador_fichas.py`) |
