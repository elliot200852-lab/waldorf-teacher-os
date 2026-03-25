const { execSync } = require('child_process');
const fs = require('fs');

const fileName = '114學年度實驗教育計畫結案報告_自動生成v2';
const parentFolderId = '1ToeOOhrGXU49ucqg5q_ScRZJPf8XLS2j';

const metadata = {
    name: fileName,
    mimeType: 'application/vnd.google-apps.document',
    parents: [parentFolderId]
};

const metadataStr = JSON.stringify(metadata).replace(/"/g, '\\"');
const cmd = `gws drive files create --file report.html --json "${metadataStr}"`;

console.log(`Running: ${cmd}`);

try {
    const output = execSync(cmd, { encoding: 'utf8' });
    console.log('Success!');
    console.log(output);
} catch (error) {
    console.error(`Error: ${error.message}`);
    if (error.stderr) console.error(`Stderr: ${error.stderr}`);
}
