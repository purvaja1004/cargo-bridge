// CargoBridge API Client
// All frontend pages include this file

const API_BASE = 'http://localhost:8000';

const CB = {
  // ── Auth ───────────────────────────────────────────────────────────────────
  getToken() { return localStorage.getItem('cb_token'); },
  getUser()  { const u = localStorage.getItem('cb_user'); return u ? JSON.parse(u) : null; },
  setAuth(token, user) {
    localStorage.setItem('cb_token', token);
    localStorage.setItem('cb_user', JSON.stringify(user));
  },
  logout() {
    localStorage.removeItem('cb_token');
    localStorage.removeItem('cb_user');
  },
  isLoggedIn() { return !!this.getToken(); },

  // ── HTTP ───────────────────────────────────────────────────────────────────
  async request(method, path, body = null) {
    const headers = { 'Content-Type': 'application/json' };
    const token = this.getToken();
    if (token) headers['Authorization'] = `Bearer ${token}`;
    const opts = { method, headers };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(API_BASE + path, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) throw new Error(data.detail || `Request failed: ${res.status}`);
    return data;
  },
  get(path)         { return this.request('GET', path); },
  post(path, body)  { return this.request('POST', path, body); },
  put(path, body)   { return this.request('PUT', path, body); },

  // ── Auth API ───────────────────────────────────────────────────────────────
  async login(email, password) {
    const res = await this.post('/login', { email, password });
    this.setAuth(res.token, res.user);
    return res.user;
  },
  async signup(data) {
    const res = await this.post('/signup', data);
    this.setAuth(res.token, res.user);
    return res.user;
  },

  // ── Listings API ───────────────────────────────────────────────────────────
  getListings()                    { return this.get('/listings'); },
  searchListings(params)           { return this.get('/listings/search?' + new URLSearchParams(params)); },
  createListing(data)              { return this.post('/listings', data); },
  updateListing(id, data)          { return this.put(`/listings/${id}`, data); },
  myListings()                     { return this.get('/my-listings'); },

  // ── Bookings API ───────────────────────────────────────────────────────────
  book(data)                       { return this.post('/book', data); },
  myBookings()                     { return this.get('/my-bookings'); },

  // ── Forwarder API ──────────────────────────────────────────────────────────
  getRequests()                    { return this.get('/requests'); },
  approveRequest(id)               { return this.post(`/approve/${id}`); },
  rejectRequest(id, message)       { return this.post(`/reject/${id}`, { message }); },

  // ── Tracking API ───────────────────────────────────────────────────────────
  track(bookingId)                 { return this.get(`/track/${bookingId}`); },
  predictions(params)              { return this.get('/predictions?' + new URLSearchParams(params || {})); },
  stats()                          { return this.get('/stats'); },
  co2(params)                      { return this.get('/co2?' + new URLSearchParams(params)); },

  // ── Helpers ────────────────────────────────────────────────────────────────
  formatRupees(n) {
    return 'Rs. ' + Math.round(n).toLocaleString('en-IN');
  },
  daysUntil(dateStr) {
    const diff = new Date(dateStr) - new Date();
    return Math.max(0, Math.ceil(diff / 86400000));
  },
  urgency(days) {
    if (days <= 4)  return { label: 'Book Now',     cls: 'urgency-high' };
    if (days <= 9)  return { label: 'Filling Fast', cls: 'urgency-med' };
    return               { label: 'Available',     cls: 'urgency-low'  };
  },
};

// ── Toast helper (works on all pages) ─────────────────────────────────────
function showToast(msg, sub = '') {
  let t = document.getElementById('_cbToast');
  if (!t) {
    t = document.createElement('div');
    t.id = '_cbToast';
    t.style.cssText = `position:fixed;bottom:2rem;right:2rem;z-index:9999;
      background:#112240;border:1px solid rgba(201,168,76,0.35);border-radius:12px;
      padding:1rem 1.4rem;min-width:260px;box-shadow:0 8px 32px rgba(0,0,0,0.4);
      animation:cbSlideIn .3s ease;display:none;`;
    document.body.appendChild(t);
    const style = document.createElement('style');
    style.textContent = `@keyframes cbSlideIn{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}`;
    document.head.appendChild(style);
  }
  t.innerHTML = `<div style="font-weight:600;font-size:.92rem;color:#f8f6f1">${msg}</div>
    ${sub ? `<div style="font-size:.8rem;color:#8892a4;margin-top:.2rem">${sub}</div>` : ''}`;
  t.style.display = 'block';
  clearTimeout(t._timer);
  t._timer = setTimeout(() => { t.style.display = 'none'; }, 3500);
}

function showError(msg) {
  showToast('⚠ ' + msg, 'Please try again');
}

window.CB = CB;
