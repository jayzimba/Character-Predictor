"""Administrator-only routes. The React UI is not trusted for this check."""

from fastapi import APIRouter, File, UploadFile

from app.core.deps import AdminUser, DbSession
from app.core.responses import success_response
from app.repositories import user as user_repository
from app.schemas.user import UserOut
from app.services import datasets as dataset_service
from app.services import evaluation as evaluation_service
from app.services import models_admin as models_admin_service
from app.services import questionnaire as questionnaire_service
from app.services import training as training_service

router = APIRouter()


@router.get("/users")
def list_users(db: DbSession, _: AdminUser):
    users = user_repository.list_users(db)
    payload = [UserOut.model_validate(user).model_dump() for user in users]
    return success_response(data=payload, message="Users loaded")


@router.get("/questions")
def list_questions(db: DbSession, _: AdminUser):
    payload = [
        item.model_dump(mode="json")
        for item in questionnaire_service.list_admin_questions(db)
    ]
    return success_response(data=payload, message="Questions loaded")


@router.get("/datasets/demo")
def demo_dataset(_: AdminUser):
    return success_response(
        data=dataset_service.demo_metadata().model_dump(),
        message="Bundled DEMO/SYNTHETIC dataset metadata",
    )


@router.post("/datasets/demo/validate")
def validate_demo_dataset(db: DbSession, _: AdminUser):
    payload = dataset_service.validate_demo(db).model_dump()
    return success_response(
        data=payload,
        message="DEMO dataset validated. Classification is not run.",
    )


@router.post("/datasets/validate")
async def validate_uploaded_dataset(
    db: DbSession,
    _: AdminUser,
    file: UploadFile = File(...),
):
    content = await file.read()
    payload = dataset_service.validate_bytes(
        db, file.filename or "upload.csv", content
    ).model_dump()
    return success_response(
        data=payload,
        message="Dataset validated. Classification is not run.",
    )


@router.post("/datasets/from-assessments")
def validate_collected_assessments(db: DbSession, _: AdminUser):
    payload = dataset_service.preview_collected_assessments(db).model_dump()
    return success_response(
        data=payload,
        message="Completed assessments mapped to category features.",
    )


@router.get("/models/training")
def last_training_run(_: AdminUser):
    run = training_service.last_training_run()
    if run is None:
        return success_response(data=None, message="No training run has been saved yet.")
    return success_response(data=run.model_dump(), message="Last training run loaded")


@router.post("/models/train/demo")
def train_demo_models(db: DbSession, _: AdminUser):
    payload = training_service.train_demo(db).model_dump()
    return success_response(
        data=payload,
        message="Classifiers fitted on the DEMO training fold. Test evaluation is later.",
    )


@router.post("/models/train")
async def train_uploaded_models(
    db: DbSession,
    _: AdminUser,
    file: UploadFile = File(...),
):
    content = await file.read()
    payload = training_service.train_upload(
        db, file.filename or "upload.csv", content
    ).model_dump()
    return success_response(
        data=payload,
        message="Classifiers fitted on the uploaded training fold. Test evaluation is later.",
    )


@router.get("/models")
def list_registered_models(db: DbSession, _: AdminUser):
    payload = [item.model_dump(mode="json") for item in evaluation_service.list_registry(db)]
    return success_response(data=payload, message="Model registry loaded")


@router.get("/models/evaluation")
def last_evaluation(_: AdminUser):
    run = evaluation_service.last_evaluation()
    if run is None:
        return success_response(data=None, message="No held-out evaluation has been saved yet.")
    return success_response(data=run.model_dump(), message="Last held-out evaluation loaded")


@router.post("/models/evaluate/demo")
def evaluate_demo_models(db: DbSession, _: AdminUser):
    payload = evaluation_service.evaluate_demo(db).model_dump()
    return success_response(
        data=payload,
        message="Held-out metrics computed with sklearn.metrics and written to the registry.",
    )


@router.post("/models/evaluate")
async def evaluate_uploaded_models(
    db: DbSession,
    _: AdminUser,
    file: UploadFile = File(...),
):
    content = await file.read()
    payload = evaluation_service.evaluate_upload(
        db, file.filename or "upload.csv", content
    ).model_dump()
    return success_response(
        data=payload,
        message="Held-out metrics computed with sklearn.metrics and written to the registry.",
    )


@router.post("/models/activate-selected")
def activate_selected_model(db: DbSession, _: AdminUser):
    payload = models_admin_service.activate_selected(db).model_dump(mode="json")
    return success_response(
        data=payload,
        message="Selected model is now ACTIVE. Previous active models were archived.",
    )


@router.post("/models/{model_id}/activate")
def activate_registered_model(model_id: int, db: DbSession, _: AdminUser):
    payload = models_admin_service.activate_model(db, model_id).model_dump(mode="json")
    return success_response(
        data=payload,
        message="Model is now ACTIVE. Previous active models were archived.",
    )
