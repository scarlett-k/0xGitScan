import requests

def get_github_info(username):
    """Fetches public GitHub repositories for a given username."""
    url = f"https://api.github.com/users/{username}/repos"
    response = requests.get(url)

    if response.status_code == 200:
        repos = response.json()
        return [repo["name"] for repo in repos]  # Return a list of repo names
    else:
        return f"Error: Unable to fetch data for {username}"
