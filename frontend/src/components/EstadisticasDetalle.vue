<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import type { Ficha } from '../types'

const props = defineProps<{
  fichas: Ficha[]
}>()

const emit = defineEmits<{
  (e: 'select-ficha', ficha: Ficha): void
}>()

const activeSubTab = ref('programas')

const tabs = [
  { id: 'programas', name: 'Programas', icon: 'lucide:book-open' },
  { id: 'aprendices', name: 'Aprendices', icon: 'lucide:graduation-cap' },
  { id: 'instructores', name: 'Instructores', icon: 'lucide:users' },
  { id: 'fechas', name: 'Fechas y Plazos', icon: 'lucide:calendar' },
  { id: 'municipios', name: 'Municipios y Oferta', icon: 'lucide:map-pin' },
  { id: 'proyectos', name: 'Proyectos y Ambientes', icon: 'lucide:layers' },
  { id: 'indicadores', name: 'Indicadores Pro', icon: 'lucide:activity' }
]

// --- COMPUTACIONES ---

// 1. PROGRAMAS
const topProgramasPorAprendices = computed(() => {
  const map: Record<string, { name: string; aprendices: number; fichas: number }> = {}
  props.fichas.forEach(f => {
    const prog = f["NOMBRE DEL PROGRAMA"] || 'DESCONOCIDO'
    if (!map[prog]) map[prog] = { name: prog, aprendices: 0, fichas: 0 }
    map[prog].aprendices += f["APRENDICES MATRICULADOS"]
    map[prog].fichas += 1
  })
  return Object.values(map).sort((a, b) => b.aprendices - a.aprendices).slice(0, 10)
})

const topProgramasPorFichas = computed(() => {
  const map: Record<string, { name: string; aprendices: number; fichas: number }> = {}
  props.fichas.forEach(f => {
    const prog = f["NOMBRE DEL PROGRAMA"] || 'DESCONOCIDO'
    if (!map[prog]) map[prog] = { name: prog, aprendices: 0, fichas: 0 }
    map[prog].aprendices += f["APRENDICES MATRICULADOS"]
    map[prog].fichas += 1
  })
  return Object.values(map).sort((a, b) => b.fichas - a.fichas).slice(0, 10)
})

const programasConVariasVersiones = computed(() => {
  const map: Record<string, Set<number>> = {}
  props.fichas.forEach(f => {
    const prog = f["NOMBRE DEL PROGRAMA"]
    const ver = f.VERSION
    if (prog) {
      if (!map[prog]) map[prog] = new Set()
      if (ver) map[prog].add(ver)
    }
  })
  return Object.entries(map)
    .filter(([_, versiones]) => versiones.size > 1)
    .map(([name, versiones]) => ({ name, versiones: Array.from(versiones).sort() }))
})

// 2. APRENDICES
const aprendicesPorRed = computed(() => {
  const map: Record<string, number> = {}
  props.fichas.forEach(f => {
    const red = f["RED DE CONOCIMIENTO"] || 'DESCONOCIDA'
    map[red] = (map[red] || 0) + f["APRENDICES MATRICULADOS"]
  })
  return Object.entries(map).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count)
})

const aprendicesPorMunicipio = computed(() => {
  const map: Record<string, number> = {}
  props.fichas.forEach(f => {
    const muni = f.MUNICIPIO || 'DESCONOCIDO'
    map[muni] = (map[muni] || 0) + f["APRENDICES MATRICULADOS"]
  })
  return Object.entries(map).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count)
})

const programasBajaMatricula = computed(() => {
  return props.fichas
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
  const map: Record<string, { name: string; aprendices: number; fichas: number }> = {}
  props.fichas.forEach(f => {
    const inst = f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"]
    if (inst && inst !== 'None' && inst.trim() !== '') {
      const key = inst.trim().toUpperCase()
      if (!map[key]) map[key] = { name: inst, aprendices: 0, fichas: 0 }
      map[key].aprendices += f["APRENDICES MATRICULADOS"]
      map[key].fichas += 1
    }
  })
  return Object.values(map).sort((a, b) => b.aprendices - a.aprendices).slice(0, 10)
})

const instructoresDiversidad = computed(() => {
  const map: Record<string, Set<string>> = {}
  props.fichas.forEach(f => {
    const inst = f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"]
    const prog = f["NOMBRE DEL PROGRAMA"]
    if (inst && inst !== 'None' && inst.trim() !== '' && prog) {
      const key = inst.trim().toUpperCase()
      if (!map[key]) map[key] = new Set()
      map[key].add(prog)
    }
  })
  return Object.entries(map)
    .map(([name, progs]) => ({ name, distinctCount: progs.size, programas: Array.from(progs) }))
    .sort((a, b) => b.distinctCount - a.distinctCount)
    .slice(0, 10)
})

const instructoresNuevos = computed(() => {
  // Instructores que aparecen en 2026 pero no en 2025
  const insts2025 = new Set<string>()
  const insts2026 = new Set<string>()
  props.fichas.forEach(f => {
    const i25 = f["INSTRUCTOR TÉCNICO 2025"]
    const i26 = f["INSTRUCTOR TÉCNICO 2026"]
    if (i25 && i25 !== 'None' && i25.trim()) insts2025.add(i25.trim().toUpperCase())
    if (i26 && i26 !== 'None' && i26.trim()) insts2026.add(i26.trim().toUpperCase())
  })
  const nuevos = Array.from(insts2026).filter(i => !insts2025.has(i))
  return nuevos.sort()
})

const instructoresYaNoAparecen = computed(() => {
  // Instructores que aparecen en 2025 pero no en 2026
  const insts2025 = new Set<string>()
  const insts2026 = new Set<string>()
  props.fichas.forEach(f => {
    const i25 = f["INSTRUCTOR TÉCNICO 2025"]
    const i26 = f["INSTRUCTOR TÉCNICO 2026"]
    if (i25 && i25 !== 'None' && i25.trim()) insts2025.add(i25.trim().toUpperCase())
    if (i26 && i26 !== 'None' && i26.trim()) insts2026.add(i26.trim().toUpperCase())
  })
  const salientes = Array.from(insts2025).filter(i => !insts2026.has(i))
  return salientes.sort()
})

// 4. FECHAS
const formacionesInicianEsteMes = computed(() => {
  const currentMonth = new Date().getMonth() // 0-11
  return props.fichas
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
  const currentMonth = new Date().getMonth() // 0-11
  return props.fichas
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
  const map: Record<string, Set<string>> = {}
  props.fichas.forEach(f => {
    const muni = f.MUNICIPIO
    const prog = f["NOMBRE DEL PROGRAMA"]
    if (muni && prog) {
      if (!map[muni]) map[muni] = new Set()
      map[muni].add(prog)
    }
  })
  return Object.entries(map)
    .filter(([_, progs]) => progs.size === 1)
    .map(([name, progs]) => ({ name, programa: Array.from(progs)[0] }))
})

// 6. PROYECTOS Y AMBIENTES
const proyectosMasFichas = computed(() => {
  const map: Record<string, { codigo: number; fichas: number; aprendices: number }> = {}
  props.fichas.forEach(f => {
    const proj = f["CÓDIGO PROYECTO"]
    if (proj && proj !== 0) {
      if (!map[proj]) map[proj] = { codigo: proj, fichas: 0, aprendices: 0 }
      map[proj].fichas += 1
      map[proj].aprendices += f["APRENDICES MATRICULADOS"]
    }
  })
  return Object.values(map).sort((a, b) => b.fichas - a.fichas).slice(0, 10)
})

const ambientesMasUsados = computed(() => {
  const map: Record<string, Set<string>> = {}
  props.fichas.forEach(f => {
    const amb = String(f.AMBIENTE || '').trim()
    if (amb && amb !== 'None' && amb !== 'nan' && amb !== '') {
      if (!map[amb]) map[amb] = new Set()
      map[amb].add(f.FICHA)
    }
  })
  return Object.entries(map)
    .map(([ambiente, fichasSet]) => ({ ambiente, count: fichasSet.size, fichas: Array.from(fichasSet) }))
    .sort((a, b) => b.count - a.count)
})

const ambientesCompartidos = computed(() => {
  return ambientesMasUsados.value.filter(a => a.count > 1)
})

// 7. INDICADORES PRO
const indicadoresPro = computed(() => {
  const totalFichas = props.fichas.length
  const totalAprendices = props.fichas.reduce((sum, f) => sum + f["APRENDICES MATRICULADOS"], 0)
  
  // Total de instructores únicos
  const instructoresSet = new Set<string>()
  props.fichas.forEach(f => {
    const i25 = f["INSTRUCTOR TÉCNICO 2025"]
    const i26 = f["INSTRUCTOR TÉCNICO 2026"]
    if (i25 && i25 !== 'None' && i25.trim()) instructoresSet.add(i25.trim().toUpperCase())
    if (i26 && i26 !== 'None' && i26.trim()) instructoresSet.add(i26.trim().toUpperCase())
  })
  
  const densidadAprendizInstructor = instructoresSet.size 
    ? (totalAprendices / instructoresSet.size).toFixed(1) 
    : '0'
    
  // Municipios con mayor variedad
  const muniProgMap: Record<string, Set<string>> = {}
  props.fichas.forEach(f => {
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
</script>

<template>
  <div class="space-y-6">
    
    <!-- Subpestañas estadísticas -->
    <div class="flex flex-wrap gap-2 border-b border-slate-200 dark:border-slate-800 pb-px">
      <button 
        v-for="t in tabs" 
        :key="t.id"
        @click="activeSubTab = t.id"
        class="flex items-center gap-2 px-4 py-2.5 text-xs font-bold uppercase tracking-wider border-b-2 -mb-px transition-colors duration-150"
        :class="activeSubTab === t.id 
          ? 'border-primary dark:border-primary-light text-primary dark:text-primary-light' 
          : 'border-transparent text-slate-500 hover:text-slate-800 dark:hover:text-slate-200'"
      >
        <Icon :icon="t.icon" class="w-4 h-4" />
        {{ t.name }}
      </button>
    </div>

    <!-- CONTENIDOS DE SUBPESTAÑAS -->
    
    <!-- 1. PROGRAMAS -->
    <div v-if="activeSubTab === 'programas'" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      
      <!-- Top Aprendices -->
      <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col">
        <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Programas con Más Aprendices</h3>
        <div class="space-y-3">
          <div v-for="(p, i) in topProgramasPorAprendices" :key="p.name" class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
            <div class="truncate max-w-[280px] capitalize font-medium text-slate-800 dark:text-slate-100">
              <span class="text-xs font-bold text-slate-400 mr-1.5">#{{ i+1 }}</span>
              {{ p.name.toLowerCase() }}
            </div>
            <div class="text-xs font-bold text-slate-600 dark:text-slate-400">
              <span class="text-success">{{ p.aprendices.toLocaleString() }}</span> apr. 
              <span class="text-slate-300 dark:text-slate-600 mx-1">|</span> 
              <span class="text-primary-light">{{ p.fichas }}</span> fichas
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
            <div v-for="(p, i) in topProgramasPorFichas" :key="p.name" class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
              <span class="truncate max-w-[280px] capitalize font-medium text-slate-800 dark:text-slate-100">
                <span class="text-xs font-bold text-slate-400 mr-1.5">#{{ i+1 }}</span>
                {{ p.name.toLowerCase() }}
              </span>
              <span class="text-xs font-bold text-primary-light">{{ p.fichas }} Fichas</span>
            </div>
          </div>
        </div>

        <!-- Múltiples versiones -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Programas con Múltiples Versiones</h3>
          <div class="space-y-3 max-h-48 overflow-y-auto pr-1">
            <div v-for="p in programasConVariasVersiones" :key="p.name" class="flex justify-between items-center text-xs pb-1">
              <span class="truncate max-w-[260px] capitalize font-medium text-slate-600 dark:text-slate-400">{{ p.name.toLowerCase() }}</span>
              <span class="font-bold text-slate-800 dark:text-slate-200 bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded">
                v{{ p.versiones.join(', v') }}
              </span>
            </div>
            <div v-if="!programasConVariasVersiones.length" class="text-center text-xs text-slate-400 italic">
              Ninguno detectado.
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
          <div v-for="r in aprendicesPorRed" :key="r.name" class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
            <span class="font-semibold text-slate-800 dark:text-slate-100 text-xs truncate max-w-[320px]">{{ r.name }}</span>
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
            <div v-for="m in aprendicesPorMunicipio" :key="m.name" class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
              <span class="capitalize font-medium text-slate-800 dark:text-slate-200">{{ m.name.toLowerCase() }}</span>
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
          <div v-for="(inst, i) in rankingInstructoresPorAprendices" :key="inst.name" class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
            <span class="capitalize font-medium text-slate-800 dark:text-slate-100">
              <span class="text-xs font-bold text-slate-400 mr-1.5">#{{ i+1 }}</span>
              {{ inst.name.toLowerCase() }}
            </span>
            <span class="font-bold text-secondary">{{ inst.aprendices.toLocaleString() }} apr. <span class="text-[10px] text-slate-400">({{ inst.fichas }} fichas)</span></span>
          </div>
        </div>
      </div>

      <!-- Diversidad e In/Out -->
      <div class="space-y-6">
        <!-- Diversidad de programas -->
        <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
          <h3 class="text-sm font-bold text-slate-700 dark:text-slate-200 mb-4">Mayor Variedad de Programas por Instructor</h3>
          <div class="space-y-3">
            <div v-for="inst in instructoresDiversidad" :key="inst.name" class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
              <span class="capitalize font-medium text-slate-800 dark:text-slate-100">{{ inst.name.toLowerCase() }}</span>
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
              <div v-for="i in instructoresNuevos" :key="i" class="py-1 capitalize truncate">{{ i.toLowerCase() }}</div>
              <div v-if="!instructoresNuevos.length" class="text-center text-slate-400 italic py-4">Ninguno</div>
            </div>
          </div>

          <div class="bg-white dark:bg-slate-800 p-4 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-48">
            <h4 class="text-xs font-bold text-danger mb-2">🧑‍🏫 Salieron en 2026</h4>
            <div class="flex-1 overflow-y-auto text-xs space-y-1 divide-y divide-slate-100 dark:divide-slate-700/50">
              <div v-for="i in instructoresYaNoAparecen" :key="i" class="py-1 capitalize truncate">{{ i.toLowerCase() }}</div>
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
          <div v-for="m in municipiosUnSoloPrograma" :key="m.name" class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
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
          <div v-for="proj in proyectosMasFichas" :key="proj.codigo" class="flex justify-between items-center text-sm border-b border-slate-100 dark:border-slate-700 pb-2">
            <span class="font-semibold text-slate-800 dark:text-slate-100 text-xs">Proyecto #{{ proj.codigo }}</span>
            <span class="font-bold text-secondary">{{ proj.fichas }} fichas <span class="text-[10px] text-slate-400">({{ proj.aprendices }} apr.)</span></span>
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
          <div v-for="a in ambientesCompartidos" :key="a.ambiente" class="py-2.5 text-xs">
            <div class="flex justify-between font-bold text-slate-800 dark:text-slate-100 mb-1">
              <span>Ambiente: {{ a.ambiente }}</span>
              <span class="text-success">{{ a.count }} fichas ocupando</span>
            </div>
            <div class="text-[10px] text-slate-400 flex flex-wrap gap-1">
              Fichas: <span v-for="f in a.fichas" :key="f" class="bg-slate-100 dark:bg-slate-700 px-1 rounded">{{ f }}</span>
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

  </div>
</template>
