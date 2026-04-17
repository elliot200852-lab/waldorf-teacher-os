const { execSync } = require('child_process');

try {
  const fileId = '1Chq2Akz6EEdYaIkYOKRMKd9AIGdZVwOKlrKDDePNG4ZM';
  const mimeType = 'application/pdf';
  // Try passing fileId as part of params since it's a path parameter in Google Drive API
  const params = JSON.stringify({ fileId, mimeType });
  const cmd = `gws drive files export --params ${JSON.stringify(params)} -o test.pdf`;
  console.log("Running:", cmd);
  execSync(cmd);
  console.log("Success!");
} catch (e) {
  console.error("Failed:", e.message);
  if (e.stdout) console.error(e.stdout.toString());
  if (e.stderr) console.error(e.stderr.toString());
}
