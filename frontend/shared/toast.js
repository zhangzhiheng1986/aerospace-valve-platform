/* ============================================================
   Avis Toast — Lightweight notification system
   Usage:
     Toast.success('Design completed');
     Toast.error('Connection failed');
     Toast.warning('Pressure exceeds limit', 5000);
     Toast.info('3 agents active');
   ============================================================ */

const Toast = (() => {
  const DEFAULT_DURATION = 4000;
  let container = null;

  function ensureContainer() {
    if (container) return container;
    container = document.createElement('div');
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
  }

  const icons = {
    success: '✅',
    error: '❌',
    warning: '⚠️',
    info: 'ℹ️',
  };

  function show(message, type = 'info', duration = DEFAULT_DURATION) {
    const el = document.createElement('div');
    el.className = `toast toast-${type}`;
    el.setAttribute('role', 'alert');
    el.setAttribute('aria-live', 'assertive');

    el.innerHTML = `
      <span class="toast-icon">${icons[type] || icons.info}</span>
      <span class="toast-body">${message}</span>
      <span class="toast-close" aria-label="Close" onclick="this.closest('.toast').remove()">×</span>
    `;

    ensureContainer().appendChild(el);

    if (duration > 0) {
      setTimeout(() => {
        if (el.parentNode) el.remove();
      }, duration);
    }

    return el;
  }

  return {
    success: (msg, dur) => show(msg, 'success', dur),
    error: (msg, dur) => show(msg, 'error', dur),
    warning: (msg, dur) => show(msg, 'warning', dur),
    info: (msg, dur) => show(msg, 'info', dur),
    dismiss: (el) => { if (el && el.parentNode) el.remove(); },
  };
})();
