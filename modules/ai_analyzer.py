import ollama
import requests
import base64
import os

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional for public repos
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

if not GITHUB_TOKEN:
    print("⚠️ Warning: GITHUB_TOKEN is not set! Using unauthenticated API requests (rate limits apply).")

def get_github_repos(username):
    """Fetch public repositories for a given GitHub username."""
    url = f"{GITHUB_API}/users/{username}/repos"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        repos = response.json()
        return [
            {"name": repo["name"], "owner": {"login": repo["owner"]["login"]}}
            for repo in repos
        ]
    
    print(f"❌ Failed to fetch repositories for {username} (Status: {response.status_code})")
    return []

def get_repo_files(owner, repo, path=""):
    """Recursively fetch files from a GitHub repository, including subdirectories."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        files = response.json()
        all_files = []

        for file in files:
            if file["type"] == "file":
                all_files.append(file)  # ✅ Add file to list
            elif file["type"] == "dir":  # ✅ Found a subdirectory
                print(f"📂 Entering subdirectory: {file['path']}")  # Debugging
                sub_files = get_repo_files(owner, repo, file["path"])  # ✅ Recursive call
                all_files.extend(sub_files)  # ✅ Add subdirectory files to list

        return all_files

    print(f"❌ Failed to fetch files for {repo} (Status: {response.status_code})")
    return []

def get_file_content(owner, repo_name, file_path):
    """Fetches and decodes the content of a file in a repository."""
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/contents/{file_path}"
    
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        content_data = response.json()
        if "content" in content_data and content_data.get("encoding") == "base64":
            return base64.b64decode(content_data["content"]).decode("utf-8", errors="ignore")

    return None

def analyze_github_repos(repos):
    """Analyze each GitHub repository separately and store only notable security findings per file."""
    
    security_findings = {}  # ✅ Store findings per repo

    for repo in repos:
        repo_name = repo["name"]
        owner = repo["owner"]["login"]
        files = get_repo_files(owner, repo_name)

        if not files:
            print(f"⚠️ Skipping {repo_name}, no supported files found.")
            continue

        repo_findings = {}  # ✅ Store findings per file

        for file in files:
            if file["type"] == "file" and file["name"].endswith((".py", ".js", ".java", ".c", ".cpp", ".go", ".yml", ".yaml", ".json", ".html", ".xml", ".travis.yml", ".gitignore", "robots.txt", ".env", ".swift")):
                content = get_file_content(owner, repo_name, file["path"])
                if not content:
                    continue  # Skip empty or unreadable files
                
                # ✅ Limit content length to avoid overwhelming AI
                snippet = content[:1500] if len(content) > 1500 else content  

                # ✅ AI prompt to analyze only this file
                prompt = f"""
                Analyze the security vulnerabilities in the following file: '{file['name']}' 
                from the repository '{repo_name}'. Identify security risks and provide recommendations.
                
                ```{snippet}```  # ✅ Limited content
                
                Only report real security vulnerabilities. Do not include best practices unless they impact security.
                """

                # ✅ Call Ollama AI model for analysis
                response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
                ai_output = response.get("message", {}).get("content", "").strip()

                if "vulnerability" in ai_output.lower() or "risk" in ai_output.lower():
                    repo_findings[file["name"]] = ai_output  # ✅ Store findings per file

        if repo_findings:  # ✅ Only store if vulnerabilities are found
            security_findings[repo_name] = repo_findings

    return security_findings  # ✅ Returns only meaningful security issues
