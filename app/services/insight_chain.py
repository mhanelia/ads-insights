"""LangChain insight generation service with multi-LLM support."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from langchain.prompts import PromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_core.language_models.chat_models import BaseChatModel

from app.config import LLMProvider, get_settings
from app.logging_config import get_logger
from app.schemas.campaign import (
    InsightResponse,
    KeyIssue,
    MetricsAnalysis,
    Priority,
    Recommendation,
    RiskAlert,
    Severity,
)
from app.services.metrics_analyzer import analysis_to_llm_context

logger = get_logger(__name__)

# Path to prompt template
PROMPT_PATH = Path(__file__).parent.parent / "prompts" / "insight_prompt.txt"


def get_llm(provider: LLMProvider) -> Optional[BaseChatModel]:
    """
    Get the appropriate LLM instance based on provider.
    
    Args:
        provider: The LLM provider to use
        
    Returns:
        LLM instance or None for mock mode
    """
    settings = get_settings()
    
    match provider:
        case LLMProvider.OPENAI:
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=settings.openai_model,
                temperature=settings.llm_temperature,
                timeout=settings.llm_timeout,
                api_key=settings.openai_api_key,
            )
        
        case LLMProvider.CLAUDE:
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=settings.anthropic_model,
                temperature=settings.llm_temperature,
                timeout=settings.llm_timeout,
                api_key=settings.anthropic_api_key,
            )
        
        case LLMProvider.GEMINI:
            from langchain_google_genai import ChatGoogleGenerativeAI
            return ChatGoogleGenerativeAI(
                model=settings.google_model,
                temperature=settings.llm_temperature,
                timeout=settings.llm_timeout,
                google_api_key=settings.google_api_key,
            )
        
        case LLMProvider.MOCK:
            return None
    
    return None


def load_prompt_template() -> str:
    """Load the prompt template from file."""
    with open(PROMPT_PATH, "r", encoding="utf-8") as f:
        return f.read()


def generate_fallback_insights(analysis: MetricsAnalysis) -> InsightResponse:
    """
    Generate basic insights without LLM.
    
    Used when:
    - LLM is in mock mode
    - LLM call fails
    - API key is not configured
    """
    logger.info("generating_fallback_insights")
    
    # Build executive summary from patterns
    issues_summary = ""
    if analysis.patterns_detected:
        critical = [p for p in analysis.patterns_detected if p.severity == Severity.CRITICAL]
        high = [p for p in analysis.patterns_detected if p.severity == Severity.HIGH]
        
        if critical:
            issues_summary = f"ATENÇÃO: {len(critical)} problema(s) crítico(s) detectado(s). "
        if high:
            issues_summary += f"{len(high)} problema(s) de alta severidade identificado(s). "
    
    executive_summary = (
        f"Análise de {analysis.total_campaigns} campanhas com gasto total de "
        f"${analysis.total_spend:,.2f} e {analysis.total_conversions} conversões. "
        f"{issues_summary}"
        f"CPA médio: ${analysis.cpa_summary.mean:.2f}."
    )
    
    # Convert patterns to key issues
    key_issues = [
        KeyIssue(
            title=p.pattern_type.replace("_", " ").title(),
            description=p.description,
            affected_campaigns=p.campaigns[:5],  # Limit to 5
            severity=p.severity,
            potential_impact="Requer análise detalhada para estimar impacto financeiro.",
        )
        for p in analysis.patterns_detected
    ]
    
    # Generate recommendations based on patterns
    recommendations = []
    
    # Check for high CPA
    if any(p.pattern_type == "high_cpa" for p in analysis.patterns_detected):
        recommendations.append(
            Recommendation(
                title="Otimizar campanhas com CPA alto",
                description="Revisar segmentação, criativos e landing pages das campanhas identificadas.",
                rationale="CPA acima da média reduz o ROI geral do investimento.",
                priority=Priority.HIGH,
                expected_outcome="Redução de 20-30% no CPA médio.",
            )
        )
    
    # Check for zero conversions
    if any(p.pattern_type == "zero_conversions_high_spend" for p in analysis.patterns_detected):
        recommendations.append(
            Recommendation(
                title="Pausar ou revisar campanhas sem conversões",
                description="Avaliar se campanhas com zero conversões devem ser pausadas imediatamente.",
                rationale="Orçamento está sendo gasto sem retorno mensurável.",
                priority=Priority.HIGH,
                expected_outcome="Economia imediata de orçamento.",
            )
        )
    
    # Check for high CTR low conversion
    if any(p.pattern_type == "high_ctr_low_conversion" for p in analysis.patterns_detected):
        recommendations.append(
            Recommendation(
                title="Revisar landing pages",
                description="Analisar a experiência pós-clique das campanhas com CTR alto mas baixa conversão.",
                rationale="Alto engajamento não está se traduzindo em conversões.",
                priority=Priority.MEDIUM,
                expected_outcome="Aumento da taxa de conversão em 10-20%.",
            )
        )
    
    # Default recommendation if none generated
    if not recommendations:
        recommendations.append(
            Recommendation(
                title="Manter monitoramento ativo",
                description="Continuar acompanhando métricas e comparando com benchmarks do setor.",
                rationale="Campanhas estão dentro dos parâmetros esperados.",
                priority=Priority.LOW,
                expected_outcome="Identificação precoce de problemas.",
            )
        )
    
    # Generate risk alerts for critical patterns
    risk_alerts = [
        RiskAlert(
            title=f"Risco: {p.pattern_type.replace('_', ' ').title()}",
            description=p.description,
            severity=p.severity,
            mitigation="Revisar campanha(s) afetada(s) imediatamente e considerar pausa.",
        )
        for p in analysis.patterns_detected
        if p.severity in [Severity.CRITICAL, Severity.HIGH]
    ]
    
    return InsightResponse(
        executive_summary=executive_summary,
        key_issues=key_issues,
        recommendations=recommendations,
        risk_alerts=risk_alerts,
        metrics_summary=analysis,
        generated_at=datetime.utcnow(),
    )


async def generate_insights(analysis: MetricsAnalysis) -> InsightResponse:
    """
    Generate insights using LLM or fallback to deterministic analysis.
    
    Args:
        analysis: MetricsAnalysis from deterministic analysis
        
    Returns:
        InsightResponse with AI-generated or fallback insights
    """
    settings = get_settings()
    
    # Check if LLM is configured
    if not settings.is_llm_configured():
        logger.warning(
            "llm_not_configured",
            provider=settings.llm_provider.value,
            message="Using fallback insights",
        )
        return generate_fallback_insights(analysis)
    
    # Get LLM instance
    llm = get_llm(settings.llm_provider)
    
    if llm is None:
        logger.info("using_mock_mode")
        return generate_fallback_insights(analysis)
    
    try:
        logger.info(
            "calling_llm",
            provider=settings.llm_provider.value,
            model=getattr(llm, "model_name", "unknown"),
        )
        
        # Prepare output parser
        parser = PydanticOutputParser(pydantic_object=InsightResponse)
        
        # Load and format prompt
        prompt_template = load_prompt_template()
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["analysis_data"],
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        
        # Prepare context
        context = analysis_to_llm_context(analysis)
        formatted_prompt = prompt.format(analysis_data=json.dumps(context, indent=2))
        
        # Call LLM
        response = await llm.ainvoke(formatted_prompt)
        
        # Parse response
        content = response.content if hasattr(response, "content") else str(response)
        
        # Try to extract JSON from response
        try:
            # Find JSON in response (handle markdown code blocks)
            if "```json" in content:
                json_start = content.find("```json") + 7
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            elif "```" in content:
                json_start = content.find("```") + 3
                json_end = content.find("```", json_start)
                content = content[json_start:json_end].strip()
            
            parsed_data = json.loads(content)
            
            # Build InsightResponse from parsed data
            insight_response = InsightResponse(
                executive_summary=parsed_data.get("executive_summary", "Análise concluída."),
                key_issues=[
                    KeyIssue(**issue) for issue in parsed_data.get("key_issues", [])
                ],
                recommendations=[
                    Recommendation(**rec) for rec in parsed_data.get("recommendations", [])
                ],
                risk_alerts=[
                    RiskAlert(**alert) for alert in parsed_data.get("risk_alerts", [])
                ],
                metrics_summary=analysis,
                generated_at=datetime.utcnow(),
            )
            
            logger.info("llm_insights_generated", issues=len(insight_response.key_issues))
            return insight_response
            
        except (json.JSONDecodeError, KeyError, TypeError) as parse_error:
            logger.warning(
                "llm_response_parse_error",
                error=str(parse_error),
                message="Falling back to deterministic insights",
            )
            return generate_fallback_insights(analysis)
        
    except Exception as e:
        logger.error(
            "llm_call_failed",
            error=str(e),
            provider=settings.llm_provider.value,
            message="Falling back to deterministic insights",
        )
        return generate_fallback_insights(analysis)
