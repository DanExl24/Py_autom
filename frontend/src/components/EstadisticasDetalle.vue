<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Icon } from '@iconify/vue'
import type { Ficha } from '../types'
import QuickDetailModal from './QuickDetailModal.vue'
import { inferJornada, getHorariosGrouped, normalizeHorario } from '../utils/horario'

const props = defineProps<{
  fichas: Ficha[]
}>()

const emit = defineEmits<{
  (e: 'select-ficha', ficha: Ficha): void
}>()

const activeSubTab = ref('horarios')

const tabs = [
  { id: 'horarios', name: 'Horarios', icon: 'lucide:clock' },
  { id: 'programas', name: 'Programas', icon: 'lucide:book-open' },
  { id: 'aprendices', name: 'Aprendices', icon: 'lucide:graduation-cap' },
  { id: 'instructores', name: 'Instructores', icon: 'lucide:users' },
  { id: 'fechas', name: 'Fechas y Plazos', icon: 'lucide:calendar' },
  { id: 'municipios', name: 'Municipios y Oferta', icon: 'lucide:map-pin' },
  { id: 'proyectos', name: 'Proyectos y Ambientes', icon: 'lucide:layers' },
  { id: 'indicadores', name: 'Indicadores Pro', icon: 'lucide:activity' },
  { id: 'trimestres', name: 'Años-Trimestres', icon: 'lucide:calendar-range' }
]

// --- FILTROS DE ESTADÍSTICAS ---
const selectedJornadaStats = ref('Todas')
const selectedHorarioStats = ref('Todos')
const fechaDesdeStats = ref('')
const fechaHastaStats = ref('')

const jornadas = ['Todas', 'Mañana', 'Tarde', 'Mixta', 'Noche', 'Horario Compuesto', 'Sin especificar']

const horariosUnicosStats = computed<string[]>(() => {
  const list = new Set<string>()
  props.fichas.forEach(f => {
    if (f.HORARIO && f.HORARIO.trim()) list.add(f.HORARIO.trim())
  })
  return ['Todos', ...Array.from(list).sort()]
})

const resetStatsFilters = () => {
  selectedJornadaStats.value = 'Todas'
  selectedHorarioStats.value = 'Todos'
  fechaDesdeStats.value = ''
  fechaHastaStats.value = ''
}

// Fichas filtradas según filtros globales de estadísticas
const fichasFiltradasStats = computed(() => {
  return props.fichas.filter(f => {
    // Jornada
    if (selectedJornadaStats.value !== 'Todas') {
      if (inferJornada(f.HORARIO) !== selectedJornadaStats.value) return false
    }
    // Horario
    if (selectedHorarioStats.value !== 'Todos') {
      if (normalizeHorario(f.HORARIO) !== normalizeHorario(selectedHorarioStats.value)) return false
    }
    // Fechas
    if (fechaDesdeStats.value) {
      if (!f["FECHA INICIO"] || f["FECHA INICIO"] < fechaDesdeStats.value) return false
    }
    if (fechaHastaStats.value) {
      if (!f["FECHA TERMINACION"] || f["FECHA TERMINACION"] > fechaHastaStats.value) return false
    }
    return true
  })
})

// --- ESTADO Y MÉTODOS PARA MODAL DE VISTA RÁPIDA ---
const quickModal = ref({
  show: false,
  title: '',
  subtitle: '',
  fichas: [] as Ficha[],
  extraMetrics: [] as { label: string; value: string | number; icon?: string }[]
})

const openQuickModal = (title: string, subtitle: string, fichas: Ficha[], extraMetrics: any[] = []) => {
  quickModal.value = {
    show: true,
    title,
    subtitle,
    fichas,
    extraMetrics
  }
}

// --- COMPUTACIONES PARA SUBPESTAÑAS ---

// 0. HORARIOS (NUEVA SECCIÓN)
const horariosGroupedStats = computed(() => {
  return getHorariosGrouped(fichasFiltradasStats.value)
})

const resumenJornadas = computed(() => {
  const counts: Record<string, { count: number; aprendices: number; fichas: Ficha[] }> = {
    'Mañana': { count: 0, aprendices: 0, fichas: [] },
    'Tarde': { count: 0, aprendices: 0, fichas: [] },
    'Mixta': { count: 0, aprendices: 0, fichas: [] },
    'Noche': { count: 0, aprendices: 0, fichas: [] },
    'Horario Compuesto': { count: 0, aprendices: 0, fichas: [] },
    'Sin especificar': { count: 0, aprendices: 0, fichas: [] }
  }

  fichasFiltradasStats.value.forEach(f => {
    const j = inferJornada(f.HORARIO)
    if (!counts[j]) {
      counts[j] = { count: 0, aprendices: 0, fichas: [] }
    }
    counts[j].count += 1
    counts[j].aprendices += f["APRENDICES MATRICULADOS"] || 0
    counts[j].fichas.push(f)
  })

  return counts
})

// 1. PROGRAMAS
const topProgramasPorAprendices = computed(() => {
  const map: Record<string, { name: string; aprendices: number; fichasCount: number; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const prog = f["NOMBRE DEL PROGRAMA"] || 'DESCONOCIDO'
    if (!map[prog]) map[prog] = { name: prog, aprendices: 0, fichasCount: 0, fichas: [] }
    map[prog].aprendices += f["APRENDICES MATRICULADOS"]
    map[prog].fichasCount += 1
    map[prog].fichas.push(f)
  })
  return Object.values(map).sort((a, b) => b.aprendices - a.aprendices)
})

const topProgramasPorFichas = computed(() => {
  const map: Record<string, { name: string; aprendices: number; fichasCount: number; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const prog = f["NOMBRE DEL PROGRAMA"] || 'DESCONOCIDO'
    if (!map[prog]) map[prog] = { name: prog, aprendices: 0, fichasCount: 0, fichas: [] }
    map[prog].aprendices += f["APRENDICES MATRICULADOS"]
    map[prog].fichasCount += 1
    map[prog].fichas.push(f)
  })
  return Object.values(map).sort((a, b) => b.fichasCount - a.fichasCount)
})

const programasConVariasVersiones = computed(() => {
  const map: Record<string, { versiones: Set<number>; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const prog = f["NOMBRE DEL PROGRAMA"]
    const ver = f.VERSION
    if (prog) {
      if (!map[prog]) map[prog] = { versiones: new Set(), fichas: [] }
      if (ver) map[prog].versiones.add(ver)
      map[prog].fichas.push(f)
    }
  })
  return Object.entries(map)
    .filter(([_, data]) => data.versiones.size > 1)
    .map(([name, data]) => ({ name, versiones: Array.from(data.versiones).sort(), fichas: data.fichas }))
})

// 2. APRENDICES
const aprendicesPorRed = computed(() => {
  const map: Record<string, { name: string; count: number; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const red = f["RED DE CONOCIMIENTO"] || 'DESCONOCIDA'
    if (!map[red]) map[red] = { name: red, count: 0, fichas: [] }
    map[red].count += f["APRENDICES MATRICULADOS"]
    map[red].fichas.push(f)
  })
  return Object.values(map).sort((a, b) => b.count - a.count)
})

const aprendicesPorMunicipio = computed(() => {
  const map: Record<string, { name: string; count: number; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const muni = f.MUNICIPIO || 'DESCONOCIDO'
    if (!map[muni]) map[muni] = { name: muni, count: 0, fichas: [] }
    map[muni].count += f["APRENDICES MATRICULADOS"]
    map[muni].fichas.push(f)
  })
  return Object.values(map).sort((a, b) => b.count - a.count)
})

const programasBajaMatricula = computed(() => {
  return fichasFiltradasStats.value
    .filter(f => f["APRENDICES MATRICULADOS"] < 15)
    .map(f => ({
      ficha: f.FICHA,
      programa: f["NOMBRE DEL PROGRAMA"],
      matriculados: f["APRENDICES MATRICULADOS"],
      instructor: f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"] || 'Sin Asignar',
      raw: f
    }))
    .sort((a, b) => a.matriculados - b.matriculados)
})

// 3. INSTRUCTORES
const rankingInstructoresPorAprendices = computed(() => {
  const map: Record<string, { name: string; aprendices: number; fichasCount: number; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const inst = f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"]
    if (inst && inst !== 'None' && inst.trim() !== '') {
      const key = inst.trim().toUpperCase()
      if (!map[key]) map[key] = { name: inst, aprendices: 0, fichasCount: 0, fichas: [] }
      map[key].aprendices += f["APRENDICES MATRICULADOS"]
      map[key].fichasCount += 1
      map[key].fichas.push(f)
    }
  })
  return Object.values(map).sort((a, b) => b.aprendices - a.aprendices)
})

const instructoresDiversidad = computed(() => {
  const map: Record<string, { name: string; progs: Set<string>; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const inst = f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"]
    const prog = f["NOMBRE DEL PROGRAMA"]
    if (inst && inst !== 'None' && inst.trim() !== '' && prog) {
      const key = inst.trim().toUpperCase()
      if (!map[key]) map[key] = { name: inst, progs: new Set(), fichas: [] }
      map[key].progs.add(prog)
      map[key].fichas.push(f)
    }
  })
  return Object.values(map)
    .map(d => ({ name: d.name, distinctCount: d.progs.size, programas: Array.from(d.progs), fichas: d.fichas }))
    .sort((a, b) => b.distinctCount - a.distinctCount)
})

const instructoresNuevos = computed(() => {
  const insts2025 = new Set<string>()
  const insts2026 = new Map<string, Ficha[]>()
  fichasFiltradasStats.value.forEach(f => {
    const i25 = f["INSTRUCTOR TÉCNICO 2025"]
    const i26 = f["INSTRUCTOR TÉCNICO 2026"]
    if (i25 && i25 !== 'None' && i25.trim()) insts2025.add(i25.trim().toUpperCase())
    if (i26 && i26 !== 'None' && i26.trim()) {
      const k = i26.trim().toUpperCase()
      if (!insts2026.has(k)) insts2026.set(k, [])
      insts2026.get(k)!.push(f)
    }
  })
  const nuevos: { name: string; fichas: Ficha[] }[] = []
  insts2026.forEach((fichas, name) => {
    if (!insts2025.has(name)) nuevos.push({ name, fichas })
  })
  return nuevos.sort((a, b) => a.name.localeCompare(b.name))
})

const instructoresYaNoAparecen = computed(() => {
  const insts2025 = new Map<string, Ficha[]>()
  const insts2026 = new Set<string>()
  fichasFiltradasStats.value.forEach(f => {
    const i25 = f["INSTRUCTOR TÉCNICO 2025"]
    const i26 = f["INSTRUCTOR TÉCNICO 2026"]
    if (i25 && i25 !== 'None' && i25.trim()) {
      const k = i25.trim().toUpperCase()
      if (!insts2025.has(k)) insts2025.set(k, [])
      insts2025.get(k)!.push(f)
    }
    if (i26 && i26 !== 'None' && i26.trim()) insts2026.add(i26.trim().toUpperCase())
  })
  const salientes: { name: string; fichas: Ficha[] }[] = []
  insts2025.forEach((fichas, name) => {
    if (!insts2026.has(name)) salientes.push({ name, fichas })
  })
  return salientes.sort((a, b) => a.name.localeCompare(b.name))
})

// 4. FECHAS
const formacionesInicianEsteMes = computed(() => {
  const currentMonth = new Date().getMonth()
  return fichasFiltradasStats.value
    .filter(f => {
      if (!f["FECHA INICIO"]) return false
      const start = new Date(f["FECHA INICIO"])
      return !isNaN(start.getTime()) && start.getMonth() === currentMonth
    })
    .map(f => ({
      ficha: f.FICHA,
      programa: f["NOMBRE DEL PROGRAMA"],
      fecha: f["FECHA INICIO"],
      raw: f
    }))
})

const formacionesTerminanEsteMes = computed(() => {
  const currentMonth = new Date().getMonth()
  return fichasFiltradasStats.value
    .filter(f => {
      if (!f["FECHA TERMINACION"]) return false
      const end = new Date(f["FECHA TERMINACION"])
      return !isNaN(end.getTime()) && end.getMonth() === currentMonth
    })
    .map(f => ({
      ficha: f.FICHA,
      programa: f["NOMBRE DEL PROGRAMA"],
      fecha: f["FECHA TERMINACION"],
      raw: f
    }))
})

// 5. MUNICIPIOS Y OFERTA
const municipiosUnSoloPrograma = computed(() => {
  const map: Record<string, { progs: Set<string>; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const muni = f.MUNICIPIO
    const prog = f["NOMBRE DEL PROGRAMA"]
    if (muni && prog) {
      if (!map[muni]) map[muni] = { progs: new Set(), fichas: [] }
      map[muni].progs.add(prog)
      map[muni].fichas.push(f)
    }
  })
  return Object.entries(map)
    .filter(([_, data]) => data.progs.size === 1)
    .map(([name, data]) => ({ name, programa: Array.from(data.progs)[0], fichas: data.fichas }))
})

// 6. PROYECTOS Y AMBIENTES
const proyectosMasFichas = computed(() => {
  const map: Record<string, { codigo: number; fichasCount: number; aprendices: number; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const proj = f["CÓDIGO PROYECTO"]
    if (proj && proj !== 0) {
      if (!map[proj]) map[proj] = { codigo: proj, fichasCount: 0, aprendices: 0, fichas: [] }
      map[proj].fichasCount += 1
      map[proj].aprendices += f["APRENDICES MATRICULADOS"]
      map[proj].fichas.push(f)
    }
  })
  return Object.values(map).sort((a, b) => b.fichasCount - a.fichasCount)
})

const ambientesMasUsados = computed(() => {
  const map: Record<string, { ambiente: string; fichas: Ficha[] }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const amb = String(f.AMBIENTE || '').trim()
    if (amb && amb !== 'None' && amb !== 'nan' && amb !== '') {
      if (!map[amb]) map[amb] = { ambiente: amb, fichas: [] }
      map[amb].fichas.push(f)
    }
  })
  return Object.values(map)
    .map(a => ({ ambiente: a.ambiente, count: a.fichas.length, fichas: a.fichas }))
    .sort((a, b) => b.count - a.count)
})

const ambientesCompartidos = computed(() => {
  return ambientesMasUsados.value.filter(a => a.count > 1)
})

// 7. INDICADORES PRO
const indicadoresPro = computed(() => {
  const totalFichas = fichasFiltradasStats.value.length
  const totalAprendices = fichasFiltradasStats.value.reduce((sum, f) => sum + f["APRENDICES MATRICULADOS"], 0)
  
  const instructoresSet = new Set<string>()
  fichasFiltradasStats.value.forEach(f => {
    const i25 = f["INSTRUCTOR TÉCNICO 2025"]
    const i26 = f["INSTRUCTOR TÉCNICO 2026"]
    if (i25 && i25 !== 'None' && i25.trim()) instructoresSet.add(i25.trim().toUpperCase())
    if (i26 && i26 !== 'None' && i26.trim()) instructoresSet.add(i26.trim().toUpperCase())
  })
  
  const densidadAprendizInstructor = instructoresSet.size 
    ? (totalAprendices / instructoresSet.size).toFixed(1) 
    : '0'
    
  const muniProgMap: Record<string, Set<string>> = {}
  fichasFiltradasStats.value.forEach(f => {
    const muni = f.MUNICIPIO
    const prog = f["NOMBRE DEL PROGRAMA"]
    if (muni && prog) {
      if (!muniProgMap[muni]) muniProgMap[muni] = new Set()
      muniProgMap[muni].add(prog)
    }
  })
  const diversidadMuni = Object.entries(muniProgMap)
    .map(([muni, progs]) => ({ name: muni, count: progs.size }))
    .sort((a, b) => b.count - a.count)[0] || { name: 'N/A', count: 0 }

  return {
    densidad: densidadAprendizInstructor,
    totalInstructores: instructoresSet.size,
    diversidadMuniName: diversidadMuni.name,
    diversidadMuniCount: diversidadMuni.count,
    promedioFicha: totalFichas ? (totalAprendices / totalFichas).toFixed(1) : '0'
  }
})

// 8. AÑOS-TRIMESTRES
const selectedTrimestreDetalle = ref<string | null>(null)

const parseTrimestre = (str: string) => {
  const yearMatch = str.match(/\d{4}/)
  const year = yearMatch ? parseInt(yearMatch[0]) : 0
  let val = 0
  if (str.toUpperCase().includes('IV')) val = 4
  else if (str.toUpperCase().includes('III')) val = 3
  else if (str.toUpperCase().includes('II')) val = 2
  else if (str.toUpperCase().includes('I')) val = 1
  return { year, val }
}

const estadisticasTrimestres = computed(() => {
  const map: Record<string, { trimestre: string; fichas: Ficha[]; totalAprendices: number }> = {}
  fichasFiltradasStats.value.forEach(f => {
    const trim = f["AÑO /TRIMESTRE DE INICIO"] || 'SIN REGISTRAR'
    if (!map[trim]) {
      map[trim] = { trimestre: trim, fichas: [], totalAprendices: 0 }
    }
    map[trim].fichas.push(f)
    map[trim].totalAprendices += f["APRENDICES MATRICULADOS"]
  })
  
  return Object.values(map).sort((a, b) => {
    const pa = parseTrimestre(a.trimestre)
    const pb = parseTrimestre(b.trimestre)
    if (pa.year !== pb.year) return pa.year - pb.year
    return pa.val - pb.val
  })
})

const fichasTrimestreSeleccionado = computed(() => {
  if (!selectedTrimestreDetalle.value) return []
  const found = estadisticasTrimestres.value.find(t => t.trimestre === selectedTrimestreDetalle.value)
  return found ? found.fichas : []
})

watch(() => estadisticasTrimestres.value, (newVal) => {
  if (newVal.length && !selectedTrimestreDetalle.value) {
    selectedTrimestreDetalle.value = newVal[0].trimestre
  }
}, { immediate: true })
</script>

<template>
  <div class="space-y-6">

    <!-- Panel de Filtros de Estadísticas (Sólo visible en el módulo Horarios) -->
    <div v-if="activeSubTab === 'horarios'" class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3">
      <div class="flex items-center justify-between">
        <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-wider flex items-center gap-1.5">
          <Icon icon="lucide:filter" class="w-4 h-4 text-blue-500" />
          Filtro de Estadísticas (Jornada, Fechas y Horario Completo)
        </h3>
        <span class="text-xs font-bold text-blue-600 dark:text-blue-400">
          {{ fichasFiltradasStats.length }} Fichas filtradas
        </span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-3 items-end">
        <!-- Filtro Jornada -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Jornada:</label>
          <select 
            v-model="selectedJornadaStats"
            class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option v-for="j in jornadas" :key="j" :value="j">{{ j }}</option>
          </select>
        </div>

        <!-- Filtro Horario Completo -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Horario Completo:</label>
          <select 
            v-model="selectedHorarioStats"
            class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500 truncate"
          >
            <option v-for="h in horariosUnicosStats" :key="h" :value="h">{{ h }}</option>
          </select>
        </div>

        <!-- Fecha Inicio Desde -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Fecha Inicio Desde:</label>
          <input 
            v-model="fechaDesdeStats"
            type="date"
            class="w-full px-2 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <!-- Fecha Hasta -->
        <div class="space-y-1 flex items-center gap-2">
          <div class="flex-1 space-y-1">
            <label class="text-[10px] font-bold text-slate-400 uppercase">Terminación Hasta:</label>
            <input 
              v-model="fechaHastaStats"
              type="date"
              class="w-full px-2 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
            />
          </div>
          <button 
            @click="resetStatsFilters"
            class="mt-4 p-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-600 dark:text-slate-300 rounded-lg text-xs transition-colors"
            title="Resetear filtros de estadísticas"
          >
            <Icon icon="lucide:rotate-ccw" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
    
    <!-- Subpestañas estadísticas -->
    <div class="flex flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-px overflow-x-auto">
      <button 
        v-for="t in tabs" 
        :key="t.id"
        @click="activeSubTab = t.id"
        class="flex items-center gap-2 px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 -mb-px transition-colors duration-150 shrink-0"
        :class="activeSubTab === t.id 
          ? 'border-primary dark:border-primary-light text-primary dark:text-primary-light' 
          : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
      >
        <Icon :icon="t.icon" class="w-4 h-4" />
        {{ t.name }}
      </button>
    </div>

    <!-- CONTENIDOS DE SUBPESTAÑAS -->

    <!-- 0. HORARIOS (NUEVA SECCIÓN DETALLADA) -->
    <div v-if="activeSubTab === 'horarios'" class="space-y-6">
      <!-- Tarjetas de Resumen por Jornadas -->
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
        <div 
          v-for="(data, jName) in resumenJornadas" 
          :key="jName"
          @click="openQuickModal(`Jornada ${jName}`, `Resumen de formaciones en jornada ${jName}`, data.fichas, [{ label: 'Aprendices', value: data.aprendices, icon: 'lucide:graduation-cap' }])"
          class="p-4 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm hover:border-blue-400 dark:hover:border-blue-500 cursor-pointer transition-all space-y-1.5 group"
        >
          <span class="text-[10px] font-extrabold uppercase tracking-wider text-slate-400 block group-hover:text-blue-500">
            {{ jName }}
          </span>
          <div class="text-2xl font-black text-slate-800 dark:text-slate-100">
            {{ data.count }} <span class="text-xs font-semibold text-slate-400">fichas</span>
          </div>
          <span class="block text-xs font-bold text-emerald-600 dark:text-emerald-400">
            {{ data.aprendices.toLocaleString() }} apr.
          </span>
        </div>
      </div>

      <!-- Ranking de Horarios más Frecuentes y Fichas Enlazadas -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
        <h3 class="text-sm font-bold text-slate-800 dark:text-slate-100 flex items-center justify-between">
          <span>Ranking de Horarios más Frecuentes</span>
          <span class="text-xs font-normal text-slate-400">Haz clic en un horario para ver las fichas enlazadas</span>
        </h3>

        <div class="space-y-3">
          <div 
            v-for="(hg, i) in horariosGroupedStats" 
            :key="hg.horario"
            @click="openQuickModal(`Horario: ${hg.horario}`, `Jornada: ${hg.jornada}`, hg.fichas, [{ label: 'Total Aprendices', value: hg.totalAprendices, icon: 'lucide:graduation-cap' }])"
            class="p-4 bg-slate-50 dark:bg-slate-900/40 rounded-xl border border-slate-200 dark:border-slate-700/80 hover:border-blue-500 cursor-pointer transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 group"
          >
            <div class="space-y-1 flex-1">
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold text-slate-400">#{{ i + 1 }}</span>
                <span class="font-bold text-slate-900 dark:text-slate-100 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {{ hg.horario }}
                </span>
              </div>
              <div class="flex items-center gap-2">
                <span class="px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300">
                  {{ hg.jornada }}
                </span>
                <span class="text-xs text-slate-400 font-semibold">• {{ hg.count }} Fichas asociadas</span>
              </div>
            </div>

            <div class="flex items-center gap-4 shrink-0">
              <div class="text-right">
                <span class="block text-sm font-black text-emerald-600 dark:text-emerald-400">{{ hg.totalAprendices }} apr.</span>
                <span class="text-[10px] text-slate-400 font-semibold">Matrícula acumulada</span>
              </div>
              <button class="px-3 py-1.5 bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-300 font-bold text-xs rounded-lg group-hover:bg-blue-600 group-hover:text-white transition-colors">
                Ver Fichas
              </button>
            </div>
          </div>

          <div v-if="!horariosGroupedStats.length" class="text-center py-10 text-xs text-slate-400 italic">
            No se encontraron horarios con los filtros seleccionados.
          </div>
        </div>
      </div>
    </div>
    
    <!-- 1. PROGRAMAS -->
    <div v-if="activeSubTab === 'programas'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Top Aprendices -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Programas con Más Aprendices (Haz clic para ver registros)</h3>
        <div class="space-y-3">
          <div 
            v-for="(p, i) in topProgramasPorAprendices" 
            :key="p.name" 
            @click="openQuickModal(`Programa: ${p.name}`, 'Listado de fichas asociadas', p.fichas, [{ label: 'Aprendices', value: p.aprendices, icon: 'lucide:graduation-cap' }])"
            class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 cursor-pointer hover:text-blue-600 transition-colors group"
          >
            <div class="truncate max-w-[280px] capitalize font-medium text-slate-800 dark:text-slate-100 group-hover:text-blue-500">
              <span class="text-xs font-bold text-slate-400 mr-1.5">#{{ i+1 }}</span>
              {{ p.name.toLowerCase() }}
            </div>
            <div class="text-xs font-bold text-slate-600 dark:text-slate-400">
              <span class="text-success">{{ p.aprendices.toLocaleString() }}</span> apr. 
              <span class="text-slate-300 dark:text-slate-600 mx-1">|</span> 
              <span class="text-primary-light">{{ p.fichasCount }}</span> fichas
            </div>
          </div>
        </div>
      </div>

      <!-- Top Fichas & Versiones -->
      <div class="space-y-6">
        <!-- Top Fichas -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Programas con Más Fichas</h3>
          <div class="space-y-3">
            <div 
              v-for="(p, i) in topProgramasPorFichas" 
              :key="p.name" 
              @click="openQuickModal(`Programa: ${p.name}`, 'Desglose por fichas', p.fichas)"
              class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 cursor-pointer hover:text-blue-600 group"
            >
              <span class="truncate max-w-[280px] capitalize font-medium text-slate-800 dark:text-slate-100 group-hover:text-blue-500">
                <span class="text-xs font-bold text-slate-400 mr-1.5">#{{ i+1 }}</span>
                {{ p.name.toLowerCase() }}
              </span>
              <span class="text-xs font-bold text-primary-light">{{ p.fichasCount }} Fichas</span>
            </div>
          </div>
        </div>

        <!-- Múltiples versiones -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Programas con Múltiples Versiones</h3>
          <div class="space-y-3 max-h-48 overflow-y-auto pr-1">
            <div 
              v-for="p in programasConVariasVersiones" 
              :key="p.name" 
              @click="openQuickModal(`Programa: ${p.name}`, `Versiones: ${p.versiones.join(', ')}`, p.fichas)"
              class="flex justify-between items-center text-xs pb-1 cursor-pointer hover:text-blue-500"
            >
              <span class="truncate max-w-[260px] capitalize font-medium text-slate-600 dark:text-slate-400">{{ p.name.toLowerCase() }}</span>
              <span class="font-bold text-slate-800 dark:text-slate-200 bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded">
                v{{ p.versiones.join(', v') }}
              </span>
            </div>
            <div v-if="!programasConVariasVersiones.length" class="text-center text-xs text-slate-400 italic">
              Ninguno detectado con los filtros.
            </div>
          </div>
        </div>
      </div>
      
    </div>

    <!-- 2. APRENDICES -->
    <div v-if="activeSubTab === 'aprendices'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Por Red -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Matrícula Total por Red de Conocimiento</h3>
        <div class="space-y-3">
          <div 
            v-for="r in aprendicesPorRed" 
            :key="r.name" 
            @click="openQuickModal(`Red: ${r.name}`, 'Fichas asociadas a la Red', r.fichas, [{ label: 'Total Aprendices', value: r.count, icon: 'lucide:graduation-cap' }])"
            class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 cursor-pointer hover:text-blue-500 group"
          >
            <span class="font-semibold text-slate-800 dark:text-slate-100 text-xs truncate max-w-[320px] group-hover:text-blue-500">{{ r.name }}</span>
            <span class="font-bold text-secondary">{{ r.count.toLocaleString() }} apr.</span>
          </div>
        </div>
      </div>

      <!-- Por Municipio & Baja Matrícula -->
      <div class="space-y-6">
        <!-- Por Municipio -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Matrícula por Municipio</h3>
          <div class="space-y-3">
            <div 
              v-for="m in aprendicesPorMunicipio" 
              :key="m.name" 
              @click="openQuickModal(`Municipio: ${m.name}`, 'Fichas activas en este municipio', m.fichas, [{ label: 'Aprendices', value: m.count, icon: 'lucide:graduation-cap' }])"
              class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 cursor-pointer hover:text-blue-500 group"
            >
              <span class="capitalize font-medium text-slate-800 dark:text-slate-200 group-hover:text-blue-500">{{ m.name.toLowerCase() }}</span>
              <span class="font-bold text-success">{{ m.count.toLocaleString() }}</span>
            </div>
          </div>
        </div>

        <!-- Baja matrícula -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-72">
          <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-3 flex items-center gap-1 text-danger">
            <Icon icon="lucide:alert-circle" class="w-4.5 h-4.5" />
            ⚠ Fichas con Baja Matrícula (Menos de 15)
          </h3>
          <div class="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-700 pr-1">
            <div 
              v-for="f in programasBajaMatricula" 
              :key="f.ficha" 
              @click="emit('select-ficha', f.raw)"
              class="flex justify-between items-center py-2 text-xs cursor-pointer hover:text-blue-900"
            >
              <div class="space-y-0.5">
                <span class="font-bold text-blue-900 dark:text-blue-400 underline decoration-dotted">{{ f.ficha }}</span>
                <span class="block capitalize font-medium text-slate-600 dark:text-slate-400 truncate max-w-[260px]">{{ f.programa.toLowerCase() }}</span>
              </div>
              <span class="font-black text-danger text-sm bg-danger/10 px-2 py-0.5 rounded">{{ f.matriculados }} apr.</span>
            </div>
            <div v-if="!programasBajaMatricula.length" class="text-center py-8 text-xs text-slate-400 italic">
              No hay fichas con matrícula inferior a 15 aprendices.
            </div>
          </div>
        </div>
      </div>
      
    </div>

    <!-- 3. INSTRUCTORES -->
    <div v-if="activeSubTab === 'instructores'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Ranking Aprendices -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Instructores con Más Aprendices a Cargo</h3>
        <div class="space-y-3">
          <div 
            v-for="(inst, i) in rankingInstructoresPorAprendices" 
            :key="inst.name" 
            @click="openQuickModal(`Instructor: ${inst.name}`, 'Fichas asignadas', inst.fichas, [{ label: 'Aprendices', value: inst.aprendices, icon: 'lucide:graduation-cap' }])"
            class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 cursor-pointer hover:text-blue-500 group"
          >
            <span class="capitalize font-medium text-slate-800 dark:text-slate-100 group-hover:text-blue-500">
              <span class="text-xs font-bold text-slate-400 mr-1.5">#{{ i+1 }}</span>
              {{ inst.name.toLowerCase() }}
            </span>
            <span class="font-bold text-secondary">{{ inst.aprendices.toLocaleString() }} apr. <span class="text-[10px] text-slate-400">({{ inst.fichasCount }} fichas)</span></span>
          </div>
        </div>
      </div>

      <!-- Diversidad e In/Out -->
      <div class="space-y-6">
        <!-- Diversidad de programas -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Mayor Variedad de Programas por Instructor</h3>
          <div class="space-y-3">
            <div 
              v-for="inst in instructoresDiversidad" 
              :key="inst.name" 
              @click="openQuickModal(`Instructor: ${inst.name}`, 'Programas impartidos', inst.fichas)"
              class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 cursor-pointer hover:text-blue-500 group"
            >
              <span class="capitalize font-medium text-slate-800 dark:text-slate-100 group-hover:text-blue-500">{{ inst.name.toLowerCase() }}</span>
              <span class="font-bold text-primary-light text-xs bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded">
                {{ inst.distinctCount }} programas diferentes
              </span>
            </div>
          </div>
        </div>

        <!-- Nuevos vs Salientes -->
        <div class="grid grid-cols-2 gap-4">
          <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-48">
            <h4 class="text-xs font-bold text-success mb-2">🧑‍🏫 Nuevos en 2026</h4>
            <div class="flex-1 overflow-y-auto text-xs space-y-1 divide-y divide-slate-100 dark:divide-slate-700/50">
              <div 
                v-for="i in instructoresNuevos" 
                :key="i.name" 
                @click="openQuickModal(`Instructor Nuevo: ${i.name}`, 'Fichas 2026', i.fichas)"
                class="py-1 capitalize truncate cursor-pointer hover:text-blue-500 font-medium"
              >
                {{ i.name.toLowerCase() }}
              </div>
              <div v-if="!instructoresNuevos.length" class="text-center text-slate-400 italic py-4">Ninguno</div>
            </div>
          </div>

          <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-48">
            <h4 class="text-xs font-bold text-danger mb-2">🧑‍🏫 Salieron en 2026</h4>
            <div class="flex-1 overflow-y-auto text-xs space-y-1 divide-y divide-slate-100 dark:divide-slate-700/50">
              <div 
                v-for="i in instructoresYaNoAparecen" 
                :key="i.name" 
                @click="openQuickModal(`Instructor Saliente: ${i.name}`, 'Fichas asignadas en 2025', i.fichas)"
                class="py-1 capitalize truncate cursor-pointer hover:text-blue-500 font-medium"
              >
                {{ i.name.toLowerCase() }}
              </div>
              <div v-if="!instructoresYaNoAparecen.length" class="text-center text-slate-400 italic py-4">Ninguno</div>
            </div>
          </div>
        </div>
      </div>

    </div>

    <!-- 4. FECHAS Y PLAZOS -->
    <div v-if="activeSubTab === 'fechas'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Inician este mes -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-96">
        <h3 class="text-sm font-bold text-success mb-4 flex items-center gap-1.5">
          <Icon icon="lucide:arrow-up-right" class="w-4 h-4" />
          Formaciones que Inician este Mes
        </h3>
        <div class="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-700 pr-1">
          <div 
            v-for="f in formacionesInicianEsteMes" 
            :key="f.ficha"
            @click="emit('select-ficha', f.raw)"
            class="flex justify-between items-center py-2.5 text-xs cursor-pointer hover:text-blue-900"
          >
            <div class="space-y-0.5">
              <span class="font-bold text-blue-900 dark:text-blue-400 underline decoration-dotted">{{ f.ficha }}</span>
              <span class="block capitalize font-medium text-slate-700 dark:text-slate-300 truncate max-w-[280px]">{{ f.programa.toLowerCase() }}</span>
            </div>
            <span class="font-bold text-success">{{ f.fecha }}</span>
          </div>
          <div v-if="!formacionesInicianEsteMes.length" class="text-center py-12 text-xs text-slate-400 italic">
            Ninguna formación inicia en el mes actual.
          </div>
        </div>
      </div>

      <!-- Terminan este mes -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-96">
        <h3 class="text-sm font-bold text-warning mb-4 flex items-center gap-1.5">
          <Icon icon="lucide:arrow-down-right" class="w-4 h-4" />
          Formaciones que Finalizan este Mes
        </h3>
        <div class="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-700 pr-1">
          <div 
            v-for="f in formacionesTerminanEsteMes" 
            :key="f.ficha"
            @click="emit('select-ficha', f.raw)"
            class="flex justify-between items-center py-2.5 text-xs cursor-pointer hover:text-blue-900"
          >
            <div class="space-y-0.5">
              <span class="font-bold text-blue-900 dark:text-blue-400 underline decoration-dotted">{{ f.ficha }}</span>
              <span class="block capitalize font-medium text-slate-700 dark:text-slate-300 truncate max-w-[280px]">{{ f.programa.toLowerCase() }}</span>
            </div>
            <span class="font-bold text-warning">{{ f.fecha }}</span>
          </div>
          <div v-if="!formacionesTerminanEsteMes.length" class="text-center py-12 text-xs text-slate-400 italic">
            Ninguna formación termina en el mes actual.
          </div>
        </div>
      </div>

    </div>

    <!-- 5. MUNICIPIOS Y OFERTA -->
    <div v-if="activeSubTab === 'municipios'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Cobertura limitada -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Municipios con un Solo Programa Activo</h3>
        <div class="space-y-3">
          <div 
            v-for="m in municipiosUnSoloPrograma" 
            :key="m.name" 
            @click="openQuickModal(`Municipio: ${m.name}`, `Único programa: ${m.programa}`, m.fichas)"
            class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 cursor-pointer hover:text-blue-500"
          >
            <span class="capitalize font-bold text-slate-800 dark:text-slate-100">{{ m.name.toLowerCase() }}</span>
            <span class="capitalize text-slate-500 dark:text-slate-400 text-xs italic">{{ m.programa.toLowerCase() }}</span>
          </div>
          <div v-if="!municipiosUnSoloPrograma.length" class="text-center text-xs text-slate-400 italic py-6">
            Todos los municipios tienen variedad de oferta.
          </div>
        </div>
      </div>

      <!-- Resumen distribución general -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4 font-black">Identificación de Cobertura</h3>
        <p class="text-xs text-slate-500 dark:text-slate-400 mb-4">
          Visualiza los municipios del Caquetá cubiertos por la red de formación administrativa y del ministerio del trabajo.
        </p>
        <div class="bg-slate-50 dark:bg-slate-900/50 p-4 rounded-xl space-y-3 text-xs text-slate-600 dark:text-slate-300">
          <div class="flex justify-between">
            <span>Sede Principal (Florencia):</span>
            <span class="font-bold text-primary">Preponderante</span>
          </div>
          <div class="flex justify-between">
            <span>Municipios Impactados:</span>
            <span class="font-bold text-secondary">{{ aprendicesPorMunicipio.length - 1 }} sub-sedes</span>
          </div>
        </div>
      </div>

    </div>

    <!-- 6. PROYECTOS Y AMBIENTES -->
    <div v-if="activeSubTab === 'proyectos'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Proyectos -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Códigos de Proyecto con Más Fichas</h3>
        <div class="space-y-3">
          <div 
            v-for="proj in proyectosMasFichas" 
            :key="proj.codigo" 
            @click="openQuickModal(`Proyecto #${proj.codigo}`, 'Fichas asociadas a este proyecto', proj.fichas, [{ label: 'Aprendices', value: proj.aprendices, icon: 'lucide:graduation-cap' }])"
            class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2 cursor-pointer hover:text-blue-500"
          >
            <span class="font-semibold text-slate-800 dark:text-slate-100 text-xs">Proyecto #{{ proj.codigo }}</span>
            <span class="font-bold text-secondary">{{ proj.fichasCount }} fichas <span class="text-[10px] text-slate-400">({{ proj.aprendices }} apr.)</span></span>
          </div>
        </div>
      </div>

      <!-- Ambientes compartidos -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-[340px]">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-3 flex items-center gap-1.5">
          <Icon icon="lucide:home" class="w-4.5 h-4.5 text-secondary" />
          Ambientes Multificha (Compartidos)
        </h3>
        <div class="flex-1 overflow-y-auto divide-y divide-slate-100 dark:divide-slate-700 pr-1">
          <div 
            v-for="a in ambientesCompartidos" 
            :key="a.ambiente" 
            @click="openQuickModal(`Ambiente: ${a.ambiente}`, 'Fichas compartiendo este ambiente', a.fichas)"
            class="py-2.5 text-xs cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700/30 p-2 rounded-lg transition-colors"
          >
            <div class="flex justify-between font-bold text-slate-800 dark:text-slate-100 mb-1">
              <span>Ambiente: {{ a.ambiente }}</span>
              <span class="text-success">{{ a.count }} fichas ocupando</span>
            </div>
            <div class="text-[10px] text-slate-500 dark:text-slate-400 flex flex-wrap items-center gap-1.5 mt-1">
              Fichas: <span v-for="f in a.fichas" :key="f.FICHA" class="bg-slate-100 dark:bg-slate-700/60 px-1.5 py-0.5 rounded text-slate-700 dark:text-slate-200 font-bold border border-slate-200 dark:border-slate-600/40">{{ f.FICHA }}</span>
            </div>
          </div>
          <div v-if="!ambientesCompartidos.length" class="text-center py-12 text-xs text-slate-400 italic">
            No se registran ambientes compartidos por múltiples fichas.
          </div>
        </div>
      </div>

    </div>

    <!-- 7. INDICADORES PRO -->
    <div v-if="activeSubTab === 'indicadores'" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      
      <!-- Densidad -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm text-center flex flex-col justify-center py-10">
        <Icon icon="lucide:user-check" class="w-10 h-10 text-secondary mx-auto mb-3" />
        <h4 class="text-2xl font-black text-slate-800 dark:text-slate-100 mb-1">{{ indicadoresPro.densidad }}</h4>
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wide">Densidad Aprendices/Instructor</p>
        <span class="block text-[10px] text-slate-500 mt-2">Basado en {{ indicadoresPro.totalInstructores }} instructores</span>
      </div>

      <!-- Diversidad Muni -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm text-center flex flex-col justify-center py-10">
        <Icon icon="lucide:globe" class="w-10 h-10 text-success mx-auto mb-3" />
        <h4 class="text-lg font-black text-slate-800 dark:text-slate-100 mb-1 capitalize">{{ indicadoresPro.diversidadMuniName.toLowerCase() }}</h4>
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wide">Municipio Mayor Variedad</p>
        <span class="block text-[10px] text-success font-extrabold mt-2">{{ indicadoresPro.diversidadMuniCount }} programas únicos</span>
      </div>

      <!-- Ocupacion promedio -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm text-center flex flex-col justify-center py-10">
        <Icon icon="lucide:activity" class="w-10 h-10 text-warning mx-auto mb-3" />
        <h4 class="text-2xl font-black text-slate-800 dark:text-slate-100 mb-1">{{ indicadoresPro.promedioFicha }}</h4>
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wide">Tamaño Promedio de Ficha</p>
        <span class="block text-[10px] text-slate-500 mt-2">Promedio de aprendices matriculados</span>
      </div>

    </div>

    <!-- 8. AÑOS-TRIMESTRES -->
    <div v-if="activeSubTab === 'trimestres'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      
      <!-- Listado de Trimestres -->
      <div class="lg:col-span-1 bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-[480px]">
        <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-widest mb-4 flex items-center gap-1.5">
          <Icon icon="lucide:calendar-range" class="w-4.5 h-4.5 text-secondary" />
          Distribución por Trimestres
        </h3>
        
        <div class="flex-1 overflow-y-auto space-y-2 pr-1">
          <div 
            v-for="t in estadisticasTrimestres" 
            :key="t.trimestre"
            @click="selectedTrimestreDetalle = t.trimestre"
            class="p-3.5 rounded-xl border cursor-pointer transition-all duration-155 flex items-center justify-between"
            :class="[
              selectedTrimestreDetalle === t.trimestre
                ? 'border-secondary bg-secondary/5 dark:bg-secondary/10 shadow-sm'
                : 'border-slate-100 dark:border-slate-800 hover:border-slate-300 dark:hover:border-slate-700 bg-slate-50/50 dark:bg-slate-900/30'
            ]"
          >
            <div>
              <span class="block text-sm font-bold text-slate-800 dark:text-slate-100 uppercase">{{ t.trimestre }}</span>
              <span class="text-[10px] text-slate-400 font-semibold">{{ t.totalAprendices }} aprendices matriculados</span>
            </div>
            <span class="px-2.5 py-0.5 rounded-lg text-xs font-black bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-200">
              {{ t.fichas.length }}
            </span>
          </div>
        </div>
      </div>

      <!-- Detalle de Fichas del Trimestre Seleccionado -->
      <div class="lg:col-span-2 bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-[480px]">
        <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 uppercase tracking-widest mb-4 flex items-center justify-between">
          <span class="flex items-center gap-1.5 flex-1 min-w-0">
            <Icon icon="lucide:list" class="w-4.5 h-4.5 text-secondary shrink-0" />
            <span class="truncate">Fichas Iniciadas en {{ selectedTrimestreDetalle || 'Selecciona un trimestre' }}</span>
          </span>
          <span class="text-[10px] text-slate-400 font-bold shrink-0">
            {{ fichasTrimestreSeleccionado.length }} formaciones
          </span>
        </h3>

        <div class="flex-1 overflow-y-auto border border-slate-100 dark:border-slate-800 rounded-xl pr-1">
          <table class="w-full text-left text-xs border-collapse">
            <thead>
              <tr class="bg-slate-50 dark:bg-slate-700/50 font-bold text-slate-500 border-b border-slate-150 dark:border-slate-800">
                <th class="p-3">Ficha</th>
                <th class="p-3">Programa</th>
                <th class="p-3">Municipio</th>
                <th class="p-3 text-center">Matriculados</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800">
              <tr 
                v-for="f in fichasTrimestreSeleccionado" 
                :key="f.FICHA" 
                @click="emit('select-ficha', f)"
                class="hover:bg-slate-50/50 dark:hover:bg-slate-700/20 cursor-pointer transition-colors duration-100"
              >
                <td class="p-3 font-bold text-blue-900 dark:text-blue-400">{{ f.FICHA }}</td>
                <td class="p-3 capitalize font-medium text-slate-700 dark:text-slate-200">{{ f["NOMBRE DEL PROGRAMA"].toLowerCase() }}</td>
                <td class="p-3 capitalize text-slate-500 dark:text-slate-400">{{ f.MUNICIPIO.toLowerCase() }}</td>
                <td class="p-3 text-center font-black text-slate-800 dark:text-slate-100">{{ f["APRENDICES MATRICULADOS"] }}</td>
              </tr>
              <tr v-if="!fichasTrimestreSeleccionado.length">
                <td colspan="4" class="p-8 text-center text-slate-400 italic">
                  Selecciona un trimestre a la izquierda para ver su desglose.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </div>

    <!-- Quick Detail Modal -->
    <QuickDetailModal 
      :show="quickModal.show"
      :title="quickModal.title"
      :subtitle="quickModal.subtitle"
      :fichas="quickModal.fichas"
      :extra-metrics="quickModal.extraMetrics"
      @close="quickModal.show = false"
      @select-ficha="(f) => emit('select-ficha', f)"
    />

  </div>
</template>
