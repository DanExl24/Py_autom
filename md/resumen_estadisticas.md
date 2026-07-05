# Consolidado de Estadísticas e Indicadores del Sistema

Este documento resume todos los indicadores, métricas, gráficos y alertas que se encuentran implementados y activos en el **Sistema de Gestión de Formaciones SENA (Caquetá 2026)**, organizados por sus respectivos módulos en la interfaz web y backend.

---

## 📊 1. Módulo: Dashboard Principal

Diseñado para proporcionar una vista ejecutiva e inmediata del estado general de la cobertura educativa.

### A. Indicadores Clave de Rendimiento (8 KPIs principales)

- **Total de Fichas:** Conteo absoluto de fichas de formación activas en la base de datos.
- **Total de Aprendices:** Suma acumulada de aprendices matriculados en todas las formaciones.
- **Total de Instructores:** Conteo de instructores técnicos únicos asignados a las etapas 2025 y 2026.
- **Redes de Conocimiento:** Cantidad de redes de conocimiento del SENA representadas en la oferta.
- **Municipios Cubiertos:** Cantidad de municipios del departamento de Caquetá con presencia de formación activa.
- **Promedio por Ficha:** Tamaño promedio del grupo (Ocupación = Total Aprendices / Total Fichas).
- **Próximo Inicio:** Fecha del inicio de formación más cercano (en adelante).
- **Próxima Finalización:** Fecha del cierre lectivo o terminación de ficha más cercano.

### B. Bandeja de Alertas Críticas (Notificaciones automatizadas)

- **Alerta de Baja Matrícula:** Conteo de fichas con matrícula inferior a 15 alumnos (umbral de alerta administrativa).
- **Alerta de Plazos Lectivos:** Conteo de fichas cuya fecha de terminación se encuentra a menos de 30 días del día actual.
- **Alerta de Asignación de Proyectos:** Conteo de fichas activas que no tienen un código de proyecto asociado (CÓDIGO PROYECTO = 0 o vacío).

### C. Visualizaciones Gráficas (6 Gráficos interactivos en Chart.js)

1.  **Aprendices por Red:** Gráfico de barras horizontales que representa las 5 redes principales y agrupa el resto en "Otras Redes".
2.  **Distribución de Oferta:** Gráfico de dona que muestra la proporción entre oferta **Abierta** vs. **Cerrada**.
3.  **Nivel de Formación:** Gráfico de dona indicando la distribución por niveles de estudio (**Tecnólogo** vs. **Técnico**).
4.  **Top 10 Programas:** Gráfico de barras horizontales que lista los programas de formación con mayor volumen de matrícula.
5.  **Ranking de Municipios:** Gráfico de barras verticales ordenado por cantidad de fichas activas en cada cabecera.
6.  **Timeline de Aperturas:** Gráfico de líneas que muestra cronológicamente el número de formaciones que inician mes a mes.

---

## 📈 2. Módulo: Estadísticas Avanzadas (Rankings y Detalle)

Ubicado en la segunda pestaña del sidebar, divide la analítica en sub-menús horizontales especializados.

### Sub-pestaña A: Programas

- **Programas con Más Aprendices:** Tabla con el listado completo y volumen acumulado de matrícula.
- **Programas con Más Fichas:** Tabla ordenada según cantidad de fichas del mismo programa.
- **Programas con Múltiples Versiones:** Identifica y muestra qué programas de formación tienen más de una versión activa en la base de datos (por ejemplo, Diseño v1 y Diseño v2).

### Sub-pestaña B: Aprendices

- **Matrícula por Red de Conocimiento:** Resumen tabular del total de aprendices por cada red técnica.
- **Matrícula por Municipio:** Desglose del total de alumnos por localización física.
- **Fichas con Baja Matrícula:** Listado interactivo de fichas con menos de 15 alumnos, mostrando su código, programa, matrícula real e instructor asignado (con clic para abrir ficha técnica).

### Sub-pestaña C: Instructores

- **Instructores con Más Aprendices:** Ranking de los 10 instructores con mayor volumen de alumnos bajo su tutoría.
- **Mayor Variedad de Programas por Instructor:** Identifica a los instructores con mayor diversidad curricular (cantidad de programas diferentes que dictan).
- **Instructores Nuevos 2026:** Detección automática de instructores que dictan formación en 2026 pero no registraban fichas en 2025.
- **Instructores Salientes:** Detección de instructores presentes en 2025 que ya no registran asignación en la etapa 2026.

### Sub-pestaña D: Fechas y Plazos

- **Formaciones que Inician este Mes:** Listado dinámico de fichas que inician etapa lectiva en el mes en curso.
- **Formaciones que Finalizan este Mes:** Listado dinámico de fichas que terminan etapa lectiva en el mes en curso.

### Sub-pestaña E: Municipios y Oferta

- **Municipios con un Solo Programa:** Lista de municipios con oferta crítica (únicamente 1 programa de formación activo).
- **Resumen de Cobertura:** Relación del número de sub-sedes activas impactadas por la sede principal (Florencia).

### Sub-pestaña F: Proyectos y Ambientes

- **Proyectos con Más Fichas:** Códigos de proyecto del SENA que absorben la mayor cantidad de fichas y aprendices.
- **Ambientes Multificha (Compartidos):** Identificación de aulas, talleres o laboratorios donde coexisten 2 o más fichas activas (útil para la planeación logística).

### Sub-pestaña G: Indicadores Pro

- **Densidad Aprendiz/Instructor:** Promedio de aprendices asignados por cada instructor único del centro.
- **Municipio Mayor Variedad:** Identifica el municipio no-sede con mayor diversidad de oferta académica.
- **Tamaño Promedio de Ficha:** Ocupación promedio general de estudiantes por grupo.

### Sub-pestaña H: Años-Trimestres

- Formaciones que empiezan en un semestre y un año en especifico: ejemplo
  T-III-2024
  T-I-2025
  T- II-2025
  T- II-2025
  T- II-2025
  T-III 2025
  T-III 2025
  T-IV 2025
  T-IV 2025

---

## 🔍 3. Módulo: Buscador Avanzado e Inteligente

Permite la filtración cruzada y búsqueda libre de las fichas con KPIs dinámicos contextuales.

### A. Filtros Cruzados

- **Buscador Texto Libre:** Filtra instantáneamente por número de ficha, nombre o código del programa, nombre del instructor, municipio o ambiente.
- **Filtros de Selección:** Listas desplegables autocompletadas dinámicamente para **Municipio**, **Red de Conocimiento** y **Nivel de Formación**.

### B. KPIs Auto-adaptativos (Se calculan en tiempo real sobre el filtro)

- **Fichas Filtradas:** Cantidad de formaciones que coinciden con los filtros activos.
- **Aprendices Filtrados:** Total de matrículas que suman las fichas del filtro.
- **Promedio Ficha:** Tamaño promedio de grupo del filtro activo.
- **Instructores Activos:** Cantidad de instructores únicos asignados al grupo filtrado.

---

## 🔄 4. Módulo: Sincronización y Validación de Datos

Módulo de control de base de datos para subir actualizaciones de Excel.

- **Validador de Columnas:** Muestra el número de columnas identificadas en el mapeo (ej. 24 columnas).
- **Validador de Registros:** Conteo total de filas leídas y sanitizadas desde la hoja `PASAN 2026`.
- **Checker de Actualización:** Muestra cuántos programas e instructores nuevos ingresaron a la base de datos tras la sincronización.

---

## 📑 5. Módulo: Reportes y Exportación

Módulo de salidas y reportabilidad de la información del centro.

- **Exportar CSV:** Descarga la base completa estructurada (compatible con Excel con codificación UTF-8 BOM).
- **Exportar JSON:** Descarga la base limpia de datos estructurados para desarrollo o integraciones.
- **Imprimir / PDF:** Estilos de impresión integrados (`@media print`) que eliminan barras laterales y menús del navegador, adaptando el dashboard general y la tabla a una estructura de reporte físico apta para guardar como PDF.
