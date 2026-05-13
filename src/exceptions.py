class IncidentSystemError(Exception):
    """Base exception for the incident management project."""


class InvalidIncidentDataError(IncidentSystemError):
    """Raised when incident data is missing or invalid."""


class ClassificationError(IncidentSystemError):
    """Raised when the priority classifier cannot process an incident."""


class DatabaseOperationError(IncidentSystemError):
    """Raised when a database operation fails."""


class FileFormatError(IncidentSystemError):
    """Raised when a CSV or JSON file has an unexpected format."""
