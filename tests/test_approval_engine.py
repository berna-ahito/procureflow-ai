from unittest.mock import MagicMock

import pytest

from app.services.approval_engine import (
    ALLOWED_TRANSITIONS,
    apply_decision,
    evaluate_rules,
    route_request,
    validate_transition,
)


class FakeRule:
    def __init__(self, name, min_amount, max_amount, category, required_role, priority, is_active=True):
        self.name = name
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.category = category
        self.required_role = required_role
        self.priority = priority
        self.is_active = is_active


@pytest.fixture
def rule_low_value():
    return FakeRule("Low", 0, 999.99, None, "manager", 10)


@pytest.fixture
def rule_high_value():
    return FakeRule("High", 1000, None, None, "finance", 20)


@pytest.fixture
def rule_it_category():
    return FakeRule("IT", 0, None, "IT", "manager", 5)


def test_match_low_value_request(rule_low_value, rule_high_value):
    result = evaluate_rules([rule_low_value, rule_high_value], 500.0, "Office")
    assert result is not None
    assert result.required_role == "manager"


def test_match_high_value_request(rule_low_value, rule_high_value):
    result = evaluate_rules([rule_low_value, rule_high_value], 2000.0, "Office")
    assert result is not None
    assert result.required_role == "finance"


def test_match_it_category_wins_priority(rule_low_value, rule_it_category):
    result = evaluate_rules([rule_low_value, rule_it_category], 500.0, "IT")
    assert result is not None
    assert result.name == "IT"
    assert result.required_role == "manager"


def test_no_match_returns_none():
    result = evaluate_rules([], 500.0, "Office")
    assert result is None


def test_category_none_matches_any(rule_low_value):
    result = evaluate_rules([rule_low_value], 100.0, "Anything")
    assert result is not None


def test_category_specific_no_match(rule_it_category):
    result = evaluate_rules([rule_it_category], 100.0, "Office")
    assert result is None


def test_inactive_rule_skipped():
    rule = FakeRule("Low", 0, 999.99, None, "manager", 10, is_active=False)
    result = evaluate_rules([rule], 500.0, "Office")
    assert result is None


def test_max_amount_none_means_no_upper_bound(rule_high_value):
    result = evaluate_rules([rule_high_value], 999999.0, "Office")
    assert result is not None
    assert result.required_role == "finance"


def test_min_amount_boundary(rule_high_value):
    result = evaluate_rules([rule_high_value], 1000.0, "Office")
    assert result is not None
    assert result.required_role == "finance"


def test_priority_order_first_wins(rule_low_value, rule_it_category):
    result = evaluate_rules([rule_low_value, rule_it_category], 500.0, "IT")
    assert result.name == "IT"


def test_status_transition_draft_to_pending_review():
    validate_transition("draft", "pending_review")


def test_status_transition_invalid_raises():
    with pytest.raises(ValueError):
        validate_transition("draft", "approved")


def test_status_transition_approved_is_terminal():
    with pytest.raises(ValueError):
        validate_transition("approved", "pending_review")


def test_allowed_transitions_dict_exists():
    assert isinstance(ALLOWED_TRANSITIONS, dict)
    assert "draft" in ALLOWED_TRANSITIONS
    assert "approved" in ALLOWED_TRANSITIONS
    assert ALLOWED_TRANSITIONS["approved"] == []


def test_needs_more_info_returns_to_draft():
    validate_transition("needs_more_info", "draft")


@pytest.mark.parametrize("from_status,to_status", [
    ("pending_approval", "approved"),
    ("pending_approval", "rejected"),
    ("pending_approval", "needs_more_info"),
    ("pending_review", "pending_approval"),
    ("pending_review", "needs_rule"),
])
def test_valid_transitions(from_status, to_status):
    validate_transition(from_status, to_status)


def _fake_db(rules=None):
    db = MagicMock()
    query_chain = MagicMock()
    query_chain.filter.return_value = query_chain
    query_chain.order_by.return_value = query_chain
    query_chain.all.return_value = rules or []
    db.query.return_value = query_chain
    return db


def _fake_request(status="pending_review", cost=500.0, category="Office"):
    req = MagicMock()
    req.status = status
    req.estimated_cost = cost
    req.category = category
    req.assigned_role = None
    return req


def test_route_request_match_sets_pending_approval(rule_low_value):
    db = _fake_db(rules=[rule_low_value])
    req = _fake_request(cost=500.0, category="Office")
    result = route_request(db, req)
    assert req.status == "pending_approval"
    assert req.assigned_role == "manager"
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(req)


def test_route_request_no_match_sets_needs_rule():
    db = _fake_db(rules=[])
    req = _fake_request(cost=500.0, category="Office")
    route_request(db, req)
    assert req.status == "needs_rule"
    assert req.assigned_role is None


def test_apply_decision_approved():
    db = _fake_db()
    req = _fake_request(status="pending_approval")
    result = apply_decision(db, req, "approved", None)
    assert req.status == "approved"
    db.commit.assert_called_once()


def test_apply_decision_rejected():
    db = _fake_db()
    req = _fake_request(status="pending_approval")
    apply_decision(db, req, "rejected", "not justified")
    assert req.status == "rejected"


def test_apply_decision_needs_more_info():
    db = _fake_db()
    req = _fake_request(status="pending_approval")
    apply_decision(db, req, "needs_more_info", "clarify budget")
    assert req.status == "needs_more_info"


def test_apply_decision_invalid_transition_raises():
    db = _fake_db()
    req = _fake_request(status="draft")
    with pytest.raises(ValueError):
        apply_decision(db, req, "approved", None)
