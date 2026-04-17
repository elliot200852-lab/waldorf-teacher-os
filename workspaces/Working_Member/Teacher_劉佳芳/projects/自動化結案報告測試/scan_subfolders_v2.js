const { execSync } = require('child_process');
const fs = require('fs');
const folders = [
  { name: '尤清1203研習', id: '10UrIo8pUXtB3PEgmKnxdbCySVuwzz5fc' },
  { name: '12月研習', id: '18YnR8vR4Nl4MEbobJu_WzDBH0iU2YVAQ' }
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

fs.writeFileSync('drive_scan_result.txt', result, 'utf8');
console.log('Done.');
