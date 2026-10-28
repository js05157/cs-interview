(() => {
  'use strict';
  const root = document.documentElement;
  const toggle = document.querySelector('#theme-toggle');
  let saved;
  try { saved = localStorage.getItem('blog-theme') || localStorage.getItem('cs-theme'); } catch (_) {}
  root.dataset.theme = ['dark','light'].includes(saved) ? saved : (matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light');
  const themeLabel = () => toggle?.setAttribute('aria-label', root.dataset.theme === 'dark' ? '라이트 모드로 전환' : '다크 모드로 전환');
  themeLabel();
  toggle?.addEventListener('click', () => {
    root.dataset.theme = root.dataset.theme === 'dark' ? 'light' : 'dark';
    try { localStorage.setItem('blog-theme',root.dataset.theme); } catch (_) {}
    themeLabel();
  });
  document.querySelectorAll('[data-close-dialog]').forEach(button => button.addEventListener('click',() => button.closest('dialog').close()));
  document.querySelectorAll('dialog').forEach(dialog => dialog.addEventListener('click',e => { if(e.target === dialog) { const r=dialog.getBoundingClientRect(); if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom) dialog.close(); } }));
  const searchDialog = document.querySelector('#search-dialog');
  const search = document.querySelector('#search');
  const results = document.querySelector('#search-results');
  const openSearch = () => { searchDialog.showModal(); search.focus(); };
  document.querySelector('#search-toggle')?.addEventListener('click',openSearch);
  document.querySelectorAll('[data-open-search]').forEach(b => b.addEventListener('click',openSearch));
  document.addEventListener('keydown',e => {
    if(e.key === '/' && !/INPUT|TEXTAREA|SELECT/.test(e.target.tagName) && !e.target.isContentEditable && !document.querySelector('dialog[open]')) {e.preventDefault();openSearch();}
  });
  let posts, sequence=0, timer;
  search?.addEventListener('input',() => {
    clearTimeout(timer);const current=++sequence;const term=search.value.trim().toLocaleLowerCase('ko');
    results.replaceChildren();if(!term) return;
    timer=setTimeout(async () => {
      try {
        if(!posts) { const response=await fetch(document.body.dataset.searchUrl);if(!response.ok)throw new Error();posts=await response.json(); }
        if(current!==sequence)return;
        const matches=posts.filter(p=>(p.title+' '+p.kind_label+' '+p.text).toLocaleLowerCase('ko').includes(term)).slice(0,20);
        results.replaceChildren();
        if(!matches.length) {const p=document.createElement('p');p.textContent='검색 결과가 없습니다.';results.append(p);}
        matches.forEach(p => { const link=document.createElement('a');link.href=p.url;const title=document.createElement('strong');title.textContent=p.title;const meta=document.createElement('span');meta.textContent=p.date+' · '+(p.kind_label||'개발 기록');link.append(title,meta);results.append(link); });
      } catch (_) {if(current===sequence)results.textContent='검색을 불러오지 못했습니다. 잠시 후 다시 시도해 주세요.';}
    },100);
  });
  const filters=[...document.querySelectorAll('[data-filter]')],rows=[...document.querySelectorAll('#all-posts .post-row')];
  function filter(kind) {
    if(!filters.some(b=>b.dataset.filter===kind))kind='all';
    filters.forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.filter===kind)));
    rows.forEach(row=>row.hidden=kind!=='all'&&row.dataset.kind!==kind);
    const empty=document.querySelector('#filter-empty');if(empty)empty.hidden=rows.some(row=>!row.hidden);
  }
  filters.forEach(b=>b.addEventListener('click',()=>{filter(b.dataset.filter);const url=new URL(location.href);if(b.dataset.filter==='all')url.searchParams.delete('type');else url.searchParams.set('type',b.dataset.filter);history.replaceState(null,'',url);}));
  if(filters.length)filter(new URL(location.href).searchParams.get('type')||'all');
  const toc=document.querySelector('#toc');
  if(toc) {
    document.querySelectorAll('#post-content h2,#post-content h3').forEach((heading,i) => {
      if(!heading.id)heading.id='section-'+i;
      const link=document.createElement('a');link.href='#'+heading.id;link.textContent=heading.textContent;
      if(heading.tagName==='H3')link.className='toc-sub';toc.append(link);
    });
    if(!toc.children.length)toc.closest('details').hidden=true;
  }
  document.querySelectorAll('.prose pre').forEach(pre=>{
    const frame=document.createElement('div');frame.className='code-frame';pre.before(frame);frame.append(pre);
    const button=document.createElement('button');button.type='button';button.className='copy-code';button.textContent='복사';button.setAttribute('aria-label','코드 복사');
    button.addEventListener('click',async()=>{
      try {await navigator.clipboard.writeText(pre.querySelector('code')?.textContent||pre.textContent);button.textContent='복사됨';}
      catch (_) {const range=document.createRange();range.selectNodeContents(pre);const selection=window.getSelection();selection.removeAllRanges();selection.addRange(range);button.textContent='선택됨';}
      setTimeout(()=>button.textContent='복사',2000);
    });frame.append(button);
  });
  const imageDialog=document.querySelector('#image-dialog');
  document.querySelectorAll('#post-content img').forEach(img=>{
    if(img.closest('a'))return;
    const button=document.createElement('button');button.type='button';button.className='image-expand';button.setAttribute('aria-label',(img.alt||'본문 이미지')+' 확대');
    img.before(button);button.append(img);
    button.addEventListener('click',()=>{const expanded=document.querySelector('#expanded-image');expanded.src=img.currentSrc||img.src;expanded.alt=img.alt;document.querySelector('#expanded-caption').textContent=img.alt;imageDialog.showModal();});
  });
  const cells=[...document.querySelectorAll('.activity-day')],detail=document.querySelector('#activity-detail');
  function showDay(cell){if(detail)detail.textContent=cell.dataset.date+' · 기여 '+cell.dataset.count+'회';}
  const activityScroll=document.querySelector('.activity-scroll');
  if(activityScroll)activityScroll.scrollLeft=activityScroll.scrollWidth;
  cells.forEach(cell=>{
    cell.addEventListener('mouseenter',()=>showDay(cell));cell.addEventListener('focus',()=>showDay(cell));
    cell.addEventListener('keydown',e=>{
      const jumps={ArrowLeft:-7,ArrowRight:7,ArrowUp:-1,ArrowDown:1};let index=cells.indexOf(cell);
      if(e.key in jumps)index+=jumps[e.key];else if(e.key==='Home')index=0;else if(e.key==='End')index=cells.length-1;else return;
      e.preventDefault();index=Math.max(0,Math.min(cells.length-1,index));cells.forEach(c=>c.tabIndex=-1);cells[index].tabIndex=0;cells[index].focus();
    });
  });
})();
