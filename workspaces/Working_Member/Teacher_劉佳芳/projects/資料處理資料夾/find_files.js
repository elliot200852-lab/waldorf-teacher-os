const { execSync } = require('child_process');
const fs = require('fs');

const filenames = [
    "113學年度實驗教育計劃成果報告＿20250729 (2)",
    "114學年實驗教育計畫申請書核章版"
];

let results = [];

filenames.forEach(name => {
    const params = {
        q: `name contains '${name}'`
    };
    const paramsStr = JSON.stringify(params).replace(/"/g, '\\"');
    const cmd = `gws drive files list --params "${paramsStr}"`;
    console.log(`Searching for: ${name}`);
    try {
        const output = execSync(cmd, { encoding: 'utf8' });
        results.push(JSON.parse(output));
    } catch (error) {
        console.error(`Error searching for ${name}`);
    }
});

fs.writeFileSync('files_found.json', JSON.stringify(results, null, 2));
console.log('Done.');
