const { execSync } = require('child_process');
const parentFolderId = '1ToeOOhrGXU49ucqg5q_ScRZJPf8XLS2j';
const fileName = '114學年度實驗教育計畫：辦理研習結案成果報告 (最終彙整版)';

const cmd = `gws drive +upload --parent ${parentFolderId} report.md`;

console.log(`Running: ${cmd}`);

try {
    const output = execSync(cmd, { encoding: 'utf8' });
    console.log('Success!');
    console.log(output);
} catch (error) {
    console.error(`Error: ${error.message}`);
    if (error.stderr) console.error(`Stderr: ${error.stderr}`);
}
