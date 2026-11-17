(() => {
  const storageKey = 'telos-demo-profile';
  const overlay = document.getElementById('entry-overlay');
  const form = document.getElementById('entry-form');
  if (!overlay || !form) return;

  const nameField = document.getElementById('entry-name');
  const emailField = document.getElementById('entry-email');
  const error = document.getElementById('entry-error');
  const profileBar = document.getElementById('user-bar');
  const welcomeName = document.getElementById('welcome-name');
  const recipientStatus = document.getElementById('recipient-status');
  let profile = readProfile();

  function readProfile() {
    try {
      const value = JSON.parse(localStorage.getItem(storageKey) || 'null');
      return value && typeof value.name === 'string' && typeof value.email === 'string' ? value : null;
    } catch (_) { return null; }
  }

  function renderProfile() {
    if (profileBar && profile) {
      profileBar.hidden = false;
      welcomeName.textContent = profile.name;
      recipientStatus.textContent = `Avisos para: ${profile.email}`;
    }
    overlay.hidden = Boolean(profile);
    if (profile) window.dispatchEvent(new CustomEvent('telos-profile-ready', {detail: {...profile}}));
  }

  function openEditor() {
    nameField.value = profile?.name || '';
    emailField.value = profile?.email || '';
    document.querySelector('#entry-title').textContent = profile ? 'Atualizar seus dados' : 'Vamos começar';
    form.querySelector('button[type="submit"]').textContent = profile ? 'Salvar e continuar' : 'Entrar na demonstração';
    error.hidden = true;
    overlay.hidden = false;
    nameField.focus();
  }

  document.getElementById('change-profile')?.addEventListener('click', openEditor);
  form.addEventListener('submit', event => {
    event.preventDefault();
    if (!form.reportValidity()) return;
    const previousProfile = readProfile();
    profile = {
      name: nameField.value.trim(),
      email: emailField.value.trim(),
      lastEmailSent: previousProfile?.lastEmailSent || '',
      pendingEmail: '',
    };
    if (!profile.name || !profile.email) {
      error.textContent = 'Preencha seu nome e um endereço de e-mail válido.';
      error.hidden = false;
      return;
    }
    if (profile.email !== previousProfile?.email) profile.lastEmailSent = '';
    try {
      localStorage.setItem(storageKey, JSON.stringify(profile));
    } catch (_) {
      error.textContent = 'Não foi possível guardar os dados neste navegador.';
      error.hidden = false;
      return;
    }
    renderProfile();
  });

  window.TelosProfile = {
    get: () => profile ? {name: profile.name, email: profile.email} : null,
    markEmailSent: () => {
      if (profile?.pendingEmail) {
        profile.lastEmailSent = profile.pendingEmail;
        profile.pendingEmail = '';
        localStorage.setItem(storageKey, JSON.stringify(profile));
      }
      if (recipientStatus && profile) recipientStatus.textContent = `Avisos para: ${profile.email}`;
    },
    setEmailPending: () => {
      if (profile) {
        profile.pendingEmail = profile.email;
        localStorage.setItem(storageKey, JSON.stringify(profile));
        if (recipientStatus) recipientStatus.textContent = `Avisos para: ${profile.email}`;
      }
    },
  };
  renderProfile();
  if (!profile) requestAnimationFrame(() => nameField.focus());
})();
