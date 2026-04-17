const { execSync } = require('child_process');
const folderId = '1_rWOMWUxQVA9LyBO1Ehf2sUHbIGbOVjK';
const q = `'${folderId}' in parents`;
const params = JSON.stringify({ q });

console.log('--- Scanning Folder ---');
try {
  const cmd = `gws drive files list --params ${JSON.stringify(params)}`;
  const out = execSync(cmd).toString();
  console.log(out);
} catch (e) {
  console.error('Error listing folder:', e.message);
}
