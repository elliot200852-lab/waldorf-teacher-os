/* ══════════════════════════════════════════════════════════
   TeacherOS — 展示網站共用互動腳本
   ══════════════════════════════════════════════════════════ */

document.addEventListener('DOMContentLoaded', () => {

  /* ── 導覽列：滾動隱藏/顯示 ── */
  const nav = document.querySelector('.site-nav');
  let lastScroll = 0;
  if (nav) {
    window.addEventListener('scroll', () => {
      const cur = window.pageYOffset;
      if (cur > lastScroll && cur > 120) nav.classList.add('hidden');
      else nav.classList.remove('hidden');
      lastScroll = cur;
    });
  }

  /* ── 導覽列：漢堡選單 ── */
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) {
    toggle.addEventListener('click', () => links.classList.toggle('open'));
    links.querySelectorAll('a').forEach(a =>
      a.addEventListener('click', () => links.classList.remove('open'))
    );
  }

  /* ── 導覽列：當前頁面 Active ── */
  const currentPage = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-links a').forEach(a => {
    const href = a.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      a.classList.add('active');
    }
  });

  /* ── Intersection Observer：進場動畫 ── */
  const reveals = document.querySelectorAll('.reveal');
  if (reveals.length) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    reveals.forEach(el => observer.observe(el));
  }

  /* ── 摺疊面板 ── */
  document.querySelectorAll('.collapse-header').forEach(header => {
    header.addEventListener('click', () => {
      const item = header.closest('.collapse-item');
      item.classList.toggle('open');
    });
  });

  /* ── Tab 切換 ── */
  document.querySelectorAll('.tab-group').forEach(group => {
    const btns = group.querySelectorAll('.tab-btn');
    const panels = group.querySelectorAll('.tab-panel');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        btns.forEach(b => b.classList.remove('active'));
        panels.forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const target = group.querySelector(`#${btn.dataset.tab}`);
        if (target) target.classList.add('active');
      });
    });
  });

  /* ── 平滑回到頂端 ── */
  document.querySelectorAll('a[href="#top"]').forEach(a => {
    a.addEventListener('click', e => {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

});
