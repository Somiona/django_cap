import asyncio
import time
from datetime import datetime
from typing import Any

import pytest
from django.conf import settings
from django.utils import timezone
from pytest import CaptureFixture

from .cap import Cap
from .solver import solve
from .utils import (
    CapConfig,
    ChallengeItem,
    ChallengeType,
    DataSource,
    RedeemResult,
    Solution,
)

settings.configure()


class MemoryDataSource(DataSource):
    """
    In-memory data source for testing and development.
    This should not be used in production.
    """

    def __init__(self, keep_challenge: bool = False) -> None:
        self.challenges: dict[str, ChallengeItem] = {}
        self.tokens: dict[str, dict[str, str | datetime]] = {}
        if keep_challenge:
            self.delete_challenge = self.pass_func

    async def pass_func(self, token: str) -> None:
        pass

    async def store_challenge(self, challenge_data: ChallengeItem) -> None:
        """Store a challenge in memory."""
        self.challenges[challenge_data.token] = challenge_data

    async def get_challenge(self, token: str) -> ChallengeItem | None:
        """Retrieve a challenge by token."""
        challenge_data = self.challenges.get(token)
        if challenge_data and challenge_data.expires > timezone.now():
            return challenge_data
        return None

    async def delete_challenge(self, token: str) -> None:
        """Delete a challenge from memory."""
        if token in self.challenges:
            del self.challenges[token]

    async def store_token(
        self, token_id: str, token_hash: str, expires_datetime: datetime
    ) -> None:
        """Store a verification token in memory."""
        self.tokens[token_id] = {"hash": token_hash, "expires": expires_datetime}

    async def validate_token(
        self, token_id: str, token_hash: str, keep_token: bool = False
    ) -> bool:
        """Validate a token against memory storage."""
        token_data = self.tokens.get(token_id)
        if not token_data:
            return False

        if token_data["expires"] < timezone.now():  # type: ignore
            # Token expired
            if token_id in self.tokens:
                del self.tokens[token_id]
            return False

        if token_data["hash"] != token_hash:
            return False

        if not keep_token:
            del self.tokens[token_id]

        return True

    async def cleanup_expired(self) -> dict[str, int]:
        """Clean up expired challenges and tokens."""

        # Clean expired challenges
        expired_challenges = [
            token
            for token, data in self.challenges.items()
            if data.expires < timezone.now()  # type: ignore
        ]
        for token in expired_challenges:
            del self.challenges[token]

        # Clean expired tokens
        expired_tokens = [
            token_id
            for token_id, data in self.tokens.items()
            if data["expires"] < timezone.now()  # type: ignore
        ]
        for token_id in expired_tokens:
            del self.tokens[token_id]

        return {"challenges": len(expired_challenges), "tokens": len(expired_tokens)}

    async def get_stats(self) -> dict[str, Any]:
        """Get statistics about current challenges and tokens."""
        return {"challenges": len(self.challenges), "tokens": len(self.tokens)}


challenge_data = [
    ["e455cea65e98bc3c36287f43769da211", "dceb"],
    ["fb8d25f6abac5aa9b6360051f37e010b", "93f1"],
    ["91ef47db578fbeb2565d3f9c82bb7960", "3698"],
    ["b7ad7667486a691cda8ef297098f64a7", "d72a"],
    ["1aca3fb7cef7a2be0dee563ed4136758", "3b58"],
    ["d9ec39af92b430e5a329274d8aa58fa8", "e1d3"],
    ["781a3cc9217d73c908a321d3fdabd62f", "22c6"],
    ["e37a0752c9ac2f3d2517747fde373ac9", "f6f1"],
    ["bba070197569f322beda5b240f639a95", "4751"],
    ["89297515aeac646bee9653ba405e0beb", "a7de"],
    ["444571a0d5039c15be6141d6cd8434f9", "a783"],
    ["ba75f2bf8e9b92cc32caa17237a52d14", "7e30"],
    ["22bfc18ba8e3ecee080c5d1ef64ed6e9", "5fcf"],
    ["885fb78ff76b4eddd2f5bc04ac5ee673", "93e5"],
    ["308758072931bb3b254a7b1ed351d04a", "3e49"],
    ["724f89bb167db4b881e1dc7b0949ac8f", "b82e"],
    ["8b79506e4630de15be225c18623eff65", "f0e5"],
    ["0c21ade6e63a4e37b13cb8b087f31863", "65c9"],
]


@pytest.mark.asyncio
async def test_solver(capsys: CaptureFixture[str]):
    timer = time.time()
    results, results_hash = await solve(challenge_data)
    elapsed = time.time() - timer
    with capsys.disabled():
        print(f"Elapsed time: {elapsed:.2f} seconds, Solved {len(results)} challenges")
    assert len(results) != 0


@pytest.mark.asyncio
async def test_generate_challenge(capsys: CaptureFixture[str]):
    timer = time.time()
    challenge = "test_token"
    config = ChallengeType(count=10, size=32, difficulty=4)
    results, results_hash = await solve(challenge, config)
    elapsed = time.time() - timer
    with capsys.disabled():
        print(f"Elapsed time: {elapsed:.2f} seconds, Solved {len(results)} challenges")
    assert len(results) != 0


@pytest.mark.asyncio
async def test_check_answer(capsys: CaptureFixture[str]):
    timer = time.time()
    challenge = "test_token"
    config = ChallengeType(count=10, size=32, difficulty=4)
    results, results_hash = await solve(challenge, config)
    challenges = Cap.generate_challenge_from_token(challenge, config)
    is_valid = Cap.check_answer(challenges, results)
    elapsed = time.time() - timer
    with capsys.disabled():
        print(
            f"Elapsed time: {elapsed:.2f} seconds, "
            f"Solved and checked {len(results)} challenges"
        )
    assert is_valid is True


@pytest.mark.asyncio
async def test_cap_core_with_memory_data_source(capsys: CaptureFixture[str]):
    data_source = MemoryDataSource()
    cap_config: CapConfig = CapConfig(10, 32, 4, 60, 60)
    cap = Cap(cap_config, data_source)

    await cap.create_challenge()
    stats = await data_source.get_stats()
    assert stats["challenges"] == 1


@pytest.mark.asyncio
async def test_cleanup_expired(capsys: CaptureFixture[str]):
    data_source = MemoryDataSource()
    cap_config: CapConfig = CapConfig(10, 32, 4, 3, 3)
    cap = Cap(cap_config, data_source)

    # Create a challenge
    challenge = await cap.create_challenge()
    timer = timezone.now()
    assert challenge.expires > timer
    stats = await data_source.get_stats()
    assert stats["challenges"] == 1

    # Simulate time passing
    await asyncio.sleep(5)  # 5000 ms

    # Cleanup expired challenges and tokens
    await data_source.cleanup_expired()
    stats = await data_source.get_stats()
    assert stats["challenges"] == 0


@pytest.mark.asyncio
async def test_redeem_challenge(capsys: CaptureFixture[str]):
    data_source = MemoryDataSource()
    cap_config: CapConfig = CapConfig(10, 32, 4, 3, 3)
    cap = Cap(cap_config, data_source)

    # Create a challenge
    challenge_item = await cap.create_challenge()
    assert challenge_item.token in data_source.challenges

    # Solve the challenge
    results, results_hash = await solve(challenge_item.token, cap.challenge)

    # Redeem the challenge
    solution = Solution(token=challenge_item.token, solutions=results)
    redeem_result: RedeemResult = await cap.redeem_challenge(solution)

    timer = timezone.now()
    assert redeem_result.success is True
    assert challenge_item.token not in data_source.challenges
    assert redeem_result.expires is not None
    assert redeem_result.expires > timer
    assert redeem_result.token is not None
    assert redeem_result.token.split(":")[0] in data_source.tokens

    await data_source.cleanup_expired()  # Cleanup after test
    assert (await data_source.get_stats())["tokens"] == 1

    await asyncio.sleep(5)  # Wait for token to expire
    await data_source.cleanup_expired()
    assert (await data_source.get_stats())["tokens"] == 0


@pytest.mark.asyncio
async def test_redeem_invalid_solution(capsys: CaptureFixture[str]):
    data_source = MemoryDataSource()
    cap_config: CapConfig = CapConfig(10, 32, 4, 3, 3)
    cap = Cap(cap_config, data_source)

    # Create a challenge
    challenge_item = await cap.create_challenge()
    assert challenge_item.token in data_source.challenges

    # Solve the challenge with incorrect solutions
    solution = Solution(token=challenge_item.token, solutions=[-1] * 10)
    redeem_result: RedeemResult = await cap.redeem_challenge(solution)

    assert redeem_result.success is False
    assert redeem_result.token is None
    assert redeem_result.expires is None


@pytest.mark.asyncio
@pytest.mark.benchmark
async def test_challenge_answer_check_speed(benchmark, capsys: CaptureFixture[str]):
    data_source = MemoryDataSource()
    cap_config: CapConfig = CapConfig(50, 32, 4, 60, 60)
    cap = Cap(cap_config, data_source)

    # Create a challenge
    challenge_item = await cap.create_challenge()
    assert challenge_item.token in data_source.challenges

    # Solve the challenge
    timer = int(time.time() * 1e3)
    results, results_hash = await solve(challenge_item.token, cap.challenge)
    elapsed = int(time.time() * 1e3) - timer
    with capsys.disabled():
        print(
            f"Elapsed time: {elapsed:.2f} ms, "
            f"Solved and checked {len(results)} challenges"
        )

    def redeem_challenge(results):
        challenges = Cap.generate_challenge_from_token(
            challenge_item.token, challenge_item.challenge
        )

        is_valid = Cap.check_answer(challenges, results)
        return is_valid

    benchmark(
        redeem_challenge,
        results,
    )
