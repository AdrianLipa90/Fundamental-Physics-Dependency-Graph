from copy import deepcopy

import pytest

from tools.validate_relational_phase_observation_bridge import (
    BridgeValidationError,
    load_bridge,
    validate_bridge,
)


def test_staging_bridge_validates():
    counts = validate_bridge(load_bridge())
    assert counts["repositories"] >= 11
    assert counts["theorems"] >= 8
    assert counts["candidate_edges"] >= 5
    assert counts["firewalls"] >= 5


def test_staging_bridge_cannot_silently_promote_active_dag():
    payload = load_bridge()
    mutated = deepcopy(payload)
    mutated["authority"]["active_federated_dag_modified"] = True
    with pytest.raises(BridgeValidationError):
        validate_bridge(mutated)


def test_source_authority_firewall_is_required():
    payload = load_bridge()
    mutated = deepcopy(payload)
    mutated["firewalls"] = [
        value
        for value in mutated["firewalls"]
        if value != "source_repository_claim_authority_remains_local"
    ]
    with pytest.raises(BridgeValidationError):
        validate_bridge(mutated)


def test_unknown_candidate_edge_endpoint_fails_closed():
    payload = load_bridge()
    mutated = deepcopy(payload)
    mutated["candidate_edges"][0]["to"] = "UNKNOWN_REPOSITORY"
    with pytest.raises(BridgeValidationError):
        validate_bridge(mutated)


def test_theorem_owner_must_be_registered():
    payload = load_bridge()
    mutated = deepcopy(payload)
    theorem_id = next(iter(mutated["theorems"]))
    mutated["theorems"][theorem_id]["owner"] = "UNKNOWN_REPOSITORY"
    with pytest.raises(BridgeValidationError):
        validate_bridge(mutated)
