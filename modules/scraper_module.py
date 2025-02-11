import requests

def get_github_repos(username):
    """Fetch public GitHub repositories for a user."""
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()  # Returns repo details as JSON
    else:
        return {"error": "GitHub API request failed"}

def get_github_user_info(username):
    """Fetch GitHub user profile details."""
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        return {"error": "Failed to retrieve user info"}

