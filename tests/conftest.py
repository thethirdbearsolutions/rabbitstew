import numpy as np
import pytest

from rabbitstew.simulation import SimConfig


@pytest.fixture
def rng():
    return np.random.default_rng(12345)


@pytest.fixture
def quick_sim():
    """A short bout configuration to keep the test suite fast."""
    return SimConfig(duration=1.0)
