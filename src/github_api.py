import requests
import streamlit as st

BASE_URL = "https://api.github.com"

class GitHubAPIError(Exception):
    pass

class GitHubClient:
    def __init__(self, token=None):
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitHub-Profile-Analyzer"
        })
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _get(self, path, params=None):
        try:
            r = self.session.get(BASE_URL + path, params=params, timeout=20)
        except requests.RequestException as e:
            raise GitHubAPIError(f"Network error while contacting GitHub: {e}")
        if r.status_code == 404:
            raise GitHubAPIError("GitHub user or resource was not found. Check the username.")
        if r.status_code == 403:
            remaining = r.headers.get("X-RateLimit-Remaining", "0")
            raise GitHubAPIError(
                f"GitHub API rate limit/permission issue (remaining requests: {remaining}). "
                "Try again later or provide a GitHub token."
            )
        if r.status_code >= 400:
            try:
                message = r.json().get("message", r.text)
            except Exception:
                message = r.text
            raise GitHubAPIError(f"GitHub API error {r.status_code}: {message}")
        return r.json()

    @st.cache_data(ttl=300, show_spinner=False)
    def get_user(_self, username):
        return _self._get(f"/users/{username}")

    @st.cache_data(ttl=300, show_spinner=False)
    def get_repositories(_self, username, limit=50):
        data = []
        page = 1
        while len(data) < limit and page <= 10:
            batch = _self._get(
                f"/users/{username}/repos",
                {"per_page": min(100, limit-len(data)), "page": page, "sort": "updated", "direction": "desc"}
            )
            if not batch:
                break
            data.extend(batch)
            page += 1
        return data[:limit]

    @st.cache_data(ttl=300, show_spinner=False)
    def get_events(_self, username, limit=100):
        data = []
        page = 1
        while len(data) < limit and page <= 3:
            batch = _self._get(
                f"/users/{username}/events/public",
                {"per_page": min(100, limit-len(data)), "page": page}
            )
            if not batch:
                break
            data.extend(batch)
            page += 1
        return data[:limit]
