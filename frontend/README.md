# AI Campaign Analyst - Frontend

Frontend Vue.js para o serviço de análise de campanhas de marketing digital.

## 🚀 Quick Start

### Pré-requisitos

- Node.js 18+ e npm/yarn
- Backend FastAPI rodando (veja README.md na raiz do projeto)

### Instalação

```bash
cd frontend
npm install
```

### Configuração

Crie um arquivo `.env` na pasta `frontend`:

```env
VITE_API_BASE_URL=http://localhost:8000
```

### Executar em Desenvolvimento

```bash
npm run dev
```

A aplicação estará disponível em `http://localhost:3000`

### Build para Produção

```bash
npm run build
```

Os arquivos compilados estarão na pasta `dist/`

### Preview da Build

```bash
npm run preview
```

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/          # Componentes Vue reutilizáveis
│   │   ├── Charts/          # Componentes de gráficos
│   │   ├── CampaignUpload.vue
│   │   ├── ExecutiveSummary.vue
│   │   ├── KeyIssues.vue
│   │   ├── Recommendations.vue
│   │   ├── RiskAlerts.vue
│   │   ├── MetricsDashboard.vue
│   │   ├── ChannelMetrics.vue
│   │   └── ExportButton.vue
│   ├── services/            # Serviços (API, exportação)
│   │   ├── api.js
│   │   └── export.js
│   ├── stores/              # Pinia stores
│   │   └── campaign.js
│   ├── utils/               # Utilitários
│   │   ├── formatters.js
│   │   └── validators.js
│   ├── views/               # Páginas/Views
│   │   ├── Home.vue
│   │   └── AnalysisResults.vue
│   ├── App.vue
│   ├── main.js
│   └── style.css
├── public/
├── index.html
├── package.json
├── vite.config.js
└── tailwind.config.js
```

## 🛠️ Stack Tecnológica

- **Vue 3** - Framework JavaScript progressivo
- **Vite** - Build tool rápido
- **Pinia** - Gerenciamento de estado
- **Vue Router** - Roteamento
- **Axios** - Cliente HTTP
- **Chart.js** - Gráficos interativos
- **Tailwind CSS** - Framework CSS utilitário
- **jsPDF** - Geração de PDFs
- **xlsx** - Geração de arquivos Excel

## ✨ Funcionalidades

### Upload de Arquivos
- Drag & drop de arquivos CSV
- Validação de tipo e tamanho
- Feedback visual durante upload
- Tratamento de erros de validação

### Visualização de Dados
- Dashboard com métricas principais
- Gráficos interativos (barras, dispersão)
- Tabelas de métricas por canal
- Top e bottom performers

### Insights e Recomendações
- Exibição de problemas identificados
- Recomendações acionáveis
- Alertas de risco
- Filtros por severidade/prioridade

### Exportação
- Exportação para PDF
- Exportação para Excel
- Exportação para JSON

## 🎨 Design

O frontend utiliza Tailwind CSS para estilização, garantindo:
- Design responsivo (mobile-first)
- Interface moderna e limpa
- Feedback visual em todas as ações
- Animações suaves

## 🔧 Configuração de CORS

O backend já está configurado para aceitar requisições de qualquer origem em desenvolvimento. Para produção, ajuste as configurações de CORS no arquivo `app/main.py`.

## 📝 Notas

- O frontend espera que o backend esteja rodando em `http://localhost:8000` por padrão
- Timeout de requisições configurado para 5 minutos (para análise de arquivos grandes)
- Todos os componentes são responsivos e funcionam em dispositivos móveis

## 🐛 Troubleshooting

### Erro de CORS
- Verifique se o backend está rodando
- Confirme que a URL da API está correta no `.env`
- Verifique as configurações de CORS no backend

### Gráficos não aparecem
- Verifique se Chart.js está instalado: `npm install chart.js vue-chartjs`
- Verifique o console do navegador para erros

### Exportação não funciona
- Verifique se jsPDF e xlsx estão instalados
- Verifique o console do navegador para erros
