const { execSync } = require('child_process');
const fs = require('fs');
const folders = [
  { name: '山鹿老師戶外教育研習', id: '1QYNPHghcdu5MWtDjTtEI0rzfYimhSNBs' },
  { name: 'Sally Davison研習', id: '1BasJtLiTXJAzmqLgE9mD3dKCkRTLqK-x' }
];

let result = '';

folders.forEach(folder => {
  result += `--- Scanning ${folder.name} (${folder.id}) ---\n`;
  try {
    const q = `'${folder.id}' in parents and trashed = false`;
    const params = JSON.stringify({ q });
    const cmd = `npx -y @googleworkspace/cli drive files list --params ${JSON.stringify(params)}`;
    const out = JSON.parse(execSync(cmd).toString());
    out.files.forEach(f => {
      result += `- ${f.name} (ID: ${f.id}) [${f.mimeType}]\n`;
    });
  } catch (e) {
    result += `Error scanning ${folder.name}: ${e.message}\n`;
  }
});

fs.writeFileSync('outdoor_sally_scan.txt', result, 'utf8');
console.log('Done.');
