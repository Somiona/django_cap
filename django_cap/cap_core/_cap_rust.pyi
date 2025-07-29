"""Type stubs for the Rust extension module."""

def rust_prng(seed: str, length: int) -> str:
    """Generate a pseudo-random string based on the seed."""
    ...

def rust_generate_challenge_from_token(
    token: str, count: int, size: int, difficulty: int
) -> list[tuple[str, str]]:
    """Generate a list of challenges given parameters"""
    ...

def rust_check_answer(challenges: list[tuple[str, str]], solutions: list[int]) -> bool:
    """Check if the provided solutions match the challenges."""
    ...

def rust_solve_pow(salt: str, target: str) -> int:
    """Solve a proof-of-work challenge."""
    ...
