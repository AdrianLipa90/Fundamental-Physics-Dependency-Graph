#!/usr/bin/env python3
"""Fail-closed validator for the staged relational phase/observation bridge."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PATH = ROOT / "bridges" / "RELATIONAL_PHASE_OBSERVATION_BRIDGE_V0_1.yaml"

SCHEMA = "FPDG_RELATIONAL_PHASE_OBSERVATION_STAGING_V0_1"
REQUIRED_REPOSITORIES = {
    "IDT",
    "GREMLIN",
    "RFC",
    "TIR",
    "RC",
    "OES",
    "QHTRI_OPTICS",
    "PHASENAV_TELESCOPE",
    "PNCS",
    "PHASENAV_CORE",
    "PHASENAV_MAS",
}
REQUIRED_FIREWALLS = {
    "W_chem_is_not_identified_with_W_sem",
    "molecular_bond_graph_is_not_automatically_the_effective_state_graph",
    "acoustic_or_phase_optics_geometry_is_not_spacetime_geometry",
    "GREMLIN_residual_routing_is_not_source_attribution",
    "source_repository_claim_authority_remains_local",
}


class BridgeValidationError(RuntimeError):
    pass


def _mapping(value: Any, name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise BridgeValidationError(f"{name} must be a mapping")
    return value


def load_bridge(path: Path | str = DEFAULT_PATH) -> dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        payload = yaml.safe_load(fh)
    return _mapping(payload, "bridge")


def validate_bridge(payload: dict[str, Any]) -> dict[str, int]:
    if payload.get("schema") != SCHEMA:
        raise BridgeValidationError(
            f"unsupported schema {payload.get('schema')!r}; expected {SCHEMA!r}"
        )
    if payload.get("status") != "CANDIDATE_STAGING_NO_FEDERATION_PROMOTION":
        raise BridgeValidationError("staging bridge must remain non-promoted")

    authority = _mapping(payload.get("authority"), "authority")
    if authority.get("active_federated_dag_modified") is not False:
        raise BridgeValidationError("active federated DAG modification must remain false")
    if authority.get("source_repository_claim_authority_preserved") is not True:
        raise BridgeValidationError("source repository authority must be preserved")

    repositories = _mapping(payload.get("repositories"), "repositories")
    missing = REQUIRED_REPOSITORIES - set(repositories)
    if missing:
        raise BridgeValidationError(f"missing required repository roles: {sorted(missing)}")

    seen_repo_names: set[str] = set()
    for key, row_value in repositories.items():
        row = _mapping(row_value, f"repositories.{key}")
        repo = row.get("repository")
        role = row.get("role")
        branch = row.get("branch")
        if not isinstance(repo, str) or "/" not in repo:
            raise BridgeValidationError(f"{key}: invalid repository")
        if repo in seen_repo_names:
            raise BridgeValidationError(f"duplicate repository mapping {repo}")
        seen_repo_names.add(repo)
        if not isinstance(role, str) or not role:
            raise BridgeValidationError(f"{key}: missing role")
        if not isinstance(branch, str) or not branch:
            raise BridgeValidationError(f"{key}: missing branch")

    theorems = _mapping(payload.get("theorems"), "theorems")
    if not theorems:
        raise BridgeValidationError("theorem registry must not be empty")
    for theorem_id, theorem_value in theorems.items():
        theorem = _mapping(theorem_value, f"theorems.{theorem_id}")
        owner = theorem.get("owner")
        if owner not in repositories:
            raise BridgeValidationError(f"{theorem_id}: unknown owner {owner!r}")
        consumer = theorem.get("consumer")
        if consumer is not None and consumer not in repositories:
            raise BridgeValidationError(
                f"{theorem_id}: unknown consumer {consumer!r}"
            )
        if not theorem.get("status") or not theorem.get("equation"):
            raise BridgeValidationError(
                f"{theorem_id}: status and equation are required"
            )

    edges = payload.get("candidate_edges")
    if not isinstance(edges, list) or not edges:
        raise BridgeValidationError("candidate_edges must be a non-empty list")
    for index, edge_value in enumerate(edges):
        edge = _mapping(edge_value, f"candidate_edges[{index}]")
        src, dst = edge.get("from"), edge.get("to")
        if src not in repositories or dst not in repositories:
            raise BridgeValidationError(
                f"candidate edge {index}: unknown endpoint {src!r}->{dst!r}"
            )
        if src == dst:
            raise BridgeValidationError(f"candidate edge {index}: self-edge")
        if edge.get("status") not in {
            "CANDIDATE_ONLY",
            "MATHEMATICAL_INTERFACE",
            "OPEN_NOT_PROMOTED",
        }:
            raise BridgeValidationError(
                f"candidate edge {index}: invalid status {edge.get('status')!r}"
            )
        if not edge.get("promotion_gate"):
            raise BridgeValidationError(
                f"candidate edge {index}: promotion_gate is required"
            )

    firewalls = payload.get("firewalls")
    if not isinstance(firewalls, list):
        raise BridgeValidationError("firewalls must be a list")
    missing_firewalls = REQUIRED_FIREWALLS - set(firewalls)
    if missing_firewalls:
        raise BridgeValidationError(
            f"missing required firewalls: {sorted(missing_firewalls)}"
        )

    return {
        "repositories": len(repositories),
        "theorems": len(theorems),
        "candidate_edges": len(edges),
        "firewalls": len(firewalls),
    }


def main() -> None:
    counts = validate_bridge(load_bridge())
    print(
        "PASS: relational phase/observation staging bridge valid; "
        + " ".join(f"{key}={value}" for key, value in counts.items())
    )


if __name__ == "__main__":
    main()
