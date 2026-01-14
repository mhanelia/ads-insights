<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">AI Campaign Analyst</h1>
            <p class="text-sm text-gray-600 mt-1">
              Análise inteligente de campanhas de marketing
            </p>
          </div>
          <div v-if="apiHealth" class="flex items-center gap-2 text-sm text-green-600">
            <svg class="h-4 w-4" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
            </svg>
            API Online
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div class="text-center mb-8">
        <h2 class="text-3xl font-bold text-gray-900 mb-2">
          Analise suas campanhas de marketing
        </h2>
        <p class="text-lg text-gray-600">
          Faça upload de um arquivo CSV e receba insights acionáveis gerados por IA
        </p>
      </div>

      <!-- Upload Component -->
      <div class="max-w-3xl mx-auto mb-8">
        <CampaignUpload
          @upload="handleUpload"
        />
      </div>

      <!-- Features -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
        <div class="bg-white rounded-lg shadow-md p-6 text-center">
          <div class="bg-primary-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <svg class="h-8 w-8 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Análise Detalhada</h3>
          <p class="text-sm text-gray-600">
            Métricas e estatísticas completas das suas campanhas
          </p>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6 text-center">
          <div class="bg-green-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <svg class="h-8 w-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Insights de IA</h3>
          <p class="text-sm text-gray-600">
            Recomendações acionáveis geradas por inteligência artificial
          </p>
        </div>

        <div class="bg-white rounded-lg shadow-md p-6 text-center">
          <div class="bg-purple-100 rounded-full p-3 w-16 h-16 mx-auto mb-4 flex items-center justify-center">
            <svg class="h-8 w-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
          </div>
          <h3 class="text-lg font-semibold text-gray-800 mb-2">Exportação</h3>
          <p class="text-sm text-gray-600">
            Exporte relatórios em PDF, Excel ou JSON
          </p>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useCampaignStore } from '@/stores/campaign';
import CampaignUpload from '@/components/CampaignUpload.vue';

const router = useRouter();
const campaignStore = useCampaignStore();
const apiHealth = ref(null);

onMounted(async () => {
  apiHealth.value = await campaignStore.checkApiHealth();
});

const handleUpload = (analysisResult) => {
  if (analysisResult) {
    router.push('/results');
  }
};
</script>
