## General info
Python-based tool that integrates with the GitHub API to scan Github repositories and automates vulnerability detection using AI. The tool identifies security risks, assesses their impact, and provides actionable remediation recommendations to enhance code security.
![image](https://github.com/user-attachments/assets/734101e8-779c-4841-85aa-35c667dcb88b)

### Features
- Analyzes github files for vulnearabilities using AI and provides structured findings (Issue → Impact → Recommendation)
- Categorizes issues by severity (High, Medium, Low)
- Supports multiple programming languages (Python, JavaScript, C, Java, YAML, etc.)
- Optimized for scanning individual repositories quickly

	
## Technologies
Project is created with:
* Python 3.12.4
* Llama 3 (AI model for vulnerability analysis)
* Ollama (Local AI runtime for executing Llama 3)
* GitHub API (Fetching repository files)

## Setup
#### **Install Dependencies**
Ensure you have **Python 3.8+** installed. Then, clone the repository and install required dependencies:
```bash
git clone https://github.com/yourusername/github-repo-scanner.git
cd github-repo-scanner
pip install -r requirements.txt
```
#### **Install Ollama (Linux/macOS)**
```
curl -fsSL https://ollama.com/install.sh | sh
```
#### **Install Ollama (Windows - Using Scoop)**
```
scoop install ollama
```
#### **Pull Llama 3 model**
```
ollama pull llama3
```
#### **Set Up GitHub API Access (Optional)**
For scanning private repositories, set up a GitHub API token:
```
export GITHUB_TOKEN=your_personal_access_token  # macOS/Linux
set GITHUB_TOKEN=your_personal_access_token     # Windows (CMD)
```
#### **Run the Scanner**
```
python main.py
```
Then, enter the GitHub repository URL when prompted.
