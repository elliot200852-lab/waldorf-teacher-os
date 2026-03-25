const { execSync } = require('child_process');
const parentFolderId = '1ToeOOhrGXU49ucqg5q_ScRZJPf8XLS2j';
const fileName = '114學年實驗教育計畫結案報告_劉佳芳_最終彙整版';

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
}
