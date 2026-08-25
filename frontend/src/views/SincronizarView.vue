<script setup lang="ts">
import { Icon } from '@iconify/vue'
import SincronizarExcel from '../components/sync/SincronizarExcel.vue'

const emit = defineEmits<{
  (e: 'sync-complete'): void
}>()
</script>

<template>
  <div class="space-y-6 print:hidden">
    <div class="flex items-center gap-2">
      <Icon icon="lucide:refresh-cw" class="w-6 h-6 text-primary dark:text-primary-light" />
      <h2 class="text-2xl font-black tracking-tight text-slate-800 dark:text-slate-100">
        Sincronización de Datos
      </h2>
    </div>

    <SincronizarExcel @sync-complete="emit('sync-complete')" />
  </div>
</template>
