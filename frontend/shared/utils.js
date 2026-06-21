/* ============================================================
   Avis Utils — Shared helper functions for all pages
   Auto-imported. No per-page duplication.
   ============================================================ */

const Utils = (() => {

  // ---- DOM helpers ----
  function $(selector, parent = document) { return parent.querySelector(selector); }
  function $$(selector, parent = document) { return Array.from(parent.querySelectorAll(selector)); }
  function create(tag, attrs = {}, children = []) {
    const el = document.createElement(tag);
    Object.entries(attrs).forEach(([k, v]) => {
      if (k === 'className') el.className = v;
      else if (k === 'innerHTML') el.innerHTML = v;
      else if (k === 'textContent') el.textContent = v;
      else if (k.startsWith('on')) el.addEventListener(k.slice(2).toLowerCase(), v);
      else if (k === 'style' && typeof v === 'object') Object.assign(el.style, v);
      else el.setAttribute(k, v);
    });
    children.forEach(c => { if (typeof c === 'string') el.appendChild(document.createTextNode(c)); else el.appendChild(c); });
    return el;
  }

  // ---- Debounce ----
  function debounce(fn, ms = 300) {
    let timer;
    return function(...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), ms);
    };
  }

  // ---- Throttle ----
  function throttle(fn, ms = 100) {
    let last = 0;
    return function(...args) {
      const now = Date.now();
      if (now - last >= ms) { last = now; fn.apply(this, args); }
    };
  }

  // ---- Formatting ----
  function formatNumber(n, decimals = 2) {
    if (n == null || isNaN(n)) return '—';
    return Number(n).toFixed(decimals);
  }

  function formatPercent(n, decimals = 1) {
    if (n == null || isNaN(n)) return '—';
    return (Number(n) * 100).toFixed(decimals) + '%';
  }

  function formatSI(value, unit = '') {
    if (value == null || isNaN(value)) return '—';
    const abs = Math.abs(value);
    if (abs >= 1e9) return (value / 1e9).toFixed(2) + ' G' + unit;
    if (abs >= 1e6) return (value / 1e6).toFixed(2) + ' M' + unit;
    if (abs >= 1e3) return (value / 1e3).toFixed(2) + ' k' + unit;
    if (abs >= 1) return value.toFixed(2) + ' ' + unit;
    if (abs >= 1e-3) return (value * 1e3).toFixed(2) + ' m' + unit;
    if (abs >= 1e-6) return (value * 1e6).toFixed(2) + ' u' + unit;
    return (value * 1e9).toFixed(2) + ' n' + unit;
  }

  function formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
  }

  function formatTime(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' });
  }

  function formatDateTime(iso) {
    if (!iso) return '—';
    return formatDate(iso) + ' ' + formatTime(iso);
  }

  // ---- Clipboard ----
  async function copyToClipboard(text) {
    try {
      await navigator.clipboard.writeText(text);
      Toast.success('已复制到剪贴板');
      return true;
    } catch (e) {
      Toast.error('复制失败');
      return false;
    }
  }

  // ---- ID Generation ----
  function uid(prefix = '') {
    return prefix + Date.now().toString(36) + Math.random().toString(36).slice(2, 8);
  }

  // ---- Storage ----
  function storeGet(key, fallback = null) {
    try { const v = localStorage.getItem('avis_' + key); return v ? JSON.parse(v) : fallback; } catch(e) { return fallback; }
  }
  function storeSet(key, value) {
    try { localStorage.setItem('avis_' + key, JSON.stringify(value)); } catch(e) {}
  }
  function storeRemove(key) {
    try { localStorage.removeItem('avis_' + key); } catch(e) {}
  }

  // ---- Sidebar Helpers ----
  function toggleSidebar(id = 'sidebar') {
    const sb = document.getElementById(id);
    if (sb) sb.classList.toggle('open');
  }

  function closeSidebarOnClickOutside(sidebarId = 'sidebar', toggleSelector = '.mobile-toggle') {
    document.addEventListener('click', (e) => {
      const sidebar = document.getElementById(sidebarId);
      if (!sidebar || !sidebar.classList.contains('open')) return;
      if (!sidebar.contains(e.target) && !e.target.closest(toggleSelector)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // ---- Modal Helpers ----
  function showModal(overlayId) {
    const el = document.getElementById(overlayId);
    if (el) el.classList.add('show');
  }

  function hideModal(overlayId) {
    const el = document.getElementById(overlayId);
    if (el) el.classList.remove('show');
  }

  function closeModalOnOverlayClick() {
    document.addEventListener('click', (e) => {
      if (e.target.classList.contains('modal-overlay') && e.target.classList.contains('show')) {
        e.target.classList.remove('show');
      }
    });
  }

  // ---- Keyboard Shortcut Registry ----
  const shortcuts = {};
  function addShortcut(key, modifiers, fn, description = '') {
    const id = [...modifiers.sort(), key].join('+');
    shortcuts[id] = { fn, description };
  }

  document.addEventListener('keydown', (e) => {
    const mods = [];
    if (e.ctrlKey || e.metaKey) mods.push('mod');
    if (e.altKey) mods.push('alt');
    if (e.shiftKey) mods.push('shift');

    const id = [...mods.sort(), e.key.toLowerCase()].join('+');
    if (shortcuts[id]) {
      // Don't trigger if user is typing in an input (unless mod-only shortcut)
      const tag = e.target.tagName;
      if (!['INPUT', 'TEXTAREA', 'SELECT'].includes(tag) || mods.length > 0) {
        e.preventDefault();
        shortcuts[id].fn();
      }
    }
  });

  return {
    $, $$, create, debounce, throttle,
    formatNumber, formatPercent, formatSI, formatDate, formatTime, formatDateTime,
    copyToClipboard, uid,
    storeGet, storeSet, storeRemove,
    toggleSidebar, closeSidebarOnClickOutside,
    showModal, hideModal, closeModalOnOverlayClick,
    addShortcut,
  };
})();
