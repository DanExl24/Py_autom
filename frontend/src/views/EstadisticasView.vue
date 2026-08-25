<script setup lang="ts">
import { Icon } from '@iconify/vue'
import type { Ficha } from '../types'
import EstadisticasDetalle from '../components/fichas/EstadisticasDetalle.vue'

defineProps<{
  fichas: Ficha[]
}>()

const emit = defineEmits<{
  (e: 'select-ficha', ficha: Ficha): void
}>()
</script>

<template>
  <div class="space-y-6">
    <div class="flex items-center gap-2 print:hidden">
      <Icon icon="lucide:trending-up" class="w-6 h-6 text-primary dark:text-primary-light" />
      <h2 class="text-2xl font-black tracking-tight text-slate-800 dark:text-slate-100">
        Estadísticas y Rankings Especializados
      </h2>
    </div>

    <EstadisticasDetalle 
      :fichas="fichas" 
      @select-ficha="(f) => emit('select-ficha', f)" 
    />
  </div>
</template>
