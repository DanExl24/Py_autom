<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { Ficha } from '../types'

defineProps<{
  ficha: Ficha | null
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()
</script>

<template>
  <div>
    <!-- Backdrop Overlay -->
    <transition
      enter-active-class="transition-opacity duration-300 ease-out"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200 ease-in"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div 
        v-if="ficha" 
        class="fixed inset-0 bg-slate-900/60 dark:bg-slate-950/80 backdrop-blur-sm z-40"
        @click="emit('close')"
      ></div>
    </transition>

    <!-- Drawer Panel -->
    <div 
      class="fixed top-0 right-0 h-full w-full sm:w-[480px] md:w-[540px] bg-white dark:bg-slate-900 shadow-2xl border-l border-slate-200 dark:border-slate-800 z-50 transform transition-transform duration-300 ease-in-out flex flex-col"
      :class="ficha ? 'translate-x-0' : 'translate-x-full'"
    >
      <!-- Header -->
      <div v-if="ficha" class="bg-primary text-white p-6 flex items-start justify-between">
        <div class="space-y-1">
          <span class="text-[10px] uppercase font-bold text-success bg-success/15 px-2 py-0.5 rounded-full border border-success/30">
            Ficha Técnica
          </span>
          <h2 class="text-2xl font-black tracking-tight">
            {{ ficha.FICHA }}
          </h2>
          <p class="text-xs text-slate-300 line-clamp-1">
            {{ ficha["RED DE CONOCIMIENTO"] }}
          </p>
        </div>
        <button 
          @click="emit('close')" 
          class="text-slate-300 hover:text-white p-1.5 hover:bg-white/10 rounded-full transition-colors"
        >
          <Icon icon="lucide:x" class="w-5 h-5" />
        </button>
      </div>

      <!-- Content (Scrollable) -->
      <div v-if="ficha" class="flex-1 overflow-y-auto p-6 space-y-6">
        
        <!-- Sección 1: Programa de Formación -->
        <div class="space-y-3">
          <h3 class="text-xs font-bold text-primary dark:text-primary-light uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-100 dark:border-slate-800 pb-1">
            <Icon icon="lucide:book-open" class="w-4 h-4 text-secondary" />
            Programa de Formación
          </h3>
          <div class="space-y-4 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Nombre del Programa</span>
              <span class="font-bold text-slate-800 dark:text-slate-100 text-sm capitalize">{{ ficha["NOMBRE DEL PROGRAMA"].toLowerCase() }}</span>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Código Programa</span>
                <span class="font-medium text-slate-700 dark:text-slate-300 text-sm">{{ ficha["CODIGO DE PROGRAMA"] }}</span>
              </div>
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Versión</span>
                <span class="font-medium text-slate-700 dark:text-slate-300 text-sm">{{ ficha.VERSION }}</span>
              </div>
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Nivel</span>
                <span class="font-bold text-slate-800 dark:text-slate-200 text-xs bg-slate-200/50 dark:bg-slate-700 px-2 py-0.5 rounded">{{ ficha.NIVEL }}</span>
              </div>
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Duración Estimada</span>
                <span class="font-bold text-secondary text-sm">{{ ficha.DURACION_CALCULADA }} meses</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Sección 2: Logística y Oferta -->
        <div class="space-y-3">
          <h3 class="text-xs font-bold text-primary dark:text-primary-light uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-100 dark:border-slate-800 pb-1">
            <Icon icon="lucide:map-pin" class="w-4 h-4 text-secondary" />
            Planificación y Logística
          </h3>
          <div class="space-y-4 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Municipio</span>
                <span class="font-bold text-slate-800 dark:text-slate-100 text-sm capitalize">{{ ficha.MUNICIPIO.toLowerCase() }}</span>
              </div>
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Ambiente</span>
                <span class="font-semibold text-slate-700 dark:text-slate-300 text-sm">{{ ficha.AMBIENTE || 'N/A' }}</span>
              </div>
            </div>
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Horario</span>
              <span class="font-medium text-slate-700 dark:text-slate-300 text-xs">{{ ficha.HORARIO || 'N/A' }}</span>
            </div>
            <div class="grid grid-cols-2 gap-4">
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Tipo de Oferta</span>
                <span class="font-semibold text-slate-800 dark:text-slate-200 text-xs bg-slate-200/50 dark:bg-slate-700 px-2 py-0.5 rounded uppercase">{{ ficha["TIPO DE OFERTA"] }}</span>
              </div>
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Matriculados</span>
                <span class="font-black text-success text-base">{{ ficha["APRENDICES MATRICULADOS"] }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Sección 3: Calendario -->
        <div class="space-y-3">
          <h3 class="text-xs font-bold text-primary dark:text-primary-light uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-100 dark:border-slate-800 pb-1">
            <Icon icon="lucide:calendar" class="w-4 h-4 text-secondary" />
            Calendario de Formación
          </h3>
          <div class="grid grid-cols-2 gap-4 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Trimestre Inicio</span>
              <span class="font-semibold text-slate-800 dark:text-slate-200 text-xs">{{ ficha["AÑO /TRIMESTRE DE INICIO"] }}</span>
            </div>
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Fecha Inicio</span>
              <span class="font-medium text-slate-700 dark:text-slate-300 text-xs">{{ ficha["FECHA INICIO"] }}</span>
            </div>
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Fin Etapa Lectiva</span>
              <span class="font-medium text-slate-700 dark:text-slate-300 text-xs">{{ ficha["FECHA FINAL ETAPA LECTIVA"] }}</span>
            </div>
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Terminación</span>
              <span class="font-bold text-warning text-xs">{{ ficha["FECHA TERMINACION"] }}</span>
            </div>
          </div>
        </div>

        <!-- Sección 4: Personal y Apoyos -->
        <div class="space-y-3">
          <h3 class="text-xs font-bold text-primary dark:text-primary-light uppercase tracking-widest flex items-center gap-1.5 border-b border-slate-100 dark:border-slate-800 pb-1">
            <Icon icon="lucide:users" class="w-4 h-4 text-secondary" />
            Personal e Instructores
          </h3>
          <div class="space-y-4 bg-slate-50 dark:bg-slate-800/40 p-4 rounded-xl border border-slate-100 dark:border-slate-800">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Instructor Técnico 2025</span>
                <span class="font-medium text-slate-700 dark:text-slate-300 capitalize text-xs">
                  {{ String(ficha["INSTRUCTOR TÉCNICO 2025"] || 'SIN ASIGNAR').toLowerCase() }}
                </span>
              </div>
              <div>
                <span class="block text-[10px] font-bold text-slate-400 uppercase">Instructor Técnico 2026</span>
                <span class="font-bold text-slate-800 dark:text-slate-100 capitalize text-xs">
                  {{ String(ficha["INSTRUCTOR TÉCNICO 2026"] || 'SIN ASIGNAR').toLowerCase() }}
                </span>
              </div>
            </div>
            <div class="h-px bg-slate-200 dark:bg-slate-700"></div>
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Apoyo Técnico Inglés</span>
              <span class="font-medium text-warning text-xs capitalize">
                {{ String(ficha["APOYO TÉCNICO INGLES"] || 'NINGUNO REGISTRADO').toLowerCase() }}
              </span>
            </div>
            <div>
              <span class="block text-[10px] font-bold text-slate-400 uppercase">Apoyo Transversales</span>
              <span class="font-medium text-slate-700 dark:text-slate-300 text-xs">
                {{ ficha["TRANSVERSALES"] || 'Ninguno registrado' }}
              </span>
            </div>
          </div>
        </div>

      </div>

      <!-- Footer / Acciones -->
      <div class="p-6 border-t border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/60 flex items-center justify-between gap-4 shrink-0">
        <div class="space-y-0.5">
          <span class="block text-[9px] uppercase font-bold text-slate-400">Código Proyecto</span>
          <span class="text-xs font-black text-slate-800 dark:text-slate-100">
            {{ ficha ? (ficha["CÓDIGO PROYECTO"] || 'SIN CÓDIGO') : '' }}
          </span>
        </div>
        <button 
          @click="emit('close')"
          class="px-6 py-2.5 bg-primary hover:bg-primary-light text-white font-bold rounded-xl text-sm transition-colors shadow-sm"
        >
          Entendido
        </button>
      </div>
    </div>
  </div>
</template>
