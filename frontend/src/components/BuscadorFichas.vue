<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import type { Ficha } from '../types'
import KpiCard from './KpiCard.vue'

const props = defineProps<{
  fichas: Ficha[]
}>()

const emit = defineEmits<{
  (e: 'select-ficha', ficha: Ficha): void
}>()

const query = ref('')
const selectedMuni = ref('Todos')
const selectedRed = ref('Todas')
const selectedNivel = ref('Todos')
const selectedTrimestre = ref('Todos')

// Opciones únicas calculadas dinámicamente
const municipios = computed(() => {
  const list = new Set(props.fichas.map(f => f.MUNICIPIO).filter(Boolean))
  return ['Todos', ...Array.from(list).sort()]
})

const redes = computed(() => {
  const list = new Set(props.fichas.map(f => f["RED DE CONOCIMIENTO"]).filter(Boolean))
  return ['Todas', ...Array.from(list).sort()]
})

const niveles = computed(() => {
  const list = new Set(props.fichas.map(f => f.NIVEL).filter(Boolean))
  return ['Todos', ...Array.from(list).sort()]
})

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

const trimestres = computed(() => {
  const list = new Set(props.fichas.map(f => f["AÑO /TRIMESTRE DE INICIO"]).filter(Boolean))
  const sorted = Array.from(list).sort((a, b) => {
    const pa = parseTrimestre(a)
    const pb = parseTrimestre(b)
    if (pa.year !== pb.year) return pa.year - pb.year
    return pa.val - pb.val
  })
  return ['Todos', ...sorted]
})

// Filtrado de fichas reactivo
const filteredFichas = computed(() => {
  const q = query.value.toLowerCase().trim()
  return props.fichas.filter(f => {
    if (selectedMuni.value !== 'Todos' && f.MUNICIPIO !== selectedMuni.value) return false
    if (selectedRed.value !== 'Todas' && f["RED DE CONOCIMIENTO"] !== selectedRed.value) return false
    if (selectedNivel.value !== 'Todos' && f.NIVEL !== selectedNivel.value) return false
    if (selectedTrimestre.value !== 'Todos' && f["AÑO /TRIMESTRE DE INICIO"] !== selectedTrimestre.value) return false
    
    if (q) {
      const instructor2025 = f["INSTRUCTOR TÉCNICO 2025"] || ''
      const instructor2026 = f["INSTRUCTOR TÉCNICO 2026"] || ''
      const searchStr = `
        ${f.FICHA} 
        ${f["NOMBRE DEL PROGRAMA"]} 
        ${f["CODIGO DE PROGRAMA"]} 
        ${f["CÓDIGO PROYECTO"] || ''} 
        ${instructor2025} 
        ${instructor2026} 
        ${f.MUNICIPIO} 
        ${f.AMBIENTE}
      `.toLowerCase()
      if (!searchStr.includes(q)) return false
    }
    return true
  })
})

const filteredKpis = computed(() => {
  const list = filteredFichas.value
  const totalFormaciones = list.length
  const totalAprendices = list.reduce((sum, f) => sum + (f["APRENDICES MATRICULADOS"] || 0), 0)
  const promedio = totalFormaciones ? Number((totalAprendices / totalFormaciones).toFixed(1)) : 0
  
  const instructores = new Set<string>()
  list.forEach(f => {
    const inst25 = f["INSTRUCTOR TÉCNICO 2025"]
    const inst26 = f["INSTRUCTOR TÉCNICO 2026"]
    if (inst25 && inst25 !== 'None' && inst25.trim()) instructores.add(inst25.trim().toUpperCase())
    if (inst26 && inst26 !== 'None' && inst26.trim()) instructores.add(inst26.trim().toUpperCase())
  })
  
  return {
    totalFormaciones,
    totalAprendices,
    promedio,
    totalInstructores: instructores.size
  }
})

const resetFilters = () => {
  query.value = ''
  selectedMuni.value = 'Todos'
  selectedRed.value = 'Todas'
  selectedNivel.value = 'Todos'
  selectedTrimestre.value = 'Todos'
}

const abrirProgramador = async (fichaNum: string) => {
  try {
    const res = await fetch(`/api/abrir-programador/${fichaNum}`)
    if (!res.ok) {
      const errData = await res.json()
      throw new Error(errData.detail || 'Ficha no encontrada en Drive')
    }
    const data = await res.json()
    if (data.url) {
      window.open(data.url, '_blank')
    }
  } catch (e: any) {
    alert(e.message || 'Error al abrir el programador')
  }
}
</script>

<template>
  <div class="space-y-6">
    <!-- Panel de Filtros -->
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm">
      <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-7 gap-4 items-end">
        
        <!-- Búsqueda texto -->
        <div class="lg:col-span-2 space-y-1.5">
          <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Buscar ficha/programa/instructor:
          </label>
          <div class="relative">
            <Icon icon="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              v-model="query"
              type="text" 
              placeholder="Ej: Oscar Yanguas, 2995479..." 
              class="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 dark:focus:border-blue-500"
            />
          </div>
        </div>

        <!-- Filtro Municipio -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Municipio:
          </label>
          <select 
            v-model="selectedMuni"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option v-for="m in municipios" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Filtro Red -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Red de Conocimiento:
          </label>
          <select 
            v-model="selectedRed"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500 truncate"
          >
            <option v-for="r in redes" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>

        <!-- Filtro Nivel -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Nivel:
          </label>
          <select 
            v-model="selectedNivel"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option v-for="n in niveles" :key="n" :value="n">{{ n }}</option>
          </select>
        </div>

        <!-- Filtro Trimestre -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Año/Trimestre:
          </label>
          <select 
            v-model="selectedTrimestre"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500 truncate"
          >
            <option v-for="t in trimestres" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <!-- Botón Reinicio -->
        <button 
          @click="resetFilters"
          class="w-full py-2 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 font-semibold rounded-lg text-sm transition-colors duration-200 flex items-center justify-center gap-1.5"
        >
          <Icon icon="lucide:rotate-ccw" class="w-4 h-4" />
          Limpiar Filtros
        </button>
        
      </div>
    </div>

    <!-- KPIs Dinámicos del Buscador -->
    <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 print:hidden">
      <KpiCard 
        title="Fichas Filtradas" 
        :value="filteredKpis.totalFormaciones" 
        icon="lucide:file-text"
        color-class="text-primary dark:text-primary-light"
        border-class="bg-primary"
      />
      <KpiCard 
        title="Aprendices Filtrados" 
        :value="filteredKpis.totalAprendices.toLocaleString()" 
        icon="lucide:graduation-cap"
        color-class="text-secondary"
        border-class="bg-secondary"
      />
      <KpiCard 
        title="Promedio Ficha" 
        :value="filteredKpis.promedio" 
        icon="lucide:users"
        color-class="text-emerald-500"
        border-class="bg-success"
      />
      <KpiCard 
        title="Instructores Activos" 
        :value="filteredKpis.totalInstructores" 
        icon="lucide:user-check"
        color-class="text-amber-500"
        border-class="bg-warning"
      />
    </div>

    <!-- Resultados -->
    <div class="bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm overflow-hidden flex flex-col">
      
      <!-- Tabla -->
      <div class="overflow-x-auto">
        <table class="w-full border-collapse text-left text-sm text-slate-600 dark:text-slate-300">
          <thead class="bg-slate-50 dark:bg-slate-700/50 text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider border-b border-slate-200 dark:border-slate-700">
            <tr>
              <th class="px-6 py-4">Ficha</th>
              <th class="px-6 py-4">Programa de Formación</th>
              <th class="px-6 py-4">Municipio</th>
              <th class="px-6 py-4 text-center">Apr.</th>
              <th class="px-6 py-4">Instructor 2026</th>
              <th class="px-6 py-4 text-center">Programador</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 dark:divide-slate-700">
            <tr 
              v-for="f in filteredFichas" 
              :key="f.FICHA"
              @click="emit('select-ficha', f)"
              class="hover:bg-slate-50/80 dark:hover:bg-slate-700/30 cursor-pointer transition-colors duration-150"
            >
              <!-- Ficha -->
              <td class="px-6 py-3.5 font-bold text-blue-900 dark:text-blue-400 whitespace-nowrap">
                {{ f.FICHA }}
              </td>
              <!-- Programa -->
              <td class="px-6 py-3.5 font-medium text-slate-800 dark:text-slate-100">
                <div class="capitalize line-clamp-1 max-w-lg font-bold">
                  {{ f["NOMBRE DEL PROGRAMA"].toLowerCase() }}
                </div>
                <div class="flex items-center gap-2 mt-1 text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                  <span class="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-750 rounded dark:text-gray-700 dark:text-slate-300 font-black text-[9px]">
                    {{ f.NIVEL }}
                  </span>
                  <span>•</span>
                  <span>Código: {{ f["CODIGO DE PROGRAMA"] }}</span>
                  <span>•</span>
                  <span>V.{{ f.VERSION }}</span>
                </div>
              </td>
              <!-- Municipio -->
              <td class="px-6 py-3.5 capitalize whitespace-nowrap">
                {{ f.MUNICIPIO.toLowerCase() }}
              </td>
              <!-- Aprendices -->
              <td class="px-6 py-3.5 text-center font-bold text-emerald-600 dark:text-emerald-400">
                {{ f["APRENDICES MATRICULADOS"] }}
              </td>
              <!-- Instructor -->
              <td class="px-6 py-3.5 truncate max-w-xs capitalize text-slate-700 dark:text-slate-400">
                {{ (f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"] || 'SIN ASIGNAR').toLowerCase() }}
              </td>
              <!-- Programador -->
              <td class="px-6 py-3.5 text-center whitespace-nowrap">
                <button 
                  @click.stop="abrirProgramador(f.FICHA)"
                  class="p-1.5 text-slate-400 hover:text-secondary hover:bg-slate-100 dark:hover:bg-slate-700/50 rounded-lg transition-colors inline-flex items-center gap-1 text-xs font-bold"
                  title="Abrir programador de Drive"
                >
                  <Icon icon="lucide:external-link" class="w-4 h-4 text-secondary" />
                  Abrir
                </button>
              </td>
            </tr>
            
            <!-- Sin resultados -->
            <tr v-if="!filteredFichas.length">
              <td colspan="6" class="px-6 py-12 text-center text-slate-400 dark:text-slate-500 italic">
                No se encontraron formaciones con los criterios de búsqueda.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>
