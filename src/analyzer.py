from collections import Counter
from datetime import datetime, timezone
import pandas as pd

class ProfileAnalyzer:
    def __init__(self, profile, repos, events):
        self.profile = profile
        self.repos = repos or []
        self.events = events or []

    def _repo_rows(self):
        rows = []
        for r in self.repos:
            rows.append({
                "name": r.get("name", ""),
                "description": r.get("description") or "",
                "language": r.get("language") or "Unknown",
                "stars": r.get("stargazers_count", 0) or 0,
                "forks": r.get("forks_count", 0) or 0,
                "open_issues": r.get("open_issues_count", 0) or 0,
                "size_kb": r.get("size", 0) or 0,
                "updated_at": str(r.get("updated_at", ""))[:10],
                "created_at": str(r.get("created_at", ""))[:10],
                "url": r.get("html_url", "")
            })
        return rows

    def build_report(self):
        rows = self._repo_rows()
        total_stars = sum(r["stars"] for r in rows)
        total_forks = sum(r["forks"] for r in rows)

        language_counts = Counter(r["language"] for r in rows if r["language"] != "Unknown")
        languages = [{"language": k, "repositories": v}
                     for k, v in language_counts.most_common()]

        event_counts = Counter(e.get("type", "Unknown") for e in self.events)
        event_types = [{"event": k, "events": v} for k, v in event_counts.most_common()]

        dates = []
        for e in self.events:
            raw = e.get("created_at")
            if raw:
                try:
                    dates.append(datetime.fromisoformat(raw.replace("Z", "+00:00")).date())
                except ValueError:
                    pass
        activity = []
        if dates:
            counts = Counter(dates)
            activity = [{"date": str(d), "events": counts[d]} for d in sorted(counts)]

        score_breakdown = self._score(rows, total_stars, total_forks, language_counts, event_counts)
        score = sum(x["points"] for x in score_breakdown)

        recommendations = self._recommendations(rows, total_stars, language_counts, event_counts)

        name = self.profile.get("name") or self.profile.get("login")
        summary = (
            f"{name} has {self.profile.get('public_repos', 0)} public repositories, "
            f"{self.profile.get('followers', 0)} followers and {total_stars} stars across "
            f"the repositories analyzed. The profile currently shows "
            f"{len(language_counts)} identifiable programming languages."
        )

        signals = [
            f"{total_stars} total stars across analyzed repositories.",
            f"{total_forks} total forks across analyzed repositories.",
            f"{len(language_counts)} programming languages represented.",
            f"{len(self.events)} recent public events returned by GitHub.",
        ]

        export = {
            "profile": self.profile,
            "score": score,
            "totals": {"stars": total_stars, "forks": total_forks},
            "repositories": rows,
            "languages": languages,
            "activity": activity,
            "event_types": event_types,
            "recommendations": recommendations
        }

        return {
            "score": score,
            "score_breakdown": score_breakdown,
            "totals": {"stars": total_stars, "forks": total_forks},
            "repositories": rows,
            "languages": languages,
            "activity": activity,
            "event_types": event_types,
            "summary": summary,
            "signals": signals,
            "recommendations": recommendations,
            "export": export
        }

    def _score(self, rows, stars, forks, languages, events):
        profile_repos = self.profile.get("public_repos", 0) or 0
        followers = self.profile.get("followers", 0) or 0
        return [
            {
                "category": "Repository portfolio",
                "points": min(20, min(profile_repos, 20)),
                "max_points": 20,
                "reason": f"{profile_repos} public repositories are listed on the profile."
            },
            {
                "category": "Community reach",
                "points": min(20, int(followers ** 0.5 * 2)),
                "max_points": 20,
                "reason": f"{followers} followers contribute to this signal."
            },
            {
                "category": "Open-source traction",
                "points": min(20, int(stars ** 0.5 * 2)),
                "max_points": 20,
                "reason": f"{stars} stars were found across analyzed repositories."
            },
            {
                "category": "Technology breadth",
                "points": min(20, len(languages) * 4),
                "max_points": 20,
                "reason": f"{len(languages)} identifiable repository languages were found."
            },
            {
                "category": "Recent activity",
                "points": min(20, len(events) // 5),
                "max_points": 20,
                "reason": f"{len(self.events)} recent public events were returned."
            },
        ]

    def _recommendations(self, rows, stars, languages, events):
        recs = []
        if not rows:
            recs.append("Publish at least one well-documented public project.")
        if stars < 10:
            recs.append("Improve project documentation and discoverability to help projects gain visibility.")
        if not any(r["description"] for r in rows):
            recs.append("Add concise README/project descriptions to public repositories.")
        if len(languages) < 3:
            recs.append("Consider demonstrating multiple technologies through focused projects.")
        if not events:
            recs.append("Maintain visible public activity through meaningful commits, issues, pull requests, or releases.")
        if rows:
            no_desc = sum(not r["description"] for r in rows)
            if no_desc:
                recs.append(f"Add descriptions to {no_desc} repositories that currently lack them.")
        if not recs:
            recs.append("Continue maintaining high-quality repositories and documenting significant engineering work.")
        return recs
