(() => {
  const box = document.getElementById('case-wizard');
  if (!box) return;

  const steps = [...box.querySelectorAll('.wizard-step')];
  const label = document.getElementById('wizard-step-label');
  const error = document.getElementById('case-error');
  const description = document.getElementById('case-description');
  const piiNotice = document.getElementById('case-pii-notice');
  const privacyPiiNotice = document.getElementById('case-pii-privacy-notice');
  const simulationExample = document.getElementById('case-example');
  let current = 0;

  function show(step) {
    current = step;
    steps.forEach((element, index) => { element.hidden = index !== step; });
    label.textContent = `ETAPA ${step + 1} DE 3`;
    error.hidden = true;
    box.hidden = false;
    box.scrollIntoView({behavior:'smooth', block:'center'});
  }

  function sanitizeDescription() {
    const patterns = [
      /\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b/gi,
      /(?<!\d)\d{2}\.?\d{3}\.?\d{3}\/?\d{4}-?\d{2}(?!\d)/g,
      /(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)/g,
    ];
    let cleaned = description.value;
    patterns.forEach(pattern => { cleaned = cleaned.replace(pattern, '[dado removido]'); });
    const removed = cleaned !== description.value;
    if (removed) description.value = cleaned;
    piiNotice.hidden = !removed;
    privacyPiiNotice.hidden = !removed;
    return removed;
  }

  document.getElementById('open-case-form').addEventListener('click', () => show(0));
  document.getElementById('close-case-form').addEventListener('click', () => { box.hidden = true; });
  document.getElementById('to-privacy').addEventListener('click', () => {
    sanitizeDescription();
    if (!document.getElementById('case-form').reportValidity()) return;
    show(1);
  });
  document.getElementById('back-to-form').addEventListener('click', () => show(0));
  document.getElementById('finish-case-form').addEventListener('click', () => location.reload());

  function renderNotice(notice) {
    simulationExample.replaceChildren();
    const card = document.createElement('article');
    card.className = 'panel notice-card';
    const title = document.createElement('h3');
    title.textContent = notice.resumo || 'Aviso demonstrativo';
    card.append(title);

    const count = document.createElement('div');
    count.className = 'impact-count';
    const number = document.createElement('strong');
    number.textContent = String((notice.casos || []).length);
    const countLabel = document.createElement('span');
    countLabel.textContent = (notice.casos || []).length === 1 ? 'caso é afetado' : 'casos são afetados';
    count.append(number, countLabel);
    card.append(count);

    const result = document.createElement('div');
    result.className = 'decision-meta';
    result.textContent = `Resultado: ${notice.resultado || 'não identificado'}`;
    card.append(result);
    const metadata = document.createElement('div');
    metadata.className = 'decision-meta';
    metadata.textContent = notice.metadata || 'Dados do processo não informados.';
    card.append(metadata);

    const list = document.createElement('ul');
    list.className = 'affected-list';
    (notice.casos || []).forEach(item => {
      const row = document.createElement('li');
      const caseName = document.createElement('span');
      caseName.textContent = item.titulo;
      const badge = document.createElement('span');
      const position = String(item.favorabilidade || '').toLowerCase();
      badge.className = `badge ${position.includes('favorável') ? 'good' : position.includes('desfavorável') ? 'bad' : 'uncertain'}`;
      badge.textContent = item.favorabilidade || 'Favorabilidade incerta';
      row.append(caseName, badge);
      list.append(row);
    });
    if (list.childElementCount) card.append(list);

    (notice.trechos || []).forEach(item => {
      const quote = document.createElement('blockquote');
      quote.className = 'evidence';
      quote.textContent = `“${item.texto}”`;
      card.append(quote);
    });
    try {
      const linkUrl = new URL(notice.link);
      const official = linkUrl.protocol === 'https:' && (linkUrl.hostname === 'stj.jus.br' || linkUrl.hostname.endsWith('.stj.jus.br'));
      if (official) {
        const isTheme = linkUrl.searchParams.has('cod_tema_inicial');
        const link = document.createElement('a');
        link.className = 'official-link';
        link.href = linkUrl.href;
        link.target = '_blank';
        link.rel = 'noopener noreferrer';
        link.textContent = isTheme ? 'Ver o tema repetitivo no site oficial do STJ →' : 'Ver a decisão no site oficial do STJ →';
        card.append(link);
      }
    } catch (_) {}

    const note = document.createElement('p');
    note.className = 'field-note';
    note.textContent = 'Exemplo demonstrativo da decisão mais parecida com a descrição; não é uma análise jurídica do caso.';
    simulationExample.append(card, note);
    simulationExample.hidden = false;
  }

  document.getElementById('case-form').addEventListener('submit', async event => {
    event.preventDefault();
    error.hidden = true;
    const personalDataRemoved = sanitizeDescription();
    const payload = {
      kind: document.getElementById('case-kind').value,
      description: description.value,
      area: document.getElementById('case-area').value,
    };
    const email = document.getElementById('case-email');
    if (email && email.value.trim()) payload.email = email.value.trim();

    try {
      const response = await fetch('/api/cases', {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify(payload),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Não foi possível cadastrar o caso.');
      const removed = personalDataRemoved || data.dados_pessoais_removidos;
      const messages = [];
      if (removed) messages.push('Removemos dados pessoais da descrição');
      if (data.message) messages.push(data.message);
      if (data.email_message) messages.push(data.email_message);
      document.getElementById('case-success').textContent = messages.join(' ');
      if (data.simulation) {
        document.getElementById('case-result-title').textContent = 'Exemplo de aviso';
        renderNotice(data.notice);
      } else {
        document.getElementById('case-result-title').textContent = 'Caso cadastrado';
        simulationExample.hidden = true;
      }
      show(2);
    } catch (exception) {
      error.textContent = exception.message;
      error.hidden = false;
    }
  });
})();
