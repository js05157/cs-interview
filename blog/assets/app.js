(() => {
  const root = document.documentElement;
  const toggle = document.querySelector('#theme-toggle');
  let saved;
  try { saved = localStorage.getItem('cs-theme'); } catch (_) { /* storage optional */ }
  root.dataset.theme = saved || (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const label = () => toggle.setAttribute('aria-label', root.dataset.theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환');
  label();
  toggle.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('cs-theme', root.dataset.theme); } catch (_) { /* optional */ }
    label();
  });
  const toc = document.querySelector('#toc');
  if (toc) {
    const fragment = document.createDocumentFragment();
    document.querySelectorAll('#post-content h2, #post-content h3').forEach((heading, index) => {
      if (!heading.id) heading.id = `section-${index}`;
      const link = document.createElement('a');
      link.href = `#${heading.id}`;
      link.textContent = heading.textContent;
      if (heading.tagName === 'H3') link.className = 'toc-sub';
      fragment.append(link);
    });
    toc.append(fragment);
  }
  const input = document.querySelector('#search');
  const panel = document.querySelector('#search-panel');
  let posts, timer, sequence = 0;
  input.addEventListener('input', () => {
    clearTimeout(timer);
    const current = ++sequence;
    const term = input.value.trim().toLocaleLowerCase('ko');
    if (!term) { panel.hidden = true; return; }
    timer = setTimeout(async () => {
      try {
        if (!posts) {
          const response = await fetch(document.body.dataset.searchUrl);
          if (!response.ok) throw new Error('search unavailable');
          posts = await response.json();
        }
        if (current !== sequence) return;
        const matches = posts.filter(p => `${p.title} ${p.category} ${p.text}`.toLocaleLowerCase('ko').includes(term)).slice(0, 15);
        panel.replaceChildren();
        if (!matches.length) panel.textContent = '검색 결과가 없습니다.';
        matches.forEach(p => {
          const link = document.createElement('a');
          link.href = p.url;
          link.textContent = `${p.title} · ${p.date}`;
          panel.append(link);
        });
      } catch (_) { if (current === sequence) panel.textContent = '검색을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.'; }
      if (current === sequence) panel.hidden = false;
    }, 150);
  });
  document.addEventListener('keydown', e => { if (e.key === 'Escape') { sequence++; panel.hidden = true; input.blur(); } });
})();
