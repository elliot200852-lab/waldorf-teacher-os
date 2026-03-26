const { execSync } = require('child_process');
const fileId = '1thSMtUtpZe64bgnYqQ02k70aefJ3sHbj6WJXupKxmeQ';
try {
  const cmd = `gws drive files get --params ${JSON.stringify(JSON.stringify({ fileId, fields: 'parents' }))}`;
  const out = execSync(cmd).toString();
  console.log(out);
} catch (e) {
  console.error(e.message);
}
