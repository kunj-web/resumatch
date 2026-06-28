import enum


class LocationType(str, enum.Enum):
    REMOTE = "remote"
    ONSITE = "onsite"
    HYBRID = "hybrid"


class JobType(str, enum.Enum):
    FULL_TIME = "full-time"
    PART_TIME = "part-time"
    CONTRACT = "contract"
    INTERNSHIP = "internship"


class ExtractionStatus(str, enum.Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"


class ResumeProcessingStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PARSED = "parsed"
    MATCHED = "matched"
    FAILED = "failed"


class UserPlan(str, enum.Enum):
    FREE = "free"
    PRO = "pro"


class TailoredResumeStatus(str, enum.Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"
    FAILED = "failed"


class JobStatus(str, enum.Enum):
    SAVED = "saved"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
