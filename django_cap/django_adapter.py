"""
Django-specific adapter for the cap.py core functionality.
This bridges the framework-agnostic cap.py with Django's ORM and settings.
"""

import logging
from datetime import datetime
from typing import Any

from django.utils import timezone

from django_cap.cap_core.cap import Cap, CapConfig, ChallengeItem, Solution
from django_cap.cap_core.utils import ChallengeType, DataSource
from django_cap.django_app_settings import (
    CHALLENGE_COUNT,  # type: ignore
    CHALLENGE_DIFFICULTY,  # type: ignore
    CHALLENGE_EXPIRES_S,  # type: ignore
    CHALLENGE_SIZE,  # type: ignore
    CLEANUP_INTERVAL_S,  # type: ignore
    TOKEN_EXPIRES_S,  # type: ignore
)
from django_cap.models import Challenge, Token

logger = logging.getLogger(__name__)


class DjangoDataSource(DataSource):
    """
    Django implementation of the CAP data source interface.
    Uses Django ORM for database operations.
    """

    async def store_challenge(self, challenge_data: ChallengeItem) -> None:
        """Store a challenge in the Django database."""
        if challenge_data.token:
            await Challenge.objects.acreate(
                token=challenge_data.token,
                challenge_data=challenge_data.challenge.as_dict(),
                expires=challenge_data.expires,
            )

    async def get_challenge(self, token: str) -> ChallengeItem | None:
        """Retrieve a challenge by token."""
        try:
            challenge_obj = await Challenge.objects.aget(token=token)
            if challenge_obj.is_expired():
                await challenge_obj.adelete()
                return None

            return ChallengeItem(
                challenge=ChallengeType.from_dict(challenge_obj.challenge_data),
                expires=challenge_obj.expires,
                token=challenge_obj.token,
            )
        except Challenge.DoesNotExist:
            return None

    async def delete_challenge(self, token: str) -> None:
        """Delete a challenge from the database."""
        try:
            challenge_obj = await Challenge.objects.aget(token=token)
            await challenge_obj.adelete()
        except Challenge.DoesNotExist:
            pass

    async def store_token(
        self, token_id: str, token_hash: str, expires_datetime: datetime
    ) -> None:
        """Store a verification token in the database."""
        await Token.objects.acreate(
            token_id=token_id,
            token_hash=token_hash,
            expires=expires_datetime,
        )

    async def validate_token(
        self, token_id: str, token_hash: str, keep_token: bool = False
    ) -> bool:
        """Validate a token against the database."""
        try:
            token_obj = await Token.objects.aget(
                token_id=token_id, token_hash=token_hash
            )
            if token_obj.is_expired():
                await token_obj.adelete()
                return False

            if not keep_token:
                await token_obj.adelete()

            return True
        except Token.DoesNotExist:
            return False

    async def cleanup_expired(self) -> dict[str, int]:
        """Clean up expired challenges and tokens."""
        now = timezone.now()

        # Clean expired challenges
        expired_challenges = Challenge.objects.filter(expires__lt=now)
        challenges_count = await expired_challenges.acount()
        await expired_challenges.adelete()

        # Clean expired tokens
        expired_tokens = Token.objects.filter(expires__lt=now)
        tokens_count = await expired_tokens.acount()
        await expired_tokens.adelete()

        if challenges_count > 0 or tokens_count > 0:
            logger.info(
                f"Cleaned up {challenges_count} expired challenges and "
                f"{tokens_count} expired tokens"
            )

        return {
            "challenges_cleaned": challenges_count,
            "tokens_cleaned": tokens_count,
        }

    async def get_stats(self) -> dict[str, Any]:
        """Get statistics about current challenges and tokens."""
        now = timezone.now()
        return {
            "active_challenges": await Challenge.objects.acount(),
            "active_tokens": await Token.objects.acount(),
            "expired_challenges": await Challenge.objects.filter(
                expires__lt=now
            ).acount(),
            "expired_tokens": await Token.objects.filter(expires__lt=now).acount(),
        }


class DjangoCapAdapter:
    """
    Django-specific adapter for Cap functionality.
    This is now just a thin wrapper around the Cap class with Django data source.
    """

    def __init__(self):
        # Load configuration from Django settings once at startup
        challenge_config = CapConfig(
            CHALLENGE_COUNT,
            CHALLENGE_SIZE,
            CHALLENGE_DIFFICULTY,
            CHALLENGE_EXPIRES_S,
            TOKEN_EXPIRES_S,
        )

        # Create Django data source
        data_source = DjangoDataSource()

        # Initialize Cap with config and data source
        self.cap = Cap(challenge_config, data_source)

        self.cleanup_interval = CLEANUP_INTERVAL_S

    async def create_challenge(self):
        """
        Create a new challenge.å
        All logic is now handled by the Cap class.
        """
        challenge_item = await self.cap.create_challenge()
        return {
            "challenge": challenge_item.challenge.as_dict(),
            "token": challenge_item.token,
            "expires": int(
                challenge_item.expires.timestamp() * 1000
            ),  # Convert to milliseconds
        }

    async def redeem_challenge(self, solution: Solution):
        """
        Redeem a challenge solution.
        All logic is now handled by the Cap class.
        """
        return await self.cap.redeem_challenge(solution)

    async def validate_token(self, token: str, keep_token: bool = True):
        """
        Validate a token.
        All logic is now handled by the Cap class.
        """
        return await self.cap.validate_token(token, keep_token)

    async def cleanup_expired(self):
        """
        Clean up expired challenges and tokens.
        """
        return await self.cap.data_source.cleanup_expired()

    async def get_stats(self):
        """
        Get statistics about current challenges and tokens.
        """
        return await self.cap.data_source.get_stats()


# Global instance - can be configured via Django settings
django_cap = DjangoCapAdapter()
