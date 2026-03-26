const { execSync } = require('child_process');
const fs = require('fs');

const folderId = '1_rWOMWUxQVA9LyBO1Ehf2sUHbIGbOVjK';
const q = `'${folderId}' in parents and trashed = false`;
const params = JSON.stringify({ q });
const cmd = `npx -y @googleworkspace/cli drive files list --params ${JSON.stringify(params)}`;
const out = JSON.parse(execSync(cmd).toString());

fs.writeFileSync('all_children_v2.json', JSON.stringify(out, null, 2), 'utf8');
console.log('Done.');
