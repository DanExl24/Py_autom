<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'
import type { Ficha } from '../types'

const props = defineProps<{
  fichas: Ficha[]
}>()

const chart1Canvas = ref<HTMLCanvasElement | null>(null)
const chart2Canvas = ref<HTMLCanvasElement | null>(null)
const chart3Canvas = ref<HTMLCanvasElement | null>(null)
const chart4Canvas = ref<HTMLCanvasElement | null>(null)
const chart5Canvas = ref<HTMLCanvasElement | null>(null)
const chart6Canvas = ref<HTMLCanvasElement | null>(null)

let chart1: Chart | null = null
let chart2: Chart | null = null
let chart3: Chart | null = null
let chart4: Chart | null = null
let chart5: Chart | null = null
let chart6: Chart | null = null

const buildCharts = () => {
  if (!props.fichas.length) return
  
  const isDark = window.matchMedia('(prefers-color-scheme: dark)').matches
  const textCol = isDark ? '#94A3B8' : '#475569'
  const gridCol = isDark ? '#334155' : '#E2E8F0'
  const primaryColor = '#1E3A5F' // Azul Petróleo
  const secondaryColor = '#2563EB' // Azul
  const successColor = '#10B981' // Verde Esmeralda
  const warningColor = '#F59E0B' // Ámbar
  const dangerColor = '#EF4444' // Rojo
  const accentColor = '#0EA5E9' // Cyan

  // Destruir gráficos previos
  const dest = (c: Chart | null) => c && c.destroy()
  dest(chart1); dest(chart2); dest(chart3); dest(chart4); dest(chart5); dest(chart6);

  // --- 1. APRENDICES POR RED ---
  const redMap: Record<string, number> = {}
  props.fichas.forEach(f => {
    const red = f["RED DE CONOCIMIENTO"] || 'DESCONOCIDA'
    redMap[red] = (redMap[red] || 0) + (f["APRENDICES MATRICULADOS"] || 0)
  })
  const sortedReds = Object.entries(redMap).sort((a, b) => b[1] - a[1])
  const topReds = sortedReds.slice(0, 5)
  const restRedsCount = sortedReds.slice(5).reduce((sum, item) => sum + item[1], 0)
  if (restRedsCount > 0) topReds.push(['OTRAS REDES', restRedsCount])

  if (chart1Canvas.value) {
    const ctx = chart1Canvas.value.getContext('2d')
    if (ctx) {
      chart1 = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: topReds.map(item => item[0].length > 18 ? item[0].slice(0, 16) + '...' : item[0]),
          datasets: [{
            data: topReds.map(item => item[1]),
            backgroundColor: secondaryColor,
            borderRadius: 4,
            borderSkipped: false
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false },
            tooltip: { backgroundColor: '#0F172A' }
          },
          scales: {
            x: { grid: { color: gridCol }, ticks: { color: textCol } },
            y: { grid: { display: false }, ticks: { color: textCol } }
          }
        }
      })
    }
  }

  // --- 2. TIPO DE OFERTA ---
  const ofertaMap: Record<string, number> = {}
  props.fichas.forEach(f => {
    let oferta = String(f["TIPO DE OFERTA"] || 'DESCONOCIDO').trim().toUpperCase()
    if (oferta.includes('ABIERTA')) oferta = 'ABIERTA'
    else if (oferta.includes('CERRADA')) oferta = 'CERRADA'
    ofertaMap[oferta] = (ofertaMap[oferta] || 0) + 1
  })

  if (chart2Canvas.value) {
    const ctx = chart2Canvas.value.getContext('2d')
    if (ctx) {
      chart2 = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(ofertaMap),
          datasets: [{
            data: Object.values(ofertaMap),
            backgroundColor: [primaryColor, successColor, warningColor, dangerColor],
            borderColor: isDark ? '#1E293B' : '#FFFFFF',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: textCol, boxWidth: 10 } }
          },
          cutout: '70%'
        }
      })
    }
  }

  // --- 3. NIVEL DE FORMACIÓN ---
  const nivelMap: Record<string, number> = {}
  props.fichas.forEach(f => {
    const nivel = String(f.NIVEL || 'DESCONOCIDO').trim().toUpperCase()
    nivelMap[nivel] = (nivelMap[nivel] || 0) + 1
  })

  if (chart3Canvas.value) {
    const ctx = chart3Canvas.value.getContext('2d')
    if (ctx) {
      chart3 = new Chart(ctx, {
        type: 'doughnut',
        data: {
          labels: Object.keys(nivelMap),
          datasets: [{
            data: Object.values(nivelMap),
            backgroundColor: [secondaryColor, accentColor, successColor],
            borderColor: isDark ? '#1E293B' : '#FFFFFF',
            borderWidth: 1
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { position: 'bottom', labels: { color: textCol, boxWidth: 10 } }
          },
          cutout: '70%'
        }
      })
    }
  }

  // --- 4. TOP 10 PROGRAMAS ---
  const progMap: Record<string, number> = {}
  props.fichas.forEach(f => {
    const prog = f["NOMBRE DEL PROGRAMA"] || 'DESCONOCIDO'
    progMap[prog] = (progMap[prog] || 0) + f["APRENDICES MATRICULADOS"]
  })
  const topProgs = Object.entries(progMap).sort((a, b) => b[1] - a[1]).slice(0, 10)

  if (chart4Canvas.value) {
    const ctx = chart4Canvas.value.getContext('2d')
    if (ctx) {
      chart4 = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: topProgs.map(item => item[0].length > 15 ? item[0].slice(0, 13) + '...' : item[0]),
          datasets: [{
            data: topProgs.map(item => item[1]),
            backgroundColor: accentColor,
            borderRadius: 4
          }]
        },
        options: {
          indexAxis: 'y',
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { grid: { color: gridCol }, ticks: { color: textCol } },
            y: { grid: { display: false }, ticks: { color: textCol } }
          }
        }
      })
    }
  }

  // --- 5. RANKING MUNICIPIOS (FICHAS) ---
  const muniMap: Record<string, number> = {}
  props.fichas.forEach(f => {
    const muni = f.MUNICIPIO || 'DESCONOCIDO'
    muniMap[muni] = (muniMap[muni] || 0) + 1
  })
  const sortedMunis = Object.entries(muniMap).sort((a, b) => b[1] - a[1]).slice(0, 8)

  if (chart5Canvas.value) {
    const ctx = chart5Canvas.value.getContext('2d')
    if (ctx) {
      chart5 = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: sortedMunis.map(item => item[0].length > 12 ? item[0].slice(0, 10) + '...' : item[0]),
          datasets: [{
            data: sortedMunis.map(item => item[1]),
            backgroundColor: successColor,
            borderRadius: 4
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: textCol } },
            y: { grid: { color: gridCol }, ticks: { color: textCol } }
          }
        }
      })
    }
  }

  // --- 6. TIMELINE APERTURAS ---
  const timelineMap: Record<string, number> = {}
  props.fichas.forEach(f => {
    const start = f["FECHA INICIO"]
    if (start && start.length >= 7) {
      const ym = start.substring(0, 7)
      timelineMap[ym] = (timelineMap[ym] || 0) + 1
    }
  })
  const sortedTimeline = Object.entries(timelineMap).sort((a, b) => a[0].localeCompare(b[0])).slice(-8)

  if (chart6Canvas.value) {
    const ctx = chart6Canvas.value.getContext('2d')
    if (ctx) {
      chart6 = new Chart(ctx, {
        type: 'line',
        data: {
          labels: sortedTimeline.map(item => item[0]),
          datasets: [{
            data: sortedTimeline.map(item => item[1]),
            borderColor: warningColor,
            backgroundColor: warningColor + '15',
            fill: true,
            tension: 0.35,
            borderWidth: 2,
            pointBackgroundColor: warningColor
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { grid: { display: false }, ticks: { color: textCol } },
            y: { grid: { color: gridCol }, ticks: { color: textCol } }
          }
        }
      })
    }
  }
}

onMounted(() => {
  buildCharts()
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', buildCharts)
})

watch(() => props.fichas, buildCharts, { deep: true })

onBeforeUnmount(() => {
  const dest = (c: Chart | null) => c && c.destroy()
  dest(chart1); dest(chart2); dest(chart3); dest(chart4); dest(chart5); dest(chart6);
  window.matchMedia('(prefers-color-scheme: dark)').removeEventListener('change', buildCharts)
})
</script>

<template>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    
    <!-- Chart 1: Aprendices por Red -->
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-80">
      <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 mb-4 flex items-center gap-2 uppercase tracking-wider">
        <span class="w-2 h-2 bg-secondary rounded-full"></span>
        Aprendices por Red
      </h3>
      <div class="relative flex-1 min-h-0">
        <canvas ref="chart1Canvas"></canvas>
      </div>
    </div>

    <!-- Chart 2: Tipo de Oferta -->
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-80">
      <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 mb-4 flex items-center gap-2 uppercase tracking-wider">
        <span class="w-2 h-2 bg-primary-light rounded-full"></span>
        Distribución de Oferta
      </h3>
      <div class="relative flex-1 min-h-0">
        <canvas ref="chart2Canvas"></canvas>
      </div>
    </div>

    <!-- Chart 3: Nivel de Formación -->
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-80">
      <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 mb-4 flex items-center gap-2 uppercase tracking-wider">
        <span class="w-2 h-2 bg-success rounded-full"></span>
        Nivel (Técnico vs Tecnólogo)
      </h3>
      <div class="relative flex-1 min-h-0">
        <canvas ref="chart3Canvas"></canvas>
      </div>
    </div>

    <!-- Chart 4: Top 10 Programas -->
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-80 md:col-span-2 lg:col-span-1">
      <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 mb-4 flex items-center gap-2 uppercase tracking-wider">
        <span class="w-2 h-2 bg-sky-500 rounded-full"></span>
        Top 10 Programas
      </h3>
      <div class="relative flex-1 min-h-0">
        <canvas ref="chart4Canvas"></canvas>
      </div>
    </div>

    <!-- Chart 5: Municipios -->
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-80">
      <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 mb-4 flex items-center gap-2 uppercase tracking-wider">
        <span class="w-2 h-2 bg-emerald-500 rounded-full"></span>
        Ranking Municipios (Fichas)
      </h3>
      <div class="relative flex-1 min-h-0">
        <canvas ref="chart5Canvas"></canvas>
      </div>
    </div>

    <!-- Chart 6: Timeline Aperturas -->
    <div class="bg-white dark:bg-slate-800 p-5 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm flex flex-col h-80">
      <h3 class="text-xs font-bold text-slate-700 dark:text-slate-200 mb-4 flex items-center gap-2 uppercase tracking-wider">
        <span class="w-2 h-2 bg-warning rounded-full"></span>
        Timeline de Aperturas
      </h3>
      <div class="relative flex-1 min-h-0">
        <canvas ref="chart6Canvas"></canvas>
      </div>
    </div>

  </div>
</template>
