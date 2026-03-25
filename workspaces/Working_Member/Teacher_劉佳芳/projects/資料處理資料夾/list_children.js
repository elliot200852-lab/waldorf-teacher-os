const { execSync } = require('child_process');
const fs = require('fs');

const parentId = '1_rWOMWUxQVA9LyBO1Ehf2sUHbIGbOVjK';
const params = {
    q: `'${parentId}' in parents`
};

const paramsStr = JSON.stringify(params).replace(/"/g, '\\"');
const cmd = `gws drive files list --params "${paramsStr}"`;
console.log(`Running: ${cmd}`);

try {
    const output = execSync(cmd, { encoding: 'utf8' });
    console.log(output);
    fs.writeFileSync('children_list.json', output);
} catch (error) {
    console.error(`Error: ${error.message}`);
}
