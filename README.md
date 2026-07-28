# Py_autom - Automatizaciones de Fichas SENA

Este proyecto consiste en un sistema de consulta, visualización y estadísticas de fichas formativas del SENA extraídas dinámicamente desde archivos Excel de Google Drive.

El sistema se compone de:

1. **Backend (API)**: Construido con FastAPI para el procesamiento de datos y la comunicación con Google Drive/Sheets.
2. **Frontend (Web)**: Construido con Vue 3, Vite, Tailwind CSS y TypeScript para la interfaz gráfica web y los paneles estadísticos.
3. **Escritorio (GUI)**: Un buscador local de fichas desarrollado con CustomTkinter.

---

## 🚀 Instrucciones para Ejecutar los Servidores

### 1. Requisitos Previos

- Asegúrate de tener instalado Python (versión 3.12 o superior) y Node.js.
- Las credenciales de Google API deben estar ubicadas en:
  - `auth/json/credentials.json`
  - `auth/json/token.json`

---

### 2. Ejecutar el Backend (FastAPI)

El backend se encarga de servir los endpoints de la API y de ejecutar los scripts de sincronización con Google Drive.

1. Abre una terminal en la raíz del proyecto.
2. Activa el entorno virtual de Python (`venv`):
   - En **PowerShell**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - En **CMD**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
3. Ejecuta la aplicación usando `uvicorn`:
   ```bash
   uvicorn src.web.main:app --reload
   ```
4. El backend estará disponible en: **`http://127.0.0.1:8000`**
   - Puedes ver la documentación interactiva de la API (Swagger) en: `http://127.0.0.1:8000/docs`

---

### 3. Ejecutar el Frontend (Vite + Vue) - Modo Desarrollo

Para trabajar en el código del frontend y ver los cambios en tiempo real:

1. Abre una nueva terminal en la raíz del proyecto.
2. Navega al directorio del frontend:
   ```bash
   cd frontend
   ```
3. Instala las dependencias necesarias (solo la primera vez):
   ```bash
   npm install
   ```
4. Inicia el servidor de desarrollo:
   ```bash
   npm run dev
   ```
5. El frontend de desarrollo estará disponible en: **`http://localhost:5173`** (o el puerto que indique la terminal).

---

### 4. Compilación e Integración para Producción

FastAPI está configurado para servir los archivos compilados del frontend de manera estática.

1. Ve a la carpeta `frontend/` y compila el proyecto:
   ```bash
   cd frontend
   ```
   ```bash
   npm run build
   ```
2. Esto generará la carpeta `frontend/dist/`.
3. Inicia el backend de FastAPI (`uvicorn src.web.main:app --reload` en la raíz).
4. Ahora podrás acceder a la aplicación completa (Frontend y API integrados) directamente desde: **`http://127.0.0.1:8000/`**
