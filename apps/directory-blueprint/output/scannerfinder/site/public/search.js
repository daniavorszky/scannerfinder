// Directory search. No server: the index is a JSON file built with the site.
// One box for a business name or a service, one for the city. Each box suggests as you type:
// services first (a pick becomes a chip in the box), then businesses (a pick opens the listing),
// and cities on the right. Nothing searches until Search is pressed; results render on /search/.
(function () {
  var form = document.getElementById('dir-search');
  if (!form) return;
  var what = form.querySelector('[name=s]'), near = form.querySelector('[name=near]');
  var listWhat = document.getElementById('sugg-what'), listNear = document.getElementById('sugg-near');
  var pickedList = document.getElementById('filter-picked');
  var results = document.getElementById('search-results');
  var onSearchPage = !!(results && results.dataset.page === 'search');
  var boxes = Array.prototype.slice.call(form.querySelectorAll('[name=f]'));
  // Technology dropdown: its value is one of the device filters; it is never shown as a chip.
  var tech = form.querySelector('[name=tech]');
  var techLabels = tech ? Array.prototype.slice.call(tech.options).map(function (o) { return o.value; }).filter(Boolean) : [];
  function isTech(v) { return techLabels.indexOf(v) !== -1; }
  function syncTech() { if (!tech) return; boxes.forEach(function (i) { if (isTech(i.value)) i.checked = i.value === tech.value; }); }
  function markTech() { if (tech) tech.classList.toggle('set', !!tech.value); }
  if (tech) tech.addEventListener('change', function () { syncTech(); renderPicked(); markTech(); });
  var index = null, loading = null;

  function load() {
    if (index) return Promise.resolve(index);
    if (!loading) loading = fetch(form.dataset.index).then(function (r) { return r.json(); }).then(function (j) { index = j; return j; });
    return loading;
  }
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, ''); }
  function words(s) { return norm(s).split(/[^a-z0-9]+/).filter(Boolean); }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function stars(r) { var f = Math.round(r); return '\u2605'.repeat(f) + '\u2606'.repeat(5 - f); }
  function score(l) { return l.r * Math.log10(l.v + 1); }
  function hide(list) { list.hidden = true; list.innerHTML = ''; }
  function hideAll() { hide(listWhat); hide(listNear); }

  // Service filters: the hidden checkboxes hold the state, the chips show it.
  function picked() { return boxes.filter(function (i) { return i.checked; }).map(function (i) { return i.value; }); }
  function setFilter(label, on) { boxes.forEach(function (i) { if (i.value === label) i.checked = on; }); renderPicked(); }
  function renderPicked() {
    pickedList.innerHTML = picked().filter(function (f) { return !isTech(f); }).map(function (f) {
      return '<li>' + esc(f) + '<button type="button" data-remove="' + esc(f) + '" aria-label="Remove ' + esc(f) + '">\u00d7</button></li>';
    }).join('');
  }
  function serviceMatches(q) {
    var n = norm(q), have = picked();
    return boxes.map(function (i) { return i.value; }).filter(function (v) {
      if (have.indexOf(v) !== -1 || isTech(v)) return false;
      return words(v).some(function (w) { return w.indexOf(n) === 0; }) || norm(v).indexOf(n) === 0;
    });
  }
  function matchFilters(l, fs) { return fs.every(function (f) { return l.a.indexOf(f) !== -1; }); }

  // Each typed word must start a word in the name or in a confirmed service, so "tr" finds a business
  // whose name starts with "Tr" and not every business whose services mention "contractor".
  function matchWhat(l, q) {
    if (!q) return true;
    var hay = ' ' + norm(l.n).replace(/[^a-z0-9]+/g, ' ') + ' ' + norm(l.a.join(' ')).replace(/[^a-z0-9]+/g, ' ') + ' ';
    return words(q).every(function (w) { return hay.indexOf(' ' + w) !== -1; });
  }
  function matchNear(l, q) {
    if (!q) return true;
    var n = norm(q);
    // The location box offers countries and regions, and a visitor may also type a town: any of the four counts.
    return [l.c, l.t, l.g, l.k].some(function (v) { return norm(v).indexOf(n) === 0; });
  }
  // Practitioners per country ('k:' + name), region ('g:' + name) and town ('t:' + region + '|' + town) for one technology, cached.
  var techCountCache = {};
  function techCounts(t) {
    if (techCountCache[t]) return techCountCache[t];
    var m = {};
    index.listings.forEach(function (l) { if (l.a.indexOf(t) === -1) return; m['k:' + l.k] = (m['k:' + l.k] || 0) + 1; m['g:' + l.g] = (m['g:' + l.g] || 0) + 1; m['t:' + l.g + '|' + norm(l.c)] = (m['t:' + l.g + '|' + norm(l.c)] || 0) + 1; });
    return (techCountCache[t] = m);
  }
  // A place matches when its name or one of its local spellings (c.a: București for Bucharest) starts with the text.
  function placeMatch(c, q) { var n = norm(q); return [c.n].concat(c.a || []).some(function (v) { return norm(v).indexOf(n) === 0; }); }
  function cityMatches(q) {
    return index.cities.filter(function (c) { return placeMatch(c, q); }).slice(0, 8);
  }
  function ratingHtml(l) { return l.v ? '<span class="rt"><i aria-hidden="true">\u2605</i> ' + l.r.toFixed(1) + ' <small>(' + l.v + ')</small></span>' : ''; }

  function showWhat() {
    var q = what.value.trim();
    if (q.length < 2) return hide(listWhat);
    load().then(function () {
      var fs = picked(), html = '';
      var services = serviceMatches(q);
      if (services.length) {
        html += '<li class="group">Services</li>' + services.map(function (v) {
          return '<li><button type="button" data-pick="' + esc(v) + '"><b>' + esc(v) + '</b><span>add filter</span></button></li>';
        }).join('');
      }
      var hits = index.listings.filter(function (l) { return matchWhat(l, q) && matchNear(l, near.value.trim()) && matchFilters(l, fs); })
        .sort(function (a, b) { return score(b) - score(a); }).slice(0, 6);
      if (hits.length) {
        html += (services.length ? '<li class="group">Businesses</li>' : '') + hits.map(function (l) {
          return '<li><a href="' + l.p + '"><b>' + esc(l.n) + '</b><span>' + esc(l.c) + ratingHtml(l) + '</span></a></li>';
        }).join('');
      }
      if (!html) return hide(listWhat);
      listWhat.innerHTML = html; listWhat.hidden = false;
    });
  }
  function showNear() {
    var q = near.value.trim();
    load().then(function () {
      // With a technology picked, each place shows how many practitioners there use it; places with none are left out.
      var t = tech && tech.value, counts = t ? techCounts(t) : null;
      var pool = q ? index.cities.filter(function (c) { return placeMatch(c, q); }) : index.cities;
      var key = function (c) { return c.k ? 'k:' + c.n : c.w ? 't:' + c.w + '|' + norm(c.n) : 'g:' + c.n; };
      var hits = counts ? pool.filter(function (c) { return counts[key(c)]; }).sort(function (a, b) { return (b.k || 0) - (a.k || 0) || counts[key(b)] - counts[key(a)]; }) : pool;
      hits = hits.slice(0, counts && !q ? 10 : 8);
      var html = '';
      if ('geolocation' in navigator) html += '<li><button type="button" class="use-location">Near me: use my location</button></li>';
      html += hits.map(function (c, i) {
        var n = counts ? counts[key(c)] : c.c;
        // A thin rule between the countries and the regions that follow them.
        var sep = i > 0 && hits[i - 1].k && !c.k ? ' class="sep"' : '';
        return '<li' + sep + '><button type="button" data-city="' + esc(c.n) + '"><b>' + esc(c.n) + (c.w ? ' <small>' + esc(c.w) + '</small>' : '') + '</b><span>' + n + (counts ? ' with ' + esc(t) : ' listed') + '</span></button></li>';
      }).join('');
      if (counts && !hits.length) html += '<li class="group">No ' + esc(t) + ' practitioners match that place</li>';
      listNear.innerHTML = html; listNear.hidden = false;
    });
  }
  // "Near me": the nearest listed practitioner decides the place. Its region when that region has a page,
  // otherwise its country (regions under the floor have no page). Nothing within MAX_KM: say so instead.
  var MAX_KM = 300;
  function nearestCity(lat, lng) {
    var best = null, bd = Infinity, rad = Math.PI / 180;
    index.listings.forEach(function (l) {
      if (!l.la && !l.lo) return;
      var a = Math.sin((l.la - lat) * rad / 2), b = Math.sin((l.lo - lng) * rad / 2);
      var d = 12742 * Math.asin(Math.sqrt(a * a + Math.cos(lat * rad) * Math.cos(l.la * rad) * b * b));
      if (d < bd) { bd = d; best = l; }
    });
    if (!best || bd > MAX_KM) return null;
    var place = function (n) { return index.cities.filter(function (c) { return c.n === n; })[0]; };
    return place(best.g) || place(best.k) || null;
  }

  // Results (search page only). The service the visitor asked for is shown first on each card.
  function chipsFor(l, q, fs) {
    var ws = words(q);
    var hit = l.a.filter(function (a) { return fs.indexOf(a) !== -1 || ws.some(function (w) { return norm(a).indexOf(w) !== -1; }); });
    var rest = l.a.filter(function (a) { return hit.indexOf(a) === -1; });
    return hit.concat(rest).slice(0, 3);
  }
  // Same tile as Card.astro: the logo, or two initials when none was found.
  function logoHtml(l) {
    if (l.o) return '<img class="logo-mark" src="' + esc(l.o) + '" alt="" width="48" height="48" loading="lazy">';
    var ini = l.n.replace(/[^\p{L}\p{N} ]/gu, '').split(/\s+/).filter(function (w) { return w && !/^(the|and|of|llc|ltd|inc)$/i.test(w); }).slice(0, 2).map(function (w) { return w[0].toUpperCase(); }).join('');
    return '<span class="logo-mark mono" aria-hidden="true">' + esc(ini) + '</span>';
  }
  // Results (search page): the region page's explorer (filters, map, cards; public/explorer.js), with the visitor's
  // technology and services ticked. The pool is one level wider than the place asked for, with that place ticked in the
  // place filter, so unticking it widens the search: a town -> its region's towns, a region -> its country's regions.
  function card(l, group, keyOf) {
    var keys = l.a.map(function (a) { return keyOf[a]; }).filter(Boolean).join(' ');
    return '<article class="card" data-attrs="' + esc(keys) + '" data-rating="' + (l.v ? l.r : 0) + '" data-reviews="' + l.v + '" data-town="' + esc(l[group] || '') + '"' +
      (l.la || l.lo ? ' data-lat="' + l.la + '" data-lng="' + l.lo + '"' : '') + ' data-name="' + esc(l.n) + '" data-path="' + esc(l.p) + '">' +
      '<div class="card-head">' + logoHtml(l) + '<h3><a href="' + l.p + '">' + esc(l.n) + '</a></h3></div>' +
      (l.v ? '<p class="rating"><span class="stars" aria-hidden="true">' + stars(l.r) + '</span> ' + l.r.toFixed(1) + ' <span class="meta">(' + l.v + ' reviews on Google)</span></p>' : '<p class="meta">No reviews yet</p>') +
      '<p class="meta">' + esc(l.c) + (group !== 'c' && l.g && l.g !== l.c ? ', ' + esc(l.g) : '') + (l.t ? ' (based in ' + esc(l.t) + ')' : '') + '</p>' +
      (l.a.length ? '<ul class="chips">' + chipsFor(l, '', []).map(function (a) { return '<li>' + esc(a) + '</li>'; }).join('') + '</ul>' : '') + '</article>';
  }
  function renderExplorer(pool, group, legend, tick, q, placeName, fs) {
    var ex = document.getElementById('explorer'), exForm = document.getElementById('ex-form');
    var groupOf = function (l) { return l[group] || ''; };
    var hits = pool.filter(function (l) { return matchFilters(l, fs) && (!tick || norm(groupOf(l)) === norm(tick)); });
    var whatText = (q ? '\u201c' + esc(q) + '\u201d' : '') + (fs.length ? (q ? ' with ' : '') + fs.map(esc).join(', ') : '');
    var head = (hits.length ? hits.length + ' result' + (hits.length === 1 ? '' : 's') + ' for ' : 'No listings match ') + whatText + (placeName ? ' near ' + esc(placeName) : '');
    results.innerHTML = '<div class="results-head"><h2>' + head + '</h2><button type="button" class="btn ghost small" id="search-clear">Clear</button></div>' +
      (hits.length ? '' : '<p>Try a shorter word, a different spelling, fewer services, or pick a place from the list.</p>');
    results.hidden = false;
    // Matomo Site Search, once per distinct search: zero-result searches are the white-space report (track.js).
    var sk = [q, placeName, fs.join(', '), tick || ''].join('|');
    if (window.sfSearch && window.sfLastSearch !== sk) { window.sfLastSearch = sk; window.sfSearch([q, placeName].filter(Boolean).join(' near '), fs.join(', '), hits.length); }
    if (!hits.length || !ex) { if (ex) ex.hidden = true; return; }
    // Technology and option boxes: counts within the pool, the searched ones ticked, empty ones hidden.
    var keyOf = {};
    Array.prototype.forEach.call(exForm.querySelectorAll('input[name=attr]'), function (i) {
      keyOf[i.dataset.label] = i.value;
      var n = pool.filter(function (l) { return l.a.indexOf(i.dataset.label) !== -1; }).length;
      i.checked = fs.indexOf(i.dataset.label) !== -1;
      i.parentNode.querySelector('small').textContent = n;
      i.parentNode.style.display = !n && !i.checked ? 'none' : '';
    });
    Array.prototype.forEach.call(exForm.querySelectorAll('fieldset'), function (f) {
      var ls = f.querySelectorAll('label.ex-check'); if (ls.length) f.style.display = Array.prototype.every.call(ls, function (x) { return x.style.display === 'none'; }) ? 'none' : '';
    });
    // Place filter: towns, regions or countries in the pool, the searched place ticked.
    var counts = {};
    pool.forEach(function (l) { var g = groupOf(l); if (g) counts[g] = (counts[g] || 0) + 1; });
    var places = Object.keys(counts).sort(function (a, b) { return counts[b] - counts[a] || a.localeCompare(b); });
    var fsPlace = document.getElementById('ex-place');
    fsPlace.querySelector('legend').textContent = legend;
    fsPlace.querySelector('.ex-towns').innerHTML = places.map(function (g) {
      return '<label class="ex-check"><input type="checkbox" name="town" value="' + esc(g) + '"' + (tick && norm(g) === norm(tick) ? ' checked' : '') + ' /> <span>' + esc(g) + '</span> <small>' + counts[g] + '</small></label>';
    }).join('');
    fsPlace.style.display = places.length < 2 && !tick ? 'none' : '';
    document.getElementById('ex-grid').innerHTML = pool.map(function (l) { return card(l, group, keyOf); }).join('');
    document.getElementById('ex-total').textContent = pool.length;
    ex.hidden = false;
    if (window.sfExplorerInit) window.sfExplorerInit();
  }
  function runSearch(q, n, fs) {
    load().then(function () {
      // A typed prefix such as "Bucur" is resolved to the place it starts (Bucharest), so the results say "near <that place>".
      var place = n ? cityMatches(n)[0] || null : null;
      if (place && place.n !== n) near.value = place.n;
      var base = index.listings.filter(function (l) { return matchWhat(l, q); });
      var pool, group = 'c', legend = 'Town', tick = '';
      if (!place && n) pool = base.filter(function (l) { return matchNear(l, n); });
      else if (!place) { pool = base; group = 'k'; legend = 'Country'; }
      else if (place.k) { pool = base.filter(function (l) { return l.k === place.n; }); group = 'g'; legend = 'Region'; }
      else if (place.w) { pool = base.filter(function (l) { return l.g === place.w; }); tick = place.n; }
      else {
        var co = (index.listings.filter(function (l) { return l.g === place.n; })[0] || {}).k;
        pool = base.filter(function (l) { return l.k === co; }); group = 'g'; legend = 'Region'; tick = place.n;
      }
      pool.sort(function (a, b) { return score(b) - score(a); });
      renderExplorer(pool, group, legend, tick, q, place ? place.n : n, fs);
    });
  }

  // Only one list is open at a time.
  what.addEventListener('input', function () { hideAll(); showWhat(); });
  what.addEventListener('focus', function () { load(); hideAll(); showWhat(); });
  near.addEventListener('input', function () { hideAll(); showNear(); });
  near.addEventListener('focus', function () { hideAll(); showNear(); });
  what.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') hide(listWhat);
    if (e.key === 'Backspace' && !what.value) { var last = picked().pop(); if (last) setFilter(last, false); }
  });
  near.addEventListener('keydown', function (e) { if (e.key === 'Escape') hide(listNear); });
  document.addEventListener('click', function (e) { if (!form.contains(e.target)) hideAll(); });

  // Picks fill the boxes; only Search (or Enter) runs the search.
  listWhat.addEventListener('click', function (e) {
    var b = e.target.closest('[data-pick]');
    if (b) { setFilter(b.dataset.pick, true); what.value = ''; hide(listWhat); what.focus(); }
  });
  pickedList.addEventListener('click', function (e) {
    var b = e.target.closest('[data-remove]');
    if (b) { setFilter(b.dataset.remove, false); what.focus(); }
  });
  listNear.addEventListener('click', function (e) {
    var a = e.target.closest('[data-city]'), b = e.target.closest('.use-location');
    if (a) { near.value = a.dataset.city; hide(listNear); near.focus(); }
    if (b) {
      b.textContent = 'Finding the nearest city\u2026';
      navigator.geolocation.getCurrentPosition(function (pos) {
        var c = nearestCity(pos.coords.latitude, pos.coords.longitude);
        if (c) { near.value = c.n; hide(listNear); near.focus(); }
        else b.textContent = 'No listed practitioner within ' + MAX_KM + ' km. Pick a country instead.';
      }, function () { b.textContent = 'Location not available. Type a city instead.'; }, { timeout: 8000, maximumAge: 600000 });
    }
  });
  form.addEventListener('submit', function (e) {
    e.preventDefault(); hideAll();
    syncTech();
    var q = what.value.trim(), n = near.value.trim(), fs = picked();
    var opt = tech && tech.selectedOptions[0];
    if (opt && opt.value && !q && fs.length === 1) {
      if (!n) { location.href = opt.dataset.path; return; }
      var cp = JSON.parse(opt.dataset.countries || '{}')[n.toLowerCase()];
      if (cp) { location.href = cp; return; }
    }
    if (!q && !fs.length && !n) { what.focus(); return; }
    var qs = new URLSearchParams();
    if (q) qs.set('s', q); if (n) qs.set('near', n); fs.forEach(function (f) { qs.append('f', f); });
    if (onSearchPage) {
      load().then(function () {
        // Only a city: go to its page.
        if (!q && !fs.length) { var c = cityMatches(n)[0]; if (c) { location.href = c.p; return; } }
        location.href = '/search/?' + qs.toString();
      });
      return;
    }
    location.href = '/search/?' + qs.toString();
  });
  if (onSearchPage) {
    var qs0 = new URLSearchParams(location.search);
    what.value = qs0.get('s') || ''; near.value = qs0.get('near') || '';
    qs0.getAll('f').forEach(function (f) { setFilter(f, true); if (tech && isTech(f)) tech.value = f; });
    if (tech && qs0.get('tech')) { tech.value = qs0.get('tech'); syncTech(); renderPicked(); }
    markTech();
    var q0 = what.value.trim(), n0 = near.value.trim(), f0 = picked();
    if (q0 || f0.length) runSearch(q0, n0, f0);
    else if (n0) load().then(function () { var c = cityMatches(n0)[0]; if (c) location.href = c.p; });
    results.addEventListener('click', function (e) {
      if (e.target.id === 'search-clear') location.href = '/search/';
    });
  }
})();
