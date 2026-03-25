const fs = require('fs');
const data = JSON.parse(fs.readFileSync('all_研習_files.json', 'utf8'));

data.forEach(folder => {
    console.log(`Folder: ${folder.folderId}`);
    folder.files.forEach(f => {
        console.log(`  - [${f.mimeType}] ${f.name} (ID: ${f.id})`);
    });
});
