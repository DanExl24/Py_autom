<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { Icon } from '@iconify/vue'
import type { Ficha, Kpis } from './types'
import KpiCard from './components/KpiCard.vue'
import DashboardCharts from './components/DashboardCharts.vue'
import BuscadorFichas from './components/BuscadorFichas.vue'
import FichaTechnicalDrawer from './components/FichaTechnicalDrawer.vue'
import EstadisticasDetalle from './components/EstadisticasDetalle.vue'
import SincronizarExcel from './components/SincronizarExcel.vue'

const rawFichas = ref<Ficha[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const activeTab = ref('dashboard')
const selectedFicha = ref<Ficha | null>(null)

// Control del tema oscuro
const isDark = ref(false)
const toggleDarkMode = () => {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.setItem('theme', 'dark')
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.setItem('theme', 'light')
  }
}

// Carga inicial de datos
const loadData = async () => {
  try {
    loading.value = true
    error.value = null
    const res = await fetch('/api/fichas')
    if (!res.ok) throw new Error('No se pudieron obtener los datos de las fichas')
    const data = await res.json()
    
    const list: Ficha[] = []
    
    // Procesar la estructura Red -> Ficha -> Info
    for (const [redNombre, fichasDict] of Object.entries(data)) {
      for (const [fichaNum, info] of Object.entries(fichasDict as any)) {
        const infoObj = info as any
        
        // Calcular duración si es nula
        let duracionCalculada = 0
        const duracion = infoObj.DURACION
        if (duracion === null || duracion === undefined || duracion === "") {
          const start = infoObj["FECHA INICIO"] ? new Date(infoObj["FECHA INICIO"]) : null
          const end = infoObj["FECHA TERMINACION"] ? new Date(infoObj["FECHA TERMINACION"]) : null
          if (start && end && !isNaN(start.getTime()) && !isNaN(end.getTime())) {
            // Calcular diferencia en meses aproximados
            duracionCalculada = Math.round((end.getTime() - start.getTime()) / (1000 * 60 * 60 * 24 * 30.44))
          }
        } else {
          duracionCalculada = parseInt(duracion) || 0
        }
        
        list.push({
          ...infoObj,
          FICHA: String(fichaNum),
          "RED DE CONOCIMIENTO": redNombre,
          "APRENDICES MATRICULADOS": parseInt(infoObj["APRENDICES MATRICULADOS"]) || 0,
          "CODIGO DE PROGRAMA": parseInt(infoObj["CODIGO DE PROGRAMA"]) || 0,
          VERSION: parseInt(infoObj.VERSION) || 1,
          "CÓDIGO PROYECTO": parseInt(infoObj["CÓDIGO PROYECTO"]) || 0,
          DURACION_CALCULADA: duracionCalculada
        })
      }
    }
    rawFichas.value = list
  } catch (e: any) {
    error.value = e.message || 'Error al conectar'
  } finally {
    loading.value = false
  }
}

// Inicializar
onMounted(() => {
  loadData()
  const savedTheme = localStorage.getItem('theme')
  const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  if (savedTheme === 'dark' || (!savedTheme && systemPrefersDark)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
})

// --- CÁLCULO DE KPIs ---
const kpis = computed<Kpis>(() => {
  if (!rawFichas.value.length) {
    return {
      totalFormaciones: 0,
      totalAprendices: 0,
      promedioAprendices: 0,
      promedioDuracion: 0,
      totalRedes: 0,
      totalMunicipios: 0,
      totalInstructores: 0
    }
  }

  const totalFormaciones = rawFichas.value.length
  const totalAprendices = rawFichas.value.reduce((sum, f) => sum + f["APRENDICES MATRICULADOS"], 0)
  const promedioAprendices = Number((totalAprendices / totalFormaciones).toFixed(1))
  
  const duraciones = rawFichas.value.map(f => f.DURACION_CALCULADA).filter(Boolean)
  const promedioDuracion = duraciones.length 
    ? Number((duraciones.reduce((sum, d) => sum + d, 0) / duraciones.length).toFixed(1))
    : 0

  const redes = new Set(rawFichas.value.map(f => f["RED DE CONOCIMIENTO"]).filter(Boolean))
  const municipios = new Set(rawFichas.value.map(f => f.MUNICIPIO).filter(Boolean))
  
  const instructores = new Set<string>()
  rawFichas.value.forEach(f => {
    const inst25 = f["INSTRUCTOR TÉCNICO 2025"]
    const inst26 = f["INSTRUCTOR TÉCNICO 2026"]
    if (inst25 && inst25 !== 'None' && inst25.trim()) instructores.add(inst25.trim().toUpperCase())
    if (inst26 && inst26 !== 'None' && inst26.trim()) instructores.add(inst26.trim().toUpperCase())
  })

  return {
    totalFormaciones,
    totalAprendices,
    promedioAprendices,
    promedioDuracion,
    totalRedes: redes.size,
    totalMunicipios: municipios.size,
    totalInstructores: instructores.size
  }
})

const proximoInicio = computed(() => {
  const hoy = new Date()
  const futuros = rawFichas.value
    .filter(f => f["FECHA INICIO"])
    .map(f => ({ fecha: new Date(f["FECHA INICIO"]), str: f["FECHA INICIO"] }))
    .filter(item => !isNaN(item.fecha.getTime()) && item.fecha >= hoy)
    .sort((a, b) => a.fecha.getTime() - b.fecha.getTime())
    
  return futuros.length ? futuros[0].str : 'No programado'
})

const proximaFinalizacion = computed(() => {
  const hoy = new Date()
  const futuros = rawFichas.value
    .filter(f => f["FECHA TERMINACION"])
    .map(f => ({ fecha: new Date(f["FECHA TERMINACION"]), str: f["FECHA TERMINACION"] }))
    .filter(item => !isNaN(item.fecha.getTime()) && item.fecha >= hoy)
    .sort((a, b) => a.fecha.getTime() - b.fecha.getTime())
    
  return futuros.length ? futuros[0].str : 'No programada'
})

// --- ALERTAS DEL DASHBOARD ---
const alertBajaMatricula = computed(() => {
  return rawFichas.value.filter(f => f["APRENDICES MATRICULADOS"] < 15).length
})

const alertProximasTerminar = computed(() => {
  const hoy = new Date()
  const limite = new Date()
  limite.setDate(limite.getDate() + 30) // 30 días
  
  return rawFichas.value.filter(f => {
    if (!f["FECHA TERMINACION"]) return false
    const term = new Date(f["FECHA TERMINACION"])
    return !isNaN(term.getTime()) && term >= hoy && term <= limite
  }).length
})

const alertSinProyecto = computed(() => {
  return rawFichas.value.filter(f => !f["CÓDIGO PROYECTO"] || f["CÓDIGO PROYECTO"] === 0).length
})

// --- REPORTES ---
const exportarCSV = () => {
  if (!rawFichas.value.length) return
  
  // Extraer headers del primer elemento
  const headers = Object.keys(rawFichas.value[0]).join(',')
  const rows = rawFichas.value.map(f => {
    return Object.values(f).map(val => {
      let strVal = String(val === null ? '' : val).replace(/"/g, '""')
      if (strVal.includes(',') || strVal.includes('\n')) {
        strVal = `"${strVal}"`
      }
      return strVal
    }).join(',')
  })
  
  // Agregar BOM UTF-8 para que Excel lo lea con caracteres especiales (tildes, eñes)
  const csvContent = 'data:text/csv;charset=utf-8,\uFEFF' + [headers, ...rows].join('\n')
  const encodedUri = encodeURI(csvContent)
  const link = document.createElement("a")
  link.setAttribute("href", encodedUri)
  link.setAttribute("download", `reporte_fichas_${new Date().toISOString().slice(0, 10)}.csv`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const exportarJSON = () => {
  if (!rawFichas.value.length) return
  const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
    JSON.stringify(rawFichas.value, null, 2)
  )}`
  const link = document.createElement("a")
  link.setAttribute("href", jsonString)
  link.setAttribute("download", `reporte_fichas_${new Date().toISOString().slice(0, 10)}.json`)
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}

const imprimirReporte = () => {
  window.print()
}
</script>

<template>
  <div class="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 flex flex-col md:flex-row transition-colors duration-200">
    
    <!-- Sidebar Azul Petróleo (#1E3A5F) -->
    <aside class="w-full md:w-64 bg-primary text-white flex flex-col shrink-0 border-r border-primary-dark/40 print:hidden">
      
      <!-- Logo / Header -->
      <div class="p-6 border-b border-primary-dark/40 flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Icon icon="lucide:school" class="w-6 h-6 text-success" />
          <h1 class="text-lg font-black tracking-wider uppercase">
            SENA Fichas
          </h1>
        </div>
        <span class="text-[10px] bg-primary-light text-slate-200 font-bold px-2 py-0.5 rounded-full">
          Admin
        </span>
      </div>

      <!-- Menú Navegación -->
      <nav class="flex-1 p-4 space-y-1.5">
        <button 
          @click="activeTab = 'dashboard'"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-150"
          :class="activeTab === 'dashboard' ? 'bg-primary-light text-white shadow-sm' : 'text-slate-300 hover:bg-primary-light/40 hover:text-white'"
        >
          <Icon icon="lucide:layout-dashboard" class="w-5 h-5" />
          Dashboard
        </button>
        <button 
          @click="activeTab = 'stats'"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-150"
          :class="activeTab === 'stats' ? 'bg-primary-light text-white shadow-sm' : 'text-slate-300 hover:bg-primary-light/40 hover:text-white'"
        >
          <Icon icon="lucide:trending-up" class="w-5 h-5" />
          Estadísticas
        </button>
        <button 
          @click="activeTab = 'search'"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-150"
          :class="activeTab === 'search' ? 'bg-primary-light text-white shadow-sm' : 'text-slate-300 hover:bg-primary-light/40 hover:text-white'"
        >
          <Icon icon="lucide:search" class="w-5 h-5" />
          Buscador
        </button>
        <button 
          @click="activeTab = 'sync'"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-150"
          :class="activeTab === 'sync' ? 'bg-primary-light text-white shadow-sm' : 'text-slate-300 hover:bg-primary-light/40 hover:text-white'"
        >
          <Icon icon="lucide:refresh-cw" class="w-5 h-5" />
          Sincronizar Excel
        </button>
        <button 
          @click="activeTab = 'reports'"
          class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-150"
          :class="activeTab === 'reports' ? 'bg-primary-light text-white shadow-sm' : 'text-slate-300 hover:bg-primary-light/40 hover:text-white'"
        >
          <Icon icon="lucide:file-bar-chart" class="w-5 h-5" />
          Reportes
        </button>
      </nav>

      <!-- Panel Inferior (Modo Oscuro) -->
      <div class="p-4 border-t border-primary-dark/40 flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-300">Modo Oscuro</span>
        <button 
          @click="toggleDarkMode"
          class="p-2 rounded-lg bg-primary-dark/60 hover:bg-primary-dark text-white transition-colors duration-150"
        >
          <Icon :icon="isDark ? 'lucide:sun' : 'lucide:moon'" class="w-4 h-4" />
        </button>
      </div>

    </aside>

    <!-- Contenido Principal -->
    <main class="flex-1 flex flex-col min-w-0">
      
      <!-- Carga inicial -->
      <div v-if="loading" class="flex-1 flex flex-col items-center justify-center p-12 print:hidden">
        <Icon icon="lucide:loader" class="w-10 h-10 text-primary animate-spin mb-4" />
        <p class="font-bold text-slate-500 dark:text-slate-400 text-sm">Cargando base de datos de fichas...</p>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="flex-1 flex flex-col items-center justify-center p-12 text-center print:hidden">
        <Icon icon="lucide:alert-triangle" class="w-12 h-12 text-danger mb-4" />
        <h3 class="text-lg font-black text-slate-850 dark:text-slate-100 mb-2">Error de conexión</h3>
        <p class="text-sm text-slate-500 dark:text-slate-400 mb-6">{{ error }}</p>
        <button 
          @click="loadData"
          class="px-4 py-2 bg-primary hover:bg-primary-light text-white font-bold rounded-xl text-sm shadow transition-colors"
        >
          Reintentar Carga
        </button>
      </div>

      <!-- Contenido de las pestañas -->
      <div v-else class="flex-1 p-6 md:p-8 space-y-6 overflow-y-auto print:p-0">
        
        <!-- PESTAÑA 1: DASHBOARD -->
        <div v-if="activeTab === 'dashboard'" class="space-y-6">
          <div class="flex items-center justify-between print:hidden">
            <div class="flex items-center gap-2">
              <Icon icon="lucide:layout-dashboard" class="w-6 h-6 text-primary dark:text-primary-light" />
              <h2 class="text-2xl font-black tracking-tight text-slate-800 dark:text-slate-100">
                Estado General de Formaciones
              </h2>
            </div>
            <span class="text-xs font-semibold text-slate-400">
              Datos activos de Caquetá 2026
            </span>
          </div>

          <!-- KPIs (8 Tarjetas) -->
          <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
            <KpiCard title="Total Fichas" :value="kpis.totalFormaciones" icon="lucide:file-text" color-class="text-primary dark:text-primary-light" border-class="bg-primary" />
            <KpiCard title="Total Aprendices" :value="kpis.totalAprendices.toLocaleString()" icon="lucide:graduation-cap" color-class="text-secondary" border-class="bg-secondary" />
            <KpiCard title="Total Instructores" :value="kpis.totalInstructores" icon="lucide:users" color-class="text-success" border-class="bg-success" />
            <KpiCard title="Redes de Conocimiento" :value="kpis.totalRedes" icon="lucide:globe" color-class="text-warning" border-class="bg-warning" />
            <KpiCard title="Municipios Cubiertos" :value="kpis.totalMunicipios" icon="lucide:map-pin" color-class="text-danger" border-class="bg-danger" />
            <KpiCard title="Promedio Ficha" :value="kpis.promedioAprendices" icon="lucide:activity" color-class="text-sky-500" border-class="bg-sky-500" />
            <KpiCard title="Próximo Inicio" :value="proximoInicio" icon="lucide:calendar" color-class="text-success" border-class="bg-success" />
            <KpiCard title="Próxima Finalización" :value="proximaFinalizacion" icon="lucide:clock" color-class="text-warning" border-class="bg-warning" />
          </div>

          <!-- Alertas Inteligentes (Bandeja compacta) -->
          <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4 print:hidden">
            <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-widest flex items-center gap-1.5">
              <Icon icon="lucide:bell" class="w-4 h-4 text-warning" />
              Notificaciones y Alertas Críticas
            </h3>
            <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <!-- Alerta Baja Matrícula -->
              <div class="flex items-start gap-3 p-3 bg-rose-50 dark:bg-rose-950/20 border border-rose-100 dark:border-rose-900/50 rounded-lg">
                <Icon icon="lucide:alert-circle" class="w-5 h-5 text-danger shrink-0 mt-0.5" />
                <div>
                  <span class="block text-xs font-bold text-rose-800 dark:text-rose-400 uppercase tracking-wide">Baja Matrícula</span>
                  <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">
                    {{ alertBajaMatricula }} programas con menos de 15 alumnos.
                  </span>
                </div>
              </div>

              <!-- Alerta Próximas a terminar -->
              <div class="flex items-start gap-3 p-3 bg-amber-50 dark:bg-amber-950/20 border border-amber-100 dark:border-amber-900/50 rounded-lg">
                <Icon icon="lucide:hourglass" class="w-5 h-5 text-warning shrink-0 mt-0.5" />
                <div>
                  <span class="block text-xs font-bold text-amber-800 dark:text-amber-400 uppercase tracking-wide">Plazos Lectivos</span>
                  <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">
                    {{ alertProximasTerminar }} fichas terminan en &lt;30 días.
                  </span>
                </div>
              </div>

              <!-- Alerta Sin proyecto -->
              <div class="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-950/20 border border-blue-100 dark:border-blue-900/50 rounded-lg">
                <Icon icon="lucide:help-circle" class="w-5 h-5 text-secondary shrink-0 mt-0.5" />
                <div>
                  <span class="block text-xs font-bold text-blue-800 dark:text-blue-400 uppercase tracking-wide">Asignación Proyectos</span>
                  <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">
                    {{ alertSinProyecto }} fichas sin código de proyecto.
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Gráficos -->
          <DashboardCharts :fichas="rawFichas" />
        </div>

        <!-- PESTAÑA 2: ESTADÍSTICAS DETALLADAS -->
        <div v-if="activeTab === 'stats'" class="space-y-6">
          <div class="flex items-center gap-2 print:hidden">
            <Icon icon="lucide:trending-up" class="w-6 h-6 text-primary dark:text-primary-light" />
            <h2 class="text-2xl font-black tracking-tight text-slate-800 dark:text-slate-100">
              Estadísticas y Rankings Especializados
            </h2>
          </div>

          <EstadisticasDetalle :fichas="rawFichas" @select-ficha="f => selectedFicha = f" />
        </div>

        <!-- PESTAÑA 3: BUSCADOR AVANZADO -->
        <div v-if="activeTab === 'search'" class="space-y-6">
          <div class="flex items-center gap-2 print:hidden">
            <Icon icon="lucide:search" class="w-6 h-6 text-primary dark:text-primary-light" />
            <h2 class="text-2xl font-black tracking-tight text-slate-800 dark:text-slate-100">
              Buscador General y Ficha Técnica
            </h2>
          </div>

          <BuscadorFichas :fichas="rawFichas" @select-ficha="f => selectedFicha = f" />
        </div>

        <!-- PESTAÑA 4: SINCRONIZAR EXCEL -->
        <div v-if="activeTab === 'sync'" class="space-y-6 print:hidden">
          <div class="flex items-center gap-2">
            <Icon icon="lucide:refresh-cw" class="w-6 h-6 text-primary dark:text-primary-light" />
            <h2 class="text-2xl font-black tracking-tight text-slate-800 dark:text-slate-100">
              Sincronización de Datos
            </h2>
          </div>

          <SincronizarExcel @sync-complete="loadData" />
        </div>

        <!-- PESTAÑA 5: REPORTES -->
        <div v-if="activeTab === 'reports'" class="space-y-6">
          <div class="flex items-center gap-2 print:hidden">
            <Icon icon="lucide:file-bar-chart" class="w-6 h-6 text-primary dark:text-primary-light" />
            <h2 class="text-2xl font-black tracking-tight text-slate-800 dark:text-slate-100">
              Exportación y Reportes
            </h2>
          </div>

          <!-- Grid de Reportes -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6 print:hidden">
            <!-- CSV Card -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col justify-between h-48 hover:shadow-md transition-shadow">
              <div class="space-y-2">
                <Icon icon="lucide:file-text" class="w-8 h-8 text-secondary" />
                <h4 class="font-bold text-slate-800 dark:text-slate-100">Exportar como CSV</h4>
                <p class="text-xs text-slate-400">Descarga un reporte estructurado compatible con Excel y software externo.</p>
              </div>
              <button 
                @click="exportarCSV"
                class="w-full py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 font-bold rounded-lg text-xs transition-colors"
              >
                Descargar CSV
              </button>
            </div>

            <!-- JSON Card -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col justify-between h-48 hover:shadow-md transition-shadow">
              <div class="space-y-2">
                <Icon icon="lucide:code-2" class="w-8 h-8 text-success" />
                <h4 class="font-bold text-slate-800 dark:text-slate-100">Exportar como JSON</h4>
                <p class="text-xs text-slate-400">Descarga la base de datos limpia de fichas para integrarla en sistemas.</p>
              </div>
              <button 
                @click="exportarJSON"
                class="w-full py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 font-bold rounded-lg text-xs transition-colors"
              >
                Descargar JSON
              </button>
            </div>

            <!-- Imprimir Card -->
            <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col justify-between h-48 hover:shadow-md transition-shadow">
              <div class="space-y-2">
                <Icon icon="lucide:printer" class="w-8 h-8 text-warning" />
                <h4 class="font-bold text-slate-800 dark:text-slate-100">Imprimir Dashboard</h4>
                <p class="text-xs text-slate-400">Imprime directamente la vista general adaptada en formato de reporte físico.</p>
              </div>
              <button 
                @click="imprimirReporte"
                class="w-full py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-800 dark:text-slate-200 font-bold rounded-lg text-xs transition-colors"
              >
                Imprimir
              </button>
            </div>
          </div>

          <!-- Vista previa para impresión -->
          <div class="hidden print:block space-y-8">
            <div class="border-b-2 border-slate-800 pb-4">
              <h1 class="text-3xl font-black uppercase text-slate-850">SENA Fichas y Cobertura Caquetá 2026</h1>
              <p class="text-sm text-slate-500">Reporte Administrativo consolidado - Generado el {{ new Date().toLocaleDateString() }}</p>
            </div>
            
            <div class="grid grid-cols-3 gap-6 text-center border border-slate-200 p-6 rounded-xl">
              <div>
                <span class="block text-xs uppercase font-bold text-slate-400">Total Formaciones</span>
                <span class="text-2xl font-black">{{ kpis.totalFormaciones }}</span>
              </div>
              <div>
                <span class="block text-xs uppercase font-bold text-slate-400">Total Matriculados</span>
                <span class="text-2xl font-black">{{ kpis.totalAprendices.toLocaleString() }}</span>
              </div>
              <div>
                <span class="block text-xs uppercase font-bold text-slate-400">Promedio Ficha</span>
                <span class="text-2xl font-black">{{ kpis.promedioAprendices }}</span>
              </div>
            </div>

            <!-- Tabla de resumen para impresión -->
            <div class="space-y-4">
              <h3 class="text-lg font-bold">Listado consolidado de formaciones</h3>
              <table class="w-full text-left text-xs border border-slate-300">
                <thead>
                  <tr class="bg-slate-100 border-b border-slate-350">
                    <th class="p-2">Ficha</th>
                    <th class="p-2">Programa</th>
                    <th class="p-2">Municipio</th>
                    <th class="p-2">Apr.</th>
                    <th class="p-2">Instructor 2026</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="f in rawFichas.slice(0, 30)" :key="f.FICHA" class="border-b border-slate-200">
                    <td class="p-2 font-bold">{{ f.FICHA }}</td>
                    <td class="p-2 capitalize">{{ f["NOMBRE DEL PROGRAMA"].toLowerCase() }}</td>
                    <td class="p-2 capitalize">{{ f.MUNICIPIO.toLowerCase() }}</td>
                    <td class="p-2 text-center font-bold">{{ f["APRENDICES MATRICULADOS"] }}</td>
                    <td class="p-2 capitalize">{{ (f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"] || 'SIN ASIGNAR').toLowerCase() }}</td>
                  </tr>
                </tbody>
              </table>
              <p class="text-[10px] text-slate-400 italic" v-if="rawFichas.length > 30">
                * Mostrando solo los primeros 30 registros de un total de {{ rawFichas.length }} formaciones.
              </p>
            </div>
          </div>
        </div>

      </div>

    </main>

    <!-- Panel Lateral Deslizante (Slide-over Drawer) para Ficha Técnica -->
    <FichaTechnicalDrawer 
      :ficha="selectedFicha"
      @close="selectedFicha = null"
    />

  </div>
</template>

<style>
/* Estilos para impresión */
@media print {
  body {
    background-color: white !important;
    color: black !important;
  }
}
</style>
