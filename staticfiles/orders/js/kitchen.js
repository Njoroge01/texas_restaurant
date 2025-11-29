// orders/static/orders/js/kitchen.js
(function () {
  'use strict';

  const API_DATA = '/orders/kitchen/data/';
  const ADVANCE_URL = (id) => `/orders/kitchen/order/${id}/advance/`;
  const POLL_INTERVAL = 5000; // ms

  function elt(tag, cls, inner) {
    const e = document.createElement(tag);
    if (cls) e.className = cls;
    if (inner !== undefined) e.innerHTML = inner;
    return e;
  }

  function renderOrderCard(o) {
    const card = elt('div', 'order-card');
    const header = elt('div', 'order-header', `<strong>#${o.id}</strong> — ${o.customer_name || '(Walk-in)'}`);
    const meta = elt('div', 'order-meta', `Table: ${o.table_number || '-'} · ${o.created_at ? new Date(o.created_at).toLocaleTimeString() : ''}`);
    const totals = elt('div', 'order-totals', `Total: ${o.total || o.subtotal || '0.00'}`);

    const btn = elt('button', 'advance-btn', 'Move →');
    btn.dataset.orderId = o.id;

    card.appendChild(header);
    card.appendChild(meta);
    card.appendChild(totals);
    card.appendChild(btn);

    return card;
  }

  async function fetchData() {
    try {
      const res = await fetch(API_DATA, { credentials: 'same-origin' });
      if (!res.ok) throw new Error('Failed fetching data');
      const json = await res.json();
      populateColumns(json);
    } catch (err) {
      console.error('Kitchen fetch error', err);
    }
  }

  function clearElem(id) {
    const el = document.getElementById(id);
    if (!el) return;
    while (el.firstChild) el.removeChild(el.firstChild);
  }

  function populateColumns(data) {
    clearElem('pending-list');
    clearElem('in-progress-list');
    clearElem('ready-list');

    data.pending.forEach(o => document.getElementById('pending-list').appendChild(renderOrderCard(o)));
    data.in_progress.forEach(o => document.getElementById('in-progress-list').appendChild(renderOrderCard(o)));
    data.ready.forEach(o => document.getElementById('ready-list').appendChild(renderOrderCard(o)));
    attachButtons();
  }

  function attachButtons() {
    document.querySelectorAll('.advance-btn').forEach(btn => {
      // avoid double-binding
      if (btn.dataset.bound === '1') return;
      btn.dataset.bound = '1';
      btn.addEventListener('click', async function () {
        const id = this.dataset.orderId;
        await advanceOrder(id);
        // refresh after action
        await fetchData();
      });
    });
  }

  // CSRF helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i=0; i<cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length+1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length+1));
          break;
        }
      }
    }
    return cookieValue;
  }

  async function advanceOrder(id) {
    const url = ADVANCE_URL(id);
    const csrftoken = getCookie('csrftoken');
    try {
      const r = await fetch(url, {
        method: 'POST',
        credentials: 'same-origin',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': csrftoken
        }
      });
      const json = await r.json();
      if (!r.ok) {
        console.error('Advance failed', json);
      }
    } catch (e) {
      console.error('Advance error', e);
    }
  }

  // init
  document.addEventListener('DOMContentLoaded', function () {
    fetchData();
    setInterval(fetchData, POLL_INTERVAL);
  });

})();
