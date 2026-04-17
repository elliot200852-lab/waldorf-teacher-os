const fs = require('fs');
const { marked } = require('marked');

const mdContent = fs.readFileSync('report_final.md', 'utf8');
const cssContent = fs.readFileSync('style.css', 'utf8');

const htmlContent = `<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>114學年度實驗教育計畫結案報告</title>
<style>
${cssContent}
</style>
</head>
<body>
${marked.parse(mdContent)}
</body>
</html>`;

fs.writeFileSync('114學年度實驗教育計畫結案報告_劉佳芳.html', htmlContent, 'utf8');
console.log('HTML file successfully generated.');
