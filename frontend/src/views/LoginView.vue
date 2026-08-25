<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Icon } from '@iconify/vue'
import { useAuth } from '../composables/useAuth'

const { loginWithGoogleCredential } = useAuth()
const googleBtnContainer = ref<HTMLElement | null>(null)
const authError = ref<string | null>(null)

const googleClientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

const handleCredentialResponse = (response: any) => {
  try {
    if (response && response.credential) {
      loginWithGoogleCredential(response.credential)
    } else {
      throw new Error('No se recibió credencial de Google.')
    }
  } catch (err: any) {
    authError.value = err.message || 'Error al iniciar sesión con Google.'
  }
}

onMounted(() => {
  if (typeof window !== 'undefined') {
    const initGsi = () => {
      const google = (window as any).google
      if (google && google.accounts && google.accounts.id) {
        google.accounts.id.initialize({
          client_id: googleClientId || 'PLACEHOLDER_CLIENT_ID',
          callback: handleCredentialResponse,
          auto_select: false,
          cancel_on_tap_outside: true,
        })

        if (googleBtnContainer.value) {
          google.accounts.id.renderButton(
            googleBtnContainer.value,
            { 
              theme: 'filled_blue', 
              size: 'large', 
              text: 'continue_with', 
              shape: 'pill',
              width: 280
            }
          )
        }
      } else {
        // Reintentar si el script aún se está cargando
        setTimeout(initGsi, 300)
      }
    }

    initGsi()
  }
})
</script>

<template>
  <div class="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center p-6 relative overflow-hidden">
    <!-- Fondos decorativos con degradados suaves -->
    <div class="absolute -top-40 -left-40 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl pointer-events-none"></div>
    <div class="absolute -bottom-40 -right-40 w-96 h-96 bg-emerald-600/20 rounded-full blur-3xl pointer-events-none"></div>

    <div class="w-full max-w-md bg-slate-850/90 backdrop-blur-md rounded-3xl p-8 border border-slate-700/60 shadow-2xl space-y-8 relative z-10">
      
      <!-- Logo y Encabezado -->
      <div class="text-center space-y-3">
        <div class="inline-flex p-3 rounded-2xl bg-primary-light/30 border border-primary-light/40 shadow-inner">
          <Icon icon="lucide:school" class="w-10 h-10 text-success" />
        </div>
        <h1 class="text-2xl font-black tracking-wider uppercase text-white">
          SENA Fichas
        </h1>
        <p class="text-xs text-slate-400 font-medium leading-relaxed">
          Plataforma de Control e Indicadores de Formaciones Caquetá 2026. Acceso exclusivo para instructores y directivos autorizados.
        </p>
      </div>

      <!-- Alerta de Seguridad / Protección -->
      <div class="p-4 rounded-xl bg-blue-950/40 border border-blue-800/40 flex items-start gap-3">
        <Icon icon="lucide:shield-check" class="w-5 h-5 text-secondary shrink-0 mt-0.5" />
        <div class="space-y-0.5">
          <span class="block text-xs font-bold text-blue-300">Acceso Protegido por OAuth 2.0</span>
          <p class="text-[11px] text-slate-400">
            Inicia sesión con tu cuenta corporativa de Google para desbloquear el Dashboard, Buscador y Sincronización.
          </p>
        </div>
      </div>

      <!-- Mensaje de Error si ocurre -->
      <div v-if="authError" class="p-3 bg-rose-950/40 border border-rose-800/50 rounded-xl text-xs text-rose-300 flex items-center gap-2">
        <Icon icon="lucide:alert-triangle" class="w-4 h-4 text-rose-400 shrink-0" />
        <span>{{ authError }}</span>
      </div>

      <!-- Contenedor del Botón Oficial de Google -->
      <div class="flex flex-col items-center justify-center space-y-4">
        <div ref="googleBtnContainer" class="min-h-[44px] flex items-center justify-center"></div>

        <!-- Fallback si no está configurado el CLIENT_ID aún en el VPS -->
        <p v-if="!googleClientId" class="text-[10px] text-slate-500 text-center">
          * Nota: Configura <code>VITE_GOOGLE_CLIENT_ID</code> en el <code>.env</code> del VPS para activar el botón oficial de Google.
        </p>
      </div>

      <!-- Footer Informativo -->
      <div class="text-center pt-4 border-t border-slate-800 text-[10px] text-slate-500">
        Sistema de Automatización y Gestión SENA • Regional Caquetá
      </div>

    </div>
  </div>
</template>
