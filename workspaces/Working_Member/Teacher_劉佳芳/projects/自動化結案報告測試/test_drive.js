const { execSync } = require('child_process');
const folderId = '1_rWOMWUxQVA9LyBO1Ehf2sUHbIGbOVjK';
const cmd = `npx -y @googleworkspace/cli drive files list --params "{\\"q\\": \\"\\'${folderId}\\' in parents\\"}" --format json`;
try {
  console.log("Running command:", cmd);
  const result = execSync(cmd, { encoding: 'utf-8' });
  console.log(result);
} catch (e) {
  console.error("Error:", e.stdout || e.message);
}
