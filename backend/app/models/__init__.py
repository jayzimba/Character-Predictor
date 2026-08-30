"""Import every model so Alembic and metadata.create_all see the full schema."""

from app.models.assessment import Assessment, AssessmentAnswer, PredictionResult
from app.models.audit import AuditLog
from app.models.enums import (
    AgeGroup,
    AlgorithmName,
    AssessmentStatus,
    Gender,
    ModelStatus,
    PersonalityCode,
    QuestionStatus,
    RoleCode,
)
from app.models.ml import MLModel, ModelMetric
from app.models.personality import PersonalityType
from app.models.questionnaire import Question, QuestionCategory, QuestionnaireVersion
from app.models.user import PasswordResetToken, Role, User

__all__ = [
    "AgeGroup",
    "AlgorithmName",
    "Assessment",
    "AssessmentAnswer",
    "AssessmentStatus",
    "AuditLog",
    "Gender",
    "MLModel",
    "ModelMetric",
    "ModelStatus",
    "PasswordResetToken",
    "PersonalityCode",
    "PersonalityType",
    "PredictionResult",
    "Question",
    "QuestionCategory",
    "QuestionStatus",
    "QuestionnaireVersion",
    "Role",
    "RoleCode",
    "User",
]
