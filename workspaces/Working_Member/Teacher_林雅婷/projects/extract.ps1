Expand-Archive -Path "g:\我的雲端硬碟\AI\歐亞非地理備課\塵土、黑金與綠洲--西亞的千年生存戰.docx" -DestinationPath "c:\資料\AI\waldorf-teacher-os\workspaces\Working_Member\Teacher_林雅婷\projects\temp_docx" -Force
$xml = Get-Content "c:\資料\AI\waldorf-teacher-os\workspaces\Working_Member\Teacher_林雅婷\projects\temp_docx\word\document.xml" -Raw
[regex]::Matches($xml, '(?<=<w:t>|<w:t xml:space="preserve">).*?(?=</w:t>)') | ForEach-Object { $_.Value } > "c:\資料\AI\waldorf-teacher-os\workspaces\Working_Member\Teacher_林雅婷\projects\temp_output.txt"
Remove-Item "c:\資料\AI\waldorf-teacher-os\workspaces\Working_Member\Teacher_林雅婷\projects\temp_docx" -Recurse -Force
