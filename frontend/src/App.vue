<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import type { Ficha } from './types'
import { useTheme } from './composables/useTheme'
import { useFichas } from './composables/useFichas'
import { useAuth } from './composables/useAuth'
import AppSidebar from './components/layout/AppSidebar.vue'
import FichaTechnicalDrawer from './components/fichas/FichaTechnicalDrawer.vue'

// Vistas
import LoginView from './views/LoginView.vue'
import DashboardView from './views/DashboardView.vue'
import EstadisticasView from './views/EstadisticasView.vue'
import BuscadorView from './views/BuscadorView.vue'
import SincronizarView from './views/SincronizarView.vue'
import ReportesView from './views/ReportesView.vue'

// Estados y composables
const { isAuthenticated } = useAuth()
const { isDark, toggleDarkMode } = useTheme()
const {
  rawFichas,
  loading,
  error,
  loadData,
  kpis,
  proximoInicio,
  proximaFinalizacion,
  alertBajaMatricula,
  alertProximasTerminar,
  alertSinProyecto
} = useFichas()

const activeTab = ref('dashboard')
const selectedFicha = ref<Ficha | null>(null)

onMounted(() => {
  if (isAuthenticated.value) {
    loadData()
  }
})
</script>

<template>
  <!-- Si el usuario NO está autenticado, mostrar pantalla de Login -->
  <LoginView v-if="!isAuthenticated" />

  <!-- Si el usuario ESTÁ autenticado, mostrar la aplicación -->
  <div v-else class="min-h-screen bg-slate-50 dark:bg-slate-950 text-slate-800 dark:text-slate-100 flex flex-col md:flex-row transition-colors duration-200">
    
    <!-- Barra Lateral (Sidebar) -->
    <AppSidebar 
      :active-tab="activeTab"
      :is-dark="isDark"
      @update:active-tab="(tab) => activeTab = tab"
      @toggle-dark="toggleDarkMode"
    />

    <!-- Contenido Principal Dinámico -->
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
          @click="loadData(false)"
          class="px-4 py-2 bg-primary hover:bg-primary-light text-white font-bold rounded-xl text-sm shadow transition-colors"
        >
          Reintentar Carga
        </button>
      </div>

      <!-- Vistas SPA según pestaña activa -->
      <div v-else class="flex-1 p-6 md:p-8 space-y-6 overflow-y-auto print:p-0">
        
        <!-- PESTAÑA 1: DASHBOARD -->
        <DashboardView 
          v-if="activeTab === 'dashboard'"
          :fichas="rawFichas"
          :kpis="kpis"
          :proximo-inicio="proximoInicio"
          :proxima-finalizacion="proximaFinalizacion"
          :alert-baja-matricula="alertBajaMatricula"
          :alert-proximas-terminar="alertProximasTerminar"
          :alert-sin-proyecto="alertSinProyecto"
        />

        <!-- PESTAÑA 2: ESTADÍSTICAS -->
        <EstadisticasView 
          v-else-if="activeTab === 'stats'"
          :fichas="rawFichas"
          @select-ficha="(f) => selectedFicha = f"
        />

        <!-- PESTAÑA 3: BUSCADOR -->
        <BuscadorView 
          v-else-if="activeTab === 'search'"
          :fichas="rawFichas"
          @select-ficha="(f) => selectedFicha = f"
        />

        <!-- PESTAÑA 4: SINCRONIZACIÓN -->
        <SincronizarView 
          v-else-if="activeTab === 'sync'"
          @sync-complete="loadData(true)"
        />

        <!-- PESTAÑA 5: REPORTES -->
        <ReportesView 
          v-else-if="activeTab === 'reports'"
          :fichas="rawFichas"
          :kpis="kpis"
        />

      </div>

    </main>

    <!-- Drawer global para Ficha Técnica -->
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
