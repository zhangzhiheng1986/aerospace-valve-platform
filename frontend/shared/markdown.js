/* ============================================================
   Avis Markdown — Safe Markdown renderer using marked.js
   Loads marked from CDN on first use (lazy). Falls back to
   basic formatting if CDN is unavailable.

   Usage:
     const html = await MD.render('**bold** and `code`');
     // or for sync basic fallback:
     const html = MD.renderBasic('**bold**');
   ============================================================ */

const MD = (() => {
  let markedLoaded = false;
  let markedLib = null;

  // Configuration for marked
  const MARKED_OPTIONS = {
    breaks: true,
    gfm: true,
  };

  async function loadMarked() {
    if (markedLoaded) return markedLib;

    try {
      // Try to load marked from CDN
      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/marked@12/marked.min.js';

      await new Promise((resolve, reject) => {
        script.onload = resolve;
        script.onerror = reject;
        setTimeout(() => reject(new Error('timeout')), 5000);
        document.head.appendChild(script);
      });

      if (typeof marked !== 'undefined') {
        markedLib = marked;
        if (markedLib.setOptions) markedLib.setOptions(MARKED_OPTIONS);
        markedLoaded = true;
      }
    } catch (e) {
      console.warn('MD: marked.js failed to load, using basic renderer');
      markedLoaded = true; // Don't retry
    }

    return markedLib;
  }

  // Safe basic renderer (XSS-safe, no innerHTML of raw input)
  function renderBasic(text) {
    if (!text) return '';

    // Escape HTML first
    const div = document.createElement('div');
    div.textContent = text;
    let safe = div.textContent;

    // Apply simple formatting on escaped text
    safe = safe.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    safe = safe.replace(/\*(.+?)\*/g, '<em>$1</em>');
    safe = safe.replace(/`([^`]+)`/g, '<code>$1</code>');
    safe = safe.replace(/^### (.+)$/gm, '<h4>$1</h4>');
    safe = safe.replace(/^## (.+)$/gm, '<h3>$1</h3>');
    safe = safe.replace(/^# (.+)$/gm, '<h2>$1</h2>');
    safe = safe.replace(/^-{3,}$/gm, '<hr>');
    safe = safe.replace(/^[*-] (.+)$/gm, '<li>$1</li>');
    safe = safe.replace(/(<li>.*<\/li>\s*)+/g, '<ul>$&</ul>');
    safe = safe.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
    safe = safe.replace(/\n\n/g, '</p><p>');
    safe = safe.replace(/\n/g, '<br>');

    return '<p>' + safe + '</p>';
  }

  // Render markdown to safe HTML
  async function render(text) {
    if (!text) return '';

    const lib = await loadMarked();

    if (lib && typeof lib.parse === 'function') {
      // marked v5+ uses .parse()
      return lib.parse(text, { ...MARKED_OPTIONS, async: false });
    } else if (lib && typeof lib === 'function') {
      // marked v4 uses direct call
      return lib(text, MARKED_OPTIONS);
    }

    // Fallback to basic renderer
    return renderBasic(text);
  }

  // Preload (call early to prime the CDN cache)
  async function preload() {
    try { await loadMarked(); } catch (e) {}
  }

  return { render, renderBasic, preload, loadMarked };
})();
