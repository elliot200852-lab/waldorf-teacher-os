const { execSync } = require('child_process');
const fs = require('fs');

const params = {
    q: "name = '114學年度實驗教育計畫辦理研習' and mimeType = 'application/vnd.google-apps.folder'"
};

const paramsStr = JSON.stringify(params).replace(/"/g, '\\"');
const cmd = `gws drive files list --params "${paramsStr}"`;
console.log(`Running: ${cmd}`);

try {
    const output = execSync(cmd, { encoding: 'utf8' });
    console.log(output);
    fs.writeFileSync('folder_found.json', output);
} catch (error) {
    console.error(`Error: ${error.message}`);
    console.error(`Stderr: ${error.stderr}`);
}
