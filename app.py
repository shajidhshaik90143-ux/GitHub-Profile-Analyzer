import json
import streamlit as st
import pandas as pd
import plotly.express as px
from src.github_api import GitHubClient, GitHubAPIError
from src.analyzer import ProfileAnalyzer
from src.utils import safe_int, format_number

st.set_page_config(
    page_title="GitHub Profile Analyzer",
    page_icon="🐙",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
.main-header {font-size: 2.4rem; font-weight: 800; margin-bottom: .2rem;}
.subtitle {color:#6b7280; margin-bottom:1.5rem;}
.metric-card {padding:1rem; border-radius:14px; border:1px solid #e5e7eb; background:#fff;}
.small-muted {color:#6b7280; font-size:.9rem;}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">🐙 GitHub Profile Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Analyze GitHub profiles, repositories, languages, activity, community signals, and developer strengths.</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuration")
    username = st.text_input("GitHub username", placeholder="e.g. torvalds")
    token = st.text_input(
        "GitHub token (optional)",
        type="password",
        help="A token increases API rate limits. It is never stored by this app."
    )
    repo_limit = st.slider("Repositories to analyze", 10, 100, 50, 10)
    st.divider()
    st.caption("Public GitHub data only. Respect GitHub's API terms and rate limits.")
    st.caption("Tip: create a fine-grained token with read-only public repository access if needed.")

if not username:
    st.info("👈 Enter a GitHub username in the sidebar to begin.")
    st.stop()

client = GitHubClient(token=token.strip() or None)

try:
    with st.spinner(f"Fetching GitHub data for @{username}..."):
        profile = client.get_user(username.strip())
        repos = client.get_repositories(username.strip(), repo_limit)
        events = client.get_events(username.strip(), 100)
except GitHubAPIError as e:
    st.error(str(e))
    st.stop()
except Exception as e:
    st.error(f"Unexpected error: {e}")
    st.stop()

analyzer = ProfileAnalyzer(profile, repos, events)
report = analyzer.build_report()

st.success(f"Loaded @{profile.get('login', username)} successfully.")

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Followers", format_number(profile.get("followers", 0)))
c2.metric("Following", format_number(profile.get("following", 0)))
c3.metric("Public repos", format_number(profile.get("public_repos", 0)))
c4.metric("Total stars", format_number(report["totals"]["stars"]))
c5.metric("Profile score", f'{report["score"]}/100')

tabs = st.tabs([
    "📊 Overview", "📦 Repositories", "💻 Languages",
    "📈 Activity", "🏆 Score", "📤 Export"
])

with tabs[0]:
    left, right = st.columns([1, 2])
    with left:
        avatar = profile.get("avatar_url")
        if avatar:
            st.image(avatar, width=180)
        st.subheader(profile.get("name") or profile.get("login"))
        st.write(f"**@{profile.get('login')}**")
        if profile.get("bio"):
            st.write(profile["bio"])
        if profile.get("location"):
            st.write(f"📍 {profile['location']}")
        if profile.get("company"):
            st.write(f"🏢 {profile['company']}")
        if profile.get("blog"):
            st.write(f"🔗 {profile['blog']}")
        st.write(f"📅 Joined {str(profile.get('created_at', ''))[:10]}")
        st.link_button("Open GitHub Profile", profile.get("html_url", "#"))
    with right:
        st.subheader("Profile Summary")
        summary = report["summary"]
        st.write(summary)
        st.subheader("Key Signals")
        for signal in report["signals"]:
            st.write(f"• {signal}")

with tabs[1]:
    df = pd.DataFrame(report["repositories"])
    if df.empty:
        st.warning("No public repositories found.")
    else:
        col1, col2, col3 = st.columns(3)
        col1.metric("Repositories analyzed", len(df))
        col2.metric("Forks", format_number(int(df["forks"].sum())))
        col3.metric("Stars", format_number(int(df["stars"].sum())))

        sort_by = st.selectbox("Sort repositories by", ["stars", "forks", "size_kb", "updated_at"])
        ascending = sort_by in ["size_kb"]
        show = df.sort_values(sort_by, ascending=ascending).copy()
        st.dataframe(
            show[["name", "description", "language", "stars", "forks", "open_issues", "updated_at", "url"]],
            use_container_width=True,
            hide_index=True
        )

        top = df.sort_values("stars", ascending=False).head(10)
        fig = px.bar(top, x="stars", y="name", orientation="h",
                     title="Top repositories by stars",
                     labels={"stars":"Stars","name":"Repository"})
        st.plotly_chart(fig, use_container_width=True)

with tabs[2]:
    lang_df = pd.DataFrame(report["languages"])
    if lang_df.empty:
        st.info("Language information is unavailable for the analyzed repositories.")
    else:
        a, b = st.columns(2)
        with a:
            fig = px.pie(lang_df, names="language", values="repositories",
                         title="Repository language distribution", hole=.45)
            st.plotly_chart(fig, use_container_width=True)
        with b:
            fig = px.bar(lang_df.head(12), x="repositories", y="language",
                         orientation="h", title="Languages by repository count")
            st.plotly_chart(fig, use_container_width=True)
        st.dataframe(lang_df, use_container_width=True, hide_index=True)

with tabs[3]:
    activity_df = pd.DataFrame(report["activity"])
    if activity_df.empty:
        st.info("No recent public event activity was returned.")
    else:
        fig = px.bar(activity_df, x="date", y="events", title="Recent public GitHub activity")
        fig.update_layout(xaxis_title="Date", yaxis_title="Events")
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Event breakdown")
        event_df = pd.DataFrame(report["event_types"])
        if not event_df.empty:
            fig2 = px.bar(event_df.head(12), x="events", y="event",
                          orientation="h", title="Most common event types")
            st.plotly_chart(fig2, use_container_width=True)

with tabs[4]:
    st.subheader(f"Developer Profile Score: {report['score']}/100")
    for item in report["score_breakdown"]:
        st.write(f"**{item['category']} — {item['points']}/{item['max_points']}**")
        st.progress(item["points"] / item["max_points"])
        st.caption(item["reason"])
    st.divider()
    st.subheader("Recommendations")
    for rec in report["recommendations"]:
        st.write(f"💡 {rec}")

with tabs[5]:
    st.subheader("Export analysis")
    export = report["export"]
    json_data = json.dumps(export, indent=2, ensure_ascii=False)
    csv_df = pd.DataFrame(report["repositories"])
    st.download_button(
        "⬇️ Download JSON report",
        data=json_data,
        file_name=f"{profile.get('login', username)}_github_analysis.json",
        mime="application/json"
    )
    st.download_button(
        "⬇️ Download repository CSV",
        data=csv_df.to_csv(index=False),
        file_name=f"{profile.get('login', username)}_repositories.csv",
        mime="text/csv"
    )
    st.json({
        "username": profile.get("login"),
        "score": report["score"],
        "stars": report["totals"]["stars"],
        "repositories_analyzed": len(repos)
    })
