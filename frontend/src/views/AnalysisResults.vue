<template>
  <div class="min-h-screen bg-gray-50">
    <!-- Header -->
    <header class="bg-white shadow-sm sticky top-0 z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div class="flex items-center justify-between">
          <div>
            <h1 class="text-2xl font-bold text-gray-900">Resultados da Análise</h1>
            <p class="text-sm text-gray-600 mt-1">
              Insights e recomendações para suas campanhas
            </p>
          </div>
          <div class="flex items-center gap-4">
            <ExportButton :analysis-data="analysisResult" />
            <button
              @click="goHome"
              class="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
            >
              Nova Análise
            </button>
          </div>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div v-if="!hasResults" class="text-center py-12">
        <p class="text-gray-600 mb-4">Nenhum resultado disponível.</p>
        <button
          @click="goHome"
          class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          Fazer Nova Análise
        </button>
      </div>

      <div v-else class="space-y-6">
        <!-- Resumo Executivo -->
        <ExecutiveSummary
          :summary="analysisResult.executive_summary"
          :generated-at="analysisResult.generated_at"
        />

        <!-- Métricas Principais -->
        <MetricsDashboard :metrics="analysisResult.metrics_summary" />

        <!-- Gráficos -->
        <div v-if="analysisResult.metrics_summary?.by_channel?.length > 0" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChannelComparison
            :channels="analysisResult.metrics_summary.by_channel"
            metric="total_cost"
            title="Custo Total por Canal"
          />
          <CPADistribution
            :channels="analysisResult.metrics_summary.by_channel"
          />
        </div>

        <div v-if="analysisResult.metrics_summary?.by_channel?.length > 0" class="grid grid-cols-1 gap-6">
          <PerformanceChart
            :channels="analysisResult.metrics_summary.by_channel"
          />
        </div>

        <!-- Métricas por Canal -->
        <ChannelMetrics
          v-if="analysisResult.metrics_summary?.by_channel?.length > 0"
          :channels="analysisResult.metrics_summary.by_channel"
        />

        <!-- Problemas Identificados -->
        <KeyIssues
          v-if="analysisResult.key_issues?.length > 0"
          :issues="analysisResult.key_issues"
        />

        <!-- Recomendações -->
        <Recommendations
          v-if="analysisResult.recommendations?.length > 0"
          :recommendations="analysisResult.recommendations"
        />

        <!-- Alertas de Risco -->
        <RiskAlerts
          v-if="analysisResult.risk_alerts?.length > 0"
          :alerts="analysisResult.risk_alerts"
        />
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue';
import { useRouter } from 'vue-router';
import { useCampaignStore } from '@/stores/campaign';
import ExecutiveSummary from '@/components/ExecutiveSummary.vue';
import MetricsDashboard from '@/components/MetricsDashboard.vue';
import ChannelMetrics from '@/components/ChannelMetrics.vue';
import KeyIssues from '@/components/KeyIssues.vue';
import Recommendations from '@/components/Recommendations.vue';
import RiskAlerts from '@/components/RiskAlerts.vue';
import ExportButton from '@/components/ExportButton.vue';
import ChannelComparison from '@/components/Charts/ChannelComparison.vue';
import CPADistribution from '@/components/Charts/CPADistribution.vue';
import PerformanceChart from '@/components/Charts/PerformanceChart.vue';

const router = useRouter();
const campaignStore = useCampaignStore();

const analysisResult = computed(() => campaignStore.analysisResult);
const hasResults = computed(() => campaignStore.hasResults);

const goHome = () => {
  campaignStore.clearResults();
  router.push('/');
};
</script>
