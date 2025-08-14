import warnings
import pytest
import sys, os

# Ensure project code directory is on path so 'simulation' package resolves
proj_root = os.path.dirname(os.path.dirname(__file__))  # .../code/tests -> .../code
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

# Import simulation package early to run centralized model rebuilds
import simulation  # noqa: F401

# Convert Pydantic forward-ref user errors into test failures if they appear as warnings.
# (Pydantic raises errors normally; to catch latent forward ref warnings we elevate them.)

def pytest_configure(config):
    # Turn any Pydantic 'class-not-fully-defined' user errors (if emitted as warnings elsewhere) into errors.
    warnings.filterwarnings(
        "error",
        message=r".*not fully defined.*model_rebuild.*",
    )

@pytest.fixture(autouse=True)
def fail_on_forward_ref_warnings():
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "error",
            message=r".*not fully defined.*model_rebuild.*",
        )
        yield
