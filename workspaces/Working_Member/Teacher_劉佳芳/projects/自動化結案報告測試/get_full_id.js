const { execSync } = require('child_process');
const folderId = '1RxrscjyYJ32_mnp_yM7y3PXSXxw4BPQ7';
const q = `'${folderId}' in parents and trashed = false`;
const params = JSON.stringify({ q });
const cmd = `npx -y @googleworkspace/cli drive files list --params ${JSON.stringify(params)}`;
const out = JSON.parse(execSync(cmd).toString());
out.files.forEach(f => {
  console.log(`FULL_ID: ${f.id} | NAME: ${f.name}`);
});
