const { execSync } = require('child_process');
const fs = require('fs');

const folderId = '1_rWOMWUxQVA9LyBO1Ehf2sUHbIGbOVjK';
const files = [
  {
    local: 'C:/Users/user/waldorf-teacher-os/workspaces/Working_Member/Teacher_劉佳芳/projects/自動化結案報告測試/report_final.md',
    remote: '114學年度實驗教育計畫結案報告_劉佳芳.md',
    mime: 'text/markdown'
  },
  {
    local: 'C:/Users/user/waldorf-teacher-os/workspaces/Working_Member/Teacher_劉佳芳/projects/自動化結案報告測試/114學年度實驗教育計畫結案報告_最新版.html',
    remote: '114學年度實驗教育計畫結案報告_劉佳芳_美化版.html',
    mime: 'text/html'
  },
  {
    local: 'C:/Users/user/waldorf-teacher-os/workspaces/Working_Member/Teacher_劉佳芳/projects/自動化結案報告測試/114學年度實驗教育計畫結案報告_最新版.pdf',
    remote: '114學年度實驗教育計畫結案報告_劉佳芳_美化版.pdf',
    mime: 'application/pdf'
  }
];

files.forEach(f => {
  if (!fs.existsSync(f.local)) {
    console.warn(`File not found: ${f.local}`);
    return;
  }
  
  const body = {
    name: f.remote,
    parents: [folderId]
  };
  
  const cmd = `gws drive files create --upload "${f.local}" --upload-content-type "${f.mime}" --json ${JSON.stringify(JSON.stringify(body))} --format json`;
  
  console.log(`Uploading ${f.remote}...`);
  try {
    const out = execSync(cmd).toString();
    const result = JSON.parse(out);
    console.log(`Success! File ID: ${result.id}`);
  } catch (err) {
    console.error(`Error uploading ${f.remote}:`, err.message);
    if (err.stdout) console.error(err.stdout.toString());
    if (err.stderr) console.error(err.stderr.toString());
  }
});
