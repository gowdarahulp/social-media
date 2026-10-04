"""API routes for aggregate anonymized demographic profiling with k-anonymity."""
from typing import Optional
from fastapi import APIRouter, Query
from backend.app.schemas.demographics import DemographicsSummary
from backend.app.demographics import DemographicProfiler

router = APIRouter(prefix="/api/demographics", tags=["Demographic Profiling"])

@router.get("/summary", response_model=DemographicsSummary)
def get_demographics_summary(
    k: Optional[int] = Query(default=20, ge=5, le=100, description="Minimum cohort size threshold (k-anonymity)")
):
    return DemographicProfiler.get_aggregate_demographics(k_threshold=k)
