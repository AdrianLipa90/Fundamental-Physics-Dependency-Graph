import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BASIS = ROOT / "interfaces" / "GLOBAL_SPACETIME_PRODUCTION_WITNESS_BASIS_V0_2.json"


def load_basis():
    return json.loads(BASIS.read_text(encoding="utf-8"))


def test_basis_refines_v01_without_changing_independent_group_count():
    data = load_basis()
    assert data["base_basis"].endswith("GLOBAL_SPACETIME_PRODUCTION_WITNESS_BASIS_V0_1.json")
    assert data["witness_group_count"] == 7
    assert data["minimality_boundary"]["claim"] == "CURRENT_ROUTE_MINIMALITY_ONLY"
    assert data["minimality_boundary"]["absolute_information_theoretic_minimality_claimed"] is False


def test_w2_requires_acyclic_product_provenance():
    data = load_basis()["refinement"]
    assert data["group"] == "W2_GSC3A_GLOBAL_PRODUCT_CLOCK"
    assert "product_provenance" in data["required"]
    prov = data["product_provenance"]
    assert prov["operator"] == "OR"
    assert set(prov["admitted"]) == {
        "FLOW_COVERAGE",
        "INDEPENDENT_SOURCE_RECEIPT_WITH_NO_PROPER_CLOCK_ANCESTRY",
    }
    assert "CLOCK_PROPERNESS" in prov["blocked_on_GSC6C_elimination_route"]
    assert "UNKNOWN" in prov["blocked_on_GSC6C_elimination_route"]


def test_basis_matches_executable_fail_closed_firewall():
    data = load_basis()
    fw = data["firewalls"]
    assert fw["proper_clock_can_be_ancestor_of_W2_when_W2_is_used_to_derive_proper_clock"] is False
    assert fw["missing_W2_product_provenance_is_admissible"] is False
    assert fw["candidate_basis_promotes_source_inputs"] is False
    assert fw["runtime_audit_can_promote"] is False
    assert data["canon_mutations"] == []


def test_adm_reparametrized_fields_are_derived_coordinates():
    excluded = set(load_basis()["derived_coordinates_excluded_from_independent_basis_addition"])
    assert "separately supplied reparametrized lapse N_tau" in excluded
    assert "separately supplied reparametrized shift b_tau" in excluded
