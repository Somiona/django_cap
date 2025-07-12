# https://github.com/tiagorangel1/cap/blob/main/server/index.js

import hashlib
import secrets
from datetime import timedelta

from cryptography.hazmat.primitives import hashes
from django.utils import timezone

from django_cap.cap_core.utils import (
    CapConfig,
    ChallengeItem,
    ChallengeType,
    DataSource,
    RedeemResult,
    Solution,
    prng,
)


class Cap:
    def __init__(self, config: CapConfig, data_source: DataSource) -> None:
        self.config = config
        self.data_source = data_source
        self.challenge = ChallengeType(
            config.challenge_count,
            config.challenge_size,
            config.challenge_difficulty,
        )
        self.challenge_expires_timedelta = timedelta(seconds=config.challenge_expires_s)
        self.token_expires_timedelta = timedelta(seconds=config.token_expires_s)

    async def create_challenge(self) -> ChallengeItem:
        token = secrets.token_hex(25)
        expires = timezone.now() + self.challenge_expires_timedelta

        challenge_item = ChallengeItem(
            challenge=self.challenge, expires=expires, token=token
        )

        # Store challenge in data source
        await self.data_source.store_challenge(challenge_item)

        return challenge_item

    @staticmethod
    def generate_challenge_from_token(
        token: str, challenge: ChallengeType
    ) -> list[tuple[str, str]]:
        # Generate challenges deterministically from token
        challenges: list[tuple[str, str]] = []
        for i in range(1, challenge.count + 1):
            # SEE https://github.com/tiagorangel1/cap/blob/8580f67f9b90b1f994cffb83de96357825266ae4/solver/index.js#L69
            # they start from 1, not 0
            salt = prng(f"{token}{i}", challenge.size)
            target = prng(f"{token}{i}d", challenge.difficulty)
            challenges.append((salt, target))
        return challenges

    @staticmethod
    def check_answer(challenges: list[tuple[str, str]], solutions: list[int]) -> bool:
        # Validate solutions
        is_valid = True
        for idx, (salt, target) in enumerate(challenges):
            if idx >= len(solutions):
                is_valid = False
                break

            solution_nonce = solutions[idx]
            digest = hashes.Hash(hashes.SHA256())
            digest.update((salt + str(solution_nonce)).encode())
            hash_result = digest.finalize().hex()

            if not hash_result.startswith(target):
                is_valid = False
                break
        return is_valid

    async def redeem_challenge(self, solution: Solution) -> RedeemResult:
        """
        Validate a solution against the stored challenge data.
        returns:
            success: bool
            message: str | None
            token: str | None
            expires: int | None
        """
        token = solution.token
        solutions = solution.solutions

        if (
            not token
            or not solutions
            or not isinstance(solutions, list)
            or any(not isinstance(s, int) for s in solutions)
        ):
            return RedeemResult(
                success=False,
                message="Invalid solution format",
            )

        # Get challenge from data source
        challenge_item = await self.data_source.get_challenge(token)
        if not challenge_item or challenge_item.expires < timezone.now():
            return RedeemResult(
                success=False,
                message="Challenge not found or expired",
            )

        challenges = Cap.generate_challenge_from_token(
            challenge_item.token, challenge_item.challenge
        )

        is_valid = Cap.check_answer(challenges, solutions)

        if not is_valid:
            return RedeemResult(
                success=False,
                message="Invalid solution",
            )

        # Delete the challenge from data source (consumed)
        await self.data_source.delete_challenge(token)

        # Generate verification token
        vertoken = secrets.token_hex(15)
        expires = timezone.now() + self.token_expires_timedelta
        id_value = secrets.token_hex(8)

        # Create hash for storage
        token_hash = hashlib.sha256(vertoken.encode()).hexdigest()

        # Store the token in data source
        await self.data_source.store_token(id_value, token_hash, expires)

        return RedeemResult(
            success=True,
            token=f"{id_value}:{vertoken}",
            expires=expires,
        )

    async def validate_token(self, token: str, keep_token: bool) -> dict:
        """
        Validate a token against the data source.
        """
        # Clean expired tokens first
        await self.data_source.cleanup_expired()

        # Parse token
        token_parts = token.split(":")
        if len(token_parts) != 2:
            return {"success": False}

        token_id, vertoken = token_parts

        # Create hash for lookup
        token_hash = hashlib.sha256(vertoken.encode()).hexdigest()

        # Check data source
        is_valid = await self.data_source.validate_token(
            token_id, token_hash, keep_token=keep_token
        )

        return {"success": is_valid}
