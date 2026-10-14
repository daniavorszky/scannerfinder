// Region page explorer (src/components/ListingExplorer.astro): live filters, sort and a Leaflet map.
// The cards are already in the page; this only hides, reorders and numbers them, and keeps the pins in step.
// On /search/ the explorer starts empty (data-deferred); public/search.js fills the cards and calls window.sfExplorerInit().
(function () {
  function init() {
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

  function apply() {
    var s = state();
    var shown = cards.filter(function (c) { return matches(c, s); }).sort(sorter(sortSel.value));
    cards.forEach(function (c) { c.hidden = true; delete c.dataset.pin; });
    shown.forEach(function (c, i) { c.hidden = false; c.dataset.pin = i + 1; grid.appendChild(c); });
    cards.filter(function (c) { return c.hidden; }).forEach(function (c) { grid.appendChild(c); });
    nEl.textContent = shown.length;
    empty.hidden = shown.length > 0;
    var n = s.attrs.length + s.towns.length + (s.rating ? 1 : 0);
    activeEl.hidden = !n; activeEl.textContent = n ? n + ' active' : '';
    drawPins(shown);
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
    apply();
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

  form.addEventListener('change', apply);
  form.addEventListener('reset', function () { setTimeout(apply, 0); });
  sortSel.addEventListener('change', apply);
  document.getElementById('ex-clear').addEventListener('click', function () { form.reset(); });
  apply();
  }
  window.sfExplorerInit = init;
  var r0 = document.getElementById('explorer');
  if (r0 && !r0.dataset.deferred) init();
})();
