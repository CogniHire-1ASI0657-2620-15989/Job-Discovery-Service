import time


class CircuitOpenError(Exception):
    pass


class CircuitBreaker:
    """Small process-local circuit breaker for the single Jooble adapter."""

    def __init__(self, failure_threshold: int = 3, recovery_seconds: float = 30.0):
        self._failure_threshold = failure_threshold
        self._recovery_seconds = recovery_seconds
        self._failures = 0
        self._opened_at: float | None = None

    def allow_request(self) -> bool:
        if self._opened_at is None:
            return True
        if time.monotonic() - self._opened_at >= self._recovery_seconds:
            return True
        return False

    def record_success(self) -> None:
        self._failures = 0
        self._opened_at = None

    def record_failure(self) -> None:
        self._failures += 1
        if self._failures >= self._failure_threshold:
            self._opened_at = time.monotonic()
