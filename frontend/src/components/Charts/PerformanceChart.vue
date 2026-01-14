<template>
  <div class="bg-white rounded-lg shadow-md p-6">
    <h3 class="text-lg font-bold text-gray-800 mb-4">Performance: CTR vs CPA</h3>
    <div class="h-64">
      <Scatter
        :data="chartData"
        :options="chartOptions"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { Scatter } from 'vue-chartjs';
import {
  Chart as ChartJS,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Legend,
} from 'chart.js';

ChartJS.register(
  LinearScale,
  PointElement,
  LineElement,
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
  const data = props.channels.map(c => ({
    x: c.avg_ctr,
    y: c.avg_cpa,
    label: c.channel,
  }));

  return {
    datasets: [
      {
        label: 'Canais',
        data,
        backgroundColor: 'rgba(14, 165, 233, 0.5)',
        borderColor: 'rgba(14, 165, 233, 1)',
        pointRadius: 8,
        pointHoverRadius: 10,
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
        title: function(context) {
          const point = context[0];
          const channel = props.channels.find(c => 
            c.avg_ctr === point.parsed.x && c.avg_cpa === point.parsed.y
          );
          return channel ? channel.channel : 'Canal';
        },
        label: function(context) {
          return [
            `CTR: ${context.parsed.x.toFixed(2)}%`,
            `CPA: ${new Intl.NumberFormat('pt-BR', {
              style: 'currency',
              currency: 'BRL',
            }).format(context.parsed.y)}`,
          ];
        },
      },
    },
  },
  scales: {
    x: {
      title: {
        display: true,
        text: 'CTR Médio (%)',
      },
      beginAtZero: true,
    },
    y: {
      title: {
        display: true,
        text: 'CPA Médio (R$)',
      },
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
