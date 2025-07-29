import pytest
from pytest import CaptureFixture

from ._cap_rust import rust_generate_challenge_from_token, rust_prng
from .cap import _py_generate_challenge_from_token
from .utils import py_prng


def test_prng():
    # Test that the PRNG is deterministic
    prng1 = rust_prng("test", 1024)
    prng2 = py_prng("test", 1024)
    assert prng1 == prng2


@pytest.mark.benchmark
def test_rust_prng_speed(benchmark, capsys: CaptureFixture[str]):
    benchmark(rust_prng, "test", 1024)


@pytest.mark.benchmark
def test_py_prng_speed(benchmark, capsys: CaptureFixture[str]):
    benchmark(py_prng, "test", 1024)


def test_generate_challenge_from_token():
    token = "test_token"

    challenges_rust = rust_generate_challenge_from_token(token, 64, 128, 16)
    challenges_py = _py_generate_challenge_from_token(token, 64, 128, 16)

    assert challenges_rust == challenges_py
    assert len(challenges_rust) == 64
    for salt, target in challenges_rust:
        assert len(salt) == 128
        assert len(target) == 16


@pytest.mark.benchmark
def test_rust_generate_speed(benchmark, capsys: CaptureFixture[str]):
    benchmark(rust_generate_challenge_from_token, "test_token", 64, 128, 16)


@pytest.mark.benchmark
def test_py_generate_speed(benchmark, capsys: CaptureFixture[str]):
    benchmark(_py_generate_challenge_from_token, "test_token", 64, 128, 16)
