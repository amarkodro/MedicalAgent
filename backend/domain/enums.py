from enum import Enum


class CaseStatus(Enum):
    QUEUED = "Queued"
    PROCESSING = "Processing"
    DIAGNOSED = "Diagnosed"
    PENDING_REVIEW = "PendingReview"
    REJECTED = "Rejected"


class Decision(Enum):
    ACCEPT = "Accept"
    REVIEW = "Review"
    REJECT = "Reject"


class FeedbackResult(Enum):
    ACCEPTED = "Accepted"
    REJECTED = "Rejected"
