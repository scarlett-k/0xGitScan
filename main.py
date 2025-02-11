import sys
import os

# 🔹 Ensure Python recognizes the "modules" directory
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

# ✅ Import from the modules directory
from modules.scraper_module import get_github_repos, get_github_user_info
from ai_analyzer import analyze_github_repos
from report_generator import generate_report

def main():
    username = input("🔍 Enter GitHub username: ")
    
    print("\n📡 Fetching real-time OSINT data...")
    repos = get_github_repos(username)

    if "error" in repos:
        print(f"❌ Error: {repos['error']}")
        return

    print(f"\n🔍 Found {len(repos)} repositories.")
    for repo in repos:
        print(f"- {repo['name']}")

    print("\n🧠 Running AI analysis with Ollama...")
    ai_analysis = analyze_github_repos(repos)

    print("\n📌 AI Insights:")
    print(ai_analysis.get("ai_analysis", "No AI analysis available."))

    # Generate and save report
    generate_report(username, repos, ai_analysis)

if __name__ == "__main__":
    main()
