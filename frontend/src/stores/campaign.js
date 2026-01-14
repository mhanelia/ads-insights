import { defineStore } from 'pinia';
import { analyzeCampaign, checkHealth } from '@/services/api';

export const useCampaignStore = defineStore('campaign', {
  state: () => ({
    analysisResult: null,
    loading: false,
    error: null,
    validationErrors: [],
    apiHealth: null,
  }),

  getters: {
    hasResults: (state) => state.analysisResult !== null,
    hasErrors: (state) => state.error !== null || state.validationErrors.length > 0,
    isLoading: (state) => state.loading,
  },

  actions: {
    async checkApiHealth() {
      try {
        this.apiHealth = await checkHealth();
        return this.apiHealth;
      } catch (error) {
        console.error('Erro ao verificar saúde da API:', error);
        return null;
      }
    },

    async analyzeFile(file) {
      this.loading = true;
      this.error = null;
      this.validationErrors = [];
      this.analysisResult = null;

      try {
        const result = await analyzeCampaign(file);
        this.analysisResult = result;
        return result;
      } catch (error) {
        if (error.response?.status === 400) {
          // Erro de validação
          const validationData = error.response.data;
          if (validationData?.validation_result?.errors) {
            this.validationErrors = validationData.validation_result.errors;
          }
          this.error = 'Erro de validação nos dados do CSV';
        } else if (error.response?.status === 422) {
          this.error = error.response.data?.detail || 'Arquivo CSV inválido';
        } else if (error.response?.status === 500) {
          this.error = 'Erro interno do servidor. Tente novamente mais tarde.';
        } else if (error.code === 'ECONNABORTED') {
          this.error = 'Tempo de requisição excedido. O arquivo pode ser muito grande.';
        } else {
          this.error = error.message || 'Erro ao analisar arquivo';
        }
        throw error;
      } finally {
        this.loading = false;
      }
    },

    clearResults() {
      this.analysisResult = null;
      this.error = null;
      this.validationErrors = [];
    },

    clearError() {
      this.error = null;
      this.validationErrors = [];
    },
  },
});
