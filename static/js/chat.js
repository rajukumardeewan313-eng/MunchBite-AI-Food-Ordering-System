(function () {
  const panel = document.getElementById('chat-panel');
  if (!panel) return;
  const log = panel.querySelector('.chat-log');
  const form = panel.querySelector('.chat-form');
  const input = form.querySelector('input');
  const sendBtn = form.querySelector('button');
  const csrf = document.querySelector('meta[name="csrf"]').content;
  const fab = document.getElementById('chat-fab');

  function add(cls, text) {
    const d = document.createElement('div');
    d.className = 'msg ' + cls;
    d.textContent = text;
    log.appendChild(d);
    log.scrollTop = log.scrollHeight;
    return d;
  }
  function greet() {
    add('bot', 'Hi! I can help with food recommendations, prices, availability, your order status, ' +
      'cancellations and support tickets. What would you like?');
  }
  async function loadHistory() {
    try {
      const r = await fetch('/api/chat/history');
      const j = await r.json();
      (j.messages || []).forEach(m => add(m.role === 'user' ? 'user' : 'bot', m.content));
    } catch (e) { /* ignore */ }
    if (!log.children.length) greet();
  }
  async function send(text) {
    text = text.trim();
    if (!text) return;
    add('user', text);
    input.value = '';
    sendBtn.disabled = true;
    const typing = add('bot typing', 'Thinking...');
    try {
      const r = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRF-Token': csrf },
        body: JSON.stringify({ message: text })
      });
      const j = await r.json().catch(() => ({}));
      typing.remove();
      if (!r.ok) add('err', j.error || 'Something went wrong. Please try again.');
      else add('bot', j.reply);
    } catch (e) {
      typing.remove();
      add('err', 'Could not reach the server. Check your connection and try again.');
    }
    sendBtn.disabled = false;
    input.focus();
  }
  form.addEventListener('submit', e => { e.preventDefault(); send(input.value); });
  panel.querySelectorAll('.chip').forEach(c => c.addEventListener('click', () => send(c.dataset.q)));
  panel.querySelector('.js-reset').addEventListener('click', async () => {
    await fetch('/api/chat/reset', { method: 'POST', headers: { 'X-CSRF-Token': csrf } });
    log.innerHTML = '';
    greet();
  });
  if (fab) {
    const toggle = () => panel.classList.toggle('open');
    fab.addEventListener('click', toggle);
    panel.querySelector('.js-close').addEventListener('click', toggle);
  }
  loadHistory();
})();
