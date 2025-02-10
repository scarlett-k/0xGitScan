from modules.scraper import get_github_info

def main():
    target = input("Enter Github uesrname: ")
    repos = get_github_info(target)
    
    print("\n Found Repositories: ")
    for repo in repos:
        print(f"- {repo}")
if __name__  == "__main__":
    main()