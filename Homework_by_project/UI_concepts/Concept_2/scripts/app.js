(function () {
  const root = document.documentElement;
  const themeKey = 'digest-cds-c2-theme';
  const questKey = 'digest-cds-c2-quest-dismissed';
  const adminSelectionKey = 'digest-cds-c2-admin-selection';
  const adminLeadKey = 'digest-cds-c2-admin-lead';
  const savedTheme = localStorage.getItem(themeKey);
  if (savedTheme) root.setAttribute('data-theme', savedTheme);

  document.querySelectorAll('[data-theme-toggle]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const next = root.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
      if (next === 'dark') {
        root.removeAttribute('data-theme');
        localStorage.setItem(themeKey, 'dark');
        btn.textContent = '☀';
        btn.setAttribute('aria-label', 'Светлая тема');
      } else {
        root.setAttribute('data-theme', 'light');
        localStorage.setItem(themeKey, 'light');
        btn.textContent = '☽';
        btn.setAttribute('aria-label', 'Тёмная тема');
      }
    });
    if (root.getAttribute('data-theme') === 'light') btn.textContent = '☽';
  });

  const quest = document.getElementById('quest-banner');
  if (quest && localStorage.getItem(questKey) === '1') quest.classList.add('hidden');

  document.querySelectorAll('[data-quest-dismiss]').forEach(function (btn) {
    btn.addEventListener('click', function () {
      if (quest) quest.classList.add('hidden');
      localStorage.setItem(questKey, '1');
    });
  });

  function initVoting() {
    const voting = document.querySelector('[data-voting]');
    if (!voting) return;
    const voteKey = 'digest-cds-c2-vote';
    const cards = Array.from(voting.querySelectorAll('[data-vote-topic]'));
    const status = document.getElementById('vote-status');
    let selected = localStorage.getItem(voteKey) || '';

    function render() {
      cards.forEach(function (card) {
        const active = card.dataset.voteTopic === selected;
        card.classList.toggle('topic-card--selected', active);
        card.setAttribute('aria-pressed', String(active));
      });
      const selectedCard = cards.find(function (card) { return card.dataset.voteTopic === selected; });
      const title = selectedCard ? selectedCard.querySelector('.text-h2, .text-h3')?.textContent.trim() : '';
      if (status) status.textContent = title ? 'Ваш голос: ' + title : 'Ваш голос: не отдан';
    }

    cards.forEach(function (card) {
      card.addEventListener('click', function () {
        selected = card.dataset.voteTopic || '';
        localStorage.setItem(voteKey, selected);
        render();
      });
    });
    render();
  }

  function initToggles() {
    document.querySelectorAll('.toggle[role="switch"]').forEach(function (toggle, index) {
      const key = 'digest-cds-c2-setting-' + (toggle.dataset.setting || index);
      const stored = localStorage.getItem(key);
      let checked = stored === null ? toggle.getAttribute('aria-checked') === 'true' : stored === '1';

      function render() {
        toggle.classList.toggle('toggle--on', checked);
        toggle.setAttribute('aria-checked', String(checked));
      }
      function flip() {
        checked = !checked;
        localStorage.setItem(key, checked ? '1' : '0');
        render();
      }
      toggle.addEventListener('click', flip);
      toggle.addEventListener('keydown', function (event) {
        if (event.key !== ' ' && event.key !== 'Enter') return;
        event.preventDefault();
        flip();
      });
      render();
    });
  }

  function initLogin() {
    const form = document.querySelector('[data-login-form]');
    if (!form) return;
    const email = form.querySelector('#email');
    const password = form.querySelector('#password');
    const error = form.querySelector('[data-login-error]');
    form.addEventListener('submit', function (event) {
      const validDomain = email && /@(sberbank\.ru|omega\.sbrf\.ru)$/i.test(email.value.trim());
      const validPassword = password && password.value.length >= 6;
      if (validDomain && validPassword) return;
      event.preventDefault();
      if (email && !validDomain) email.setCustomValidity('Используйте корпоративный адрес @sberbank.ru или @omega.sbrf.ru.');
      if (password && !validPassword) password.setCustomValidity('Пароль должен содержать не менее 6 символов.');
      if (error) error.textContent = 'Проверьте корпоративный email и пароль.';
      form.reportValidity();
    });
    [email, password].forEach(function (field) {
      if (!field) return;
      field.addEventListener('input', function () { field.setCustomValidity(''); });
    });
  }

  function initAdmin() {
    const admin = document.querySelector('[data-admin]');
    if (!admin) return;

    const rows = Array.from(admin.querySelectorAll('[data-admin-row]'));
    const selectionSummary = admin.querySelector('#admin-selection-summary');
    const leadInput = admin.querySelector('[data-admin-lead]');
    const saveHint = admin.querySelector('#admin-save-hint');
    const previewPanel = admin.querySelector('[data-admin-preview-panel]');
    const previewLead = admin.querySelector('[data-admin-preview-lead]');
    const previewList = admin.querySelector('[data-admin-preview-list]');
    const sendHint = admin.querySelector('#admin-send-hint');
    const savedSelection = JSON.parse(localStorage.getItem(adminSelectionKey) || 'null');
    const savedLead = localStorage.getItem(adminLeadKey);

    if (Array.isArray(savedSelection)) {
      rows.forEach(function (row, index) {
        const checkbox = row.querySelector('[data-admin-item]');
        if (checkbox) checkbox.checked = savedSelection[index] === true;
      });
    }
    if (savedLead && leadInput) leadInput.value = savedLead;

    function saveSelection() {
      localStorage.setItem(adminSelectionKey, JSON.stringify(rows.map(function (row) {
        const checkbox = row.querySelector('[data-admin-item]');
        return Boolean(checkbox && checkbox.checked);
      })));
    }

    function updateRow(row) {
      const checkbox = row.querySelector('[data-admin-item]');
      const label = row.querySelector('.admin-row__include span');
      const exclusion = row.querySelector('[data-admin-exclusion]');
      if (!checkbox) return;
      row.classList.toggle('admin-row--excluded', !checkbox.checked);
      if (label) label.textContent = checkbox.checked ? 'Включить' : 'Исключить';
      if (exclusion) {
        exclusion.hidden = checkbox.checked;
        if (!checkbox.checked && !exclusion.textContent.trim()) exclusion.textContent = 'Исключено администратором';
      }
    }

    function selectedRows() {
      return rows.filter(function (row) {
        const checkbox = row.querySelector('[data-admin-item]');
        return checkbox && checkbox.checked;
      });
    }

    function renderPreview(previewRows) {
      if (!previewPanel || !previewLead || !previewList) return;
      previewLead.textContent = leadInput ? leadInput.value.trim() : '';
      previewList.innerHTML = '';
      previewRows.forEach(function (row) {
        const item = document.createElement('li');
        item.innerHTML = '<strong></strong><span></span>';
        item.querySelector('strong').textContent = row.dataset.title || 'Материал';
        item.querySelector('span').textContent = row.dataset.dek || '';
        previewList.appendChild(item);
      });
      previewPanel.hidden = false;
      previewPanel.focus();
    }

    function updateSummary() {
      const count = selectedRows().length;
      if (selectionSummary) selectionSummary.textContent = 'Выбрано ' + count + ' из ' + rows.length + ' материалов';
      rows.forEach(updateRow);
      saveSelection();
    }

    rows.forEach(function (row) {
      const checkbox = row.querySelector('[data-admin-item]');
      if (checkbox) checkbox.addEventListener('change', updateSummary);
      const previewButton = row.querySelector('[data-admin-preview-item]');
      if (previewButton) {
        previewButton.addEventListener('click', function () {
          renderPreview([row]);
          if (sendHint) sendHint.textContent = 'Показано превью выбранного материала. Состав shortlist сохранён.';
        });
      }
    });

    const selectAll = admin.querySelector('[data-admin-select-all]');
    if (selectAll) {
      selectAll.addEventListener('click', function () {
        rows.forEach(function (row) {
          const checkbox = row.querySelector('[data-admin-item]');
          if (checkbox) checkbox.checked = true;
        });
        updateSummary();
      });
    }

    const clearAll = admin.querySelector('[data-admin-clear]');
    if (clearAll) {
      clearAll.addEventListener('click', function () {
        rows.forEach(function (row) {
          const checkbox = row.querySelector('[data-admin-item]');
          if (checkbox) checkbox.checked = false;
        });
        updateSummary();
      });
    }

    if (leadInput) {
      leadInput.addEventListener('input', function () {
        localStorage.setItem(adminLeadKey, leadInput.value);
        if (saveHint) saveHint.textContent = 'Черновик сохранён в прототипе.';
        if (!previewPanel || previewPanel.hidden) return;
        previewLead.textContent = leadInput.value.trim();
      });
    }

    const previewButton = admin.querySelector('[data-admin-preview]');
    if (previewButton) {
      previewButton.addEventListener('click', function () {
        const chosen = selectedRows();
        renderPreview(chosen);
        if (sendHint) sendHint.textContent = chosen.length
          ? 'Предпросмотр обновлён: ' + chosen.length + ' материалов и текущий объединяющий текст.'
          : 'Выберите хотя бы один материал для предпросмотра.';
        if (previewPanel && !previewPanel.hidden) {
          previewPanel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        const originalLabel = 'Предпросмотр выпуска';
        previewButton.textContent = chosen.length ? 'Предпросмотр обновлён' : originalLabel;
        window.setTimeout(function () {
          previewButton.textContent = originalLabel;
        }, 1800);
      });
    }

    updateSummary();
  }

  function initKnowledge() {
    const knowledge = document.querySelector('[data-knowledge]');
    if (!knowledge) return;

    const search = knowledge.querySelector('[data-knowledge-search]');
    const role = knowledge.querySelector('[data-knowledge-role]');
    const topic = knowledge.querySelector('[data-knowledge-topic]');
    const format = knowledge.querySelector('[data-knowledge-format]');
    const reset = knowledge.querySelector('[data-knowledge-reset]');
    const count = knowledge.querySelector('[data-knowledge-count]');
    const empty = knowledge.querySelector('[data-knowledge-empty]');
    const cards = Array.from(knowledge.querySelectorAll('[data-knowledge-card]'));
    function applyFilters() {
      const query = search ? search.value.trim().toLowerCase() : '';
      const selectedRole = role ? role.value : '';
      const selectedTopic = topic ? topic.value : '';
      const selectedFormat = format ? format.value : '';
      let visibleCount = 0;

      cards.forEach(function (card) {
        const matchesQuery = !query || card.dataset.search.includes(query);
        const matchesRole = !selectedRole || card.dataset.role.includes(selectedRole);
        const matchesTopic = !selectedTopic || card.dataset.topic.includes(selectedTopic);
        const matchesFormat = !selectedFormat || card.dataset.format === selectedFormat;
        const visible = matchesQuery && matchesRole && matchesTopic && matchesFormat;
        card.hidden = !visible;
        if (visible) visibleCount += 1;
      });

      if (count) count.textContent = 'Показано ' + visibleCount + ' из ' + cards.length + ' материалов';
      if (empty) empty.hidden = visibleCount !== 0;
    }

    [search, role, topic, format].forEach(function (control) {
      if (control) control.addEventListener('input', applyFilters);
      if (control && control.tagName === 'SELECT') control.addEventListener('change', applyFilters);
    });
    if (reset) {
      reset.addEventListener('click', function () {
        if (search) search.value = '';
        if (role) role.value = '';
        if (topic) topic.value = '';
        if (format) format.value = '';
        applyFilters();
      });
    }
    applyFilters();
  }

  document.querySelectorAll('[data-related-terms]').forEach(function (select) {
    select.addEventListener('change', function () {
      if (select.value) window.location.href = select.value;
    });
  });

  initKnowledge();
  initAdmin();
  initVoting();
  initToggles();
  initLogin();
})();
