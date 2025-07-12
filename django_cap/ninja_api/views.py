"""
Django Ninja API views for the cap functionality.
This provides a more structured API        return ChallengeResponse(
            challenge=challenge_data.challenge,
            token=challenge_data.token,
            expires=challenge_data.expires
        ) automatic documentation.
"""

from django.http import HttpRequest
from ninja import NinjaAPI, Schema
from ninja.errors import ValidationError

from django_cap.cap_core.cap import Solution
from django_cap.django_adapter import django_cap
from django_cap.django_app_settings import NINJA_API_ENABLE_DOCS  # type: ignore

# Create a separate API instance for cap functionality
cap_api = NinjaAPI(
    title="Django Cap API",
    version="1.0.0",
    description="Proof of Work (PoW) Captcha API based on cap.js",
    docs_url="/docs/" if NINJA_API_ENABLE_DOCS else None,
    openapi_url="/openapi.json" if NINJA_API_ENABLE_DOCS else None,
)


class ChallengeResponse(Schema):
    challenge: dict[str, int]
    token: str
    expires: int  # in milliseconds


class SolutionRequest(Schema):
    token: str
    solutions: list[int]


class RedeemResponse(Schema):
    success: bool
    message: str | None = None
    token: str | None = None
    expires: int | None = None  # in milliseconds


class ValidateRequest(Schema):
    token: str
    keepToken: bool | None = False


class ValidateResponse(Schema):
    success: bool


# API endpoints
@cap_api.post("/challenge", response=ChallengeResponse)
async def create_challenge(request: HttpRequest):
    """
    Create a new challenge.

    This endpoint generates a new proof-of-work challenge with configurable parameters.
    """
    try:
        challenge_data = await django_cap.create_challenge()
        return challenge_data

    except Exception as e:
        raise ValidationError([{"message": str(e)}]) from e


@cap_api.post("/redeem", response=RedeemResponse)
async def redeem_challenge(request: HttpRequest, payload: SolutionRequest):
    """
    Redeem a challenge solution.

    Submit the solution to a challenge to get a valid token.
    """
    try:
        solution = Solution(token=payload.token, solutions=payload.solutions)

        result = await django_cap.redeem_challenge(solution)

        return RedeemResponse(
            success=result.success,
            message=result.message,
            token=result.token,
            expires=int(result.expires.timestamp() * 1000) if result.expires else None,
        )

    except Exception as e:
        raise ValidationError([{"message": str(e)}]) from e


@cap_api.post("/validate", response=ValidateResponse)
async def validate_token(request: HttpRequest, payload: ValidateRequest):
    """
    Validate a token.

    Check if a token is valid and optionally keep it for future use.
    """
    try:
        keep_token = payload.keepToken or False
        result = await django_cap.validate_token(payload.token, keep_token)

        return ValidateResponse(success=result["success"])

    except Exception as e:
        raise ValidationError([{"message": str(e)}]) from e
