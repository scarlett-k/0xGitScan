import ollama
import json

def analyze_github_repos(repos):
    """Uses a local AI model (Mistral/Llama2) to analyze GitHub repositories for security insights."""
    
    if not repos or "error" in repos:
        return {"error": "No valid repositories found to analyze"}

    # Format the data for better AI processing
    repo_names = [repo["name"] for repo in repos if "name" in repo]
    repo_descriptions = [repo.get("description", "No description") for repo in repos]

    prompt = (
        f"Analyze the following GitHub repositories for security risks:\n\n"
        f"Repositories: {repo_names}\n"
        f"Descriptions: {repo_descriptions}\n\n"
        f"Provide insights on any vulnerabilities/weak security practices shown any files and how a penetration tester can exploit them, Refer to Top Security Vulnerabilities in GitHub Repositories. And then give recommendations on how to get rid of these risks or mitigate them."
    )

    response = ollama.chat(model="mistral", messages=[{"role": "user", "content": prompt}])

    # Check if the response contains a message
    if "message" in response:
        return {"ai_analysis": response["message"]["content"]}
    else:
        return {"error": "Ollama failed to generate an analysis."}
