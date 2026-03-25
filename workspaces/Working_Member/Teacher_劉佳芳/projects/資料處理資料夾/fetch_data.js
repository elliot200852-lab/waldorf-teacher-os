const { execSync } = require('child_process');
const fs = require('fs');

const folders = [
    { name: 'Susan', id: '10UrIo8pUXtB3PEgmKnxdbCySVuwzz5fc' },
    { name: 'MountainDeer', id: '1QYNPHghcdu5MWtDjTtEI0rzfYimhSNBs' },
    { name: 'YuQing', id: '18YnR8vR4Nl4MEbobJu_WzDBH0iU2YVAQ' }
];

folders.forEach(folder => {
    const params = { q: `'${folder.id}' in parents` };
    const paramsStr = JSON.stringify(params).replace(/"/g, '\\"');
    const cmd = `gws drive files list --params "${paramsStr}"`;
    try {
        const output = execSync(cmd, { encoding: 'utf8' });
        const files = JSON.parse(output).files;
        files.forEach(f => {
            let outputName = `${folder.name}_${f.name.replace(/\//g, '_')}`;
            if (f.mimeType === 'application/vnd.google-apps.document' || f.mimeType === 'application/vnd.google-apps.spreadsheet') {
                 console.log(`Exporting ${f.name} (ID: ${f.id})`);
                 const exportParams = { fileId: f.id, mimeType: 'text/plain' };
                 const exportParamsStr = JSON.stringify(exportParams).replace(/"/g, '\\"');
                 const exportCmd = `gws drive files export --params "${exportParamsStr}" -o "${outputName}.txt"`;
                 try {
                     execSync(exportCmd);
                 } catch (e) {
                     console.error(`Failed to export ${f.name}: ${e.message}`);
                 }
            } else if (f.mimeType === 'text/plain' || f.mimeType === 'text/markdown') {
                 console.log(`Downloading ${f.name} (ID: ${f.id})`);
                 const getParams = { fileId: f.id, alt: 'media' };
                 const getParamsStr = JSON.stringify(getParams).replace(/"/g, '\\"');
                 const getCmd = `gws drive files get --params "${getParamsStr}" -o "${outputName}"`;
                 try {
                     execSync(getCmd);
                 } catch (e) {
                     console.error(`Failed to download ${f.name}: ${e.message}`);
                 }
            }
        });
    } catch (e) {}
});
