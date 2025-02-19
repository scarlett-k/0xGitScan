import sys
import os

# 🔹 Ensure Python recognizes the "modules" directory
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

# ✅ Import modules (Fix import paths if needed)
from modules.ai_analyzer import analyze_github_repos, get_github_repos
from modules.report_generator import generate_report

# ✅ Ensure GITHUB_TOKEN is available
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional for public repos
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def main():
    print(f"🔑 GitHub Token Set: {'Yes ✅' if GITHUB_TOKEN else 'No ❌ (May hit rate limits)'}")

    username = input("🔍 Enter GitHub username: ")
    
    print("\n📡 Fetching GitHub repos...")
    repos = get_github_repos(username)

    # ✅ Handle cases where repos are empty or API fails
    if not repos or isinstance(repos, dict) and "error" in repos:
        print(f"❌ Error: No repositories found or API issue.")
        return

    # ✅ Print found repositories
    print(f"\n🔍 Found {len(repos)} repositories.")
    for repo in repos:
        print(f"- {repo['name']}")

    print("\n📝 Fetching and analyzing repositories...")
    
    # ✅ Analyze each repository after fetching files
    ai_findings = {}
    for repo in repos:
        repo_name = repo["name"]
        print(f"\n🔍 Processing repository: {repo_name}")

        findings = analyze_github_repos([repo])  # ✅ Pass one repo at a time
        
        if findings and repo_name in findings:
            ai_findings[repo_name] = findings[repo_name]  # ✅ Store findings only if issues are found

    # ✅ Print only if vulnerabilities are found
    if ai_findings:
        print("\n📌 AI-Detected Security Issues:")
        for repo, files in ai_findings.items():
            print(f"\n🔴 Security Findings in {repo}:")
            for file, details in files.items():
                print(f"\n📂 File: {file}\n{details}\n")
    else:
        print("\n✅ No major security vulnerabilities detected in any repositories.")

    # ✅ Generate and save report safely
    print("\n📄 Generating report...")
    try:
        generate_report(username, repos, ai_findings)
        print("✅ Report successfully generated!")
    except Exception as e:
        print(f"❌ Failed to generate report: {e}")

if __name__ == "__main__":
    main()
