<template>
  <div class="relative" ref="containerRef">
    <button
      ref="buttonRef"
      @click.stop="toggleMenu"
      :disabled="!props.analysisData"
      class="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <svg class="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
      Exportar
      <svg class="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
      </svg>
    </button>

    <div
      v-if="showMenu"
      ref="menuRef"
      @click.stop
      class="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-10"
    >
      <button
        @click.stop="handleExport('pdf')"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
      >
        <svg class="h-4 w-4 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
        </svg>
        Exportar como PDF
      </button>
      <button
        @click.stop="handleExport('excel')"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
      >
        <svg class="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Exportar como Excel
      </button>
      <button
        @click.stop="handleExport('json')"
        class="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center gap-2"
      >
        <svg class="h-4 w-4 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
        </svg>
        Exportar como JSON
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { exportToPDF, exportToExcel, exportToJSON } from '@/services/export';

const props = defineProps({
  analysisData: {
    type: Object,
    required: false,
    default: null,
  },
});

const showMenu = ref(false);
const menuRef = ref(null);
const buttonRef = ref(null);
const containerRef = ref(null);

const toggleMenu = () => {
  if (!props.analysisData) {
    alert('Nenhum dado disponível para exportar. Faça uma análise primeiro.');
    return;
  }
  showMenu.value = !showMenu.value;
};

const handleExport = (format) => {
  if (!props.analysisData) {
    console.error('Nenhum dado de análise disponível para exportar');
    alert('Nenhum dado disponível para exportar. Faça uma análise primeiro.');
    showMenu.value = false;
    return;
  }

  const data = props.analysisData;
  
  try {
    switch (format) {
      case 'pdf':
        exportToPDF(data);
        break;
      case 'excel':
        exportToExcel(data);
        break;
      case 'json':
        exportToJSON(data);
        break;
      default:
        console.error('Formato de exportação inválido:', format);
        return;
    }
    showMenu.value = false;
  } catch (error) {
    console.error('Erro ao exportar:', error);
    alert(`Erro ao exportar arquivo: ${error.message || 'Tente novamente.'}`);
  }
};

const handleClickOutside = (event) => {
  // Não fechar se o clique foi dentro do container (botão ou menu)
  if (containerRef.value && containerRef.value.contains(event.target)) {
    return;
  }
  showMenu.value = false;
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
