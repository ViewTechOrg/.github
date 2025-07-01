const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');

async function run() {
  try {
    // Mengambil token dari environment variable yang disediakan oleh workflow
    const token = process.env.GITHUB_TOKEN;
    if (!token) {
      core.setFailed('GITHUB_TOKEN tidak ditemukan. Pastikan variabel lingkungan GITHUB_TOKEN telah diatur.');
      return;
    }
    const octokit = github.getOctokit(token);

    // Konfigurasi
    const ORG_NAME = 'ViewTechOrg';
    const REPO_LIMIT = 3;
    const README_PATH = path.join(process.env.GITHUB_WORKSPACE, 'profile/README.md');
    const START_TAG = '<!--START_SECTION:top-repos-->';
    const END_TAG = '<!--END_SECTION:top-repos-->';

    console.log(`Memperbarui repositori populer untuk organisasi: ${ORG_NAME}`);

    // Ambil detail organisasi untuk mendapatkan URL avatar
    const { data: org } = await octokit.rest.orgs.get({ org: ORG_NAME });
    const avatarUrl = org.avatar_url;
    const orgUrl = org.html_url;

    // Ambil semua repositori publik
    const repos = await octokit.paginate(octokit.rest.repos.listForOrg, {
      org: ORG_NAME,
      type: 'public',
    });

    // Urutkan berdasarkan bintang dan ambil 3 teratas
    const sortedRepos = repos
      .filter(repo => !repo.fork)
      .sort((a, b) => b.stargazers_count - a.stargazers_count)
      .slice(0, REPO_LIMIT);

    console.log(`Menemukan ${sortedRepos.length} repositori teratas.`);
    
    // Buat "kotak" HTML untuk setiap repositori
    const repoBoxesHtml = sortedRepos.map(repo => {
      const description = repo.description || 'Tidak ada deskripsi.';
      return `<table>
  <tr>
    <td>
      <a href="${repo.html_url}" target="_blank"><b>${repo.name}</b></a> (⭐ ${repo.stargazers_count})
      <br>
      ${description}
    </td>
  </tr>
</table>`;
    }).join('\n');

    // Gabungkan avatar dan kotak repositori
    const finalHtml = `<p align="center">
  <a href="${orgUrl}"><img src="${avatarUrl}&s=100" width="100px;" alt="Avatar Organisasi"/></a>
</p>

${repoBoxesHtml}`;

    // Baca, modifikasi, dan tulis kembali file README.md
    const readmeContent = fs.readFileSync(README_PATH, 'utf-8');
    const startTagIndex = readmeContent.indexOf(START_TAG);
    const endTagIndex = readmeContent.indexOf(END_TAG);

    if (startTagIndex === -1 || endTagIndex === -1) {
      throw new Error(`Tag ${START_TAG} atau ${END_TAG} tidak ditemukan di README.`);
    }

    const newReadme = [
      readmeContent.slice(0, startTagIndex + START_TAG.length),
      '\n',
      finalHtml,
      '\n',
      readmeContent.slice(endTagIndex)
    ].join('');

    fs.writeFileSync(README_PATH, newReadme);
    console.log('Berhasil memperbarui bagian repositori populer di README.');

  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
