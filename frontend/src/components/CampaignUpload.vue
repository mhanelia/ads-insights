<template>
  <div class="w-full">
    <div
      @drop.prevent="handleDrop"
      @dragover.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @click="triggerFileInput"
      :class="[
        'border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-all',
        isDragging ? 'border-primary-500 bg-primary-50' : 'border-gray-300 hover:border-primary-400',
        loading && 'opacity-50 cursor-not-allowed'
      ]"
    >
      <input
        ref="fileInput"
        type="file"
        accept=".csv"
        @change="handleFileSelect"
        class="hidden"
        :disabled="loading"
      />

      <div v-if="!loading && !selectedFile" class="space-y-4">
        <svg
          class="mx-auto h-12 w-12 text-gray-400"
          stroke="currentColor"
          fill="none"
          viewBox="0 0 48 48"
        >
          <path
            d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
            stroke-width="2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
        <div>
          <p class="text-lg font-medium text-gray-700">
            Arraste e solte seu arquivo CSV aqui
          </p>
          <p class="text-sm text-gray-500 mt-1">
            ou clique para selecionar
          </p>
        </div>
        <p class="text-xs text-gray-400">
          Formatos suportados: CSV (máx. 10MB)
        </p>
      </div>

      <div v-if="loading" class="space-y-4">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mx-auto"></div>
        <p class="text-lg font-medium text-gray-700">
          Analisando arquivo...
        </p>
        <p class="text-sm text-gray-500">
          Isso pode levar alguns minutos
        </p>
      </div>

      <div v-if="selectedFile && !loading" class="space-y-2">
        <svg
          class="mx-auto h-12 w-12 text-green-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
          />
        </svg>
        <p class="text-lg font-medium text-gray-700">
          {{ selectedFile.name }}
        </p>
        <p class="text-sm text-gray-500">
          {{ formatFileSize(selectedFile.size) }}
        </p>
        <button
          @click.stop="removeFile"
          class="mt-2 text-sm text-red-600 hover:text-red-700"
        >
          Remover arquivo
        </button>
      </div>
    </div>

    <!-- Mensagens de erro -->
    <div v-if="validationErrors.length > 0" class="mt-4">
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <h3 class="text-sm font-medium text-red-800 mb-2">
          Erros de validação encontrados:
        </h3>
        <ul class="list-disc list-inside text-sm text-red-700 space-y-1">
          <li v-for="(error, index) in validationErrors" :key="index">
            <strong>{{ error.field }}</strong>: {{ error.message }}
            <span v-if="error.row" class="text-red-600"> (Linha {{ error.row }})</span>
          </li>
        </ul>
      </div>
    </div>

    <div v-if="error && !validationErrors.length" class="mt-4">
      <div class="bg-red-50 border border-red-200 rounded-lg p-4">
        <p class="text-sm text-red-800">{{ error }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useCampaignStore } from '@/stores/campaign';
import { isValidCSVFile, isValidFileSize } from '@/utils/validators';
import { formatFileSize } from '@/utils/formatters';

const props = defineProps({
  modelValue: File,
});

const emit = defineEmits(['update:modelValue', 'upload']);

const campaignStore = useCampaignStore();
const fileInput = ref(null);
const isDragging = ref(false);
const selectedFile = ref(null);

const loading = computed(() => campaignStore.loading);
const error = computed(() => campaignStore.error);
const validationErrors = computed(() => campaignStore.validationErrors);

const triggerFileInput = () => {
  if (!loading.value) {
    fileInput.value?.click();
  }
};

const handleFileSelect = (event) => {
  const file = event.target.files[0];
  if (file) {
    processFile(file);
  }
};

const handleDrop = (event) => {
  isDragging.value = false;
  const file = event.dataTransfer.files[0];
  if (file) {
    processFile(file);
  }
};

const processFile = async (file) => {
  // Validação no frontend
  if (!isValidCSVFile(file)) {
    campaignStore.error = 'Por favor, selecione um arquivo CSV válido.';
    return;
  }

  if (!isValidFileSize(file)) {
    campaignStore.error = 'O arquivo é muito grande. Tamanho máximo: 10MB.';
    return;
  }

  selectedFile.value = file;
  emit('update:modelValue', file);

  // Upload automático
  try {
    await campaignStore.analyzeFile(file);
    emit('upload', campaignStore.analysisResult);
  } catch (err) {
    // Erro já tratado no store
    console.error('Erro ao fazer upload:', err);
  }
};

const removeFile = () => {
  selectedFile.value = null;
  if (fileInput.value) {
    fileInput.value.value = '';
  }
  campaignStore.clearError();
  emit('update:modelValue', null);
};
</script>
