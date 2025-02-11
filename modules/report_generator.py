import json

def generate_report(username, repos, ai_analysis):
    """Generates a structured JSON and Markdown report for OSINT AI analysis."""

    # Ensure AI analysis is properly formatted
    formatted_ai_analysis = ai_analysis.get("ai_analysis", "No AI analysis available.")

    # Force JSON to recognize line breaks
    formatted_ai_analysis = formatted_ai_analysis.replace("\n", "\n")

    report_data = {
        "target": username,
        "github_repositories": [repo["name"] for repo in repos if "name" in repo],
        "ai_analysis": formatted_ai_analysis
    }

    json_filename = f"osint_report_{username}.json"
    md_filename = f"osint_report_{username}.md"

    # ✅ Save JSON with proper indentation
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(report_data, json_file, indent=4, ensure_ascii=False)

    # ✅ Save Markdown file for better readability
    with open(md_filename, "w", encoding="utf-8") as md_file:
        md_file.write(f"# OSINT Analysis Report: {username}\n\n")
        md_file.write("## 🔍 GitHub Repositories:\n")
        for repo in report_data["github_repositories"]:
            md_file.write(f"- {repo}\n")
        
        md_file.write("\n## 🧠 AI Analysis:\n")
        md_file.write(formatted_ai_analysis)  # Markdown respects line breaks!

    print(f"\n📄 Reports saved as: {json_filename} and {md_filename}")
    return report_data
