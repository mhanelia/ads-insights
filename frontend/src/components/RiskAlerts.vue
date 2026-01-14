<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h2 class="text-2xl font-bold text-gray-800 mb-4">Alertas de Risco</h2>

    <div v-if="alerts.length === 0" class="text-center py-8 text-gray-500">
      <p>Nenhum alerta de risco encontrado.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(alert, index) in alerts"
        :key="index"
        class="border-l-4 rounded-lg p-4"
        :class="getSeverityClasses(alert.severity)"
      >
        <div class="flex items-start justify-between">
          <div class="flex-1">
            <div class="flex items-center gap-2 mb-2">
              <svg
                class="h-5 w-5"
                :class="getSeverityIconClasses(alert.severity)"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fill-rule="evenodd"
                  d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                  clip-rule="evenodd"
                />
              </svg>
              <h3 class="text-lg font-semibold text-gray-800">{{ alert.title }}</h3>
              <span
                class="px-2 py-1 text-xs font-medium rounded-full"
                :class="getSeverityBadgeClasses(alert.severity)"
              >
                {{ getSeverityLabel(alert.severity) }}
              </span>
            </div>
            <p class="text-gray-700 mb-3">{{ alert.description }}</p>
            <div v-if="alert.mitigation" class="mt-3 pt-3 border-t border-gray-200">
              <p class="text-sm font-medium text-gray-600 mb-1">Como mitigar:</p>
              <p class="text-gray-700">{{ alert.mitigation }}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  alerts: {
    type: Array,
    default: () => [],
  },
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

const getSeverityIconClasses = (severity) => {
  const classes = {
    critical: 'text-red-600',
    high: 'text-orange-500',
    medium: 'text-yellow-500',
    low: 'text-blue-500',
  };
  return classes[severity] || 'text-gray-500';
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
