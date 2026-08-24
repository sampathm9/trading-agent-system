from enum import Enum


class RuntimeState(str, Enum):
    CREATED = "CREATED"
    PREFLIGHT = "PREFLIGHT"
    READY = "READY"
    RUNNING = "RUNNING"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    EMERGENCY_STOP = "EMERGENCY_STOP"
    FAILED = "FAILED"


class RuntimeStateMachine:

    def __init__(self):
        self.state = RuntimeState.CREATED
        self.history = [
            RuntimeState.CREATED.value
        ]

    def transition(self, new_state):
        if isinstance(new_state, str):
            new_state = RuntimeState(new_state)

        self.state = new_state
        self.history.append(new_state.value)

        return self.state

    def is_running(self):
        return self.state == RuntimeState.RUNNING

    def is_stopped(self):
        return self.state in {
            RuntimeState.STOPPED,
            RuntimeState.EMERGENCY_STOP,
            RuntimeState.FAILED,
        }
