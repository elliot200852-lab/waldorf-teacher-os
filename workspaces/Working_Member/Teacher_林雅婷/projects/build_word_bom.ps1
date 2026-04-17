$files = @(
    "c:\資料\AI\waldorf-teacher-os\workspaces\Working_Member\Teacher_林雅婷\projects\第一天_非洲地形故事與題庫.md",
    "c:\資料\AI\waldorf-teacher-os\workspaces\Working_Member\Teacher_林雅婷\projects\第二天_非洲氣候農業故事與題庫.md",
    "c:\資料\AI\waldorf-teacher-os\workspaces\Working_Member\Teacher_林雅婷\projects\第三天_非洲礦業人文故事與題庫.md"
)

$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Add()
$selection = $word.Selection

$doc.Content.Font.Name = "微軟正黑體"
$doc.Content.Font.Size = 12

# Add Page Numbers to Footer
$footer = $doc.Sections.Item(1).Footers.Item(1)
$pageNumbers = $footer.PageNumbers
$pageNumbers.Add(1, $true) | Out-Null

for ($i = 0; $i -lt $files.Length; $i++) {
    $content = Get-Content -Path $files[$i] -Encoding UTF8
    
    foreach ($line in $content) {
        if ([string]::IsNullOrWhiteSpace($line) -or $line.TrimEnd() -match "^---$") {
            continue
        }
        
        $selection.Font.Name = "微軟正黑體"
        
        $text = $line.TrimEnd(" `t")
        
        if ($text.StartsWith("### ")) {
            $selection.Font.Size = 16
            $selection.Font.Bold = 1
            $selection.TypeText($text.Substring(4))
            $selection.TypeParagraph()
        } elseif ($text.StartsWith("## ")) {
            $selection.Font.Size = 18
            $selection.Font.Bold = 1
            $selection.TypeText($text.Substring(3))
            $selection.TypeParagraph()
        } elseif ($text.StartsWith("# ")) {
            $selection.Font.Size = 20
            $selection.Font.Bold = 1
            $selection.TypeText($text.Substring(2))
            $selection.TypeParagraph()
        } else {
            $selection.Font.Size = 12
            
            if ($text.Contains("**")) {
                $parts = $text -split "\*\*"
                for ($j = 0; $j -lt $parts.Length; $j++) {
                    if ($j % 2 -eq 1) {
                        $selection.Font.Bold = 1
                    } else {
                        $selection.Font.Bold = 0
                    }
                    if ($parts[$j] -ne "") {
                        $selection.TypeText($parts[$j])
                    }
                }
            } else {
                $selection.Font.Bold = 0
                $selection.TypeText($text)
            }
            $selection.TypeParagraph()
        }
        $selection.Font.Bold = 0
    }
    
    if ($i -lt ($files.Length - 1)) {
        $selection.InsertBreak(7) # wdPageBreak = 7
    }
}

$savePath = "g:\我的雲端硬碟\AI\歐亞非地理備課\非洲三日故事綜合講義.docx"
$doc.SaveAs([ref]$savePath, [ref]16)
$doc.Close([ref]$false)
$word.Quit()
[System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null
echo "Word Document Created!"
