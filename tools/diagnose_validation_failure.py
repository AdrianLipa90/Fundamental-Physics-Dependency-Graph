#!/usr/bin/env python3
"""Run the full exact-pain stack from a source-side validation failure receipt.

Pipeline:
validation failure receipt -> FPDG evidence -> claim frontier and/or exact interface
coordinate -> dependency/interface seams -> micro coordinates -> graph bottlenecks ->
deterministic probe order -> repository-agnostic pain signature -> incident retrieval ->
GREMLIN candidate packet.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUILD_DIR = ROOT / "build"
sys.path.insert(0, str(ROOT / "tools"))

from analyze_diagnostic_bottlenecks import BottleneckError, analyze as analyze_bottlenecks, render_markdown as render_bottlenecks  # noqa: E402
from build_diagnostic_probe_plan import ProbePlanError, build_plan, render_markdown as render_probe_plan  # noqa: E402
from build_gremlin_pain_packet import PacketError, build_packet  # noqa: E402
from build_pain_signature import SignatureError, build_signature  # noqa: E402
from diagnose_inconsistency import DiagnosisError, diagnose, load_claims, load_graph, render_markdown  # noqa: E402
from enrich_gremlin_pain_packet_with_micro import MicroPacketError, enrich  # noqa: E402
from ingest_validation_failure import ReceiptError, load_json, receipt_to_evidence  # noqa: E402
from localize_interface_evidence import InterfaceEvidenceError, enrich_interface_diagnosis  # noqa: E402
from localize_interface_seams import (  # noqa: E402
    GRAPH_PATH as SEAM_GRAPH_PATH,
    INTERFACES_PATH as SEAM_INTERFACES_PATH,
    SeamError,
    load_yaml as load_seam_yaml,
    localize as localize_seams,
    render_markdown as render_seam_markdown,
)
from localize_micro_coordinates import MicroLocalizationError, localize as localize_micro, render_markdown as render_micro_markdown  # noqa: E402
from match_pain_signatures import DEFAULT_INCIDENT_DIR, MatchError, collect_incidents, match_signature  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--threshold", type=float, default=0.55)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    if not 0.0 <= args.threshold <= 1.0:
        print("FAIL: threshold must be in [0,1]", file=sys.stderr)
        return 1

    try:
        evidence = receipt_to_evidence(load_json(args.receipt))
        claims = load_claims(ROOT / "claims.jsonl")
        graph = load_graph()
        diagnosis = enrich_interface_diagnosis(diagnose(graph, claims, evidence), evidence)
        seams = localize_seams(
            diagnosis,
            load_seam_yaml(SEAM_GRAPH_PATH),
            load_seam_yaml(SEAM_INTERFACES_PATH),
        )
        micro = localize_micro(diagnosis, evidence)
        bottlenecks = analyze_bottlenecks(diagnosis, graph)
        signature = build_signature(diagnosis, seams)
        signature_path = BUILD_DIR / "PAIN_SIGNATURE.json"
        matches = match_signature(
            signature,
            collect_incidents(DEFAULT_INCIDENT_DIR, signature_path),
            args.threshold,
        )
        plan = build_plan(seams, micro, matches)
        packet = build_packet(diagnosis, seams, signature, matches)
        packet_micro = enrich(packet, micro)
        packet_micro["diagnostic_bottlenecks"] = bottlenecks
        packet_micro["diagnostic_probe_plan"] = plan

        BUILD_DIR.mkdir(exist_ok=True)
        outputs = {
            "VALIDATION_INCONSISTENCY_EVIDENCE.json": evidence,
            "INCONSISTENCY_EVIDENCE.json": evidence,
            "INCONSISTENCY_DIAGNOSIS.json": diagnosis,
            "PAIN_SEAM_REPORT.json": seams,
            "PAIN_MICRO_COORDINATES.json": micro,
            "DIAGNOSTIC_BOTTLENECKS.json": bottlenecks,
            "DIAGNOSTIC_PROBE_PLAN.json": plan,
            "PAIN_SIGNATURE.json": signature,
            "PAIN_SIGNATURE_MATCHES.json": matches,
            "GREMLIN_PAIN_PACKET.json": packet,
            "GREMLIN_PAIN_PACKET_MICRO.json": packet_micro,
        }
        for name, payload in outputs.items():
            (BUILD_DIR / name).write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        (BUILD_DIR / "INCONSISTENCY_DIAGNOSIS.md").write_text(render_markdown(diagnosis), encoding="utf-8")
        (BUILD_DIR / "PAIN_SEAM_REPORT.md").write_text(render_seam_markdown(seams), encoding="utf-8")
        (BUILD_DIR / "PAIN_MICRO_COORDINATES.md").write_text(render_micro_markdown(micro), encoding="utf-8")
        (BUILD_DIR / "DIAGNOSTIC_BOTTLENECKS.md").write_text(render_bottlenecks(bottlenecks), encoding="utf-8")
        (BUILD_DIR / "DIAGNOSTIC_PROBE_PLAN.md").write_text(render_probe_plan(plan), encoding="utf-8")

        first_probes = [
            zone["first_probe"]
            for zone in plan.get("zones", [])
            if isinstance(zone.get("first_probe"), dict)
        ]
        first_probes.extend(
            row["first_probe"]
            for row in plan.get("integration_zones", [])
            if isinstance(row.get("first_probe"), dict)
        )
        summary = {
            "schema": "FPDG_VALIDATION_PAIN_SUMMARY_V0_1",
            "status": diagnosis["status"],
            "localization_mode": diagnosis["localization_mode"],
            "minimal_failing_frontier": diagnosis["minimal_failing_frontier"],
            "interface_pain_points": diagnosis.get("integration_pain_points", []),
            "seam_status": seams["status"],
            "finest_micro_precision": micro["finest_precision"],
            "first_deterministic_probes": first_probes,
            "mandatory_bottleneck_edge_count": sum(
                len(zone.get("mandatory_edges", [])) for zone in bottlenecks.get("zones", [])
            ),
            "incident_match_count": matches["match_count"],
            "gremlin_claim_zones": len(packet_micro.get("zones", [])),
            "gremlin_integration_zones": len(packet_micro.get("integration_zones", [])),
            "causal_inference_performed": False,
            "candidate_edges_included": False,
        }
        (BUILD_DIR / "VALIDATION_PAIN_SUMMARY.json").write_text(
            json.dumps(summary, indent=2) + "\n", encoding="utf-8"
        )
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            probe_ids = [row.get("probe_id") for row in first_probes]
            print(
                f"{summary['status']}: frontier={summary['minimal_failing_frontier']} "
                f"interfaces={len(summary['interface_pain_points'])} "
                f"finest={summary['finest_micro_precision']} first_probes={probe_ids} "
                f"matches={summary['incident_match_count']}"
            )
        return 0 if diagnosis["status"] == "LOCALIZED" else 2
    except (
        OSError,
        json.JSONDecodeError,
        ReceiptError,
        DiagnosisError,
        InterfaceEvidenceError,
        SeamError,
        MicroLocalizationError,
        BottleneckError,
        ProbePlanError,
        SignatureError,
        MatchError,
        PacketError,
        MicroPacketError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
