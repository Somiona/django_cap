import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from django_cap.cap_core.cap import Solution
from django_cap.django_adapter import django_cap


@require_http_methods(["POST"])
async def create_challenge(request):
    """
    Create a new challenge.

    POST /challenge/
    """
    challenge_data = await django_cap.create_challenge()
    try:
        return JsonResponse(challenge_data)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["POST"])
async def redeem_challenge(request):
    """
    Redeem a challenge solution.

    POST /redeem/
    Body: {
        "token": "challenge_token",
        "solutions": [nonce1, nonce2, ...]
    }
    """
    try:
        data = json.loads(request.body)

        solution = Solution(
            token=data.get("token"), solutions=data.get("solutions", [])
        )

        result = await django_cap.redeem_challenge(solution)
        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)


@require_http_methods(["POST"])
async def validate_token(request):
    """
    Validate a token.

    POST /validate/
    Body: {
        "token": "token_to_validate",
        "keepToken": false
    }
    """
    try:
        data = json.loads(request.body)

        token = data.get("token")
        if not token:
            return JsonResponse({"error": "Token is required"}, status=400)

        keep_token = data.get("keepToken", False)
        result = await django_cap.validate_token(token, keep_token)

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
