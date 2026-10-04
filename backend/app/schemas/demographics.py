"""Demographic profiling schemas with k-anonymity guarantee."""
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class DemographicDistribution(BaseModel):
    category: str
    count: int
    percentage: float
    confidence: float

class CohortDistribution(BaseModel):
    name: str
    is_suppressed: bool = False
    distribution: List[DemographicDistribution] = Field(default_factory=list)
    k_threshold: int = 20

class DemographicsSummary(BaseModel):
    total_analyzed_users: int
    k_threshold: int = 20
    privacy_guarantee: str = "k-anonymity strictly enforced; sub-threshold cohorts are suppressed"
    age_groups: List[DemographicDistribution]
    geography: List[DemographicDistribution]
    languages: List[DemographicDistribution]
    professional_interests: List[DemographicDistribution]
    confidence_overall: float
    limitations: List[str] = Field(default_factory=list)
