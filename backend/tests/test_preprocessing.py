"""Phase 10: validate and featurise datasets without classifying."""

from io import BytesIO

import pandas as pd
from sklearn.preprocessing import StandardScaler

from app.database.seed import (
    DEMO_ADMIN_EMAIL,
    DEMO_ADMIN_PASSWORD,
    DEMO_USER_EMAIL,
    DEMO_USER_PASSWORD,
    seed_all,
)
from app.ml.constants import FEATURE_COLUMNS, LABEL_COLUMN, LABEL_ORDER, ORIGIN_COLUMN
from app.ml.dataset import demo_csv_path
from app.ml.dataset.generate_demo import build_demo_frame
from app.ml.feature_engineering import category_scores_from_likert
from app.ml.instrument import instrument_from_catalog
from app.ml.preprocessing import DatasetError, knn_scaler_pipeline, prepare_csv, prepare_dataset
from app.services.scoring import weighted_likert


def _auth(api_client, email: str, password: str) -> dict[str, str]:
    response = api_client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['data']['access_token']}"}


def test_category_score_uses_reverse_and_weight():
    instrument = instrument_from_catalog()
    reverse_item = next(item for item in instrument.items if item.reverse_scored)
    answers = {item.key: 3 for item in instrument.items}
    answers[reverse_item.key] = 1
    scores = category_scores_from_likert(answers, instrument)
    directed = weighted_likert(1, reverse_item.weight, True)
    other = next(
        item
        for item in instrument.items_for_category(reverse_item.category_code)
        if item.key != reverse_item.key
    )
    expected = float((directed + weighted_likert(3, other.weight, other.reverse_scored)) / 2)
    assert scores[f"{reverse_item.category_code}_score"] == expected


def test_bundled_demo_csv_is_labelled_synthetic():
    text = demo_csv_path().read_text(encoding="utf-8")
    assert "DEMO/SYNTHETIC" in text.splitlines()[0]
    instrument = instrument_from_catalog()
    prepared = prepare_csv(demo_csv_path(), instrument)
    report = prepared.report
    assert report.is_synthetic is True
    assert report.rows_kept == 100
    assert report.format == "likert"
    assert report.feature_names == list(FEATURE_COLUMNS)
    assert report.class_counts == {label: 25 for label in LABEL_ORDER}
    assert report.split["train_size"] == 80
    assert report.split["held_out_size"] == 20
    assert report.split["stratified"] is True
    assert report.scaling_applied is False
    assert "accuracy" not in report.to_dict()
    assert prepared.X.shape == (100, 16)
    scaler = knn_scaler_pipeline().named_steps["scaler"]
    assert isinstance(scaler, StandardScaler)
    assert not hasattr(scaler, "n_features_in_")


def test_cleaning_drops_bad_rows_and_duplicates():
    instrument = instrument_from_catalog()
    frame = build_demo_frame(n_per_class=3, seed=1)
    dirty = pd.concat(
        [
            frame,
            frame.iloc[[0]],
            pd.DataFrame(
                [
                    {**frame.iloc[0].to_dict(), "q01": 9},
                    {**frame.iloc[1].to_dict(), LABEL_COLUMN: "INTJ"},
                    {**frame.iloc[2].to_dict(), "q02": None},
                ]
            ),
        ],
        ignore_index=True,
    )
    prepared = prepare_dataset(dirty, instrument)
    assert prepared.report.duplicates_removed == 1
    assert prepared.report.invalid_range_dropped == 1
    assert prepared.report.invalid_label_dropped == 1
    assert prepared.report.missing_dropped == 1
    assert prepared.report.rows_kept == 12


def test_category_score_csv_format():
    instrument = instrument_from_catalog()
    likert = prepare_dataset(build_demo_frame(n_per_class=5, seed=2), instrument)
    scores = pd.DataFrame(likert.X, columns=likert.feature_names)
    scores[LABEL_COLUMN] = likert.y_labels
    scores[ORIGIN_COLUMN] = "DEMO/SYNTHETIC"
    prepared = prepare_dataset(scores, instrument)
    assert prepared.report.format == "category_scores"
    assert prepared.report.rows_kept == 20
    assert prepared.report.split["train_size"] == 16


def test_missing_label_column_is_rejected():
    instrument = instrument_from_catalog()
    frame = build_demo_frame(n_per_class=2, seed=3).drop(columns=[LABEL_COLUMN])
    try:
        prepare_dataset(frame, instrument)
    except DatasetError as exc:
        assert "personality_type" in str(exc)
    else:
        raise AssertionError("expected DatasetError")


def test_validate_demo_requires_admin(api_client, db_session):
    seed_all(db_session)
    denied = api_client.post("/api/admin/datasets/demo/validate")
    assert denied.status_code == 401

    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    forbidden = api_client.post("/api/admin/datasets/demo/validate", headers=user)
    assert forbidden.status_code == 403

    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    ok = api_client.post("/api/admin/datasets/demo/validate", headers=admin)
    assert ok.status_code == 200
    data = ok.json()["data"]
    assert data["is_synthetic"] is True
    assert data["trained"] is False
    assert data["ready_for_training"] is True
    assert data["rows_kept"] == 100
    assert "accuracy" not in data


def test_upload_csv_validation(api_client, db_session):
    seed_all(db_session)
    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    content = demo_csv_path().read_bytes()
    response = api_client.post(
        "/api/admin/datasets/validate",
        headers=admin,
        files={"file": ("temperament_demo_v1.csv", BytesIO(content), "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["data"]["source"] == "temperament_demo_v1.csv"
    assert response.json()["data"]["is_synthetic"] is True


def test_collected_assessments_have_features_but_no_label(api_client, db_session):
    seed_all(db_session)
    user = _auth(api_client, DEMO_USER_EMAIL, DEMO_USER_PASSWORD)
    started = api_client.post(
        "/api/assessments",
        headers=user,
        json={"consent_accepted": True},
    ).json()["data"]
    questions = api_client.get("/api/questions", headers=user).json()["data"]["questions"]
    api_client.post(
        f"/api/assessments/{started['id']}/answers",
        headers=user,
        json={"answers": [{"question_id": q["id"], "response_value": 3} for q in questions]},
    )
    submitted = api_client.post(
        f"/api/assessments/{started['id']}/submit",
        headers=user,
    )
    assert submitted.status_code == 200

    admin = _auth(api_client, DEMO_ADMIN_EMAIL, DEMO_ADMIN_PASSWORD)
    preview = api_client.post("/api/admin/datasets/from-assessments", headers=admin)
    assert preview.status_code == 200
    data = preview.json()["data"]
    assert data["unlabelled_collected"] == 1
    assert data["rows_kept"] == 0
    assert data["ready_for_training"] is False
    assert data["trained"] is False
