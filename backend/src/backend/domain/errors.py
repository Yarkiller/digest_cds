class DomainError(Exception):
    """Base domain error."""


class MaterialNotFoundError(DomainError):
    def __init__(self, material_id: int | str) -> None:
        super().__init__(f"material {material_id} not found")
        self.material_id = material_id


class IssueNotFoundError(DomainError):
    def __init__(self, number: int) -> None:
        super().__init__(f"issue {number} not found")
        self.number = number


class MaterialValidationError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MaterialNotReadyError(DomainError):
    def __init__(self, material_id: int) -> None:
        super().__init__(f"material {material_id} is not ready for indexing")
        self.material_id = material_id


class PersistenceError(DomainError):
    """Raised when an infrastructure adapter cannot complete a persistence operation."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class VotingCycleClosedError(DomainError):
    """Raised when cast_vote is attempted while cycle status is not open (D-51)."""

    def __init__(self, cycle_id: str) -> None:
        super().__init__(f"voting cycle {cycle_id} is closed")
        self.cycle_id = cycle_id


class VoteConflictError(DomainError):
    """Raised when expected_updated_at does not match the stored vote (D-54)."""

    def __init__(self, cycle_id: str, user_id: str) -> None:
        super().__init__(f"vote conflict for cycle {cycle_id} user {user_id}")
        self.cycle_id = cycle_id
        self.user_id = user_id


class InvalidVoteError(DomainError):
    """Raised for empty, unknown, or out-of-cycle topic_id."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
