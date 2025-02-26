import sys
import os
import re
import requests

# 🔹 Ensure Python recognizes the "modules" directory before importing
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

from modules.ai_analyzer import analyze_github_repos, fetch_repo_files

# ✅ Ensure GITHUB_TOKEN is available (Optional for public repos)
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def main():
    print("\n🔍 GitHub Security Scanner")
    repo_url = input("🔗 Enter the GitHub repository URL: ").strip()

    # ✅ Validate and extract username/repo name from URL
    match = re.match(r"https://github\.com/([^/]+)/([^/]+)", repo_url)
    if not match:
        print("❌ Invalid GitHub URL format. Use: https://github.com/user/repo")
        sys.exit(1)

    username, repo_name = match.groups()
    print(f"\n📡 Fetching repository files for {username}/{repo_name}...")

    repos = [{"name": repo_name, "owner": {"login": username}}]  # ✅ Prepare repo structure
    files = fetch_repo_files(repos[0]["owner"]["login"], repos[0]["name"])  # ✅ Corrected function call

    if not files:
        print(f"❌ No files found in {repo_name}. Check if the repository exists, is public, or if the API request failed.")
        sys.exit(1)

    print(f"\n✅ {repo_name}: {len(files)} files fetched.")

    # ✅ Prepare repo data structure
    repos = [{"name": repo_name, "owner": {"login": username}, "files": files}]

    print("\n🧠 Running AI security analysis... (This may take a moment)")

    # ✅ Run AI analysis on fetched files
    ai_findings = analyze_github_repos(repos)

    # ✅ Debugging: Ensure properly formatted AI findings before printing
    print("\n🔍 DEBUG: Structured AI Findings (Before Display):")
    for risk, issues in ai_findings.items():
        print(f"{risk}: {len(issues)} issues")


    # ✅ Print vulnerabilities grouped by risk level
    if any(ai_findings.values()):
        print("\n📌 AI-Detected Security Issues (Grouped by Risk Level):")

        for risk_level, risk_header in [
            ("High", "🔴 High Risk Issues"), 
            ("Medium", "⚠️ Medium Risk Issues"), 
            ("Low", "🟢 Low Risk / Best Practices")
        ]:
            if ai_findings[risk_level]:  
                print(f"\n{risk_header}:")
                for issue in ai_findings[risk_level]:
                    print(issue.strip(), "\n")  # ✅ Strip whitespace for clean output

    else:
        print("\n✅ No major security vulnerabilities detected.")

if __name__ == "__main__":
    main()