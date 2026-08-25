<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { Ficha, Kpis } from '../types'

const props = defineProps<{
  fichas: Ficha[]
  kpis: Kpis
}>()

const exportarCSV = () => {
  if (!props.fichas.length) return
  
  // Extraer headers del primer elemento
  const headers = Object.keys(props.fichas[0]).join(',')
  const rows = props.fichas.map(f => {
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
  if (!props.fichas.length) return
  const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
    JSON.stringify(props.fichas, null, 2)
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
  <div class="space-y-6">
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
            <tr v-for="f in fichas.slice(0, 30)" :key="f.FICHA" class="border-b border-slate-200">
              <td class="p-2 font-bold">{{ f.FICHA }}</td>
              <td class="p-2 capitalize">{{ f["NOMBRE DEL PROGRAMA"].toLowerCase() }}</td>
              <td class="p-2 capitalize">{{ f.MUNICIPIO.toLowerCase() }}</td>
              <td class="p-2 text-center font-bold">{{ f["APRENDICES MATRICULADOS"] }}</td>
              <td class="p-2 capitalize">{{ (f["INSTRUCTOR TÉCNICO 2026"] || f["INSTRUCTOR TÉCNICO 2025"] || 'SIN ASIGNAR').toLowerCase() }}</td>
            </tr>
          </tbody>
        </table>
        <p class="text-[10px] text-slate-400 italic" v-if="fichas.length > 30">
          * Mostrando solo los primeros 30 registros de un total de {{ fichas.length }} formaciones.
        </p>
      </div>
    </div>
  </div>
</template>
