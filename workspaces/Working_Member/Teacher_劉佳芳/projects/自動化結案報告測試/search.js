const { execSync } = require('child_process');
const q = `name contains '114學年度實驗教育計畫辦理研習'`;
const params = JSON.stringify({ q });
const cmd = `gws drive files list --params ${JSON.stringify(params)} --format json`;
try {
  const result = execSync(cmd).toString();
  console.log(result);
} catch (e) {
  console.error("Error executing command:", e.message);
  if (e.stdout) console.error("Stdout:", e.stdout.toString());
  if (e.stderr) console.error("Stderr:", e.stderr.toString());
}
