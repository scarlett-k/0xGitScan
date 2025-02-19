import ollama
import requests
import base64
import os

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # Optional for public repos
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

if not GITHUB_TOKEN:
    print("⚠️ Warning: GITHUB_TOKEN is not set! Using unauthenticated API requests (rate limits apply).")

def get_repo_files(owner, repo):
    """Fetches a list of files in a given GitHub repository."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/"
    response = requests.get(url, headers=HEADERS)

    print(f"🔄 Checking {repo} for files... (Status: {response.status_code})")  # ✅ Debugging

    if response.status_code == 200:
        files = response.json()
        print(f"✅ {repo} has {len(files)} files.")
        return files

    print(f"❌ Failed to fetch files for {repo} (Status: {response.status_code})")
    print(f"Response: {response.text}")  # ✅ See API error details
    return []  # Return empty list on failure

def get_file_content(owner, repo_name, file_path):
    url = f"{GITHUB_API}/repos/{owner}/{repo_name}/contents/{file_path}"
    
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        content_data = response.json()
        
        # Decode Base64 content
        if "content" in content_data and "encoding" in content_data and content_data["encoding"] == "base64":
            decoded_content = base64.b64decode(content_data["content"]).decode("utf-8", errors="ignore")
            
            # print(f"✅ Decoded Content: {decoded_content[:200]}")  # ✅ Debugging: Print content preview
            return decoded_content  # ✅ Returns readable source code
        
        return content_data.get("content", "")  # Return content if no encoding
    
    print(f"❌ Failed to fetch {file_path} (Status Code: {response.status_code})")
    print(f"Response: {response.text}")  # ✅ Debugging: Print API response
    return None  # Return None if request fails

def analyze_github_repos(repos):
    """Uses Ollama (Mistral/Llama2) to analyze GitHub repositories for security vulnerabilities based on actual code."""

    if not repos or "error" in repos:
        return {"error": "No valid repositories found to analyze"}

    repo_names = [repo["name"] for repo in repos if "name" in repo]
    repo_descriptions = [repo.get("description", "No description") for repo in repos]
    repo_code_snippets = []

    # Iterate through each repo to fetch and extract code
    for repo in repos:
        owner = repo["owner"]["login"]
        repo_name = repo["name"]
        files = get_repo_files(owner, repo_name)
        
        if not files:
            print(f"⚠️ No files found in {repo_name}. Skipping analysis.")
            continue  # Skip repo if it has no code

        print(f"🔍 Found {len(files)} files in {repo_name}")

        for file in files:
            if file["type"] == "file" and file["name"].endswith((
    ".py", ".js", ".java", ".c", ".cpp", ".go", ".yml", ".yaml", ".json", ".html", ".xml", ".travis.yml", ".gitignore", "robots.txt", ".env", ".swift")):

                print(f"✅ Fetching: {file['name']}")
                code_content = get_file_content(owner, repo_name, file["path"])
                
                if code_content:
                    # print(f"\n🔍 **Fetched Code from {file['name']} in {repo_name}:**\n{code_content[:200]}...\n")
                    repo_code_snippets.append(f"### {file['name']}\n{code_content[:500]}")
                else:
                    print("❌ Skipping empty or unreadable file")
            else:
                print(f"❌ Skipping {file['name']} (Not a supported code file)")

    prompt = f"Analyze the following GitHub repositories for security risks:\n\nRepositories: {repo_names}\nDescriptions: {repo_descriptions}\n\nHere are extracted source code snippets:\n\n{repo_code_snippets}\n\nFind any security vulnerabilities in the repositories based on the actual source code."

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])

    if "message" in response and "content" in response["message"]:
        return {"ai_analysis": response["message"]["content"]}

    print("❌ Ollama response did not contain expected data:", response)
    return {"error": "Ollama failed to generate an analysis."}
