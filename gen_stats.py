# gen_stats.py
import requests

ORG = "ViewTechOrg"
headers = {"Accept": "application/vnd.github+json"}

repos = requests.get(f"https://api.github.com/orgs/{ORG}/repos?per_page=100").json()
stars = sum(r.get("stargazers_count", 0) for r in repos)
forks = sum(r.get("forks_count", 0) for r in repos)
total_repos = len(repos)

members = requests.get(f"https://api.github.com/orgs/{ORG}/members").json()
total_members = len(members)

md = f"""<!--ORG_STATS_START-->
📊 **Statistik ViewTechOrg (Live)**

- 🔧 Total Repos: `{total_repos}`
- ⭐ Total Stars: `{stars}`
- 🍴 Total Forks: `{forks}`
- 👥 Anggota Terdaftar: `{total_members}`
- 📦 Bahasa Dominan: `Shell`, `Python`
<!--ORG_STATS_END-->
"""

with open("org_stats.md", "w") as f:
    f.write(md)
