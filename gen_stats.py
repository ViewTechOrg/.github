import requests
import os
import sys
import re

# --- Konfigurasi --
ORG_NAME = "ViewTechOrg"
README_PATH = "profile/README.md"
START_TAG = "<!--ORG_STATS_START-->"
END_TAG = "<!--ORG_STATS_END-->"

GITHUB_TOKEN = os.environ.get("TOKEN")

def make_api_request(url):
    """Membuat permintaan ke API GitHub dengan header yang benar dan penanganan error."""
    headers = {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    try:
        response = requests.get(url, headers=headers)
        # Lemparkan error jika respons tidak sukses (misal: 403 Forbidden, 404 Not Found)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error saat melakukan request ke {url}: {e}", file=sys.stderr)
        sys.exit(1) # Keluar dari skrip dengan status error

def fetch_paginated_data(url):
    """Mengambil data dari endpoint API GitHub yang memiliki paginasi."""
    results = []
    page = 1
    while True:
        # Menambahkan parameter paginasi ke URL
        paginated_url = f"{url}{'?' if '?' not in url else '&'}per_page=100&page={page}"
        data = make_api_request(paginated_url)
        if not data:
            break
        results.extend(data)
        page += 1
    return results

def generate_org_stats():
    """Mengambil data organisasi, memproses, dan menghasilkan konten markdown."""
    print(f"Memulai pengambilan data untuk organisasi: {ORG_NAME}...")

    org_data = make_api_request(f"https://api.github.com/orgs/{ORG_NAME}")
    print("Mengambil data repositori...")
    repos = fetch_paginated_data(org_data['repos_url'])
    print("Mengambil data anggota...")
    members = fetch_paginated_data(f"https://api.github.com/orgs/{ORG_NAME}/members")

    if not isinstance(repos, list):
        print(f"Error: Data repositori yang diterima bukan list. Data: {repos}", file=sys.stderr)
        sys.exit(1)

    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:3]

    print("Membangun konten statistik...")
    lines = [
        f"- 🔭 **Total Proyek Publik**: {org_data.get('public_repos', 0)}",
        f"- 👥 **Jumlah Anggota**: {len(members)}",
        f"- 🌟 **Total Bintang di Semua Proyek**: {total_stars}",
        "",
        "### 🚀 Top 3 Repositori dengan Bintang Terbanyak:",
    ]
    for repo in top_repos:
        lines.append(f"- [{repo['name']}]({repo['html_url']}) — ⭐ {repo['stargazers_count']}")
    
    return "\n".join(lines)

def inject_stats_into_readme(stats_content):
    """Menyisipkan konten statistik ke dalam file README di antara tag yang ditentukan."""
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print(f"Error: File README tidak ditemukan di '{README_PATH}'", file=sys.stderr)
        sys.exit(1)

    # Gunakan regex untuk mengganti konten di antara tag secara aman
    # re.DOTALL membuat '.' cocok dengan newline, penting untuk blok multiline
    pattern = re.compile(f"({re.escape(START_TAG)})(.*?)({re.escape(END_TAG)})", re.DOTALL)
    
    if not pattern.search(readme_content):
        print(f"Error: Tag '{START_TAG}' atau '{END_TAG}' tidak ditemukan di README.", file=sys.stderr)
        sys.exit(1)

    # Bangun konten baru: start_tag + baris baru + statistik + baris baru + end_tag
    replacement_text = f"\\1\n{stats_content}\n\\3"
    
    new_readme_content = pattern.sub(replacement_text, readme_content)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_readme_content)
    
    print(f"Statistik berhasil disisipkan ke dalam '{README_PATH}'")

if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN tidak ditemukan. Pastikan workflow memiliki izin yang benar.", file=sys.stderr)
        sys.exit(1)

    stats_content = generate_org_stats()    
    inject_stats_into_readme(stats_content)
