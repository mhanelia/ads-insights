<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-lg font-bold text-gray-800 mb-4">Distribuição de CPA por Canal</h3>
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
});

const chartData = computed(() => {
  const labels = props.channels.map(c => c.channel);
  const data = props.channels.map(c => c.avg_cpa);

  return {
    labels,
    datasets: [
      {
        label: 'CPA Médio',
        data,
        backgroundColor: props.channels.map((_, index) => {
          const colors = [
            'rgba(239, 68, 68, 0.5)',
            'rgba(249, 115, 22, 0.5)',
            'rgba(234, 179, 8, 0.5)',
            'rgba(34, 197, 94, 0.5)',
            'rgba(59, 130, 246, 0.5)',
            'rgba(147, 51, 234, 0.5)',
          ];
          return colors[index % colors.length];
        }),
        borderColor: props.channels.map((_, index) => {
          const colors = [
            'rgba(239, 68, 68, 1)',
            'rgba(249, 115, 22, 1)',
            'rgba(234, 179, 8, 1)',
            'rgba(34, 197, 94, 1)',
            'rgba(59, 130, 246, 1)',
            'rgba(147, 51, 234, 1)',
          ];
          return colors[index % colors.length];
        }),
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
          return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
          }).format(value);
        },
      },
    },
  },
  scales: {
    y: {
      beginAtZero: true,
      ticks: {
        callback: function(value) {
          return new Intl.NumberFormat('pt-BR', {
            style: 'currency',
            currency: 'BRL',
            maximumFractionDigits: 0,
          }).format(value);
        },
      },
    },
  },
};
</script>
