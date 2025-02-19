import sys
import os

# 🔹 Ensure Python recognizes the "modules" directory
sys.path.append(os.path.join(os.path.dirname(__file__), "modules"))

# ✅ Import modules (Fix import paths if needed)
from modules.ai_analyzer import analyze_github_repos,  get_github_repos
from modules.report_generator import generate_report

# ✅ Ensure GITHUB_TOKEN is available
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional for public repos
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def main():
    print(f"🔑 GitHub Token Set: {'Yes ✅' if GITHUB_TOKEN else 'No ❌ (May hit rate limits)'}")

    username = input("🔍 Enter GitHub username: ")
    
    print("\n📡 Fetching Github repos...")
    repos = get_github_repos(username)

    # ✅ Debug: Check what `repos` looks like
    # print(f"DEBUG: repos response = {repos}")

    # ✅ Handle cases where repos are empty or API fails
    if not repos or isinstance(repos, dict) and "error" in repos:
        print(f"❌ Error: No repositories found or API issue.")
        return
    #printing out the found repo names
    print(f"\n🔍 Found {len(repos)} repositories.")
    for repo in repos:
        print(f"- {repo['name']}")


    print("\n📝 Fetching files...")
    # Let ai_analyzer.py process and fetch files first
    ai_analysis = analyze_github_repos(repos)

    # ✅ Now print the actual fetched files
    for repo in repos:
        if "files" in repo and isinstance(repo["files"], list) and repo["files"]: #ALEX HELP
            print(f"✅ {repo['name']} has {len(repo['files'])} files.")
        else:
            print(f"⚠️ {repo['name']} has no usable files or only unsupported ones.")


    print("\n🧠 Running AI analysis with Ollama...")
    ai_analysis = analyze_github_repos(repos)

    # ✅ Handle AI response safely
    if ai_analysis and "ai_analysis" in ai_analysis:
        print("\n📌 AI Insights:")
        print(ai_analysis["ai_analysis"])
    else:
        print("\n❌ AI analysis failed. Check API logs.")

    # ✅ Generate and save report safely
    print("\n📄 Generating report...")
    try:
        generate_report(username, repos, ai_analysis)
        print("✅ Report successfully generated!")
    except Exception as e:
        print(f"❌ Failed to generate report: {e}")

if __name__ == "__main__":
    main()