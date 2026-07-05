<script setup lang="ts">
import { ref } from 'vue'
import { Icon } from '@iconify/vue'

const emit = defineEmits<{
  (e: 'sync-complete'): void
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const dragActive = ref(false)
const uploading = ref(false)
const progress = ref(0)
const uploadResult = ref<{
  success: boolean
  records?: number
  columns?: number
  newPrograms?: number
  newInstructors?: number
  error?: string
} | null>(null)

const triggerFileSelect = () => {
  if (fileInput.value) fileInput.value.click()
}

const handleDrag = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  if (e.type === 'dragenter' || e.type === 'dragover') {
    dragActive.value = true
  } else if (e.type === 'dragleave') {
    dragActive.value = false
  }
}

const handleDrop = (e: DragEvent) => {
  e.preventDefault()
  e.stopPropagation()
  dragActive.value = false
  if (e.dataTransfer?.files && e.dataTransfer.files[0]) {
    uploadFile(e.dataTransfer.files[0])
  }
}

const handleFileChange = (e: Event) => {
  const target = e.target as HTMLInputElement
  if (target.files && target.files[0]) {
    uploadFile(target.files[0])
  }
}

const uploadFile = async (file: File) => {
  // Validar extensión
  if (!file.name.endsWith('.xlsx') && !file.name.endsWith('.xls')) {
    uploadResult.value = {
      success: false,
      error: 'Formato inválido. Por favor, selecciona un archivo Excel (.xlsx o .xls)'
    }
    return
  }

  uploading.value = true
  progress.value = 10
  uploadResult.value = null

  // Simulación de barra de progreso animada para un look más interactivo y premium
  const interval = setInterval(() => {
    if (progress.value < 85) {
      progress.value += Math.floor(Math.random() * 15) + 5
    }
  }, 150)

  try {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch('/api/sincronizar', {
      method: 'POST',
      body: formData
    })
    
    clearInterval(interval)
    progress.value = 100

    if (!res.ok) {
      const errorData = await res.json()
      throw new Error(errorData.detail || 'Error al procesar el archivo Excel')
    }

    const data = await res.json()
    uploadResult.value = {
      success: true,
      records: data.registros || 0,
      columns: data.columnas || 0,
      newPrograms: data.programas_nuevos || 0,
      newInstructors: data.instructores_nuevos || 0
    }
    
    // Notificar al componente principal para recargar
    emit('sync-complete')
  } catch (e: any) {
    clearInterval(interval)
    progress.value = 0
    uploadResult.value = {
      success: false,
      error: e.message || 'Error de red al subir el archivo'
    }
  } finally {
    uploading.value = false
  }
}
</script>

<template>
  <div class="max-w-2xl mx-auto space-y-6">
    
    <!-- Título y descripción del módulo -->
    <div class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-2">
      <h2 class="text-lg font-black text-slate-800 dark:text-slate-100 flex items-center gap-2">
        <Icon icon="lucide:refresh-cw" class="w-5 h-5 text-secondary" />
        Sincronización de Base de Datos Excel
      </h2>
      <p class="text-xs text-slate-500 dark:text-slate-400">
        Sube el archivo Excel actualizado de formaciones. El sistema extraerá de forma automática las redes, instructores, programas y aprendices de la etapa 2026, refrescando el dashboard al instante.
      </p>
    </div>

    <!-- Zona de Carga / Dropzone -->
    <div 
      @dragenter="handleDrag"
      @dragover="handleDrag"
      @dragleave="handleDrag"
      @drop="handleDrop"
      @click="triggerFileSelect"
      class="border-2 border-dashed rounded-2xl p-10 text-center cursor-pointer transition-all duration-200 flex flex-col items-center justify-center space-y-4"
      :class="[
        dragActive 
          ? 'border-secondary bg-secondary/5' 
          : 'border-slate-300 dark:border-slate-700 hover:border-secondary/60 bg-white dark:bg-slate-800'
      ]"
    >
      <input 
        ref="fileInput"
        type="file" 
        accept=".xlsx, .xls"
        class="hidden" 
        @change="handleFileChange"
      />
      
      <div class="p-4 bg-slate-50 dark:bg-slate-700/50 rounded-full text-slate-400 dark:text-slate-500">
        <Icon icon="lucide:file-spreadsheet" class="w-10 h-10 text-secondary" />
      </div>

      <div class="space-y-1">
        <p class="text-sm font-bold text-slate-700 dark:text-slate-200">
          Arrastra tu archivo Excel aquí o haz clic para buscarlo
        </p>
        <p class="text-xs text-slate-400">
          Formatos admitidos: .xlsx, .xls (Tamaño máximo: 15MB)
        </p>
      </div>
    </div>

    <!-- Barra de Progreso -->
    <div v-if="uploading" class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-3">
      <div class="flex justify-between text-xs font-bold text-slate-500 uppercase tracking-wider">
        <span>Leyendo y validando base de datos...</span>
        <span>{{ progress }}%</span>
      </div>
      <div class="w-full bg-slate-100 dark:bg-slate-700 h-2.5 rounded-full overflow-hidden">
        <div 
          class="bg-secondary h-full transition-all duration-150 ease-out"
          :style="{ width: `${progress}%` }"
        ></div>
      </div>
    </div>

    <!-- Resultados e Indicadores de Sincronización -->
    <div v-if="uploadResult" class="space-y-4">
      
      <!-- Éxito -->
      <div v-if="uploadResult.success" class="bg-white dark:bg-slate-800 p-6 rounded-xl border border-slate-200 dark:border-slate-700 shadow-sm space-y-4">
        <div class="flex items-center gap-3">
          <div class="p-2 bg-success/10 rounded-full text-success">
            <Icon icon="lucide:check-circle" class="w-6 h-6" />
          </div>
          <div>
            <h4 class="text-sm font-bold text-slate-800 dark:text-slate-100">Sincronización Finalizada</h4>
            <p class="text-xs text-slate-400">La base de datos fue actualizada en caliente con éxito.</p>
          </div>
        </div>

        <!-- Validaciones Checker -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2 text-xs font-semibold text-slate-600 dark:text-slate-400">
          <div class="flex items-center gap-2">
            <Icon icon="lucide:check" class="w-4 h-4 text-success" />
            <span>{{ uploadResult.columns }} columnas validadas</span>
          </div>
          <div class="flex items-center gap-2">
            <Icon icon="lucide:check" class="w-4 h-4 text-success" />
            <span>{{ uploadResult.records }} registros importados</span>
          </div>
          <div class="flex items-center gap-2">
            <Icon icon="lucide:check" class="w-4 h-4 text-success" />
            <span>{{ uploadResult.newPrograms }} programas nuevos identificados</span>
          </div>
          <div class="flex items-center gap-2">
            <Icon icon="lucide:check" class="w-4 h-4 text-success" />
            <span>{{ uploadResult.newInstructors }} instructores nuevos</span>
          </div>
        </div>
      </div>

      <!-- Error -->
      <div v-else class="bg-rose-50 dark:bg-rose-950/20 p-6 rounded-xl border border-rose-100 dark:border-rose-900/50 flex gap-3">
        <div class="p-2 bg-danger/10 rounded-full text-danger shrink-0 h-10 w-10 flex items-center justify-center">
          <Icon icon="lucide:alert-octagon" class="w-5 h-5" />
        </div>
        <div class="space-y-1">
          <h4 class="text-sm font-bold text-rose-900 dark:text-rose-400">Fallo en la Validación</h4>
          <p class="text-xs text-rose-700 dark:text-rose-500 font-medium">
            {{ uploadResult.error }}
          </p>
        </div>
      </div>

    </div>

  </div>
</template>
