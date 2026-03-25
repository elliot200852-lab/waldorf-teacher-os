const { execSync } = require('child_process');
const fs = require('fs');

const folders = [
    '10UrIo8pUXtB3PEgmKnxdbCySVuwzz5fc',
    '1QYNPHghcdu5MWtDjTtEI0rzfYimhSNBs',
    '18YnR8vR4Nl4MEbobJu_WzDBH0iU2YVAQ'
];

let allChildren = [];

folders.forEach(id => {
    const params = { q: `'${id}' in parents` };
    const paramsStr = JSON.stringify(params).replace(/"/g, '\\"');
    const cmd = `gws drive files list --params "${paramsStr}"`;
    try {
        const output = execSync(cmd, { encoding: 'utf8' });
        allChildren.push({ folderId: id, files: JSON.parse(output).files });
    } catch (e) {}
});

fs.writeFileSync('all_研習_files.json', JSON.stringify(allChildren, null, 2));
