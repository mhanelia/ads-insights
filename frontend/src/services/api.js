import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 minutos para análise de grandes arquivos
  headers: {
    'Content-Type': 'multipart/form-data',
  },
});

// Interceptor para requisições
api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor para respostas
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Tratamento de erros específicos
    if (error.code === 'ECONNABORTED') {
      error.message = 'Tempo de requisição excedido. O arquivo pode ser muito grande.';
    }
    return Promise.reject(error);
  }
);

/**
 * Verifica a saúde da API
 */
export async function checkHealth() {
  const response = await api.get('/health');
  return response.data;
}

/**
 * Analisa um arquivo CSV de campanhas
 */
export async function analyzeCampaign(file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/analyze-campaign', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
}

export default api;
