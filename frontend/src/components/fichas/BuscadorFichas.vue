<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import type { Ficha } from '../../types'
import KpiCard from '../dashboard/KpiCard.vue'
import QuickDetailModal from './QuickDetailModal.vue'
import { inferJornada, getHorariosGrouped, normalizeHorario } from '../../utils/horario'

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
const selectedJornada = ref('Todas')
const selectedHorario = ref('Todos')
const fechaDesde = ref('')
const fechaHasta = ref('')

const showTopHorariosModal = ref(false)

// Estado para Quick Detail Modal
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

const jornadas = ['Todas', 'Mañana', 'Tarde', 'Mixta', 'Noche', 'Horario Compuesto', 'Sin especificar']

const horariosUnicos = computed<string[]>(() => {
  const list = new Set<string>()
  props.fichas.forEach(f => {
    if (f.HORARIO && f.HORARIO.trim()) list.add(f.HORARIO.trim())
  })
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

// Horarios más repetidos
const horariosMasRepetidos = computed(() => {
  return getHorariosGrouped(filteredFichas.value)
})

// Filtrado de fichas reactivo
const filteredFichas = computed(() => {
  const q = query.value.toLowerCase().trim()
  return props.fichas.filter(f => {
    if (selectedMuni.value !== 'Todos' && f.MUNICIPIO !== selectedMuni.value) return false
    if (selectedRed.value !== 'Todas' && f["RED DE CONOCIMIENTO"] !== selectedRed.value) return false
    if (selectedNivel.value !== 'Todos' && f.NIVEL !== selectedNivel.value) return false
    if (selectedTrimestre.value !== 'Todos' && f["AÑO /TRIMESTRE DE INICIO"] !== selectedTrimestre.value) return false
    
    // Filtro por Jornada
    if (selectedJornada.value !== 'Todas') {
      const jInferida = inferJornada(f.HORARIO)
      if (jInferida !== selectedJornada.value) return false
    }

    // Filtro por Horario
    if (selectedHorario.value !== 'Todos') {
      if (normalizeHorario(f.HORARIO) !== normalizeHorario(selectedHorario.value)) return false
    }

    // Filtro por Rango de Fechas
    if (fechaDesde.value) {
      if (!f["FECHA INICIO"] || f["FECHA INICIO"] < fechaDesde.value) return false
    }
    if (fechaHasta.value) {
      if (!f["FECHA TERMINACION"] || f["FECHA TERMINACION"] > fechaHasta.value) return false
    }
    
    if (q) {
      const instructor2025 = f["INSTRUCTOR TÉCNICO 2025"] || ''
      const instructor2026 = f["INSTRUCTOR TÉCNICO 2026"] || ''
      const jInferida = inferJornada(f.HORARIO)
      const searchStr = `
        ${f.FICHA} 
        ${f["NOMBRE DEL PROGRAMA"]} 
        ${f["CODIGO DE PROGRAMA"]} 
        ${f["CÓDIGO PROYECTO"] || ''} 
        ${instructor2025} 
        ${instructor2026} 
        ${f.MUNICIPIO} 
        ${f.AMBIENTE}
        ${f.HORARIO || ''}
        ${jInferida}
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
  selectedJornada.value = 'Todas'
  selectedHorario.value = 'Todos'
  fechaDesde.value = ''
  fechaHasta.value = ''
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
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 items-end">
        
        <!-- Búsqueda texto -->
        <div class="lg:col-span-2 space-y-1.5">
          <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
            Buscar ficha/programa/instructor/horario:
          </label>
          <div class="relative">
            <Icon icon="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input 
              v-model="query"
              type="text" 
              placeholder="Ej: Oscar Yanguas, 2995479, Mañana, 06:00..." 
              class="w-full pl-9 pr-4 py-2 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500 dark:focus:border-blue-500"
            />
          </div>
        </div>

        <!-- Filtro Jornada -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Icon icon="lucide:sun-moon" class="w-3.5 h-3.5 text-amber-500" />
            Jornada:
          </label>
          <select 
            v-model="selectedJornada"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option v-for="j in jornadas" :key="j" :value="j">{{ j }}</option>
          </select>
        </div>

        <!-- Filtro Horario Completo -->
        <div class="space-y-1.5">
          <label class="text-xs font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider flex items-center gap-1">
            <Icon icon="lucide:clock" class="w-3.5 h-3.5 text-blue-500" />
            Horario Específico:
          </label>
          <select 
            v-model="selectedHorario"
            class="w-full px-3 py-2 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-sm text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500 truncate"
          >
            <option v-for="h in horariosUnicos" :key="h" :value="h">{{ h }}</option>
          </select>
        </div>

      </div>

      <!-- Fila 2 de Filtros (Municipio, Red, Nivel, Trimestre, Fechas) -->
      <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4 items-end pt-2 border-t border-slate-100 dark:border-slate-700/60">
        
        <!-- Filtro Municipio -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Municipio:</label>
          <select 
            v-model="selectedMuni"
            class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option v-for="m in municipios" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>

        <!-- Filtro Red -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Red de Conocimiento:</label>
          <select 
            v-model="selectedRed"
            class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500 truncate"
          >
            <option v-for="r in redes" :key="r" :value="r">{{ r }}</option>
          </select>
        </div>

        <!-- Filtro Nivel -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Nivel:</label>
          <select 
            v-model="selectedNivel"
            class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          >
            <option v-for="n in niveles" :key="n" :value="n">{{ n }}</option>
          </select>
        </div>

        <!-- Filtro Trimestre -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Trimestre Inicio:</label>
          <select 
            v-model="selectedTrimestre"
            class="w-full px-3 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500 truncate"
          >
            <option v-for="t in trimestres" :key="t" :value="t">{{ t }}</option>
          </select>
        </div>

        <!-- Fecha Desde -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Inicio Desde:</label>
          <input 
            v-model="fechaDesde"
            type="date"
            class="w-full px-2 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

        <!-- Fecha Hasta -->
        <div class="space-y-1">
          <label class="text-[10px] font-bold text-slate-400 uppercase">Termina Hasta:</label>
          <input 
            v-model="fechaHasta"
            type="date"
            class="w-full px-2 py-1.5 bg-slate-50 dark:bg-slate-700/50 border border-slate-200 dark:border-slate-600 rounded-lg text-xs text-slate-800 dark:text-slate-100 focus:outline-none focus:border-blue-500"
          />
        </div>

      </div>

      <!-- Botones de Acción -->
      <div class="flex flex-wrap items-center justify-between gap-3 pt-2">
        <button 
          @click="showTopHorariosModal = !showTopHorariosModal"
          class="py-1.5 px-3 bg-blue-50 dark:bg-blue-900/30 hover:bg-blue-100 dark:hover:bg-blue-900/50 text-blue-700 dark:text-blue-300 font-bold rounded-lg text-xs transition-colors flex items-center gap-1.5 border border-blue-200 dark:border-blue-800"
        >
          <Icon icon="lucide:bar-chart-2" class="w-4 h-4" />
          {{ showTopHorariosModal ? 'Ocultar Horarios Repetidos' : 'Ver Horarios Más Repetidos' }}
        </button>

        <button 
          @click="resetFilters"
          class="py-1.5 px-4 bg-slate-100 dark:bg-slate-700 hover:bg-slate-200 dark:hover:bg-slate-600 text-slate-700 dark:text-slate-200 font-semibold rounded-lg text-xs transition-colors duration-200 flex items-center justify-center gap-1.5"
        >
          <Icon icon="lucide:rotate-ccw" class="w-3.5 h-3.5" />
          Limpiar Filtros
        </button>
      </div>

    </div>

    <!-- Panel Desplegable: Horarios Más Repetidos -->
    <div v-if="showTopHorariosModal" class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-bold text-slate-800 dark:text-slate-100 flex items-center gap-2">
          <Icon icon="lucide:clock" class="w-4 h-4 text-blue-500" />
          Horarios más repetidos y Fichas enlazadas
        </h3>
        <span class="text-xs text-slate-400 font-medium">{{ horariosMasRepetidos.length }} Horarios identificados</span>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3 max-h-72 overflow-y-auto pr-1">
        <div 
          v-for="hg in horariosMasRepetidos" 
          :key="hg.horario"
          @click="openQuickModal(`Horario: ${hg.horario}`, `Jornada: ${hg.jornada}`, hg.fichas, [{ label: 'Aprendices', value: hg.totalAprendices, icon: 'lucide:graduation-cap' }])"
          class="p-3 bg-slate-50 dark:bg-slate-700/40 rounded-xl border border-slate-200 dark:border-slate-600/60 hover:border-blue-400 transition-all cursor-pointer space-y-2 group"
        >
          <div class="flex items-start justify-between gap-2">
            <span class="text-xs font-bold text-slate-800 dark:text-slate-200 group-hover:text-blue-600 dark:group-hover:text-blue-400 line-clamp-2">
              {{ hg.horario }}
            </span>
            <span class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/60 text-blue-800 dark:text-blue-300 font-black text-[10px] rounded-full shrink-0">
              {{ hg.count }} fichas
            </span>
          </div>

          <div class="flex items-center justify-between text-[11px] text-slate-500 dark:text-slate-400 pt-1 border-t border-slate-200/60 dark:border-slate-600/40">
            <span class="px-1.5 py-0.5 rounded bg-amber-100 dark:bg-amber-950/80 text-amber-800 dark:text-amber-300 font-extrabold text-[9px]">
              {{ hg.jornada }}
            </span>
            <span class="font-bold text-emerald-600 dark:text-emerald-400">
              {{ hg.totalAprendices }} aprendices
            </span>
          </div>
        </div>
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
              <th class="px-6 py-4">Horario / Jornada</th>
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
                <div class="capitalize line-clamp-1 max-w-md font-bold">
                  {{ f["NOMBRE DEL PROGRAMA"].toLowerCase() }}
                </div>
                <div class="flex items-center gap-2 mt-1 text-[10px] text-slate-400 font-semibold uppercase tracking-wider">
                  <span class="px-1.5 py-0.5 bg-slate-100 dark:bg-slate-700 rounded text-slate-700 dark:text-slate-300 font-black text-[9px]">
                    {{ f.NIVEL }}
                  </span>
                  <span>•</span>
                  <span>Código: {{ f["CODIGO DE PROGRAMA"] }}</span>
                  <span>•</span>
                  <span>V.{{ f.VERSION }}</span>
                </div>
              </td>
              <!-- Horario / Jornada -->
              <td class="px-6 py-3.5 max-w-xs">
                <div class="text-xs font-semibold text-slate-800 dark:text-slate-200 line-clamp-2">
                  {{ f.HORARIO || 'SIN HORARIO' }}
                </div>
                <div class="mt-1">
                  <span 
                    class="px-2 py-0.5 text-[10px] font-black rounded uppercase tracking-wider inline-block"
                    :class="{
                      'bg-amber-100 text-amber-800 dark:bg-amber-950/80 dark:text-amber-300': inferJornada(f.HORARIO) === 'Mañana',
                      'bg-orange-100 text-orange-800 dark:bg-orange-950/80 dark:text-orange-300': inferJornada(f.HORARIO) === 'Tarde',
                      'bg-purple-100 text-purple-800 dark:bg-purple-950/80 dark:text-purple-300': inferJornada(f.HORARIO) === 'Mixta',
                      'bg-indigo-100 text-indigo-800 dark:bg-indigo-950/80 dark:text-indigo-300': inferJornada(f.HORARIO) === 'Noche',
                      'bg-rose-100 text-rose-800 dark:bg-rose-950/80 dark:text-rose-300': inferJornada(f.HORARIO) === 'Horario Compuesto',
                      'bg-slate-100 text-slate-700 dark:bg-slate-700 dark:text-slate-300': inferJornada(f.HORARIO) === 'Sin especificar' || inferJornada(f.HORARIO) === 'No registrada'
                    }"
                  >
                    Jornada: {{ inferJornada(f.HORARIO) }}
                  </span>
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
              <td colspan="7" class="px-6 py-12 text-center text-slate-400 dark:text-slate-500 italic">
                No se encontraron formaciones con los criterios de búsqueda.
              </td>
            </tr>
          </tbody>
        </table>
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
