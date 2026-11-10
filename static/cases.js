(() => {
  const box=document.getElementById('case-wizard');
  if(!box) return;
  const steps=[...box.querySelectorAll('.wizard-step')];
  const label=document.getElementById('wizard-step-label');
  const error=document.getElementById('case-error');
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
  document.getElementById('case-form').addEventListener('submit',async event=>{
    event.preventDefault();error.hidden=true;
    const payload={kind:document.getElementById('case-kind').value,client_name:document.getElementById('case-client').value,description:document.getElementById('case-description').value,area:document.getElementById('case-area').value};
    try{const response=await fetch('/api/cases',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});const data=await response.json();if(!response.ok)throw new Error(data.error||'Não foi possível cadastrar o caso.');document.getElementById('case-success').textContent=data.message;show(2);}
    catch(e){error.textContent=e.message;error.hidden=false;}
  });
})();
