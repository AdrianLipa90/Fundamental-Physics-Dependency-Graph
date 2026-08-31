import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "interfaces" / "GSC3CDE_PHYSICAL_REALIZATION_DECOMPOSITION_CANDIDATE_V0_3.json"


def load_doc():
    return json.loads(DOC.read_text(encoding="utf-8"))


def test_candidate_is_noncanonical_and_fail_closed():
    d = load_doc()
    assert d["promotion_authority"] is False
    assert d["canonical_graph_mutation"] is False
    assert d["canon_mutations"] == []
    fw = d["firewalls"]
    assert fw["gremlin_can_promote"] is False
    assert fw["terminal36d_can_promote"] is False
    assert fw["phasenav36d_can_promote"] is False
    assert fw["candidate_edge_enters_canonical_graph"] is False


def test_numbering_collision_is_resolved():
    d = load_doc()
    assert "PR #102" in d["numbering"]["GSC3C"]
    assert "PR #104" in d["numbering"]["GSC3D"]
    assert "PR #103" in d["numbering"]["GSC3E"]


def test_gsc3d_alias_cannot_bypass_gsc3e_w0_binding():
    d = load_doc()
    route = d["tir_rfc_kinematic_alias_route"]
    req = set(route["requirements"])
    assert "FPDG.GSC3CDE.BETA_SHIFT_INTERFACE_ALIAS_THEOREM" in req
    assert "FPDG.GSC3CDE.SAME_PATCH_CLOCK_IDENTITY" in req
    assert "FPDG.GSC3CDE.GSC3E_COVARIANT_FAMILY_FIREWALL" in req
    assert "FPDG.GSC3CDE.SHARED_MATCHING_ONE_FORM_W0" in req
    assert route["target"] == "FPDG.GSC3CDE.RFE9_EXTRINSIC_CURVATURE_CROSSLINK"
    assert "W_q=A_qp W_p" in route["underdetermination_firewall"]


def test_w0_witness_remains_open_source_binding():
    d = load_doc()
    nodes = {n["id"]: n for n in d["candidate_nodes"]}
    assert nodes["FPDG.GSC3CDE.GSC3E_COVARIANT_FAMILY_FIREWALL"]["status"] == "HOSTED_PASS"
    assert nodes["FPDG.GSC3CDE.SHARED_MATCHING_ONE_FORM_W0"]["status"] == "OPEN_SOURCE_BINDING"
    assert nodes["FPDG.GSC3CDE.SHARED_MATCHING_ONE_FORM_W0"]["authority"] == "CANDIDATE_ONLY"


def test_product_and_event_routes_remain_separate():
    d = load_doc()
    assert d["product_route"]["target"] == "FPDG.GSC3CDE.PRODUCT_TRIVIALIZATION"
    assert d["event_route"]["target"] == "FPDG.GSC3CDE.EVENT_PLACEMENT"
    assert d["physical_event_spacetime_composition"]["target"] == "FPDG.GSC3CDE.PHYSICAL_EVENT_ON_SHARED_SPACETIME"


def test_source_validation_heads_are_typed():
    d = load_doc()
    src = d["source_validations"]
    assert src["gsc3d_beta_shift_alias"]["rfc_pr"] == 104
    assert src["gsc3d_beta_shift_alias"]["conclusion"] == "success"
    assert src["gsc3e_w0_source_binding_firewall"]["rfc_pr"] == 103
    assert src["gsc3e_w0_source_binding_firewall"]["head"] == "ab31c1fba78094efd7b01625adaebc1a44868845"
    assert src["gsc3e_w0_source_binding_firewall"]["conclusion"] == "success"
