import os

def fetch_org_data(org):
    headers = {
        "Authorization": f"Bearer {os.environ.get('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json",
    }

    org_data = requests.get(f"https://api.github.com/orgs/{org}", headers=headers).json()
    repos = requests.get(f"https://api.github.com/orgs/{org}/repos?per_page=100", headers=headers).json()
    members = requests.get(f"https://api.github.com/orgs/{org}/members", headers=headers).json()

    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    top_repo = sorted(repos, key=lambda x: x.get("stargazers_count", 0), reverse=True)[:3]

    return {
        "name": org_data.get("name", org),
        "public_repos": org_data.get("public_repos", 0),
        "followers": org_data.get("followers", 0),
        "members": len(members),
        "stars": total_stars,
        "top_repos": [(r["name"], r["stargazers_count"], r["html_url"]) for r in top_repo]
    }
