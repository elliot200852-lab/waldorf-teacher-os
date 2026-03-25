const { execSync } = require('child_process');
const fs = require('fs');

const fileId = '1y_CBAS2J2CcjW1UEDmT-ua0Xek3MnhhD';
const outputName = 'report_ref.pdf';

const params = { alt: 'media' };
const paramsStr = JSON.stringify(params).replace(/"/g, '\\"');
const cmd = `gws drive files get ${fileId} --params "${paramsStr}"`;

console.log(`Downloading: ${fileId}`);
try {
    // gws might output the binary to stdout. We need to capture it.
    // However, execSync might have trouble with large binary buffers.
    // Let's try to redirect in the shell instead, but using node to build the cmd.
    const fullCmd = `${cmd} > ${outputName}`;
    execSync(fullCmd);
    console.log(`Saved to ${outputName}`);
} catch (error) {
    console.error(`Error: ${error.message}`);
}
