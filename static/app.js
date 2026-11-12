(() => {
  const form = document.getElementById('watch-form');
  const button = document.getElementById('watch-button');
  const errorBox = document.getElementById('form-error');
  const progressPanel = document.getElementById('progress-panel');
  const progressTitle = document.getElementById('progress-title');
  const progressMessage = document.getElementById('progress-message');
  const progressBar = document.getElementById('progress-bar');
  const content = document.getElementById('last-round-content');
  const date = document.getElementById('last-round-date');
  const emailAction = document.getElementById('email-action');
  const emailButton = document.getElementById('email-send-button');
  const emailStatus = document.getElementById('email-send-status');
  let lastRenderKey = '';

  function node(tag, className, text) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== undefined && text !== null) element.textContent = String(text);
    return element;
  }

  function officialLink(url) {
    try {
      const parsed = new URL(url);
      return parsed.protocol === 'https:' && (parsed.hostname === 'stj.jus.br' || parsed.hostname.endsWith('.stj.jus.br'));
    } catch (_) { return false; }
  }

  function renderRound(round) {
    const key = round ? `${round.data_rodada || ''}-${round.concluidas}-${(round.avisos || []).length}-${(round.revisar || []).length}-${(round.sem_impacto || []).length}-${round.email_status || ''}` : 'empty';
    if (key === lastRenderKey) return;
    lastRenderKey = key;
    content.replaceChildren();
    if (!round) {
      content.append(node('div', 'empty-state', 'Ainda não há uma rodada salva neste computador. Os avisos concluídos aparecerão aqui para consulta posterior.'));
      date.textContent = '';
      return;
    }
    date.textContent = round.data_rodada ? new Date(round.data_rodada).toLocaleString('pt-BR', {dateStyle:'medium', timeStyle:'short'}) : '';
    const summary = node('div', 'round-summary');
    summary.append(node('span', 'summary-chip', round.area || 'STJ'));
    const itemLabel = round.tipo_item === 'tema repetitivo' ? 'temas analisados' : 'decisões analisadas';
    summary.append(node('span', 'summary-chip', `${round.concluidas} de ${round.selecionadas} ${itemLabel}`));
    if (round.email_enviado === true) summary.append(node('span', 'summary-chip', 'E-mail enviado'));
    if (round.email_enviado === false) summary.append(node('span', 'summary-chip', 'E-mail não enviado'));
    content.append(summary);
    if (round.interrompida) content.append(node('div', 'empty-state', 'A rodada foi interrompida antes de analisar todas as decisões selecionadas.'));

    (round.sem_impacto || []).forEach(item => {
      const card = node('article', 'panel notice-card no-impact-card');
      card.append(node('h3', '', 'Nenhum caso com relação direta confirmada'));
      card.append(node('div', 'decision-meta', item.metadata || 'Dados do processo não informados.'));
      if (officialLink(item.link)) {
        const linkLabel = item.link.includes('cod_tema_inicial=') ? 'Ver o tema repetitivo no site oficial do STJ →' : 'Ver a decisão no site oficial do STJ →';
        const link = node('a', 'official-link', linkLabel);
        link.href = item.link; link.target = '_blank'; link.rel = 'noopener noreferrer'; card.append(link);
      }
      content.append(card);
    });

    if (!round.avisos || round.avisos.length === 0) {
      content.append(node('div', 'empty-state', 'Nenhum aviso direto nesta rodada.'));
    } else {
      const grid = node('div', 'notice-grid');
      round.avisos.forEach(item => {
        const card = node('article', 'panel notice-card');
        card.append(node('h3', '', item.resumo));
        const count = node('div', 'impact-count');
        count.append(node('strong', '', (item.casos || []).length));
        count.append(node('span', '', (item.casos || []).length === 1 ? 'caso do escritório é afetado' : 'casos do escritório são afetados'));
        card.append(count);
        card.append(node('div', 'decision-meta', `Resultado: ${item.resultado || 'não identificado'}`));
        card.append(node('div', 'decision-meta', item.metadata || 'Dados do processo não informados.'));
        if (item.casos && item.casos.length) {
          const list = node('ul', 'affected-list');
          item.casos.forEach(affected => {
            const row = node('li');
            row.append(node('span', '', affected.titulo));
            const pos = String(affected.favorabilidade || '').toLowerCase();
            row.append(node('span', `badge ${pos.includes('favorável') ? 'good' : pos.includes('desfavorável') ? 'bad' : 'uncertain'}`, affected.favorabilidade));
            list.append(row);
          });
          card.append(list);
        }
        (item.trechos || []).forEach(evidence => {
          const quote = node('blockquote', 'evidence');
          if (evidence.caso && (item.trechos || []).length > 1) quote.append(node('small', '', evidence.caso));
          quote.append(document.createTextNode(`“${evidence.texto}”`));
          card.append(quote);
        });
        if (item.somente_ementa) card.append(node('p', 'decision-meta', 'Análise feita somente com a ementa do acórdão.'));
        if (officialLink(item.link)) {
          const linkLabel = item.link.includes('cod_tema_inicial=') ? 'Ver o tema repetitivo no site oficial do STJ →' : 'Ver a decisão no site oficial do STJ →';
          const link = node('a', 'official-link', linkLabel);
          link.href = item.link; link.target = '_blank'; link.rel = 'noopener noreferrer';
          card.append(link);
        }
        grid.append(card);
      });
      content.append(grid);
    }

    const reviewHeader = node('div', 'review-section');
    reviewHeader.append(node('h3', '', 'REVISAR À MÃO'));
    if (!round.revisar || round.revisar.length === 0) {
      reviewHeader.append(node('div', 'empty-state', 'Nenhum item para revisão manual nesta rodada.'));
    } else {
      round.revisar.forEach(review => {
        const card = node('article', 'panel review-card');
        card.append(node('div', 'decision-meta', review.metadata || 'Dados do processo não informados.'));
        (review.casos || []).forEach(item => {
          card.append(node('div', 'review-case-title', item.titulo));
          const columns = node('div', 'opinion-grid');
          const first = node('div', 'opinion'); first.append(node('strong', '', 'PARECER 1')); first.append(document.createTextNode(item.parecer_1 || 'Não foi possível ler este parecer, confira a decisão no link oficial'));
          const second = node('div', 'opinion'); second.append(node('strong', '', 'PARECER 2')); second.append(document.createTextNode(item.parecer_2 || 'Não foi possível ler este parecer, confira a decisão no link oficial'));
          columns.append(first, second); card.append(columns);
        });
        card.append(node('div', 'divergence', `Ponto de divergência: ${review.divergencia || 'Os pareceres não chegaram a uma conclusão segura em comum.'}`));
        if (officialLink(review.link)) {
          const linkLabel = review.link.includes('cod_tema_inicial=') ? 'Ver o tema repetitivo no site oficial do STJ →' : 'Ver a decisão no site oficial do STJ →';
          const link = node('a', 'official-link', linkLabel);
          link.href = review.link; link.target = '_blank'; link.rel = 'noopener noreferrer'; card.append(link);
        }
        reviewHeader.append(card);
      });
    }
    content.append(reviewHeader);
  }

  function applyState(state) {
    const running = Boolean(state.running);
    button.disabled = running;
    button.querySelector('span:first-child').textContent = running ? 'Rodada em andamento' : 'Vigiar agora';
    if (running || state.phase === 'error') {
      progressPanel.hidden = false;
      progressTitle.textContent = running ? 'O Telos está trabalhando' : 'Não foi possível concluir';
      progressMessage.textContent = state.message || 'A última rodada continua disponível abaixo.';
      const pct = state.progress_total ? Math.max(5, Math.min(100, 100 * state.progress_current / state.progress_total)) : 8;
      progressBar.style.width = `${pct}%`;
    } else if (state.phase === 'complete' && state.message && state.message !== 'Pronto para vigiar o STJ.') {
      progressPanel.hidden = false;
      progressTitle.textContent = 'Rodada concluída';
      progressMessage.textContent = state.message;
      progressBar.style.width = '100%';
    } else {
      progressPanel.hidden = true;
    }
    renderRound(state.last_round || null);
    emailAction.hidden = !state.email_available;
    if (state.email_status === 'sending') {
      emailButton.disabled = true; emailButton.textContent = 'Enviando…'; emailStatus.textContent = 'O serviço de e-mail está processando o envio.';
    } else if (state.email_status === 'sent') {
      emailButton.disabled = false; emailButton.textContent = 'Enviar novamente por e-mail'; emailStatus.textContent = `${state.message || 'Avisos enviados.'} Clique novamente para reenviar esta rodada.`;
    } else if (state.email_status === 'failed') {
      emailButton.disabled = false; emailButton.textContent = 'Tentar enviar novamente'; emailStatus.textContent = 'Não foi possível enviar os avisos. Eles continuam disponíveis nesta página.';
    } else {
      emailButton.disabled = false; emailButton.textContent = 'Enviar avisos por e-mail'; emailStatus.textContent = '';
    }
  }

  const initialState = window.TELOS_INITIAL_STATE || {};
  const areaSelect = document.getElementById('area');
  if (areaSelect) areaSelect.value = initialState.demo_mode ? 'todas' : 'imobiliario';

  async function refreshState() {
    try {
      const response = await fetch('/api/state', {cache:'no-store'});
      if (!response.ok) throw new Error('state');
      applyState(await response.json());
    } catch (_) {
      progressPanel.hidden = false;
      progressTitle.textContent = 'Conexão instável';
      progressMessage.textContent = 'A última rodada salva continua visível nesta página.';
    }
  }

  form.addEventListener('submit', async event => {
    event.preventDefault();
    errorBox.hidden = true;
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    payload.decision_count = Number(payload.decision_count || 5);
    payload.area = payload.area || 'todas';
    button.disabled = true;
    button.querySelector('span:first-child').textContent = 'Preparando…';
    try {
      const response = await fetch('/api/run', {
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(payload)
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Não foi possível iniciar a rodada.');
      progressPanel.hidden = false;
      progressTitle.textContent = 'O Telos está trabalhando';
      progressMessage.textContent = 'Buscando itens no STJ…';
      refreshState();
    } catch (error) {
      errorBox.textContent = error.message || 'Não foi possível iniciar a rodada.';
      errorBox.hidden = false;
      button.disabled = false;
      button.querySelector('span:first-child').textContent = 'Vigiar agora';
    }
  });

  emailButton.addEventListener('click', async () => {
    emailButton.disabled = true;
    emailButton.textContent = 'Preparando…';
    try {
      const response = await fetch('/api/send-email', {
        method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({
          extra_email:document.getElementById('extra-email').value.trim()
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || 'Não foi possível iniciar o envio.');
      emailStatus.textContent = 'O envio começou.';
      refreshState();
    } catch (error) {
      emailStatus.textContent = error.message || 'Não foi possível iniciar o envio.';
      emailButton.disabled = false;
    }
  });

  applyState(window.TELOS_INITIAL_STATE || {});
  window.setInterval(refreshState, 1600);
})();
