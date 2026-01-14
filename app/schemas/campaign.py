"""Pydantic schemas for campaign analysis."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Severity levels for issues and alerts."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Priority(str, Enum):
    """Priority levels for recommendations."""
    
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


# Input Schemas
class CampaignDataRow(BaseModel):
    """Schema for a single campaign data row from CSV."""
    
    campaign_name: str = Field(..., description="Nome da campanha")
    impressions: int = Field(..., ge=0, description="Número de impressões")
    clicks: int = Field(..., ge=0, description="Número de cliques")
    ctr: float = Field(..., ge=0, le=100, description="Click-through rate (%)")
    conversions: int = Field(..., ge=0, description="Número de conversões")
    cost: float = Field(..., ge=0, description="Custo total da campanha")
    cpa: float = Field(..., ge=0, description="Custo por aquisição")
    channel: str = Field(..., description="Canal de marketing")


# Validation Schemas
class ValidationError(BaseModel):
    """Represents a single validation error."""
    
    field: str = Field(..., description="Campo com erro")
    message: str = Field(..., description="Mensagem de erro")
    row: Optional[int] = Field(None, description="Linha do CSV (se aplicável)")
    value: Optional[str] = Field(None, description="Valor inválido encontrado")


class ValidationResult(BaseModel):
    """Result of CSV validation."""
    
    is_valid: bool = Field(..., description="Se a validação passou")
    errors: list[ValidationError] = Field(default_factory=list, description="Lista de erros")
    warnings: list[ValidationError] = Field(default_factory=list, description="Lista de avisos")
    rows_processed: int = Field(0, description="Número de linhas processadas")


# Metrics Analysis Schemas
class MetricsSummary(BaseModel):
    """Summary statistics for a metric."""
    
    mean: float = Field(..., description="Média")
    median: float = Field(..., description="Mediana")
    std: float = Field(..., description="Desvio padrão")
    min: float = Field(..., description="Valor mínimo")
    max: float = Field(..., description="Valor máximo")


class ChannelMetrics(BaseModel):
    """Aggregated metrics by channel."""
    
    channel: str = Field(..., description="Nome do canal")
    total_impressions: int = Field(..., description="Total de impressões")
    total_clicks: int = Field(..., description="Total de cliques")
    total_conversions: int = Field(..., description="Total de conversões")
    total_cost: float = Field(..., description="Custo total")
    avg_ctr: float = Field(..., description="CTR médio")
    avg_cpa: float = Field(..., description="CPA médio")
    campaign_count: int = Field(..., description="Número de campanhas")


class PatternDetection(BaseModel):
    """Detected pattern/issue in campaign data."""
    
    pattern_type: str = Field(..., description="Tipo de padrão detectado")
    campaigns: list[str] = Field(..., description="Campanhas afetadas")
    description: str = Field(..., description="Descrição do padrão")
    severity: Severity = Field(..., description="Severidade do problema")


class MetricsAnalysis(BaseModel):
    """Complete metrics analysis result."""
    
    total_campaigns: int = Field(..., description="Total de campanhas analisadas")
    total_spend: float = Field(..., description="Gasto total")
    total_conversions: int = Field(..., description="Total de conversões")
    
    impressions_summary: MetricsSummary = Field(..., description="Resumo de impressões")
    ctr_summary: MetricsSummary = Field(..., description="Resumo de CTR")
    cpa_summary: MetricsSummary = Field(..., description="Resumo de CPA")
    conversions_summary: MetricsSummary = Field(..., description="Resumo de conversões")
    
    by_channel: list[ChannelMetrics] = Field(..., description="Métricas por canal")
    
    patterns_detected: list[PatternDetection] = Field(
        default_factory=list, 
        description="Padrões problemáticos detectados"
    )
    
    top_performers: list[str] = Field(..., description="Top 3 campanhas por conversão")
    bottom_performers: list[str] = Field(..., description="Bottom 3 campanhas por conversão")


# Insight Response Schemas
class KeyIssue(BaseModel):
    """A key issue identified in the campaign data."""
    
    title: str = Field(..., description="Título do problema")
    description: str = Field(..., description="Descrição detalhada")
    affected_campaigns: list[str] = Field(..., description="Campanhas afetadas")
    severity: Severity = Field(..., description="Severidade")
    potential_impact: str = Field(..., description="Impacto potencial")


class Recommendation(BaseModel):
    """An actionable recommendation."""
    
    title: str = Field(..., description="Título da recomendação")
    description: str = Field(..., description="O que fazer")
    rationale: str = Field(..., description="Por que fazer")
    priority: Priority = Field(..., description="Prioridade")
    expected_outcome: str = Field(..., description="Resultado esperado")


class RiskAlert(BaseModel):
    """A risk alert for attention."""
    
    title: str = Field(..., description="Título do alerta")
    description: str = Field(..., description="Descrição do risco")
    severity: Severity = Field(..., description="Severidade")
    mitigation: str = Field(..., description="Como mitigar")


class InsightResponse(BaseModel):
    """Complete insight response from the analysis."""
    
    executive_summary: str = Field(
        ..., 
        description="Resumo executivo em 2-3 frases"
    )
    key_issues: list[KeyIssue] = Field(
        ..., 
        description="Principais problemas identificados"
    )
    recommendations: list[Recommendation] = Field(
        ..., 
        description="Recomendações acionáveis"
    )
    risk_alerts: list[RiskAlert] = Field(
        ..., 
        description="Alertas de risco"
    )
    metrics_summary: MetricsAnalysis = Field(
        ..., 
        description="Resumo das métricas analisadas"
    )
    generated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Data/hora da geração"
    )
    
    class Config:
        """Pydantic config."""
        
        json_schema_extra = {
            "example": {
                "executive_summary": "A análise identificou 3 campanhas com problemas críticos...",
                "key_issues": [],
                "recommendations": [],
                "risk_alerts": [],
                "metrics_summary": {},
                "generated_at": "2024-01-15T10:30:00Z"
            }
        }
