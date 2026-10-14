// Region page explorer (src/components/ListingExplorer.astro): live filters, sort and a Leaflet map.
// The cards are already in the page; this only hides, reorders and numbers them, and keeps the pins in step.
// Results are paged 10 at a time (like mypeptidematch.com/clinics/<state>/<city>); the map shows the current page's pins.
(function () {
  var root = document.getElementById('explorer');
  if (!root) return;
  var form = document.getElementById('ex-form');
  var grid = document.getElementById('ex-grid');
  var sortSel = document.getElementById('ex-sort');
  var nEl = document.getElementById('ex-n');
  var empty = document.getElementById('ex-empty');
  var activeEl = root.querySelector('.ex-active');
  var mapEl = document.getElementById('ex-map');
  var cards = Array.prototype.slice.call(grid.querySelectorAll('.card'));
  cards.forEach(function (c, i) { c.dataset.order = i; });
  var rangeEl = document.getElementById('ex-range');
  var pagesEl = document.getElementById('ex-pages');
  var PER = 10, page = 1, lastShown = [];
  var map = null, layer = null, markers = {};

  // Mobile: the filter panel starts closed so the results come first.
  var panel = root.querySelector('.ex-panel');
  if (window.matchMedia('(max-width: 860px)').matches) panel.removeAttribute('open');

  function state() {
    var attrs = [], towns = [], rating = 0;
    Array.prototype.forEach.call(form.elements, function (el) {
      if (el.name === 'attr' && el.checked) attrs.push(el.value);
      if (el.name === 'town' && el.checked) towns.push(el.value);
      if (el.name === 'rating' && el.checked) rating = parseFloat(el.value) || 0;
    });
    return { attrs: attrs, towns: towns, rating: rating };
  }
  function matches(c, s) {
    var has = ' ' + (c.dataset.attrs || '') + ' ';
    if (!s.attrs.every(function (k) { return has.indexOf(' ' + k + ' ') !== -1; })) return false;
    if (s.towns.length && s.towns.indexOf(c.dataset.town) === -1) return false;
    if (s.rating && !(parseFloat(c.dataset.rating) >= s.rating)) return false;
    return true;
  }
  function sorter(mode) {
    var r = function (c) { return parseFloat(c.dataset.rating) || 0; }, v = function (c) { return parseInt(c.dataset.reviews, 10) || 0; };
    if (mode === 'rating') return function (a, b) { return r(b) - r(a) || v(b) - v(a); };
    if (mode === 'reviews') return function (a, b) { return v(b) - v(a) || r(b) - r(a); };
    if (mode === 'name') return function (a, b) { return a.dataset.name.localeCompare(b.dataset.name); };
    return function (a, b) { return a.dataset.order - b.dataset.order; };
  }

  // Filters and sort start again from page 1.
  function apply() {
    var s = state();
    lastShown = cards.filter(function (c) { return matches(c, s); }).sort(sorter(sortSel.value));
    lastShown.forEach(function (c, i) { c.dataset.pin = i + 1; grid.appendChild(c); });
    cards.forEach(function (c) { if (lastShown.indexOf(c) === -1) { delete c.dataset.pin; grid.appendChild(c); } });
    nEl.textContent = lastShown.length;
    empty.hidden = lastShown.length > 0;
    var n = s.attrs.length + s.towns.length + (s.rating ? 1 : 0);
    activeEl.hidden = !n; activeEl.textContent = n ? n + ' active' : '';
    showPage(1, false);
  }
  function showPage(p, scroll) {
    var total = Math.max(1, Math.ceil(lastShown.length / PER));
    page = Math.min(Math.max(1, p), total);
    var from = (page - 1) * PER, to = Math.min(from + PER, lastShown.length);
    var onPage = lastShown.slice(from, to);
    cards.forEach(function (c) { c.hidden = onPage.indexOf(c) === -1; });
    if (rangeEl) rangeEl.textContent = lastShown.length > PER ? ' · showing ' + (from + 1) + '–' + to : '';
    renderPager(total);
    drawPins(onPage);
    if (scroll) root.querySelector('.ex-bar').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
  // 1 … 4 5 6 … 12: first, last, and the current page with one neighbour each side.
  function renderPager(total) {
    if (!pagesEl) return;
    pagesEl.hidden = total < 2;
    if (total < 2) { pagesEl.innerHTML = ''; return; }
    var nums = [];
    for (var i = 1; i <= total; i++) if (i === 1 || i === total || Math.abs(i - page) <= 1) nums.push(i);
    var html = '<button type="button" class="ex-pg ex-pg-step" data-p="' + (page - 1) + '" aria-label="Previous page"' + (page === 1 ? ' disabled' : '') + '>‹</button>';
    nums.forEach(function (i, k) {
      if (k && i - nums[k - 1] > 1) html += '<span class="ex-pg-gap" aria-hidden="true">…</span>';
      html += '<button type="button" class="ex-pg" data-p="' + i + '"' + (i === page ? ' aria-current="page"' : '') + ' aria-label="Page ' + i + '">' + i + '</button>';
    });
    html += '<button type="button" class="ex-pg ex-pg-step" data-p="' + (page + 1) + '" aria-label="Next page"' + (page === total ? ' disabled' : '') + '>›</button>';
    pagesEl.innerHTML = html;
  }

  // ---- map ----
  function esc(t) { return String(t).replace(/[&<>"]/g, function (ch) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[ch]; }); }
  function initMap() {
    if (map || !mapEl || !window.L) return;
    map = L.map(mapEl, { scrollWheelZoom: false, zoomControl: true });
    L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18, attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);
    layer = L.layerGroup().addTo(map);
    map.on('focus', function () { map.scrollWheelZoom.enable(); });
    map.on('blur', function () { map.scrollWheelZoom.disable(); });
    showPage(page, false);
  }
  function drawPins(shown) {
    if (!map) return;
    layer.clearLayers(); markers = {};
    var pts = [];
    shown.forEach(function (c) {
      var lat = parseFloat(c.dataset.lat), lng = parseFloat(c.dataset.lng);
      if (!isFinite(lat) || !isFinite(lng)) return;
      var num = c.dataset.pin;
      var icon = L.divIcon({ className: 'ex-pin', html: '<span><b>' + num + '</b></span>', iconSize: [30, 30], iconAnchor: [15, 30], popupAnchor: [0, -28] });
      var r = parseFloat(c.dataset.rating), v = parseInt(c.dataset.reviews, 10) || 0;
      var m = L.marker([lat, lng], { icon: icon, title: c.dataset.name, riseOnHover: true })
        .bindPopup('<a class="ex-pop-name" href="' + esc(c.dataset.path) + '">' + esc(c.dataset.name) + '</a>' +
          '<span class="ex-pop-meta">' + esc(c.dataset.town) + (v ? ' · ★ ' + r.toFixed(1) + ' (' + v + ')' : '') + '</span>');
      m.on('click', function () { highlight(c, false); });
      m.addTo(layer); markers[num] = m; pts.push([lat, lng]);
    });
    if (pts.length === 1) map.setView(pts[0], 12);
    else if (pts.length) map.fitBounds(pts, { padding: [28, 28], maxZoom: 13 });
  }
  if (pagesEl) pagesEl.addEventListener('click', function (e) {
    var b = e.target.closest('button[data-p]'); if (!b || b.disabled) return;
    showPage(parseInt(b.dataset.p, 10), true);
  });
  function highlight(card, scroll) {
    cards.forEach(function (c) { c.classList.remove('ex-hot'); });
    card.classList.add('ex-hot');
    if (scroll) card.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }
  // Card hover lifts its pin.
  grid.addEventListener('mouseover', function (e) {
    var c = e.target.closest('.card'); if (!c || !map) return;
    Object.keys(markers).forEach(function (k) { var el = markers[k].getElement(); if (el) el.classList.toggle('on', k === c.dataset.pin); });
  });
  grid.addEventListener('mouseleave', function () {
    Object.keys(markers).forEach(function (k) { var el = markers[k].getElement(); if (el) el.classList.remove('on'); });
  });

  // Load the map (and its tiles) only when it scrolls near the screen.
  if (mapEl) {
    var start = function () { if (window.L) initMap(); else window.addEventListener('load', initMap, { once: true }); };
    if ('IntersectionObserver' in window) {
      var io = new IntersectionObserver(function (es) { if (es.some(function (x) { return x.isIntersecting; })) { io.disconnect(); start(); } }, { rootMargin: '300px' });
      io.observe(mapEl);
    } else start();
  }

  // "View all <places>": the places under the floor (.ex-minor) stay hidden until asked for.
  var moreBtn = form.querySelector('.ex-more'), moreBox = form.querySelector('.ex-towns');
  if (moreBtn && moreBox) {
    var moreLabel = moreBtn.textContent;
    moreBtn.addEventListener('click', function () {
      var open = !moreBox.classList.contains('show-all');
      moreBox.classList.toggle('show-all', open);
      moreBtn.setAttribute('aria-expanded', open ? 'true' : 'false');
      moreBtn.textContent = open ? moreBtn.dataset.less : moreLabel;
    });
  }
  form.addEventListener('change', apply);
  form.addEventListener('reset', function () { setTimeout(apply, 0); });
  sortSel.addEventListener('change', apply);
  document.getElementById('ex-clear').addEventListener('click', function () { form.reset(); });
  apply();

  // Preset filters (2026-10-14, Dan). A device pill above the map (data-filter) or a region link on a device page (data-place)
  // filters this map in place; its href stays a real page for crawlers and no-JS. A link from another page carries
  // #device=<key>, #option=<key> and/or #place=<name>, and the map opens with those ticked.
  function box(name, value) {
    return Array.prototype.find.call(form.elements, function (el) { return el.name === name && el.value === value; }) || null;
  }
  function preset(attr, place, scroll) {
    var a = attr ? box('attr', attr) : null, p = place ? box('town', place) : null;
    if ((attr && !a) || (place && !p) || (!a && !p)) return false;
    Array.prototype.forEach.call(form.elements, function (el) {
      if (el.type === 'checkbox') el.checked = false;
      if (el.name === 'rating') el.checked = el.value === '0';
    });
    if (a) a.checked = true;
    if (p) { p.checked = true; if (moreBox && p.closest('.ex-minor') && !moreBox.classList.contains('show-all')) moreBtn.click(); }
    apply();
    if (scroll) root.scrollIntoView({ behavior: scroll, block: 'start' });
    var h = [];
    if (a) h.push((a.dataset.kind || 'device') + '=' + encodeURIComponent(attr));
    if (p) h.push('place=' + encodeURIComponent(place));
    history.replaceState(null, '', '#' + h.join('&'));
    return true;
  }
  document.addEventListener('click', function (e) {
    var link = e.target.closest && e.target.closest('a[data-filter], a[data-place]');
    if (!link || e.metaKey || e.ctrlKey || e.shiftKey || e.button) return;
    if (preset(link.dataset.filter, link.dataset.place, 'smooth')) e.preventDefault();
  });
  if (location.hash.length > 1) {
    var q = new URLSearchParams(location.hash.slice(1));
    preset(q.get('device') || q.get('option'), q.get('place'), 'auto');
  }
})();
