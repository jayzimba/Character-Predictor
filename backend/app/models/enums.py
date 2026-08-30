"""Controlled vocabularies stored as VARCHAR, not MySQL ENUM types.

Defence note: VARCHAR + application constants is easier to migrate than
native ENUM. Changing a MySQL ENUM later requires ALTER TABLE.
"""

from enum import Enum


class RoleCode(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"


class Gender(str, Enum):
    FEMALE = "FEMALE"
    MALE = "MALE"
    OTHER = "OTHER"
    PREFER_NOT_TO_SAY = "PREFER_NOT_TO_SAY"


class AgeGroup(str, Enum):
    UNDER_18 = "UNDER_18"
    AGE_18_24 = "AGE_18_24"
    AGE_25_34 = "AGE_25_34"
    AGE_35_44 = "AGE_35_44"
    AGE_45_54 = "AGE_45_54"
    AGE_55_PLUS = "AGE_55_PLUS"


class QuestionStatus(str, Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class AssessmentStatus(str, Enum):
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"


class ModelStatus(str, Enum):
    TRAINED = "TRAINED"
    ACTIVE = "ACTIVE"
    ARCHIVED = "ARCHIVED"


class AlgorithmName(str, Enum):
    DECISION_TREE = "DECISION_TREE"
    NAIVE_BAYES = "NAIVE_BAYES"
    KNN = "KNN"


class PersonalityCode(str, Enum):
    CHOLERIC = "CHOLERIC"
    MELANCHOLIC = "MELANCHOLIC"
    PHLEGMATIC = "PHLEGMATIC"
    SANGUINE = "SANGUINE"
