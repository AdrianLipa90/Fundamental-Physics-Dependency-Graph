#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PATH = HERE / "FPDG_600CELL_S3_CANDIDATE_WORKING_LAYER_V0_2.json"


def main() -> int:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    assert data["schema"] == "FPDG_CANDIDATE_WORKING_LAYER_V0_2"
    assert data["status"] == "CANDIDATE"
    assert data["active_working"] is True
    assert data["canonical_graph_unchanged"] is True

    nodes = data["nodes"]
    edges = data["edges"]
    ids = [row["id"] for row in nodes]
    assert len(ids) == len(set(ids))
    assert all(row["status"] == "CANDIDATE" for row in nodes)
    allowed = set(ids)
    assert all(edge["from"] in allowed and edge["to"] in allowed for edge in edges)

    rules = data["rules"]
    assert rules["candidate_can_feed_candidate"] is True
    assert rules["candidate_can_satisfy_canonical_gate_without_promotion"] is False
    assert rules["candidate_is_executable"] is True
    assert rules["candidate_is_not_failed"] is True
    assert rules["candidate_must_preserve_status"] is True
    assert rules["candidate_physical_binding_is_not_implied"] is True

    required = {
        "TIR_600CELL_S3_RANK_CLOSURE_CANDIDATE_V0_2",
        "PNCS_600CELL_S3_RANK_CLOSURE_CANDIDATE_V0_2",
        "PNCS_SUPPORT_MASK_PARENT_G_V0_2",
        "PNCS_GREMLIN_ROUND28_RELATION_BINDING_V0_2",
    }
    assert required <= allowed

    validated = data["validated_candidate_results"]
    assert validated["s3_full_sector_sampling"] == "ell=0..5"
    assert validated["ell6_first_rank_collapse"] == "49->25"
    assert validated["ell7_cumulative_finite_closure"] == "116->120 with 4 new directions"

    print(json.dumps({
        "schema": "FPDG_600CELL_WORKING_LAYER_VALIDATION_V0_2",
        "status": "PASS",
        "candidate_status": "ACTIVE_WORKING",
        "nodes": len(nodes),
        "edges": len(edges),
        "canonical_graph_unchanged": True,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
