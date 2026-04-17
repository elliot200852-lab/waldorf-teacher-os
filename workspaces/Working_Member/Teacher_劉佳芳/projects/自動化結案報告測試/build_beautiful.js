const fs = require('fs');
const { marked } = require('marked');

// 讀取 report_final.md 作為來源
const mdContent = fs.readFileSync('report_final.md', 'utf8');

// 將 markdown 內容轉換為 HTML
const parsedHtml = marked.parse(mdContent);

const htmlContent = `<!DOCTYPE html>
<html class="spring" lang="zh-TW">
<head>
<meta charset="utf-8"/>
<meta content="width=device-width, initial-scale=1.0" name="viewport"/>
<title>114學年度實驗教育計畫結案報告</title>
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+TC:wght@400;700&family=Playfair+Display:ital,wght@0,400;0,700;1,400&family=Plus+Jakarta+Sans:wght@400;500;600&family=Noto+Sans+TC:wght@400;500;700&display=swap" rel="stylesheet"/>
<link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap" rel="stylesheet"/>
<script src="https://cdn.tailwindcss.com?plugins=forms,typography,container-queries"></script>
<script>
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        "primary": "var(--primary)",
        "secondary": "var(--secondary)",
        "accent": "var(--accent)",
        "on-primary": "#ffffff",
        "on-surface": "var(--on-surface)",
        "on-surface-variant": "var(--on-surface-variant)",
        "surface": "var(--bg-wash-1)",
        "surface-container": "var(--bg-wash-2)",
        "surface-container-low": "var(--bg-wash-3)",
        "outline-variant": "var(--outline-variant)",
      },
      fontFamily: {
        "headline": ["Playfair Display", "Noto Serif TC", "Georgia", "serif"],
        "body": ["Plus Jakarta Sans", "Noto Sans TC", "PingFang TC", "Microsoft JhengHei", "sans-serif"],
        "label": ["Plus Jakarta Sans", "Noto Sans TC", "sans-serif"],
      },
    },
  },
}
</script>
<style>
html.spring {
  --primary: #6B7F5E;
  --secondary: #9B7BB0;
  --accent: #D4A574;
  --bg-wash-1: #F0F5EB;
  --bg-wash-2: #E8F0D8;
  --bg-wash-3: #F2E8F5;
  --on-surface: #2A3325;
  --on-surface-variant: #4A5544;
  --outline-variant: #C4D1B8;
  --season-icon: "eco";
  --gradient-body: radial-gradient(circle at top left, #F0F5EB 0%, #E8F0D8 40%, #F2E8F5 100%);
  --gradient-header: linear-gradient(135deg, #6B7F5E 0%, #9B7BB0 100%);
}
body { background: var(--gradient-body); min-height: 100vh; }
.watercolor-wash-header {
  background: var(--gradient-header);
  mask-image: url("data:image/svg+xml;utf8,<svg viewBox='0 0 100 100' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'><path d='M0,0 C20,10 40,-5 60,5 C80,15 100,0 100,0 L100,90 C80,100 60,85 40,95 C20,105 0,90 0,90 Z' fill='black'/></svg>");
  -webkit-mask-image: url("data:image/svg+xml;utf8,<svg viewBox='0 0 100 100' preserveAspectRatio='none' xmlns='http://www.w3.org/2000/svg'><path d='M0,0 C20,10 40,-5 60,5 C80,15 100,0 100,0 L100,90 C80,100 60,85 40,95 C20,105 0,90 0,90 Z' fill='black'/></svg>");
  mask-size: 100% 100%; -webkit-mask-size: 100% 100%;
}
.hand-drawn-border {
  border: 2px solid var(--primary);
  border-radius: 255px 15px 225px 15px/15px 225px 15px 255px;
}
.botanical-overlay {
  position: fixed; top: 0; left: 0; width: 100%; height: 100%;
  pointer-events: none; opacity: 0.06; z-index: 50;
}
.drop-cap::first-letter {
  font-size: 3.5rem; font-family: "Playfair Display", "Noto Serif TC", serif;
  float: left; margin-right: 0.75rem; line-height: 1; color: var(--primary);
}
@media print {
  body { background: white !important; color: #1C1C18 !important; min-height: auto !important; }
  .botanical-overlay { display: none !important; }
  .watercolor-wash-header {
    background: var(--primary) !important; mask-image: none !important; -webkit-mask-image: none !important; border-radius: 0 !important;
  }
  header { display: none !important; }
  main { max-width: 100% !important; padding: 0 2rem !important; overflow: visible !important; }
  .hand-drawn-border { border-radius: 4px !important; }
  .hand-drawn-border, blockquote { break-inside: avoid; }
  .page-break { page-break-after: always; break-after: page; }
}
table { width: 100%; border-collapse: collapse; background: white; margin-top: 10px; margin-bottom: 20px; }
th, td { border: 1px solid var(--outline-variant); padding: 8px 12px; }
th { background-color: var(--primary); color: white; }
tr:nth-child(even) { background-color: var(--bg-wash-1); }
</style>
</head>
<body class="font-body text-[var(--on-surface)] selection:bg-[var(--secondary)]/20">
<div class="botanical-overlay"></div>
<header id="site-header" class="sticky top-0 z-40 bg-[var(--bg-wash-1)]/80 backdrop-blur-xl print:hidden transition-opacity duration-300">
  <div class="flex justify-between items-center w-full px-8 py-6 max-w-screen-xl mx-auto">
    <div class="flex items-center gap-3">
      <span class="material-symbols-outlined text-[var(--primary)]" style="font-size: 2rem;">eco</span>
      <h1 class="font-headline text-3xl tracking-wide leading-relaxed text-[var(--primary)]">114學年度實驗教育計畫結案報告</h1>
    </div>
  </div>
  <div class="bg-gradient-to-b from-[var(--outline-variant)] to-transparent h-4 opacity-20"></div>
</header>
<main class="max-w-[900px] mx-auto px-8 py-6 relative overflow-hidden">
  <div class="absolute -top-10 -right-10 opacity-[0.07] rotate-12">
    <span class="material-symbols-outlined text-[12rem] text-[var(--primary)]">eco</span>
  </div>

  <section class="mb-6 text-center">
    <div class="watercolor-wash-header p-5 mb-3 inline-block w-full">
      <h2 class="font-headline text-4xl md:text-5xl text-on-primary leading-tight font-bold italic mb-2">114學年度實驗教育計畫結案報告</h2>
      <p class="text-on-primary/90 font-label tracking-[0.2em] uppercase text-sm">宜蘭縣立慈心華德福教育實驗高級中等學校</p>
    </div>
  </section>

  <!-- Tailwind Typography plugin handles standard markdown output styling properly -->
  <div class="prose prose-stone prose-lg max-w-none text-[var(--on-surface)] leading-[1.6]
    prose-headings:font-headline prose-headings:text-[var(--primary)]
    prose-h3:border-b prose-h3:border-[var(--outline-variant)]/30 prose-h3:pb-1.5
    prose-h4:text-[var(--secondary)] prose-h4:font-bold
    prose-p:text-[18px] prose-li:text-[18px]
    prose-a:text-[var(--primary)] hover:prose-a:text-[var(--secondary)]
  ">
    ${parsedHtml}
  </div>

</main>

<footer class="bg-[var(--bg-wash-1)] w-full border-t border-[var(--outline-variant)]/30 mt-6 pt-6 pb-6 print:hidden">
  <div class="max-w-4xl mx-auto flex flex-col items-center gap-3 px-6 text-center">
    <div class="w-full opacity-15 flex justify-center items-center gap-2 py-2">
      <span class="material-symbols-outlined text-[var(--secondary)]">eco</span>
      <span class="material-symbols-outlined text-[var(--secondary)]">eco</span>
      <span class="material-symbols-outlined text-[var(--secondary)]">eco</span>
    </div>
    <div class="space-y-2">
      <p class="text-[var(--primary)] font-headline italic text-lg">宜蘭縣立慈心華德福教育實驗高級中等學校</p>
    </div>
    <div class="text-[var(--secondary)] font-body text-xs tracking-widest uppercase opacity-60">
      114學年度實驗教育計畫結案報告
    </div>
  </div>
</footer>
</body>
</html>`;

fs.writeFileSync('114學年度實驗教育計畫結案報告_最終版.html', htmlContent, 'utf8');
console.log('Beautiful HTML file successfully generated.');
