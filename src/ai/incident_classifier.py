from src.models.incident import Incident


class IncidentClassifier:
    high_keywords = ("outage", "breach", "data loss", "down", "malware")
    medium_keywords = ("slow", "error", "failed", "timeout", "locked")
    risky_categories = ("security", "database", "network")

    def predict_priority(self, incident: Incident) -> str:
        score = self._calculate_score(incident)

        if score >= 6:
            return "high"
        if score >= 3:
            return "medium"
        return "low"

    def _calculate_score(self, incident: Incident) -> int:
        text = f"{incident.title} {incident.description}".lower()
        score = 0

        if incident.affected_users >= 50:
            score += 3
        elif incident.affected_users >= 10:
            score += 2

        if incident.category in self.risky_categories:
            score += 2

        if any(keyword in text for keyword in self.high_keywords):
            score += 3

        if any(keyword in text for keyword in self.medium_keywords):
            score += 1

        return score
