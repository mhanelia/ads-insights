import jsPDF from 'jspdf';
import * as XLSX from 'xlsx';

/**
 * Exporta os resultados da análise para PDF
 */
export function exportToPDF(analysisData) {
  if (!analysisData) {
    throw new Error('Dados de análise não disponíveis');
  }

  const doc = new jsPDF();
  let yPosition = 20;
  const pageHeight = doc.internal.pageSize.height;
  const margin = 20;
  const lineHeight = 7;

  // Título
  doc.setFontSize(18);
  doc.text('Relatório de Análise de Campanhas', margin, yPosition);
  yPosition += 15;

  // Data de geração
  doc.setFontSize(10);
  doc.setTextColor(100, 100, 100);
  doc.text(`Gerado em: ${new Date(analysisData.generated_at).toLocaleString('pt-BR')}`, margin, yPosition);
  yPosition += 10;

  doc.setTextColor(0, 0, 0);

  // Resumo Executivo
  doc.setFontSize(14);
  doc.text('Resumo Executivo', margin, yPosition);
  yPosition += 8;
  doc.setFontSize(10);
  const executiveLines = doc.splitTextToSize(analysisData.executive_summary, 170);
  executiveLines.forEach(line => {
    if (yPosition > pageHeight - 20) {
      doc.addPage();
      yPosition = 20;
    }
    doc.text(line, margin, yPosition);
    yPosition += lineHeight;
  });
  yPosition += 5;

  // Métricas Principais
  if (yPosition > pageHeight - 40) {
    doc.addPage();
    yPosition = 20;
  }
  doc.setFontSize(14);
  doc.text('Métricas Principais', margin, yPosition);
  yPosition += 8;
  doc.setFontSize(10);
  const metrics = analysisData.metrics_summary;
  doc.text(`Total de Campanhas: ${metrics.total_campaigns}`, margin, yPosition);
  yPosition += lineHeight;
  doc.text(`Gasto Total: R$ ${metrics.total_spend.toFixed(2)}`, margin, yPosition);
  yPosition += lineHeight;
  doc.text(`Total de Conversões: ${metrics.total_conversions}`, margin, yPosition);
  yPosition += 10;

  // Problemas Identificados
  if (analysisData.key_issues && analysisData.key_issues.length > 0) {
    if (yPosition > pageHeight - 40) {
      doc.addPage();
      yPosition = 20;
    }
    doc.setFontSize(14);
    doc.text('Problemas Identificados', margin, yPosition);
    yPosition += 8;
    doc.setFontSize(10);
    analysisData.key_issues.forEach((issue, index) => {
      if (yPosition > pageHeight - 30) {
        doc.addPage();
        yPosition = 20;
      }
      doc.setFontSize(11);
      doc.text(`${index + 1}. ${issue.title} (${issue.severity})`, margin, yPosition);
      yPosition += lineHeight;
      doc.setFontSize(10);
      const descLines = doc.splitTextToSize(issue.description, 170);
      descLines.forEach(line => {
        if (yPosition > pageHeight - 20) {
          doc.addPage();
          yPosition = 20;
        }
        doc.text(line, margin + 5, yPosition);
        yPosition += lineHeight;
      });
      yPosition += 3;
    });
    yPosition += 5;
  }

  // Recomendações
  if (analysisData.recommendations && analysisData.recommendations.length > 0) {
    if (yPosition > pageHeight - 40) {
      doc.addPage();
      yPosition = 20;
    }
    doc.setFontSize(14);
    doc.text('Recomendações', margin, yPosition);
    yPosition += 8;
    doc.setFontSize(10);
    analysisData.recommendations.forEach((rec, index) => {
      if (yPosition > pageHeight - 30) {
        doc.addPage();
        yPosition = 20;
      }
      doc.setFontSize(11);
      doc.text(`${index + 1}. ${rec.title} (${rec.priority})`, margin, yPosition);
      yPosition += lineHeight;
      doc.setFontSize(10);
      const descLines = doc.splitTextToSize(rec.description, 170);
      descLines.forEach(line => {
        if (yPosition > pageHeight - 20) {
          doc.addPage();
          yPosition = 20;
        }
        doc.text(line, margin + 5, yPosition);
        yPosition += lineHeight;
      });
      yPosition += 3;
    });
  }

  // Salvar PDF
  doc.save(`analise-campanhas-${new Date().toISOString().split('T')[0]}.pdf`);
}

/**
 * Exporta os resultados da análise para Excel
 */
export function exportToExcel(analysisData) {
  if (!analysisData) {
    throw new Error('Dados de análise não disponíveis');
  }

  const workbook = XLSX.utils.book_new();

  // Aba 1: Resumo
  const summaryData = [
    ['Relatório de Análise de Campanhas'],
    ['Gerado em:', new Date(analysisData.generated_at).toLocaleString('pt-BR')],
    [],
    ['Resumo Executivo'],
    [analysisData.executive_summary],
    [],
    ['Métricas Principais'],
    ['Total de Campanhas', analysisData.metrics_summary.total_campaigns],
    ['Gasto Total', analysisData.metrics_summary.total_spend],
    ['Total de Conversões', analysisData.metrics_summary.total_conversions],
  ];
  const summarySheet = XLSX.utils.aoa_to_sheet(summaryData);
  XLSX.utils.book_append_sheet(workbook, summarySheet, 'Resumo');

  // Aba 2: Problemas
  if (analysisData.key_issues && analysisData.key_issues.length > 0) {
    const issuesData = [
      ['Título', 'Descrição', 'Severidade', 'Campanhas Afetadas', 'Impacto Potencial']
    ];
    analysisData.key_issues.forEach(issue => {
      issuesData.push([
        issue.title,
        issue.description,
        issue.severity,
        issue.affected_campaigns.join(', '),
        issue.potential_impact
      ]);
    });
    const issuesSheet = XLSX.utils.aoa_to_sheet(issuesData);
    XLSX.utils.book_append_sheet(workbook, issuesSheet, 'Problemas');
  }

  // Aba 3: Recomendações
  if (analysisData.recommendations && analysisData.recommendations.length > 0) {
    const recsData = [
      ['Título', 'Descrição', 'Racional', 'Prioridade', 'Resultado Esperado']
    ];
    analysisData.recommendations.forEach(rec => {
      recsData.push([
        rec.title,
        rec.description,
        rec.rationale,
        rec.priority,
        rec.expected_outcome
      ]);
    });
    const recsSheet = XLSX.utils.aoa_to_sheet(recsData);
    XLSX.utils.book_append_sheet(workbook, recsSheet, 'Recomendações');
  }

  // Aba 4: Alertas
  if (analysisData.risk_alerts && analysisData.risk_alerts.length > 0) {
    const alertsData = [
      ['Título', 'Descrição', 'Severidade', 'Mitigação']
    ];
    analysisData.risk_alerts.forEach(alert => {
      alertsData.push([
        alert.title,
        alert.description,
        alert.severity,
        alert.mitigation
      ]);
    });
    const alertsSheet = XLSX.utils.aoa_to_sheet(alertsData);
    XLSX.utils.book_append_sheet(workbook, alertsSheet, 'Alertas');
  }

  // Aba 5: Métricas por Canal
  if (analysisData.metrics_summary?.by_channel && analysisData.metrics_summary.by_channel.length > 0) {
    const channelData = [
      ['Canal', 'Impressões', 'Cliques', 'Conversões', 'Custo Total', 'CTR Médio', 'CPA Médio', 'Nº Campanhas']
    ];
    analysisData.metrics_summary.by_channel.forEach(channel => {
      channelData.push([
        channel.channel,
        channel.total_impressions,
        channel.total_clicks,
        channel.total_conversions,
        channel.total_cost,
        channel.avg_ctr,
        channel.avg_cpa,
        channel.campaign_count
      ]);
    });
    const channelSheet = XLSX.utils.aoa_to_sheet(channelData);
    XLSX.utils.book_append_sheet(workbook, channelSheet, 'Métricas por Canal');
  }

  // Salvar Excel
  XLSX.writeFile(workbook, `analise-campanhas-${new Date().toISOString().split('T')[0]}.xlsx`);
}

/**
 * Exporta os resultados da análise para JSON
 */
export function exportToJSON(analysisData) {
  if (!analysisData) {
    throw new Error('Dados de análise não disponíveis');
  }

  const dataStr = JSON.stringify(analysisData, null, 2);
  const dataBlob = new Blob([dataStr], { type: 'application/json' });
  const url = URL.createObjectURL(dataBlob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `analise-campanhas-${new Date().toISOString().split('T')[0]}.json`;
  link.click();
  URL.revokeObjectURL(url);
}
