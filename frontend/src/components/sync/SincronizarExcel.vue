<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { Icon } from '@iconify/vue'
import { fichasApi } from '../../services/fichasApi'
import { useAuth } from '../../composables/useAuth'

const emit = defineEmits<{
  (e: 'sync-complete'): void
}>()

const { driveAccessToken, requestDriveAccessToken } = useAuth()

const syncing = ref(false)
const requestingAuth = ref(false)
const tokenErrorDetected = ref(false)
const syncLogs = ref<string[]>([])
const terminalBody = ref<HTMLElement | null>(null)
const successMsg = ref(false)

const ejecutarSyncConToken = async (tokenParaUsar?: string | null) => {
  syncing.value = true
  successMsg.value = false
  tokenErrorDetected.value = false
  syncLogs.value = ['[INFO] Conectando con el endpoint de actualización...']

  try {
    const response = await fichasApi.fetchActualizarStream(tokenParaUsar)

    if (!response.ok) {
      throw new Error(`El servidor respondió con código ${response.status}`)
    }

    const reader = response.body?.getReader()
    const decoder = new TextDecoder()

    if (!reader) {
      throw new Error('No se pudo abrir el canal de transmisión de datos (stream).')
    }

    let partialLine = ''
    while (true) {
      const { value, done } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      const text = partialLine + chunk
      const lines = text.split('\n')

      partialLine = lines.pop() || ''

      for (const line of lines) {
        if (line.trim()) {
          syncLogs.value.push(line.trim())
          await scrollTerminal()

          // Detectar si hubo error de credenciales o token inválido
          if (
            line.includes('invalid_grant') || 
            line.includes('No se pudo autenticar') || 
            line.includes('token expirado') ||
            line.includes('RefreshError')
          ) {
            tokenErrorDetected.value = true
          }
        }
      }
    }

    if (partialLine.trim()) {
      syncLogs.value.push(partialLine.trim())
      await scrollTerminal()
    }

    const hasError = syncLogs.value.some(l => l.includes('[ERROR]'))
    if (!hasError && !tokenErrorDetected.value) {
      successMsg.value = true
      emit('sync-complete')
    }

  } catch (e: any) {
    syncLogs.value.push(`[ERROR] Sincronización fallida: ${e.message || e}`)
    await scrollTerminal()
  } finally {
    syncing.value = false
  }
}

const iniciarSincronizacion = async () => {
  await ejecutarSyncConToken(driveAccessToken.value)
}

// Renueva o solicita nuevo token a Google mediante ventana emergente
const solicitarNuevoTokenYReintentar = async () => {
  try {
    requestingAuth.value = true
    syncLogs.value.push('[INFO] Solicitando nuevo token de acceso a Google Cloud...')
    await scrollTerminal()

    const nuevoToken = await requestDriveAccessToken(true)
    syncLogs.value.push('[INFO] ✅ Permiso de Google Drive otorgado con éxito. Reintentando sincronización...')
    await scrollTerminal()

    await ejecutarSyncConToken(nuevoToken)
  } catch (err: any) {
    syncLogs.value.push(`[ERROR] No se pudo obtener el token de Google: ${err.message}`)
    await scrollTerminal()
  } finally {
    requestingAuth.value = false
  }
}

const scrollTerminal = async () => {
  await nextTick()
  if (terminalBody.value) {
    terminalBody.value.scrollTop = terminalBody.value.scrollHeight
  }
}
</script>

<template>
  <div class="max-w-3xl mx-auto space-y-6">
    
    <!-- Título y descripción -->
    <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-2">
      <h2 class="text-lg font-black text-slate-800 dark:text-slate-100 flex items-center gap-2">
        <Icon icon="lucide:refresh-cw" class="w-5 h-5 text-secondary" />
        Sincronización en Vivo (Google Drive)
      </h2>
      <p class="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">
        Descarga la última versión del archivo consolidado (`CONSOLIDADO PROGRAMAS REGULAR - 2026.xlsx`) directamente desde Google Drive. Si tu token expira, puedes renovarlo con un solo clic usando tu cuenta de Google.
      </p>
    </div>

    <!-- Panel de Acciones / Botones -->
    <div class="flex flex-wrap items-center justify-center gap-4">
      
      <!-- Botón Principal de Sincronización -->
      <button 
        @click="iniciarSincronizacion"
        :disabled="syncing || requestingAuth"
        class="flex items-center gap-2 px-8 py-3.5 bg-primary hover:bg-primary-light disabled:bg-primary/50 text-white font-bold rounded-xl text-sm transition-all shadow-md active:scale-95 disabled:scale-100 disabled:pointer-events-none select-none"
      >
        <Icon 
          :icon="syncing ? 'lucide:loader-2' : 'lucide:cloud-lightning'" 
          class="w-5 h-5 text-success" 
          :class="{ 'animate-spin': syncing }" 
        />
        {{ syncing ? 'Sincronizando...' : 'Iniciar Sincronización desde Drive' }}
      </button>

      <!-- Botón para Renovar Token OAuth On-Demand -->
      <button 
        @click="solicitarNuevoTokenYReintentar"
        :disabled="syncing || requestingAuth"
        class="flex items-center gap-2 px-5 py-3.5 bg-secondary/10 hover:bg-secondary/20 text-secondary border border-secondary/30 font-bold rounded-xl text-sm transition-all shadow-sm active:scale-95 disabled:pointer-events-none select-none"
        title="Solicita una nueva autorización de Google Drive en caso de expiración"
      >
        <Icon 
          :icon="requestingAuth ? 'lucide:loader' : 'lucide:key-round'" 
          class="w-4 h-4" 
          :class="{ 'animate-spin': requestingAuth }"
        />
        {{ requestingAuth ? 'Autorizando con Google...' : 'Renovar Token de Drive' }}
      </button>
    </div>

    <!-- Alerta de Token Inválido / Caducado con Botón Rápido -->
    <div 
      v-if="tokenErrorDetected"
      class="bg-amber-500/10 border border-amber-500/30 p-4 rounded-xl flex items-center justify-between gap-4"
    >
      <div class="flex items-start gap-3">
        <Icon icon="lucide:alert-triangle" class="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div class="space-y-0.5">
          <h4 class="font-bold text-xs text-amber-300">Token de Google Drive Invalido o Expirado</h4>
          <p class="text-[11px] text-slate-400">
            Google requiere una nueva autorización para acceder a los archivos. Haz clic en el botón para renovarlo al instante.
          </p>
        </div>
      </div>

      <button 
        @click="solicitarNuevoTokenYReintentar"
        :disabled="requestingAuth"
        class="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 font-bold rounded-lg text-xs shadow shrink-0 transition-colors"
      >
        Renovar y Reintentar Ahora
      </button>
    </div>

    <!-- Consola Terminal retro-moderna -->
    <div class="bg-slate-950 rounded-xl border border-slate-800 shadow-2xl overflow-hidden flex flex-col h-[320px]">
      
      <!-- Cabecera de consola -->
      <div class="bg-slate-900 border-b border-slate-800 px-4 py-2 flex items-center justify-between">
        <div class="flex items-center gap-1.5">
          <span class="w-3 h-3 rounded-full bg-rose-500"></span>
          <span class="w-3 h-3 rounded-full bg-amber-500"></span>
          <span class="w-3 h-3 rounded-full bg-emerald-500"></span>
        </div>
        <span class="text-[10px] font-mono text-slate-500 uppercase tracking-widest font-black">
          live sync logs
        </span>
        <Icon icon="lucide:terminal" class="w-4 h-4 text-slate-500" />
      </div>

      <!-- Cuerpo de Consola -->
      <div 
        ref="terminalBody"
        class="flex-1 overflow-y-auto p-4 font-mono text-xs space-y-1.5 scrollbar-thin select-text"
      >
        <div v-for="(log, i) in syncLogs" :key="i" class="leading-relaxed">
          <span v-if="log.startsWith('[INFO]')" class="text-blue-400">{{ log }}</span>
          <span v-else-if="log.startsWith('[ERROR]')" class="text-rose-400 font-bold">{{ log }}</span>
          <span v-else-if="log.startsWith('[COMPLETADO]')" class="text-emerald-400 font-bold">{{ log }}</span>
          <span v-else class="text-slate-300">{{ log }}</span>
        </div>

        <div v-if="!syncLogs.length" class="text-slate-500 italic py-16 text-center select-none">
          Esperando inicio de sincronización...
        </div>
      </div>
    </div>

    <!-- Mensaje de éxito posterior -->
    <div 
      v-if="successMsg"
      class="bg-emerald-500/10 border border-emerald-500/30 p-4 rounded-xl flex items-start gap-3 text-emerald-800 dark:text-emerald-400 text-xs font-semibold"
    >
      <Icon icon="lucide:check-circle" class="w-5 h-5 shrink-0 mt-0.5" />
      <div>
        <h4 class="font-black text-sm mb-0.5">Sincronización Exitosa</h4>
        <p class="font-normal text-slate-500 dark:text-slate-400">
          La base de datos local `fichas.json` ha sido actualizada en caliente. Los gráficos y KPI de todas las vistas reflejan las formaciones al instante.
        </p>
      </div>
    </div>

  </div>
</template>

<style scoped>
/* Scrollbar delgado para la terminal */
.scrollbar-thin::-webkit-scrollbar {
  width: 6px;
}
.scrollbar-thin::-webkit-scrollbar-track {
  background: transparent;
}
.scrollbar-thin::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 9999px;
}
.scrollbar-thin::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
</style>
