const { execSync } = require('child_process');
const folderId = '1ToeOOhrGXU49ucqg5q_ScRZJPf8XLS2j';
const params = { q: `'${folderId}' in parents` };
const paramsStr = JSON.stringify(params).replace(/"/g, '\\"');
const cmd = `gws drive files list --params "${paramsStr}"`;
try {
    const output = execSync(cmd, { encoding: 'utf8' });
    console.log(output);
} catch (e) {
    console.error(e.message);
}
