"""
Position lifecycle: pending → open → managing → closed.

States
------
  PENDING   Trigger conditions not yet met. Watching.
  FIRED     Conditions met, order submitted, awaiting fill.
  OPEN      Order filled. Managing stop/target.
  CLOSED    Exit filled (stop, target, or manual).
  EXPIRED   Trigger window closed with no fill (e.g. past 11:00 AM ET).
  BLOCKED   Risk or autonomy gate prevented execution.
"""

from enum import Enum


class State(str, Enum):
    PENDING = "pending"
    FIRED = "fired"
    OPEN = "open"
    CLOSED = "closed"
    EXPIRED = "expired"
    BLOCKED = "blocked"


VALID_TRANSITIONS: dict[State, set[State]] = {
    State.PENDING: {State.FIRED, State.EXPIRED, State.BLOCKED},
    State.FIRED:   {State.OPEN, State.BLOCKED},
    State.OPEN:    {State.CLOSED},
    State.CLOSED:  set(),
    State.EXPIRED: set(),
    State.BLOCKED: set(),
}


class StateMachine:
    def __init__(self):
        self._states: dict[str, State] = {}  # ticker → state

    def get(self, ticker: str) -> State:
        return self._states.get(ticker, State.PENDING)

    def transition(self, ticker: str, new_state: State) -> bool:
        current = self.get(ticker)
        if new_state not in VALID_TRANSITIONS.get(current, set()):
            return False
        self._states[ticker] = new_state
        return True

    def is_watchable(self, ticker: str) -> bool:
        return self.get(ticker) == State.PENDING

    def all_states(self) -> dict[str, State]:
        return dict(self._states)
