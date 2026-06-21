/* ============================================================
   Avis API Client — Unified fetch wrapper for all 37 pages
   Usage:
     const data = await API.get('/api/avis/health');
     const result = await API.post('/api/avis/chat', { message: 'hi' });
   ============================================================ */

const API = (() => {
  const BASE = '';
  const TIMEOUT_MS = 30000;

  let authToken = (() => {
    // Try to read token injected by Flask template
    if (typeof AUTH_TOKEN !== 'undefined') return AUTH_TOKEN;
    // Fallback: check localStorage
    try { return localStorage.getItem('avis_auth_token'); } catch(e) { return null; }
  })();

  function setAuthToken(token) {
    authToken = token;
    try { localStorage.setItem('avis_auth_token', token); } catch(e) {}
  }

  function clearAuthToken() {
    authToken = null;
    try { localStorage.removeItem('avis_auth_token'); } catch(e) {}
  }

  function buildHeaders(extra = {}) {
    const h = { 'Content-Type': 'application/json', ...extra };
    if (authToken) h['Authorization'] = `Bearer ${authToken}`;
    return h;
  }

  async function request(method, url, body = null, opts = {}) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), opts.timeout || TIMEOUT_MS);

    try {
      const resp = await fetch(BASE + url, {
        method,
        headers: buildHeaders(opts.headers),
        body: body ? JSON.stringify(body) : null,
        signal: controller.signal,
      });

      clearTimeout(timer);

      // Handle 401 — redirect to login
      if (resp.status === 401 && !opts.skipAuthRedirect) {
        clearAuthToken();
        if (typeof window !== 'undefined' && window.location) {
          window.location.href = '/login';
        }
        throw new Error('Authentication required');
      }

      // Handle other errors
      if (!resp.ok && !opts.raw) {
        let detail = '';
        try { const err = await resp.json(); detail = err.error || err.message || ''; } catch(e) {}
        throw new Error(detail || `HTTP ${resp.status}: ${resp.statusText}`);
      }

      // Parse response
      if (opts.raw) return resp;
      const text = await resp.text();
      try { return JSON.parse(text); } catch(e) { return text; }

    } catch (e) {
      clearTimeout(timer);
      if (e.name === 'AbortError') throw new Error('Request timed out');
      throw e;
    }
  }

  return {
    get: (url, opts) => request('GET', url, null, opts),
    post: (url, body, opts) => request('POST', url, body, opts),
    put: (url, body, opts) => request('PUT', url, body, opts),
    delete: (url, opts) => request('DELETE', url, null, opts),
    setAuthToken,
    clearAuthToken,
    getAuthToken: () => authToken,
  };
})();
