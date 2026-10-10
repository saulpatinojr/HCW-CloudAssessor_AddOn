from datetime import UTC, datetime

from cloud_assessor_core.model import Assessment, Summary

from cloud_assessment_lab.store import AssessmentStore


def _assessment(i=0):
    return Assessment(
        id=f"a{i}",
        created_at=datetime(2026, 10, 10, tzinfo=UTC),
        catalog_version="1.0.0",
        core_version="0.1.0",
        source_format="arg-json",
        summary=Summary(
            resourceCount=0,
            byType={},
            criteriaCount=0,
            findingsCount=0,
            observed=0,
            **{"pass": 0, "fail": 0},
            unknown=0,
            notApplicable=0,
        ),
        scorecards=[],
        findings=[],
        unknown_by_design=[],
        ingestion_warnings=[],
    )


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_put_get_delete_with_token_and_404_semantics():
    store = AssessmentStore(ttl_seconds=60, max_items=5)
    stored = store.put(_assessment(), {"report.md": b"x"})
    assert len(stored.owner_token) >= 32 and stored.id != stored.owner_token
    assert store.get(stored.id, stored.owner_token)[1] == {"report.md": b"x"}
    assert store.get(stored.id, "wrong") is None
    assert store.get(stored.id, None) is None and store.get("", stored.owner_token) is None
    assert store.get("nope", stored.owner_token) is None
    assert store.expires_at(stored.id, stored.owner_token) == stored.expires_at
    assert store.delete(stored.id, "wrong") is False
    assert store.delete(stored.id, stored.owner_token) is True
    assert store.delete(stored.id, stored.owner_token) is False
    assert store.size == 0


def test_ttl_sweep_and_expiry_on_read():
    clock = Clock()
    store = AssessmentStore(ttl_seconds=10, max_items=5, clock=clock)
    s = store.put(_assessment(), {})
    clock.now += 11
    assert store.get(s.id, s.owner_token) is None
    assert store.sweep() == 1 and store.size == 0


def test_eviction_oldest_first():
    clock = Clock()
    store = AssessmentStore(ttl_seconds=100, max_items=2, clock=clock)
    first = store.put(_assessment(1), {})
    clock.now += 1
    second = store.put(_assessment(2), {})
    clock.now += 1
    third = store.put(_assessment(3), {})
    assert store.size == 2
    assert store.get(first.id, first.owner_token) is None
    assert store.get(second.id, second.owner_token) is not None and store.get(third.id, third.owner_token) is not None
    store.clear()
    assert store.size == 0
