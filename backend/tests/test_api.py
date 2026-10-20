from app import app as flask_app


def test_case_endpoint_does_not_claim_a_legal_probability():
    response = flask_app.test_client().post(
        "/api/case/predict",
        json={"evidence_strength": "Strong", "past_record": "None"},
    )

    assert response.status_code == 200
    body = response.get_json()
    assert body["possible_outcome"]["probability"] == "Not calculated"
    assert body["possible_outcome"]["result"] == "Not predicted"
    assert body["assessment_status"] == "educational_checklist_only"


def test_case_endpoint_rejects_unknown_input_values():
    response = flask_app.test_client().post(
        "/api/case/predict",
        json={"evidence_strength": "Guaranteed", "past_record": "None"},
    )

    assert response.status_code == 400


def test_ipc_explain_rejects_missing_section():
    response = flask_app.test_client().post(
        "/api/ipc/assistant/explain",
        json={"section": ""},
    )

    assert response.status_code == 400
