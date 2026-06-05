from app.core.config import settings
from app.db.models import PurchaseRequest
from app.schemas.ai_review import AIReviewResult
from app.services.ai_review_base import AIReviewProvider
from app.services.mock_ai_provider import MockAIProvider


def _load_provider() -> AIReviewProvider:
    if settings.ai_provider == "groq":
        from app.services.groq_provider import GroqProvider
        return GroqProvider()
    return MockAIProvider()


_provider: AIReviewProvider = _load_provider()


def generate_ai_review(request: PurchaseRequest) -> AIReviewResult:
    return _provider.review(request)
