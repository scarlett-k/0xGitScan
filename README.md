## General info
Python-based tool that integrates with the GitHub API to scan Github repositories and automates vulnerability detection using AI. The tool identifies security risks, assesses their impact, and provides actionable remediation recommendations to enhance code security.
![image](https://github.com/user-attachments/assets/21f99718-403e-421a-b62e-1ce488cc6725)

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
git clone https://github.com/scarlett-k/0xGitScan
cd 0xgitscan
pip install -r requirements.txt
```
#### **Install Ollama (Linux/macOS)**
```
curl -fsSL https://ollama.com/install.sh | sh
```

#### **Install Ollama (Windows)**
Download Ollama for Windows from the official website: https://ollama.com/download                                 
Run the installer and follow the setup instructions.
After installation, verify it's working by opening PowerShell or Command Prompt and running:
```
ollama --version
```
#### **Pull Llama 3 model (or whatever model you'd like to use!)**
```
ollama pull llama3
```
#### **Set Up GitHub API Access (Optional)**
For scanning private repositories, set up a GitHub API token:
```
export GITHUB_TOKEN=your_personal_access_token  # macOS/Linux
set GITHUB_TOKEN=your_personal_access_token     # Windows (CMD)
```
#### **Customizing the LLM Model (Optional)**
By default, this project uses Llama 3 as the language model. However, you can easily switch to a different model supported by Ollama by modifying the model parameter in the following line of code:
```
response = ollama.chat(model="llama3", messages=[{"role": "user", "content": prompt}])
```
To use a different model, simply replace "llama3" with the name of your preferred LLM.
#### **Run the Scanner**
```
python main.py
```
Then, enter the GitHub repository URL when prompted.
