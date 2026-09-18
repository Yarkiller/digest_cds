class DomainError(Exception):
    """Base domain error."""


class MaterialNotFoundError(DomainError):
    def __init__(self, material_id: int) -> None:
        super().__init__(f"material {material_id} not found")
        self.material_id = material_id


class MaterialValidationError(DomainError):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class MaterialNotReadyError(DomainError):
    def __init__(self, material_id: int) -> None:
        super().__init__(f"material {material_id} is not ready for indexing")
        self.material_id = material_id
