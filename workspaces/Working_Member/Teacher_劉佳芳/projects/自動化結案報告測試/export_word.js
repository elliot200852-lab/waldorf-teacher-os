const { execSync } = require('child_process');
const fs = require('fs');

const finalFolderId = '1ToeOOhrGXU49ucqg5q_ScRZJPf8XLS2j';
const htmlFile = 'C:/Users/user/waldorf-teacher-os/workspaces/Working_Member/Teacher_劉佳芳/projects/自動化結案報告測試/114學年度實驗教育計畫結案報告_最新版.html';
const docName = '114學年度實驗教育計畫結案報告_自動生成';
const wordFile = 'C:/Users/user/waldorf-teacher-os/workspaces/Working_Member/Teacher_劉佳芳/projects/自動化結案報告測試/114學年度實驗教育計畫結案報告_自動生成.docx';

function runCmd(cmd) {
  return execSync(cmd).toString();
}

try {
  console.log('--- Step 1: Converting HTML to Google Docs ---');
  if (!fs.existsSync(htmlFile)) {
    throw new Error(`HTML file not found: ${htmlFile}`);
  }
  
  const createDocParams = {
    name: docName,
    mimeType: 'application/vnd.google-apps.document',
    parents: [finalFolderId] // Optional: Create directly in the folder if possible, but let's just create and then we'll export it.
  };
  
  const createCmd = `gws drive files create --upload "${htmlFile}" --upload-content-type "text/html" --json ${JSON.stringify(JSON.stringify(createDocParams))} --format json`;
  
  const docOut = runCmd(createCmd);
  const docResult = JSON.parse(docOut);
  const googleDocId = docResult.id;
  console.log(`Created Google Doc with ID: ${googleDocId}`);
  
  console.log('\n--- Step 2: Exporting Google Doc to Word (.docx) ---');
  const exportMime = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document';
  const exportParams = { fileId: googleDocId, mimeType: exportMime };
  const exportCmd = `gws drive files export --params ${JSON.stringify(JSON.stringify(exportParams))} --output "${wordFile}"`;
  runCmd(exportCmd);
  console.log(`Exported Word document to: ${wordFile}`);
  
  console.log('\n--- Step 3: Uploading Word (.docx) to Target Folder ---');
  const uploadParams = {
    name: `${docName}.docx`,
    parents: [finalFolderId]
  };
  
  const uploadCmd = `gws drive files create --upload "${wordFile}" --upload-content-type "${exportMime}" --json ${JSON.stringify(JSON.stringify(uploadParams))} --format json`;
  const uploadOut = runCmd(uploadCmd);
  const uploadResult = JSON.parse(uploadOut);
  const finalId = uploadResult.id;
  console.log(`Uploaded final Word File ID: ${finalId}`);
  console.log(`https://drive.google.com/file/d/${finalId}/view`);
  
} catch (err) {
  console.error('Error occurred:', err.message);
  if (err.stdout) console.error('Stdout:', err.stdout.toString());
  if (err.stderr) console.error('Stderr:', err.stderr.toString());
}
