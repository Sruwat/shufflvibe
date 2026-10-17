from venue_pipeline_backend.venue_pipeline.admission import admit
from venue_pipeline_backend.venue_pipeline.scoring import FACTORS
from venue_pipeline_backend.venue_pipeline.market_ready import build_market_ready


def _row(**overrides):
    row = {
        "google_details": {"primaryType": "bar", "rating": 4.4, "userRatingCount": 500, "businessStatus": "OPERATIONAL"},
        "official_data": {"official_status": "fetched", "official_name": "Example Bar", "fit_out_year": 2020, "fit_out_status": "estimated"},
        "osm_data": {},
        "scores": {factor: 70 for factor in FACTORS},
        "score_evidence": {factor: ["official page evidence"] for factor in FACTORS[:5]},
        "not_specialised": [],
        "shuffl_review_summary": {"review_source": "none", "review_license_status": "not_available", "shuffl_review_count": 0},
    }
    row.update(overrides)
    return row


def test_admission_requires_score_and_identity_evidence():
    result = admit([_row()])[0]
    assert result["admission_decision"] == "Admitted"
    assert result["evidence_audit"]["identity_source"] == "official_website"
    assert result["evidence_audit"]["score_audit"]["coverage_count"] == 5


def test_missing_fit_out_is_insufficient_evidence_not_admitted():
    row = _row(official_data={"official_status": "fetched", "official_name": "Example Bar"})
    result = admit([row])[0]
    assert result["admission_decision"] == "Insufficient evidence"
    assert "fit_out_evidence_missing" in result["admission_reason"]


def test_non_owned_review_evidence_is_rejected():
    row = _row(shuffl_review_summary={"review_source": "google", "review_license_status": "not_available", "shuffl_review_count": 3})
    result = admit([row])[0]
    assert result["admission_decision"] == "Rejected"
    assert "unlicensed_review_evidence" in result["admission_reason"]


def test_market_ready_exports_evidence_audit_and_factor_audit():
    row = _row(google_place_id="abc123")
    admitted = admit([row])
    payload = build_market_ready(admitted, [{"area": "Hauz Khas", "city": "New Delhi"}])
    assert payload["admission_log"][0]["evidence_audit"]
    assert len(payload["score_evidence_audit"]) == 1
    assert len(payload["score_evidence"]) == len(FACTORS)


def test_out_of_range_score_is_rejected():
    scores = {factor: 70 for factor in FACTORS}
    scores["energy"] = 101
    result = admit([_row(scores=scores)])[0]
    assert result["admission_decision"] == "Rejected"
    assert "invalid_score_values" in result["admission_reason"]
    assert "energy" in result["evidence_audit"]["score_audit"]["invalid_factors"]


def test_fit_out_must_be_from_fetched_official_source():
    official = {"official_status": "not_found", "official_name": "Example Bar", "fit_out_year": 2020, "fit_out_status": "estimated"}
    result = admit([_row(official_data=official)])[0]
    assert result["admission_decision"] == "Insufficient evidence"
    assert "fit_out_evidence_missing" in result["admission_reason"]
