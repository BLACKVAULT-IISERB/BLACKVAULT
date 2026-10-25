import pytest
from blackvault import AppState, seed_demo_state
from blackvault.service import Blackvault

@pytest.fixture
def state(): return seed_demo_state(AppState())

@pytest.fixture
def app(state): return Blackvault(state, b"x" * 32)
