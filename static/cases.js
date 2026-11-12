(() => {
  const box=document.getElementById('case-wizard');
  if(!box) return;
  const steps=[...box.querySelectorAll('.wizard-step')];
  const label=document.getElementById('wizard-step-label');
  const error=document.getElementById('case-error');
  const simulationExample=document.getElementById('case-example');
  let current=0;
  function show(n){current=n;steps.forEach((el,i)=>el.hidden=i!==n);label.textContent=`ETAPA ${n+1} DE 3`;error.hidden=true;box.hidden=false;box.scrollIntoView({behavior:'smooth',block:'center'});}
  document.getElementById('open-case-form').addEventListener('click',()=>show(0));
  document.getElementById('close-case-form').addEventListener('click',()=>{box.hidden=true;});
  document.getElementById('to-privacy').addEventListener('click',()=>{
    const form=document.getElementById('case-form');
    if(!form.reportValidity()) return;
    show(1);
  });
  document.getElementById('back-to-form').addEventListener('click',()=>show(0));
  document.getElementById('finish-case-form').addEventListener('click',()=>location.reload());
  function renderNotice(notice){
    simulationExample.replaceChildren();
    const card=document.createElement('article');card.className='panel notice-card';
    const title=document.createElement('h3');title.textContent=notice.resumo||'Aviso demonstrativo';card.append(title);
    const count=document.createElement('div');count.className='impact-count';
    const number=document.createElement('strong');number.textContent=String((notice.casos||[]).length);
    const labelText=document.createElement('span');labelText.textContent=(notice.casos||[]).length===1?'caso é afetado':'casos são afetados';
    count.append(number,labelText);card.append(count);
    const result=document.createElement('div');result.className='decision-meta';result.textContent=`Resultado: ${notice.resultado||'não identificado'}`;card.append(result);
    const metadata=document.createElement('div');metadata.className='decision-meta';metadata.textContent=notice.metadata||'Dados do processo não informados.';card.append(metadata);
    const list=document.createElement('ul');list.className='affected-list';
    (notice.casos||[]).forEach(item=>{const row=document.createElement('li');const name=document.createElement('span');name.textContent=item.titulo;const badge=document.createElement('span');const position=String(item.favorabilidade||'').toLowerCase();badge.className=`badge ${position.includes('favorável')?'good':position.includes('desfavorável')?'bad':'uncertain'}`;badge.textContent=item.favorabilidade||'Favorabilidade incerta';row.append(name,badge);list.append(row);});
    if(list.childElementCount)card.append(list);
    (notice.trechos||[]).forEach(item=>{const quote=document.createElement('blockquote');quote.className='evidence';quote.textContent=`“${item.texto}”`;card.append(quote);});
    try{const linkUrl=new URL(notice.link);const official=linkUrl.hostname==='tjsp.jus.br'||linkUrl.hostname.endsWith('.tjsp.jus.br')||linkUrl.hostname==='stj.jus.br'||linkUrl.hostname.endsWith('.stj.jus.br');if(linkUrl.protocol==='https:'&&official){const court=linkUrl.hostname.endsWith('.stj.jus.br')||linkUrl.hostname==='stj.jus.br'?'STJ':'TJSP';const link=document.createElement('a');link.className='official-link';link.href=linkUrl.href;link.target='_blank';link.rel='noopener noreferrer';link.textContent=`Ver a decisão no site oficial do ${court} →`;card.append(link);}}catch(_){}
    const note=document.createElement('p');note.className='field-note';note.textContent='Exemplo demonstrativo da decisão mais parecida com a descrição; não é uma análise jurídica do caso.';simulationExample.append(card,note);simulationExample.hidden=false;
  }
  document.getElementById('case-form').addEventListener('submit',async event=>{
    event.preventDefault();error.hidden=true;
    const payload={kind:document.getElementById('case-kind').value,client_name:document.getElementById('case-client').value,description:document.getElementById('case-description').value,area:document.getElementById('case-area').value};
    const email=document.getElementById('case-email');if(email&&email.value.trim())payload.email=email.value.trim();
    try{const response=await fetch('/api/cases',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await response.json();if(!response.ok)throw new Error(data.error||'Não foi possível cadastrar o caso.');document.getElementById('case-success').textContent=[data.message,data.email_message].filter(Boolean).join(' ');if(data.simulation){document.getElementById('case-result-title').textContent='Exemplo de aviso';renderNotice(data.notice);}else{document.getElementById('case-result-title').textContent='Caso cadastrado';simulationExample.hidden=true;}show(2);}
    catch(e){error.textContent=e.message;error.hidden=false;}
  });
})();
