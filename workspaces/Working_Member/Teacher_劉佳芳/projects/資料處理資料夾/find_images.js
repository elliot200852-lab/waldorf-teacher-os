const fs = require('fs');
const data = JSON.parse(fs.readFileSync('all_研習_files.json', 'utf8'));
data.forEach(fold => {
    fold.files.forEach(f => {
        if(f.mimeType.startsWith('image/')) {
            console.log(`Image in ${fold.folderId}: ${f.name} (ID: ${f.id})`);
        }
    });
});
