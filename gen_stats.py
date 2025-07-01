import requests
import os

ORG_NAME = "ViewTechOrg"
README_PATH = "profile/README.md"
START_TAG = "<!--ORG_STATS_START-->"
END_TAG = "<!--ORG_STATS_END-->"

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

def build_stats_md(data):
    lines = [
        f"- 🔭 **Total Proyek Publik**: {data['public_repos']}",
        f"- 👥 **Jumlah Anggota**: {data['members']}",
        f"- 🌟 **Total Stars**: {data['stars']}",
        "",
        "### 🚀 Top Repositori:",
    ]
    for name, stars, url in data["top_repos"]:
        lines.append(f"- [{name}]({url}) — ⭐ {stars}")
    return "\n".join(lines)

def inject_to_readme(content, start_tag, end_tag, readme_path):
    with open(readme_path, "r", encoding="utf-8") as f:
        lines = f.read()

    start = lines.find(start_tag)
    end = lines.find(end_tag, start)

    if start == -1 or end == -1:
        raise ValueError("Start or end tag not found in README.")

    new_lines = lines[:start+len(start_tag)] + "\n" + content + "\n" + lines[end:]
    
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(new_lines)

if __name__ == "__main__":
    org_data = fetch_org_data(ORG_NAME)
    stats_md = build_stats_md(org_data)
    inject_to_readme(stats_md, START_TAG, END_TAG, README_PATH)
