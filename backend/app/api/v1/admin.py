"""Administrator-only routes. The React UI is not trusted for this check."""

from fastapi import APIRouter, File, Query, UploadFile

from app.core.deps import AdminUser, DbSession
from app.core.responses import success_response
from app.repositories import user as user_repository
from app.schemas.evaluation import ModelNotesPatch
from app.schemas.questionnaire import QuestionPatch, QuestionWrite
from app.schemas.user import UserOut
from app.services import admin_overview as admin_overview_service
from app.services import audit_admin as audit_admin_service
from app.services import datasets as dataset_service
from app.services import evaluation as evaluation_service
from app.services import models_admin as models_admin_service
from app.services import questionnaire as questionnaire_service
from app.services import training as training_service

router = APIRouter()


@router.get("/overview")
def admin_overview(db: DbSession, _: AdminUser):
    data = admin_overview_service.get_overview(db)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Admin overview loaded",
    )


@router.get("/assessments")
def list_admin_assessments(db: DbSession, _: AdminUser):
    data = admin_overview_service.list_assessments(db)
    return success_response(
        data=[item.model_dump(mode="json") for item in data],
        message="Assessments loaded",
    )


@router.get("/users")
def list_users(db: DbSession, _: AdminUser):
    users = user_repository.list_users(db)
    payload = [UserOut.model_validate(user).model_dump() for user in users]
    return success_response(data=payload, message="Users loaded")


@router.get("/audit-logs")
def list_audit_logs(
    db: DbSession,
    _: AdminUser,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    payload, disclaimer = audit_admin_service.list_logs(
        db, limit=limit, offset=offset
    )
    data = payload.model_dump(mode="json")
    data["disclaimer"] = disclaimer
    return success_response(data=data, message="Audit log loaded")


@router.get("/questions/options")
def question_options(db: DbSession, _: AdminUser):
    payload = questionnaire_service.question_options(db).model_dump()
    return success_response(data=payload, message="Question options loaded")


@router.get("/questions")
def list_questions(db: DbSession, _: AdminUser):
    payload = [
        item.model_dump(mode="json")
        for item in questionnaire_service.list_admin_questions(db)
    ]
    return success_response(data=payload, message="Questions loaded")


@router.post("/questions")
def create_question(payload: QuestionWrite, db: DbSession, admin: AdminUser):
    data = questionnaire_service.create_admin_question(db, payload, actor=admin)
    return success_response(
        data=data.model_dump(mode="json"),
        message="Question created",
        status_code=201,
    )


@router.patch("/questions/{question_id}")
def update_question(
    question_id: int,
    payload: QuestionPatch,
    db: DbSession,
    admin: AdminUser,
):
    data = questionnaire_service.update_admin_question(
        db, question_id, payload, actor=admin
    )
    message = "Question updated"
    if payload.status == "INACTIVE":
        message = "Question deactivated"
    elif payload.status == "ACTIVE":
        message = "Question activated"
    return success_response(data=data.model_dump(mode="json"), message=message)


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
    payload = [item.model_dump(mode="json") for item in models_admin_service.list_models(db)]
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
def activate_selected_model(db: DbSession, admin: AdminUser):
    payload = models_admin_service.activate_selected(db, actor=admin).model_dump(mode="json")
    return success_response(
        data=payload,
        message="Selected model is now ACTIVE. Previous active models were archived.",
    )


@router.get("/models/{model_id}")
def get_registered_model(model_id: int, db: DbSession, _: AdminUser):
    payload = models_admin_service.get_model(db, model_id).model_dump(mode="json")
    return success_response(data=payload, message="Model loaded")


@router.patch("/models/{model_id}")
def update_registered_model(
    model_id: int,
    payload: ModelNotesPatch,
    db: DbSession,
    admin: AdminUser,
):
    data = models_admin_service.update_notes(
        db, model_id, payload.notes, actor=admin
    ).model_dump(mode="json")
    return success_response(data=data, message="Model notes updated")


@router.post("/models/{model_id}/activate")
def activate_registered_model(model_id: int, db: DbSession, admin: AdminUser):
    payload = models_admin_service.activate_model(db, model_id, actor=admin).model_dump(
        mode="json"
    )
    return success_response(
        data=payload,
        message="Model is now ACTIVE. Previous active models were archived.",
    )


@router.post("/models/{model_id}/archive")
def archive_registered_model(model_id: int, db: DbSession, admin: AdminUser):
    payload = models_admin_service.archive_model(db, model_id, actor=admin).model_dump(
        mode="json"
    )
    return success_response(
        data=payload,
        message="Model archived. Stored predictions keep this model_id.",
    )
