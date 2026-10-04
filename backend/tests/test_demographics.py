"""Tests for demographic inference and strict k-anonymity guardrails."""
import pytest
from backend.app.connectors.replay import ReplayConnector
from backend.app.db.repository import PostRepository
from backend.app.demographics import DemographicProfiler

@pytest.mark.anyio
async def test_k_anonymity_enforcement_and_demographics():
    PostRepository.clear_all()
    connector = ReplayConnector()
    posts = await connector.fetch(limit=380)
    for p in posts:
        PostRepository.insert_post(p)

    # 1. Check with k=20
    summary = DemographicProfiler.get_aggregate_demographics(k_threshold=20)
    assert summary.total_analyzed_users >= 50
    assert summary.k_threshold == 20
    assert "k-Anonymity strictly enforced" in summary.privacy_guarantee

    # Verify no category in reported distributions has 0 < count < 20
    for group_name, dist_list in [
        ("age", summary.age_groups),
        ("geo", summary.geography),
        ("lang", summary.languages),
        ("interests", summary.professional_interests)
    ]:
        for d in dist_list:
            if not d.category.startswith("Protected"):
                assert d.count >= 20, f"Violation of k-anonymity in {group_name}: {d.category} has count {d.count} < 20"

    # 2. Check higher threshold k=35 triggers suppression
    strict_summary = DemographicProfiler.get_aggregate_demographics(k_threshold=35)
    suppressed_items = [d for d in strict_summary.geography if d.category.startswith("Protected")]
    assert len(suppressed_items) > 0
    assert suppressed_items[0].count > 0

    # 3. Check limitations and ethics section
    assert len(summary.limitations) >= 3
    assert any("re-identification" in lit for lit in summary.limitations)
