import ollama
import requests
import base64
import os
import concurrent.futures
import re

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}"} if GITHUB_TOKEN else {}

def fetch_repo_files(owner, repo, path=""):
    """Fetch all files recursively from a GitHub repository, including subdirectories."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        files = response.json()
        all_files = []
        for file in files:
            if file["type"] == "file":
                all_files.append(file)
            elif file["type"] == "dir":
                all_files.extend(fetch_repo_files(owner, repo, file["path"]))  
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

def analyze_file(owner, repo_name, file):
    """Analyzes a single file using AI and returns security findings if any exist."""
    content = get_file_content(owner, repo_name, file["path"])
    if not content:
        return None  

    snippet = content[:5000]  

    prompt = f"""
    Analyze the security vulnerabilities in the following file: '{file['name']}'
    from the repository '{repo_name}'. Identify **only real security issues** and provide actionable recommendations.
    Indicate the level of the issue by marking it as "High Risk", "Medium Risk" or "Low Risk". If a file has no security issue at all, then state "No security vulnerabilities found" for that file.

    📌 **File Content for Analysis:**  
    ```{snippet}```  

    ---
    **Issues Format**:
    - **Issue Level:** High Risk / Medium Risk / Low Risk
    - **Issue:** [Describe the security issue]
      **Impact:** [Explain why this is dangerous]
      **Recommendation:** [Provide a specific fix]
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    ai_output = response.get("message", {}).get("content", "").strip()
    
    if ai_output:
        return (file["name"], ai_output)

    return None  

def extract_findings(ai_output, repo_name, file_name):
    """Parses AI output and extracts security findings into structured categories."""
    parsed_findings = {"High": [], "Medium": [], "Low": []}

    for risk_marker, risk_level in [
        ("High Risk", "High"),
        ("Medium Risk", "Medium"),
        ("Low Risk", "Low"),
    ]:
        if risk_marker in ai_output:
            findings_block = ai_output.split(risk_marker, 1)[-1].strip()

            # Remove unnecessary "Issue Level:" mentions
            findings_block = re.sub(r"\*\*Issue Level:\*\* (High|Medium|Low) Risk", "", findings_block).strip()

            # Extract issues while keeping "Issue", "Impact", and "Recommendation" together
            issues = re.split(r"- \*\*Issue:\*\*", findings_block)[1:]

            issues = [issue.replace("```", "").strip() for issue in issues if issue.strip()]

            seen_issues = set()
            for issue in issues:
                issue_lines = issue.strip().split("\n")
                formatted_issue = f"📂 **{repo_name}** ({file_name})"

                for part in issue_lines:
                    if "**Issue Level:**" in part:
                        continue  

                    if "**Issue:**" in part or "**Impact:**" in part or "**Recommendation:**" in part:
                        formatted_issue += f"\n  - {part.strip()}"
                    else:
                        formatted_issue += f"\n    {part.strip()}"

                if formatted_issue not in seen_issues:
                    parsed_findings[risk_level].append(formatted_issue)
                    seen_issues.add(formatted_issue)

    return parsed_findings

def analyze_github_repos(repos):
    """Analyzes GitHub repositories and categorizes security issues by severity."""
    security_findings = {"High": [], "Medium": [], "Low": []}

    for repo in repos:
        repo_name = repo["name"]
        owner = repo["owner"]["login"]
        files = repo.get("files", [])

        code_files = [file for file in files if file["name"].endswith(
            (".py", ".js", ".java", ".c", ".cpp", ".go", ".yml", ".yaml",
             ".json", ".html", ".xml", ".travis.yml", ".gitignore", "robots.txt", ".env", ".swift"))]

        if not code_files:
            continue  

        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda file: analyze_file(owner, repo_name, file), code_files))

        for result in results:
            if result:
                file_name, ai_output = result
                parsed_findings = extract_findings(ai_output, repo_name, file_name)

                for risk_level in ["High", "Medium", "Low"]:
                    security_findings[risk_level].extend(parsed_findings[risk_level])

    print("\n🔍 DEBUG: Processed AI Findings:")
    for level, findings in security_findings.items():
        print(f"{level}: {len(findings)} issues found.")

    return security_findings
