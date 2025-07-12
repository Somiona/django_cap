from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ChallengeType:
    count: int
    size: int
    difficulty: int

    def as_dict(self) -> dict[str, int]:
        return {
            "c": self.count,
            "s": self.size,
            "d": self.difficulty,
        }

    @staticmethod
    def from_dict(data: dict[str, int]) -> "ChallengeType":
        return ChallengeType(
            count=data.get("c", 0),
            size=data.get("s", 0),
            difficulty=data.get("d", 0),
        )


@dataclass(frozen=True)
class RedeemResult:
    success: bool
    message: str | None = None
    token: str | None = None
    expires: datetime | None = None


@dataclass
class ChallengeItem:
    challenge: ChallengeType
    expires: datetime
    token: str


@dataclass(frozen=True)
class CapConfig:
    challenge_count: int
    challenge_size: int
    challenge_difficulty: int
    challenge_expires_s: int
    token_expires_s: int


@dataclass(frozen=True)
class Solution:
    token: str
    solutions: list[int]


class DataSource(ABC):
    """
    Abstract base class for CAP data operations.
    This interface defines the contract for challenge and token storage.
    """

    @abstractmethod
    async def store_challenge(self, challenge_data: ChallengeItem) -> None:
        """Store a challenge in the data source."""
        pass

    @abstractmethod
    async def get_challenge(self, token: str) -> ChallengeItem | None:
        """
        Retrieve a challenge by token.
        Returns None if challenge not found or expired.
        """
        pass

    @abstractmethod
    async def delete_challenge(self, token: str) -> None:
        """Delete a challenge from the data source."""
        pass

    @abstractmethod
    async def store_token(
        self, token_id: str, token_hash: str, expires_datetime: datetime
    ) -> None:
        """Store a verification token in the data source."""
        pass

    @abstractmethod
    async def validate_token(
        self, token_id: str, token_hash: str, keep_token: bool = False
    ) -> bool:
        """
        Validate a token against the data source.
        If keep_token is False, the token will be deleted after validation.
        Returns True if token is valid, False otherwise.
        """
        pass

    @abstractmethod
    async def cleanup_expired(self) -> dict[str, int]:
        """
        Clean up expired challenges and tokens.
        Returns a dict with counts of cleaned items.
        """
        pass

    @abstractmethod
    async def get_stats(self) -> dict[str, Any]:
        """Get statistics about current challenges and tokens."""
        pass


def prng(seed: str, length: int) -> str:
    def fnv1a(s: str) -> int:
        hash = 2166136261
        for ch in s:
            hash ^= ord(ch)
            hash += (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24)
            hash &= 0xFFFFFFFF  # force 32-bit unsigned
        return hash

    state = fnv1a(seed)
    result = ""

    def next_num(state: int):
        state ^= state << 13
        state ^= (state & 0xFFFFFFFF) >> 17
        state ^= state << 5
        return state

    while len(result) < length:
        state = next_num(state)
        rnd = state & 0xFFFFFFFF
        result += f"{rnd:08x}"

    return result[:length]
