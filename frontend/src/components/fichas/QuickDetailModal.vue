<script setup lang="ts">
import { ref, computed } from 'vue'
import { Icon } from '@iconify/vue'
import type { Ficha } from '../../types'
import { inferJornada } from '../../utils/horario'

const props = defineProps<{
  show: boolean
  title: string
  subtitle?: string
  fichas: Ficha[]
  extraMetrics?: { label: string; value: string | number; icon?: string; color?: string }[]
}>()

const emit = defineEmits<{
  (e: 'close'): void
  (e: 'select-ficha', ficha: Ficha): void
}>()

const searchQuery = ref('')
const selectedJornadaFilter = ref('Todas')

const jornadasUnicas = computed(() => {
  const list = new Set(props.fichas.map(f => inferJornada(f.HORARIO)))
  return ['Todas', ...Array.from(list).sort()]
})

const filteredFichas = computed(() => {
  let list = props.fichas
  if (selectedJornadaFilter.value !== 'Todas') {
    list = list.filter(f => inferJornada(f.HORARIO) === selectedJornadaFilter.value)
  }
  const q = searchQuery.value.toLowerCase().trim()
  if (q) {
    list = list.filter(f => 
      f.FICHA.includes(q) ||
      f["NOMBRE DEL PROGRAMA"].toLowerCase().includes(q) ||
      f.MUNICIPIO.toLowerCase().includes(q) ||
      (f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"] || '').toLowerCase().includes(q)
    )
  }
  return list
})

import { fichasApi } from '../../services/fichasApi'

const totalAprendices = computed(() => props.fichas.reduce((sum, f) => sum + (f["APRENDICES MATRICULADOS"] || 0), 0))

const abrirProgramador = async (fichaNum: string) => {
  try {
    const data = await fichasApi.abrirProgramador(fichaNum)
    if (data.url) window.open(data.url, '_blank')
  } catch (e: any) {
    alert(e.message || 'Error al abrir el programador')
  }
}
</script>

<template>
  <Teleport to="body">
    <transition
      enter-active-class="transition duration-200 ease-out"
      enter-from-class="opacity-0 scale-95"
      enter-to-class="opacity-100 scale-100"
      leave-active-class="transition duration-150 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div 
        v-if="show" 
        class="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 md:p-10"
      >
        <!-- Overlay -->
        <div 
          class="fixed inset-0 bg-slate-900/70 dark:bg-slate-950/85 backdrop-blur-sm transition-opacity"
          @click="emit('close')"
        ></div>

        <!-- Modal Container -->
        <div class="relative w-full max-w-4xl max-h-[90vh] bg-white dark:bg-slate-900 rounded-2xl shadow-2xl border border-slate-200 dark:border-slate-800 flex flex-col overflow-hidden z-10">
          
          <!-- Header -->
          <div class="p-6 bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white flex items-start justify-between border-b border-slate-800">
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-blue-500/20 text-blue-300 border border-blue-400/30">
                  Vista Rápida de Registro
                </span>
                <span class="text-xs text-slate-300 font-bold">• {{ fichas.length }} Ficha(s) enlazada(s)</span>
              </div>
              <h2 class="text-xl sm:text-2xl font-black tracking-tight text-white capitalize">
                {{ title }}
              </h2>
              <p v-if="subtitle" class="text-xs text-slate-300 line-clamp-1 font-medium">
                {{ subtitle }}
              </p>
            </div>
            <button 
              @click="emit('close')"
              class="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-full transition-colors"
              title="Cerrar modal"
            >
              <Icon icon="lucide:x" class="w-6 h-6" />
            </button>
          </div>

          <!-- Métricas Resumen -->
          <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 p-4 bg-slate-50 dark:bg-slate-800/50 border-b border-slate-200 dark:border-slate-800">
            <div class="p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
              <div class="p-2.5 rounded-lg bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
                <Icon icon="lucide:file-text" class="w-5 h-5" />
              </div>
              <div>
                <span class="block text-[10px] font-bold uppercase text-slate-400">Total Fichas</span>
                <span class="text-base font-black text-slate-800 dark:text-slate-100">{{ fichas.length }}</span>
              </div>
            </div>

            <div class="p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3">
              <div class="p-2.5 rounded-lg bg-emerald-50 dark:bg-emerald-900/30 text-emerald-600 dark:text-emerald-400">
                <Icon icon="lucide:graduation-cap" class="w-5 h-5" />
              </div>
              <div>
                <span class="block text-[10px] font-bold uppercase text-slate-400">Total Aprendices</span>
                <span class="text-base font-black text-emerald-600 dark:text-emerald-400">{{ totalAprendices.toLocaleString() }}</span>
              </div>
            </div>

            <!-- Métricas dinámicas adicionales -->
            <template v-if="extraMetrics && extraMetrics.length">
              <div 
                v-for="(m, idx) in extraMetrics" 
                :key="idx"
                class="p-3 bg-white dark:bg-slate-800 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex items-center gap-3"
              >
                <div class="p-2.5 rounded-lg bg-amber-50 dark:bg-amber-900/30 text-amber-600 dark:text-amber-400">
                  <Icon :icon="m.icon || 'lucide:info'" class="w-5 h-5" />
                </div>
                <div>
                  <span class="block text-[10px] font-bold uppercase text-slate-400">{{ m.label }}</span>
                  <span class="text-sm font-bold text-slate-800 dark:text-slate-100 truncate max-w-[120px] block">{{ m.value }}</span>
                </div>
              </div>
            </template>
          </div>

          <!-- Barra de Búsqueda y Filtros dentro del Modal -->
          <div class="p-4 bg-white dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex flex-wrap gap-3 items-center justify-between">
            <div class="relative flex-1 min-w-[200px]">
              <Icon icon="lucide:search" class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
              <input 
                v-model="searchQuery" 
                type="text" 
                placeholder="Filtrar dentro de estos registros (ficha, programa, municipio)..."
                class="w-full pl-9 pr-4 py-1.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs text-slate-800 dark:text-slate-100 placeholder-slate-400 focus:outline-none focus:border-blue-500"
              />
            </div>
            
            <div v-if="jornadasUnicas.length > 2" class="flex items-center gap-2">
              <label class="text-[10px] font-bold text-slate-400 uppercase">Jornada:</label>
              <select 
                v-model="selectedJornadaFilter"
                class="px-2.5 py-1 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-xs font-semibold text-slate-700 dark:text-slate-200"
              >
                <option v-for="j in jornadasUnicas" :key="j" :value="j">{{ j }}</option>
              </select>
            </div>
          </div>

          <!-- Lista de Fichas Asociadas -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
            <div 
              v-for="f in filteredFichas" 
              :key="f.FICHA"
              class="p-4 bg-slate-50 dark:bg-slate-800/40 rounded-xl border border-slate-200 dark:border-slate-700/70 hover:border-blue-400 dark:hover:border-blue-500 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4 group cursor-pointer"
              @click="emit('select-ficha', f)"
            >
              <div class="space-y-1 flex-1">
                <div class="flex flex-wrap items-center gap-2">
                  <span class="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/50 text-blue-900 dark:text-blue-300 font-black text-xs rounded">
                    Ficha {{ f.FICHA }}
                  </span>
                  <span class="px-2 py-0.5 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 font-bold text-[10px] rounded uppercase">
                    {{ f.NIVEL }}
                  </span>
                  <span class="px-2 py-0.5 bg-amber-100 dark:bg-amber-950/60 text-amber-800 dark:text-amber-300 font-extrabold text-[10px] rounded border border-amber-300/40">
                    Jornada: {{ inferJornada(f.HORARIO) }}
                  </span>
                </div>
                <h4 class="font-bold text-slate-900 dark:text-slate-100 text-sm capitalize group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                  {{ f["NOMBRE DEL PROGRAMA"].toLowerCase() }}
                </h4>
                <div class="flex flex-wrap items-center gap-3 text-xs text-slate-500 dark:text-slate-400">
                  <span>📍 <strong class="capitalize">{{ f.MUNICIPIO.toLowerCase() }}</strong></span>
                  <span>•</span>
                  <span>🗓 {{ f.HORARIO || 'Sin horario' }}</span>
                  <span>•</span>
                  <span>👨‍🏫 {{ (f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"] || 'Sin asignar').toLowerCase() }}</span>
                </div>
              </div>

              <div class="flex items-center gap-3 shrink-0">
                <div class="text-right">
                  <span class="block text-xs font-black text-emerald-600 dark:text-emerald-400">{{ f["APRENDICES MATRICULADOS"] }} apr.</span>
                  <span class="text-[10px] text-slate-400 font-semibold">{{ f["AÑO /TRIMESTRE DE INICIO"] }}</span>
                </div>

                <button 
                  @click.stop="abrirProgramador(f.FICHA)"
                  class="p-2 text-slate-400 hover:text-blue-600 hover:bg-blue-50 dark:hover:bg-slate-700 rounded-lg transition-colors border border-slate-200 dark:border-slate-700"
                  title="Abrir programador de Drive"
                >
                  <Icon icon="lucide:external-link" class="w-4 h-4" />
                </button>
              </div>
            </div>

            <div v-if="!filteredFichas.length" class="text-center py-10 text-slate-400 italic text-xs">
              No se encontraron fichas que coincidan con la búsqueda.
            </div>
          </div>

          <!-- Footer -->
          <div class="p-4 bg-slate-50 dark:bg-slate-900 border-t border-slate-200 dark:border-slate-800 flex justify-between items-center">
            <span class="text-xs text-slate-400 font-medium">
              Haz clic en cualquier ficha para abrir su Ficha Técnica completa.
            </span>
            <button 
              @click="emit('close')"
              class="px-5 py-2 bg-slate-800 dark:bg-slate-700 hover:bg-slate-700 dark:hover:bg-slate-600 text-white font-bold text-xs rounded-xl transition-colors"
            >
              Cerrar
            </button>
          </div>

        </div>
      </div>
    </transition>
  </Teleport>
</template>
