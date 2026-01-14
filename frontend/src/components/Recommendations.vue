<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <div class="flex justify-between items-center mb-4">
      <h2 class="text-2xl font-bold text-gray-800">Recomendações</h2>
      <select
        v-model="selectedPriority"
        class="border border-gray-300 rounded-md px-3 py-1 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
      >
        <option value="">Todas as prioridades</option>
        <option value="high">Alta</option>
        <option value="medium">Média</option>
        <option value="low">Baixa</option>
      </select>
    </div>

    <div v-if="filteredRecommendations.length === 0" class="text-center py-8 text-gray-500">
      <p>Nenhuma recomendação disponível.</p>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(rec, index) in filteredRecommendations"
        :key="index"
        class="border rounded-lg p-5 hover:shadow-lg transition-shadow"
        :class="getPriorityClasses(rec.priority)"
      >
        <div class="flex items-start justify-between mb-3">
          <h3 class="text-lg font-semibold text-gray-800 flex-1">{{ rec.title }}</h3>
          <span
            class="px-3 py-1 text-xs font-medium rounded-full ml-3"
            :class="getPriorityBadgeClasses(rec.priority)"
          >
            {{ getPriorityLabel(rec.priority) }}
          </span>
        </div>
        <div class="space-y-2">
          <div>
            <p class="text-sm font-medium text-gray-600 mb-1">O que fazer:</p>
            <p class="text-gray-700">{{ rec.description }}</p>
          </div>
          <div v-if="rec.rationale">
            <p class="text-sm font-medium text-gray-600 mb-1">Por que fazer:</p>
            <p class="text-gray-700">{{ rec.rationale }}</p>
          </div>
          <div v-if="rec.expected_outcome" class="mt-3 pt-3 border-t border-gray-200">
            <p class="text-sm font-medium text-primary-600 mb-1">Resultado esperado:</p>
            <p class="text-primary-700 font-medium">{{ rec.expected_outcome }}</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
  recommendations: {
    type: Array,
    default: () => [],
  },
});

const selectedPriority = ref('');

const filteredRecommendations = computed(() => {
  if (!selectedPriority.value) {
    return props.recommendations;
  }
  return props.recommendations.filter(rec => rec.priority === selectedPriority.value);
});

const getPriorityClasses = (priority) => {
  const classes = {
    high: 'border-primary-500 bg-primary-50',
    medium: 'border-yellow-500 bg-yellow-50',
    low: 'border-gray-300 bg-gray-50',
  };
  return classes[priority] || 'border-gray-300 bg-gray-50';
};

const getPriorityBadgeClasses = (priority) => {
  const classes = {
    high: 'bg-primary-600 text-white',
    medium: 'bg-yellow-500 text-white',
    low: 'bg-gray-500 text-white',
  };
  return classes[priority] || 'bg-gray-500 text-white';
};

const getPriorityLabel = (priority) => {
  const labels = {
    high: 'Alta Prioridade',
    medium: 'Média Prioridade',
    low: 'Baixa Prioridade',
  };
  return labels[priority] || priority;
};
</script>
