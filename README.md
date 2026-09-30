# 🐙 GitHub Profile Analyzer

A strong portfolio-ready Streamlit application for analyzing public GitHub profiles through the GitHub REST API.

## Features

- GitHub username lookup
- Optional personal access token for higher API limits
- Profile overview and metadata
- Repository portfolio analysis
- Stars, forks, issues and repository size
- Programming language distribution
- Recent public activity analysis
- Event-type breakdown
- Developer profile score with transparent categories
- Actionable improvement recommendations
- Interactive Plotly charts
- JSON and CSV exports
- API caching to reduce repeated requests
- Responsive Streamlit dashboard

## Project Structure

```text
GitHub Profile Analyzer/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
└── src/
    ├── __init__.py
    ├── github_api.py
    ├── analyzer.py
    └── utils.py
```

## Windows Setup

```powershell
cd "GitHub Profile Analyzer"
python -m venv .venv
.venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

Open the URL shown by Streamlit, normally:

```text
http://localhost:8501
```

## Optional GitHub Token

Unauthenticated GitHub API requests have a lower rate limit. A token can increase the available API quota.

Do not hard-code a token in source code or commit it to GitHub.

## Notes

- The application analyzes public GitHub information.
- Repository language data comes from repository metadata, not byte-level language statistics.
- The profile score is an application-defined heuristic, not an official GitHub metric.
- Recent public events are limited by GitHub's public events endpoint.
- API availability and rate limits can change.

## Suggested Enhancements

For an advanced version, add:
- GitHub OAuth login
- Compare two or more profiles
- Contribution calendar analysis
- README quality analysis
- Commit frequency analysis per repository
- Issue/PR analytics
- Organization analysis
- PDF report generation
- PostgreSQL history storage
- Background scheduled analysis
- GitHub webhook integration
- Admin dashboard
