<script setup lang="ts">
import { Icon } from '@iconify/vue'
import { fichasApi } from '../../services/fichasApi'
import { useAuth } from '../../composables/useAuth'

defineProps<{
  activeTab: string
  isDark: boolean
}>()

const emit = defineEmits<{
  (e: 'update:activeTab', tab: string): void
  (e: 'toggle-dark'): void
}>()

const { user, logout } = useAuth()

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: 'lucide:layout-dashboard' },
  { id: 'stats', label: 'Estadísticas', icon: 'lucide:trending-up' },
  { id: 'search', label: 'Buscador', icon: 'lucide:search' },
  { id: 'sync', label: 'Sincronizar Excel', icon: 'lucide:refresh-cw' },
  { id: 'reports', label: 'Reportes', icon: 'lucide:file-bar-chart' },
]

const abrirCtkBuscador = async () => {
  try {
    await fichasApi.abrirBuscadorGui()
  } catch (e: any) {
    alert(e.message || 'Error al iniciar la aplicación de escritorio')
  }
}
</script>

<template>
  <aside class="w-full md:w-64 bg-primary text-white flex flex-col shrink-0 border-r border-primary-dark/40 print:hidden md:sticky md:top-0 md:h-screen">
    
    <!-- Logo / Header -->
    <div class="p-6 border-b border-primary-dark/40 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <Icon icon="lucide:school" class="w-6 h-6 text-success" />
        <h1 class="text-lg font-black tracking-wider uppercase">
          SENA Fichas
        </h1>
      </div>
      <span class="text-[10px] bg-primary-light text-slate-200 font-bold px-2 py-0.5 rounded-full">
        Admin
      </span>
    </div>

    <!-- Perfil del Usuario Autenticado -->
    <div v-if="user" class="px-4 py-3 border-b border-primary-dark/30 flex items-center gap-3 bg-primary-dark/20">
      <img 
        v-if="user.picture" 
        :src="user.picture" 
        :alt="user.name"
        referrerpolicy="no-referrer"
        class="w-9 h-9 rounded-full border border-primary-light object-cover shrink-0" 
      />
      <div v-else class="w-9 h-9 rounded-full bg-primary-light flex items-center justify-center font-bold text-xs shrink-0">
        {{ user.name.charAt(0).toUpperCase() }}
      </div>
      <div class="flex-1 min-w-0">
        <span class="block text-xs font-bold text-slate-100 truncate">{{ user.name }}</span>
        <span class="block text-[10px] text-slate-300 truncate">{{ user.email }}</span>
      </div>
      <button 
        @click="logout"
        title="Cerrar sesión"
        class="p-1.5 text-slate-400 hover:text-rose-400 hover:bg-rose-950/40 rounded-lg transition-colors"
      >
        <Icon icon="lucide:log-out" class="w-4 h-4" />
      </button>
    </div>

    <!-- Menú Navegación -->
    <nav class="flex-1 p-4 space-y-1.5">
      <button 
        v-for="item in navItems"
        :key="item.id"
        @click="emit('update:activeTab', item.id)"
        class="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-semibold transition-all duration-150"
        :class="activeTab === item.id ? 'bg-primary-light text-white shadow-sm' : 'text-slate-300 hover:bg-primary-light/40 hover:text-white'"
      >
        <Icon :icon="item.icon" class="w-5 h-5" />
        {{ item.label }}
      </button>
    </nav>

    <!-- Panel Inferior (Modo Oscuro y Herramientas) -->
    <div class="p-4 border-t border-primary-dark/40 flex flex-col gap-3">
      <button 
        @click="abrirCtkBuscador"
        class="w-full flex items-center justify-center gap-2 px-3 py-2 bg-primary-dark/60 hover:bg-primary-dark text-slate-200 hover:text-white rounded-lg text-xs font-bold transition-all border border-primary-dark/30 shadow-sm"
        title="Abrir buscador flotante CustomTkinter en la PC"
      >
        <Icon icon="lucide:terminal" class="w-4 h-4 text-success" />
        Lanzar Buscador GUI
      </button>
      
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold text-slate-300">Modo Oscuro</span>
        <button 
          @click="emit('toggle-dark')"
          class="p-2 rounded-lg bg-primary-dark/60 hover:bg-primary-dark text-white transition-colors duration-150"
        >
          <Icon :icon="isDark ? 'lucide:sun' : 'lucide:moon'" class="w-4 h-4" />
        </button>
      </div>
    </div>

  </aside>
</template>
