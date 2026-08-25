<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { Ficha, Kpis } from '../types'
import KpiCard from '../components/dashboard/KpiCard.vue'
import DashboardCharts from '../components/dashboard/DashboardCharts.vue'

defineProps<{
  fichas: Ficha[]
  kpis: Kpis
  proximoInicio: string
  proximaFinalizacion: string
  alertBajaMatricula: number
  alertProximasTerminar: number
  alertSinProyecto: number
}>()
</script>

<template>
  <div class="space-y-6">
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
    <DashboardCharts :fichas="fichas" />
  </div>
</template>
