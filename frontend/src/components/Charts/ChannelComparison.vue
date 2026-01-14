<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-lg font-bold text-gray-800 mb-4">{{ title }}</h3>
    <div class="h-64">
      <Bar
        :data="chartData"
        :options="chartOptions"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Bar } from 'vue-chartjs';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const props = defineProps({
  channels: {
    type: Array,
    default: () => [],
  },
  metric: {
    type: String,
    default: 'total_cost',
  },
  title: {
    type: String,
    default: 'Comparação por Canal',
  },
});

const chartData = computed(() => {
  const labels = props.channels.map(c => c.channel);
  const data = props.channels.map(c => {
    switch (props.metric) {
      case 'total_cost':
        return c.total_cost;
      case 'total_conversions':
        return c.total_conversions;
      case 'total_clicks':
        return c.total_clicks;
      case 'total_impressions':
        return c.total_impressions;
      default:
        return c.total_cost;
    }
  });

  return {
    labels,
    datasets: [
      {
        label: getMetricLabel(props.metric),
        data,
        backgroundColor: 'rgba(14, 165, 233, 0.5)',
        borderColor: 'rgba(14, 165, 233, 1)',
        borderWidth: 1,
      },
    ],
  };
});

const chartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: {
      display: false,
    },
    tooltip: {
      callbacks: {
        label: function(context) {
          const value = context.parsed.y;
          if (props.metric === 'total_cost') {
            return new Intl.NumberFormat('pt-BR', {
              style: 'currency',
              currency: 'BRL',
            }).format(value);
          }
          return new Intl.NumberFormat('pt-BR').format(value);
        },
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
    },
  },
};

function getMetricLabel(metric) {
  const labels = {
    total_cost: 'Custo Total',
    total_conversions: 'Conversões',
    total_clicks: 'Cliques',
    total_impressions: 'Impressões',
  };
  return labels[metric] || metric;
}
</script>
