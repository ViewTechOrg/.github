import requests
import os
import sys

# Konfigurasi
ORG_NAME = "ViewTechOrg"
OUTPUT_FILENAME = "org_stats.md"
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
        paginated_url = f"{url}?per_page=100&page={page}"
        data = make_api_request(paginated_url)
        if not data:
            break
        results.extend(data)
        page += 1
    return results

# --- Fungsi Utama ---
def generate_org_stats():
    """Mengambil data organisasi, memproses, dan menghasilkan konten markdown."""
    print(f"Memulai pengambilan data untuk organisasi: {ORG_NAME}...")

    # 1. Ambil data dasar organisasi
    org_data = make_api_request(f"https://api.github.com/orgs/{ORG_NAME}")
    # 2. Ambil semua repositori (dengan paginasi)
    print("Mengambil data repositori...")
    repos = fetch_paginated_data(f"https://api.github.com/orgs/{ORG_NAME}/repos")
    
    # Pastikan 'repos' adalah list sebelum diproses lebih lanjut
    if not isinstance(repos, list):
        print(f"Error: Data repositori yang diterima bukan list. Data: {repos}", file=sys.stderr)
        sys.exit(1)

    # 3. Ambil semua anggota (dengan paginasi)
    print("Mengambil data anggota...")
    members = fetch_paginated_data(f"https://api.github.com/orgs/{ORG_NAME}/members")

    # 4. Hitung statistik
    total_stars = sum(repo.get("stargazers_count", 0) for repo in repos)
    
    # Urutkan repositori berdasarkan jumlah bintang dan ambil 3 teratas
    top_repos = sorted(repos, key=lambda r: r.get("stargazers_count", 0), reverse=True)[:3]

    # 5. Bangun konten Markdown
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

# --- Eksekusi Skrip ---
if __name__ == "__main__":
    if not GITHUB_TOKEN:
        print("Error: GITHUB_TOKEN tidak ditemukan. Pastikan workflow memiliki izin yang benar.", file=sys.stderr)
        sys.exit(1)

    stats_content = generate_org_stats()
    
    # Tulis konten ke file output. Workflow akan menggunakan file ini.
    with open(OUTPUT_FILENAME, "w", encoding="utf-8") as f:
        f.write(stats_content)
        
    print(f"Statistik berhasil dibuat dan disimpan di '{OUTPUT_FILENAME}'")

