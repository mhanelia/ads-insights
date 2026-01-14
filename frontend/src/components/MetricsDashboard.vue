<template>
  <div class="space-y-6">
    <!-- Cards de Métricas Principais -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total de Campanhas</p>
            <p class="text-3xl font-bold text-gray-800 mt-2">
              {{ metrics.total_campaigns }}
            </p>
          </div>
          <div class="bg-primary-100 rounded-full p-3">
            <svg class="h-6 w-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Gasto Total</p>
            <p class="text-3xl font-bold text-gray-800 mt-2">
              {{ formatCurrency(metrics.total_spend) }}
            </p>
          </div>
          <div class="bg-green-100 rounded-full p-3">
            <svg class="h-6 w-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <div class="flex items-center justify-between">
          <div>
            <p class="text-sm font-medium text-gray-600">Total de Conversões</p>
            <p class="text-3xl font-bold text-gray-800 mt-2">
              {{ formatNumber(metrics.total_conversions) }}
            </p>
          </div>
          <div class="bg-purple-100 rounded-full p-3">
            <svg class="h-6 w-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>

    <!-- Resumo de Métricas -->
    <div class="bg-white rounded-lg shadow-md p-6">
      <h3 class="text-xl font-bold text-gray-800 mb-4">Resumo de Métricas</h3>
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <p class="text-sm text-gray-600 mb-1">CTR Médio</p>
          <p class="text-lg font-semibold text-gray-800">
            {{ formatPercentage(metrics.ctr_summary?.mean || 0) }}
          </p>
          <p class="text-xs text-gray-500">
            Min: {{ formatPercentage(metrics.ctr_summary?.min || 0) }} | 
            Max: {{ formatPercentage(metrics.ctr_summary?.max || 0) }}
          </p>
        </div>
        <div>
          <p class="text-sm text-gray-600 mb-1">CPA Médio</p>
          <p class="text-lg font-semibold text-gray-800">
            {{ formatCurrency(metrics.cpa_summary?.mean || 0) }}
          </p>
          <p class="text-xs text-gray-500">
            Min: {{ formatCurrency(metrics.cpa_summary?.min || 0) }} | 
            Max: {{ formatCurrency(metrics.cpa_summary?.max || 0) }}
          </p>
        </div>
        <div>
          <p class="text-sm text-gray-600 mb-1">Impressões Médias</p>
          <p class="text-lg font-semibold text-gray-800">
            {{ formatNumber(Math.round(metrics.impressions_summary?.mean || 0)) }}
          </p>
          <p class="text-xs text-gray-500">
            Total: {{ formatNumber(metrics.impressions_summary?.max ? metrics.impressions_summary.max * metrics.total_campaigns : 0) }}
          </p>
        </div>
        <div>
          <p class="text-sm text-gray-600 mb-1">Conversões Médias</p>
          <p class="text-lg font-semibold text-gray-800">
            {{ formatNumber(Math.round(metrics.conversions_summary?.mean || 0)) }}
          </p>
          <p class="text-xs text-gray-500">
            Total: {{ formatNumber(metrics.total_conversions) }}
          </p>
        </div>
      </div>
    </div>

    <!-- Top e Bottom Performers -->
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Top Performers</h3>
        <div v-if="metrics.top_performers && metrics.top_performers.length > 0" class="space-y-2">
          <div
            v-for="(campaign, index) in metrics.top_performers"
            :key="campaign"
            class="flex items-center gap-3 p-2 bg-green-50 rounded"
          >
            <span class="flex items-center justify-center w-6 h-6 bg-green-500 text-white rounded-full text-sm font-bold">
              {{ index + 1 }}
            </span>
            <span class="text-gray-700">{{ campaign }}</span>
          </div>
        </div>
        <p v-else class="text-gray-500 text-sm">Nenhum dado disponível</p>
      </div>

      <div class="bg-white rounded-lg shadow-md p-6">
        <h3 class="text-lg font-bold text-gray-800 mb-4">Campanhas com Baixa Performance</h3>
        <div v-if="metrics.bottom_performers && metrics.bottom_performers.length > 0" class="space-y-2">
          <div
            v-for="(campaign, index) in metrics.bottom_performers"
            :key="campaign"
            class="flex items-center gap-3 p-2 bg-red-50 rounded"
          >
            <span class="flex items-center justify-center w-6 h-6 bg-red-500 text-white rounded-full text-sm font-bold">
              {{ index + 1 }}
            </span>
            <span class="text-gray-700">{{ campaign }}</span>
          </div>
        </div>
        <p v-else class="text-gray-500 text-sm">Nenhum dado disponível</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { formatCurrency, formatNumber, formatPercentage } from '@/utils/formatters';

defineProps({
  metrics: {
    type: Object,
    required: true,
  },
});
</script>
