<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">Resumo Executivo</h2>
    <p class="text-gray-700 leading-relaxed">{{ summary }}</p>
    <div v-if="generatedAt" class="mt-4 text-sm text-gray-500">
      Gerado em: {{ formatDate(generatedAt) }}
    </div>
  </div>
</template>

<script setup>
import { formatDate } from '@/utils/formatters';

defineProps({
  summary: {
    type: String,
    required: true,
  },
  generatedAt: {
    type: String,
    default: null,
  },
});
</script>
