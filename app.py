import os
import sys
from fastapi import FastAPI
from pydantic import BaseModel

# ✅ Ensure Python recognizes the "modules" directory
sys.path.insert(0, os.path.abspath("modules"))

# ✅ Import OSINT functions
from scraper_module import get_github_repos, get_github_user_info
from ai_analyzer import analyze_github_repos
from report_generator import generate_report

app = FastAPI()

# 📌 Request Models
class GitHubLookupRequest(BaseModel):
    username: str

@app.get("/")
def home():
    return {"message": "Welcome to OSINT AI Recon Web API"}

@app.post("/github_lookup/")
def github_lookup(request: GitHubLookupRequest):
    """Retrieve GitHub user info, analyze security risks, and generate reports."""
    username = request.username

    # 🟢 Fetch repositories
    repos = get_github_repos(username)
    if "error" in repos:
        return {"error": repos["error"]}

    # 🧠 AI analysis on repositories
    ai_analysis = analyze_github_repos(repos)

    # 📄 Generate report
    report_data = generate_report(username, repos, ai_analysis)

    return {
        "github_username": username,
        "repositories": [repo["name"] for repo in repos if "name" in repo],
        "ai_analysis": ai_analysis.get("ai_analysis", "No AI analysis available."),
        "report": report_data
    }
