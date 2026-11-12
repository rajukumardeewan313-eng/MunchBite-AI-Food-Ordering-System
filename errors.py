"""Application exceptions. ServiceError messages are safe to show to users."""


class ServiceError(Exception):
    """A business-rule / validation problem with a user-friendly message."""


class DBError(Exception):
    """Database is unreachable or a query failed. Details are only logged."""
