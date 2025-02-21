import ollama
import requests
import base64
import os
import concurrent.futures  # ✅ Enables parallel execution
import re

GITHUB_API = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")  # ✅ Ensure GitHub Token is used if available
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
                all_files.extend(fetch_repo_files(owner, repo, file["path"]))  # 🔹 Recursively fetch subdirectory files
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
        return None  # ✅ Return None if file is empty or couldn't be fetched

    snippet = content[:5000]  # ✅ Limit snippet to prevent AI overload

    prompt = f"""
    Analyze the security vulnerabilities in the following file: '{file['name']}'
    from the repository '{repo_name}'. Identify **only real security issues** and provide actionable recommendations.

    📌 **File Content for Analysis:**  
    ```{snippet}```  

    ---
    **🔴 High Risk Issues**
    - **Issue:** Describe the problem clearly.  
      **Impact:** Explain why this is dangerous.  
      ➜ **Recommendation:** Provide a specific fix.

    **⚠️ Medium Risk Issues**
    - **Issue:** Explain the security concern.  
      **Impact:** Describe potential consequences.  
      ➜ **Recommendation:** Offer an actionable fix.

    **🟢 Low Risk / Best Practices**
    - **Issue:** Mention a best practice or minor issue.  
      **Impact:** Explain if relevant.  
      ➜ **Recommendation:** Suggest an improvement.
    """

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])
    ai_output = response.get("message", {}).get("content", "").strip()
    
    if ai_output:
        return (file["name"], ai_output)

    return None  # ✅ Return None if AI finds no issues

def analyze_github_repos(repos):
    """Analyze GitHub repositories and categorize findings into High, Medium, and Low risk groups globally."""
    
    security_findings = {"High": [], "Medium": [], "Low": []}

    for repo in repos:
        repo_name = repo["name"]
        owner = repo["owner"]["login"]
        files = repo.get("files", [])

        # ✅ Filter for relevant source code files
        code_files = [file for file in files if file["name"].endswith(
            (".py", ".js", ".java", ".c", ".cpp", ".go", ".yml", ".yaml",
             ".json", ".html", ".xml", ".travis.yml", ".gitignore", "robots.txt", ".env", ".swift"))]

        if not code_files:
            continue  # Skip if no relevant files

        # ✅ Run AI analysis in parallel for multiple files
        with concurrent.futures.ThreadPoolExecutor() as executor:
            results = list(executor.map(lambda file: analyze_file(owner, repo_name, file), code_files))

        # ✅ Process results globally across all repositories
        for result in results:
            if result:
                file_name, ai_output = result

                # ✅ Extract individual vulnerabilities per severity level from AI output
                current_risk_level = None
                parsed_findings = {"High": [], "Medium": [], "Low": []}

                for risk_level_marker, risk_level in [
                    ("🔴 High Risk Issues", "High"),
                    ("⚠️ Medium Risk Issues", "Medium"),
                    ("🟢 Low Risk / Best Practices", "Low"),
                ]:
                    if risk_level_marker in ai_output:
                        findings_block = ai_output.split(risk_level_marker)[1].strip()  # Extract findings under this risk level

                        # ✅ Remove risk level markers from appearing inside issue entries
                        findings_block = findings_block.replace("🔴 High Risk Issues", "").replace("⚠️ Medium Risk Issues", "").replace("🟢 Low Risk / Best Practices", "")

                        # ✅ Split issues while keeping "Issue", "Impact", and "Recommendation" together
                        issues = re.split(r"- \*\*Issue:\*\*", findings_block)[1:]  # Split only on properly formatted issues

                        for issue in issues:
                            issue_lines = issue.strip().split("\n")

                            # ✅ Remove stray/blank "Issue:" entries
                            issue_lines = [line for line in issue_lines if line.strip() and line.strip() != "**Issue:**"]

                            if not issue_lines:
                                continue  # Skip empty issues

                            # ✅ Format correctly, ensuring all parts are grouped properly
                            formatted_issue = f"📂 **{repo_name}** ({file_name})"
                            for part in issue_lines:
                                if "**Impact:**" in part or "➜ **Recommendation:**" in part:
                                    formatted_issue += f"\n  - {part.strip()}"
                                else:
                                    formatted_issue += f"\n  - **Issue:** {part.strip()}"

                            # ✅ Ensure risk levels appear ONLY ONCE in `main.py`
                            parsed_findings[risk_level].append(formatted_issue)




                # ✅ Append results only if there are findings
                for risk_level in ["High", "Medium", "Low"]:
                    if parsed_findings[risk_level]:
                        security_findings[risk_level].extend(parsed_findings[risk_level])

    print("\n🔍 DEBUG: Processed AI Findings:")
    for level, findings in security_findings.items():
        print(f"{level}: {len(findings)} issues found.")

    return security_findings