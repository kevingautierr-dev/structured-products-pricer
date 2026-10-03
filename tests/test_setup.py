import numpy as np
from pricer import __version__


def test_package_imports():
    """The pricer package is importable from src/."""
    assert __version__ == "0.1.0"


def test_rng_is_reproducible():
    """Same seed gives same draws: needed later for common random numbers in Greeks."""
    a = np.random.default_rng(42).standard_normal(5)
    b = np.random.default_rng(42).standard_normal(5)
    assert np.allclose(a, b)