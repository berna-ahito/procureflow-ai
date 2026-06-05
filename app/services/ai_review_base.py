from abc import ABC, abstractmethod

from app.db.models import PurchaseRequest
from app.schemas.ai_review import AIReviewResult


class AIReviewProvider(ABC):
    @abstractmethod
    def review(self, request: PurchaseRequest) -> AIReviewResult: ...
