const form = document.querySelector('#chat-form');
const textarea = document.querySelector('#message');
const messages = document.querySelector('#messages');
const statusEl = document.querySelector('#status');
const commandList = document.querySelector('#command-list');
const button = form.querySelector('button');

function addMessage(role, text) {
  const article = document.createElement('article');
  article.className = `message ${role}`;
  const title = document.createElement('strong');
  title.textContent = role === 'user' ? 'You' : 'Gravion Bot';
  const body = document.createElement('p');
  body.textContent = text;
  article.append(title, body);
  messages.append(article);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(text) {
  const clean = text.trim();
  if (!clean) return;
  addMessage('user', clean);
  textarea.value = '';
  button.disabled = true;
  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: clean, session_id: 'web' }),
    });
    const data = await response.json();
    addMessage('bot', data.reply || data.error || 'No reply returned.');
  } catch {
    addMessage('bot', 'The web shell could not reach the bot endpoint.');
  } finally {
    button.disabled = false;
    textarea.focus();
  }
}

function renderCommands(commands) {
  commandList.replaceChildren();
  for (const item of commands) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'command-item';
    btn.dataset.command = item.command;
    const code = document.createElement('code');
    code.textContent = item.command;
    const desc = document.createElement('span');
    desc.textContent = item.description;
    btn.append(code, desc);
    commandList.append(btn);
  }
}

async function loadStatus() {
  try {
    const response = await fetch('/api/health');
    const data = await response.json();
    statusEl.textContent = data.bot_configured ? 'Bot endpoint configured' : 'Web shell ready · built-in commands active';
    if (Array.isArray(data.commands)) renderCommands(data.commands);
  } catch {
    statusEl.textContent = 'Web shell status unavailable';
  }
}

form.addEventListener('submit', async (event) => {
  event.preventDefault();
  await sendMessage(textarea.value);
});

document.addEventListener('click', async (event) => {
  const target = event.target.closest('[data-command]');
  if (!target) return;
  await sendMessage(target.dataset.command);
});

loadStatus();
