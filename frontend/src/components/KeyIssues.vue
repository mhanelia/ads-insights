<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Problemas Identificados</h2>
      <select
        v-model="selectedSeverity"
        class="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        <option value="">Todas as severidades</option>
        <option value="critical">Crítico</option>
        <option value="high">Alto</option>
        <option value="medium">Médio</option>
        <option value="low">Baixo</option>
      </select>
    </div>

    <div v-if="filteredIssues.length === 0" class="text-center py-8 text-gray-500">
      <p>Nenhum problema encontrado.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(issue, index) in filteredIssues"
        :key="index"
        class="border-l-4 rounded p-4"
        :class="getSeverityClasses(issue.severity)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <h3 class="text-lg font-semibold text-gray-800">{{ issue.title }}</h3>
              <span
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="getSeverityBadgeClasses(issue.severity)"
              >
                {{ getSeverityLabel(issue.severity) }}
              </span>
            </div>
            <p class="text-gray-700 mb-3">{{ issue.description }}</p>
            <div v-if="issue.affected_campaigns && issue.affected_campaigns.length > 0" class="mb-2">
              <p class="text-sm font-medium text-gray-600 mb-1">Campanhas afetadas:</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="campaign in issue.affected_campaigns"
                  :key="campaign"
                  class="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                >
                  {{ campaign }}
                </span>
              </div>
            </div>
            <div v-if="issue.potential_impact" class="mt-2">
              <p class="text-sm text-gray-600">
                <strong>Impacto potencial:</strong> {{ issue.potential_impact }}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  issues: {
    type: Array,
    default: () => [],
  },
});

const selectedSeverity = ref('');

const filteredIssues = computed(() => {
  if (!selectedSeverity.value) {
    return props.issues;
  }
  return props.issues.filter(issue => issue.severity === selectedSeverity.value);
});

const getSeverityClasses = (severity) => {
  const classes = {
    critical: 'border-red-600 bg-red-50',
    high: 'border-orange-500 bg-orange-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-blue-500 bg-blue-50',
  };
  return classes[severity] || 'border-gray-300 bg-gray-50';
};

const getSeverityBadgeClasses = (severity) => {
  const classes = {
    critical: 'bg-red-600 text-white',
    high: 'bg-orange-500 text-white',
    medium: 'bg-yellow-500 text-white',
    low: 'bg-blue-500 text-white',
  };
  return classes[severity] || 'bg-gray-500 text-white';
};

const getSeverityLabel = (severity) => {
  const labels = {
    critical: 'Crítico',
    high: 'Alto',
    medium: 'Médio',
    low: 'Baixo',
  };
  return labels[severity] || severity;
};
</script>
