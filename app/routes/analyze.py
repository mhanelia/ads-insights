"""Campaign analysis endpoint."""

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.logging_config import get_logger
from app.schemas.campaign import InsightResponse, ValidationResult
from app.services.csv_loader import load_csv_file
from app.services.csv_transformer import CSVFormat
from app.services.insight_chain import generate_insights
from app.services.metrics_analyzer import analyze_metrics
from app.services.validator import validate_campaign_data

router = APIRouter()
logger = get_logger(__name__)


@router.post(
    "/analyze-campaign",
    response_model=InsightResponse,
    summary="Analyze marketing campaign data",
    description=(
        "Upload a CSV file with campaign data and receive AI-powered insights, "
        "recommendations, and risk alerts."
    ),
    responses={
        200: {
            "description": "Analysis completed successfully",
            "model": InsightResponse,
        },
        400: {
            "description": "Validation failed - invalid data in CSV",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Validation failed",
                        "validation_result": {
                            "is_valid": False,
                            "errors": [
                                {
                                    "field": "campaign_name",
                                    "message": "Required column 'campaign_name' is missing",
                                }
                            ],
                        },
                    }
                }
            },
        },
        422: {
            "description": "File is not a valid CSV",
        },
    },
)
async def analyze_campaign(
    file: UploadFile = File(
        ...,
        description="CSV file with campaign data",
    ),
) -> InsightResponse:
    """
    Analyze marketing campaign data from a CSV file.
    
    Supports two CSV formats:
    1. Original format with columns: campaign_name, impressions, clicks, ctr, conversions, cost, cpa, channel
    2. Meta Ads format (Portuguese) exported from Meta Business Suite
    
    The format is detected automatically.
    
    Returns structured insights including:
    - Executive summary
    - Key issues identified
    - Actionable recommendations
    - Risk alerts
    - Detailed metrics summary
    """
    logger.info(
        "analyze_campaign_started",
        filename=file.filename,
        content_type=file.content_type,
    )
    
    # Validate file type
    if file.content_type not in ["text/csv", "application/csv", "application/vnd.ms-excel"]:
        if not (file.filename and file.filename.endswith(".csv")):
            logger.warning(
                "invalid_file_type",
                content_type=file.content_type,
                filename=file.filename,
            )
            raise HTTPException(
                status_code=422,
                detail="File must be a CSV",
            )
    
    # Step 1: Load CSV (auto-detects format)
    try:
        df, csv_format = await load_csv_file(file)
        logger.info("csv_format_detected", format=csv_format.value)
    except ValueError as e:
        logger.error("csv_load_error", error=str(e))
        raise HTTPException(
            status_code=422,
            detail=f"Invalid CSV file: {e}",
        )
    
    # Step 2: Validate data
    validation_result = validate_campaign_data(df)
    
    if not validation_result.is_valid:
        logger.warning(
            "validation_failed",
            errors=len(validation_result.errors),
        )
        raise HTTPException(
            status_code=400,
            detail={
                "message": "Validation failed",
                "validation_result": validation_result.model_dump(),
            },
        )
    
    # Log warnings if any
    if validation_result.warnings:
        logger.info(
            "validation_warnings",
            warnings=len(validation_result.warnings),
        )
    
    # Step 3: Analyze metrics (deterministic)
    analysis = analyze_metrics(df)
    
    # Step 4: Generate insights (LLM or fallback)
    insights = await generate_insights(analysis)
    
    logger.info(
        "analyze_campaign_completed",
        campaigns=analysis.total_campaigns,
        issues=len(insights.key_issues),
        recommendations=len(insights.recommendations),
    )
    
    return insights
