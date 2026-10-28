(() => {
  'use strict';
  const form=document.querySelector('#compose-form');if(!form)return;
  const status=document.querySelector('#editor-status'),preview=document.querySelector('#markdown-preview');
  const md=window.markdownit ? window.markdownit({html:false,linkify:true,typographer:false}) : null;
  const key='personal-blog-draft';
  const today=new Intl.DateTimeFormat('sv-SE',{timeZone:'Asia/Seoul'}).format(new Date());
  form.elements.date.value=today;
  try {const draft=JSON.parse(sessionStorage.getItem(key)||'null');if(draft)Object.keys(draft).forEach(k=>{if(form.elements[k])form.elements[k].value=draft[k];});} catch (_) {}
  function values(){return {title:form.elements.title.value.trim(),date:form.elements.date.value,kind:form.elements.kind.value,tags:form.elements.tags.value,published:form.elements.published.value,body:form.elements.body.value};}
  function update() {const v=values();if(md)preview.innerHTML=md.render(v.body);else preview.textContent=v.body;try{sessionStorage.setItem(key,JSON.stringify(v));}catch(_){}}
  form.addEventListener('input',update);update();
  function draft() {
    const v=values();if(!v.title||!v.date||!v.body.trim())throw new Error('제목·날짜·본문을 입력해 주세요.');
    if(!['cs','development','project','ssafy','essay'].includes(v.kind)||!/^\d{4}-\d{2}-\d{2}$/.test(v.date))throw new Error('날짜와 글 종류를 확인해 주세요.');
    let body=v.body;
    if(body.includes('{% endraw'))throw new Error('원고에 Liquid raw 경계가 있습니다. GitHub에서 별도로 검토해 주세요.');
    if(body.includes('{{')||body.includes('{%'))body='{% raw %}\n'+body+'\n{% endraw %}';
    const slug=v.title.normalize('NFKC').toLowerCase().replace(/[^\p{L}\p{N}]+/gu,'-').replace(/^-|-$/g,'').slice(0,70)||'note';
    const filename=v.date+'-manual-'+slug+'.md';
    const tags=v.tags.split(',').map(x=>x.trim()).filter(Boolean);
    const text=['---','layout: post','title: '+JSON.stringify(v.title),'date: '+JSON.stringify(v.date+' 00:00:00 +0900'),'content_type: '+v.kind,'tags: '+JSON.stringify(tags),'published: '+v.published,'---','',body,''].join('\n');
    return {filename,text};
  }
  form.addEventListener('submit',async e=>{
    e.preventDefault();
    try {
      const d=draft();const url=new URL('https://github.com/js05157/cs-interview/new/master/blog/_posts');
      url.searchParams.set('filename',d.filename);
      if(encodeURIComponent(d.text).length<6000)url.searchParams.set('value',d.text);
      else {try {await navigator.clipboard.writeText(d.text);status.textContent='원고를 복사했습니다. GitHub 편집기에 붙여넣고 저장하세요.';}catch(_){status.textContent='긴 원고는 Markdown 다운로드 후 GitHub에 업로드하세요.';}}
      const opened=window.open(url.href,'_blank','noopener,noreferrer');
      if(!status.textContent)status.textContent='GitHub 로그인 후 내용을 확인하고 커밋하세요.';
    } catch(error){status.textContent=error.message;}
  });
  document.querySelector('#download-draft').addEventListener('click',()=>{
    try {const d=draft(),url=URL.createObjectURL(new Blob([d.text],{type:'text/markdown;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download=d.filename;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);status.textContent='Markdown 파일을 다운로드했습니다.';}catch(error){status.textContent=error.message;}
  });
  document.querySelector('#clear-draft').addEventListener('click',()=>{form.reset();form.elements.date.value=today;try{sessionStorage.removeItem(key);}catch(_){}update();status.textContent='입력을 초기화했습니다.';});
})();
