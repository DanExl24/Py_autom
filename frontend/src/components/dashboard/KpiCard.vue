<script setup lang="ts">
import { Icon } from '@iconify/vue'

defineProps<{
  title: string
  value: string | number
  icon: string
  colorClass: string
  borderClass: string
}>()
</script>

<template>
  <div class="relative bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-slate-200 dark:border-slate-700 overflow-hidden transition-all duration-300 hover:shadow-md hover:-translate-y-0.5 group">
    <!-- Línea decorativa de acento superior -->
    <div class="absolute top-0 left-0 w-full h-1" :class="borderClass"></div>
    <div class="flex items-center justify-between p-5">
      <div>
        <p class="text-xs font-bold text-slate-400 dark:text-slate-400 uppercase tracking-wider mb-1">
          {{ title }}
        </p>
        <h3 class="text-2xl font-black text-slate-800 dark:text-slate-100">
          {{ value }}
        </h3>
      </div>
      <div class="p-3 rounded-lg bg-slate-50 dark:bg-slate-700/50 group-hover:scale-105 transition-all duration-300">
        <Icon :icon="icon" class="w-6 h-6" :class="colorClass" />
      </div>
    </div>
  </div>
</template>
