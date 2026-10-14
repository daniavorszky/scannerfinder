// Matomo (self-hosted, EU: stats.mkstack.com, site 3). Cookieless, so no consent banner.
// Listing clicks → events  Listing / <phone|website|directions|maps|claim> / <slug>.
// Searches → Matomo Site Search (keyword, technology as category, result count; 0 = white space).
// Only scannerfinder.com sends hits; other hosts fill _paq without loading Matomo (for testing).
(function () {
  var _paq = window._paq = window._paq || [];
  var u = 'https://stats.mkstack.com/';
  var live = /(^|\.)scannerfinder\.com$/.test(location.hostname);
  _paq.push(['disableCookies']);
  _paq.push(['setTrackerUrl', u + 'matomo.php']);
  _paq.push(['setSiteId', '3']);
  _paq.push(['enableLinkTracking']);
  // The search page reports itself through sfSearch once results render, not as a plain page view.
  var q = new URLSearchParams(location.search);
  var searchPage = location.pathname === '/search/' && (q.get('s') || q.getAll('f').length);
  if (!searchPage) _paq.push(['trackPageView']);
  window.sfSearch = function (keyword, tech, results) {
    _paq.push(['trackSiteSearch', keyword || '(technology only)', tech || false, results]);
  };
  var el = document.querySelector('[data-sf-listing]');
  if (el) {
    var slug = el.getAttribute('data-sf-listing');
    document.addEventListener('click', function (e) {
      var a = e.target.closest && e.target.closest('a[href]');
      if (!a) return;
      var type = a.getAttribute('data-sf') || (a.getAttribute('href').indexOf('tel:') === 0 ? 'phone' : '');
      if (type) _paq.push(['trackEvent', 'Listing', type, slug]);
    });
  }
  if (!live) return;
  var g = document.createElement('script');
  g.async = true; g.src = u + 'matomo.js';
  document.head.appendChild(g);
})();
