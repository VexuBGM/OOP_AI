from src.models.incident import Incident
from src.exceptions import ClassificationError


class IncidentClassifier:
    high_keywords = (
        "outage",
        "breach",
        "data loss",
        "down",
        "malware",
        "administrator",
        "certificate",
    )
    medium_keywords = (
        "slow",
        "error",
        "failed",
        "fails",
        "timeout",
        "locked",
        "permission",
        "suspicious",
        "unavailable",
    )
    risky_categories = ("security", "database", "network")

    def predict_priority(self, incident: Incident) -> str:
        try:
            self._validate_incident(incident)
            score = self._calculate_score(incident)
        except ClassificationError:
            raise
        except (AttributeError, TypeError, ValueError) as error:
            raise ClassificationError(f"Cannot classify incident: {error}") from error

        if score >= 6:
            return "high"
        if score >= 3:
            return "medium"
        return "low"

    def _validate_incident(self, incident: Incident) -> None:
        text_fields = {
            "title": incident.title,
            "description": incident.description,
            "category": incident.category,
            "reported_by": incident.reported_by,
        }
        missing_fields = [
            name
            for name, value in text_fields.items()
            if not isinstance(value, str) or not value.strip()
        ]
        if missing_fields:
            raise ClassificationError(
                f"Missing incident fields: {', '.join(missing_fields)}."
            )
        if not isinstance(incident.affected_users, int) or incident.affected_users < 0:
            raise ClassificationError("Affected users must be a non-negative integer.")

    def _calculate_score(self, incident: Incident) -> int:
        text = f"{incident.title} {incident.description}".lower()
        score = 0

        if incident.affected_users >= 50:
            score += 5
        elif incident.affected_users >= 30:
            score += 3
        elif incident.affected_users >= 10:
            score += 2
        elif incident.affected_users >= 5:
            score += 2

        if incident.category in self.risky_categories:
            score += 2

        if any(keyword in text for keyword in self.high_keywords):
            score += 4

        if any(keyword in text for keyword in self.medium_keywords):
            score += 1

        return score
