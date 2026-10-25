"""BLACKVAULT synthetic banking authorization prototype."""
from .service import Blackvault
from .models import Proposal, Decision
from .state import AppState, seed_demo_state

__all__ = ["Blackvault", "Proposal", "Decision", "AppState", "seed_demo_state"]
