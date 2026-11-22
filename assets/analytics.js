/* Google Analytics 4 for wedbybetty.com.
 * GA4 Measurement ID (from
 * GA4 > Admin > Data streams). Nothing loads unless it matches G-XXXXXXXXXX.
 * Tracking is skipped on localhost and Netlify deploy previews. */
(function () {
  var GA_MEASUREMENT_ID = 'G-XSXMZG8KS7';
  var host = location.hostname;
  var isProd = host === 'wedbybetty.com' || host === 'www.wedbybetty.com';
  if (!/^G-[A-Z0-9]+$/.test(GA_MEASUREMENT_ID) || !isProd) return;

  var s = document.createElement('script');
  s.async = true;
  s.src = 'https://www.googletagmanager.com/gtag/js?id=' + GA_MEASUREMENT_ID;
  document.head.appendChild(s);

  window.dataLayer = window.dataLayer || [];
  window.gtag = function () { dataLayer.push(arguments); };
  gtag('js', new Date());
  gtag('config', GA_MEASUREMENT_ID);

  // Conversion: the success pages are only reached after a form submission.
  var path = location.pathname;
  if (/^\/success(-es)?(\.html)?\/?$/.test(path)) {
    gtag('event', 'generate_lead', {
      method: 'contact_form',
      language: /-es/.test(path) ? 'es' : 'en'
    });
  }

  // Phone / email link clicks and form submissions.
  document.addEventListener('click', function (e) {
    var a = e.target.closest && e.target.closest('a[href^="tel:"], a[href^="mailto:"]');
    if (!a) return;
    var isTel = a.getAttribute('href').indexOf('tel:') === 0;
    gtag('event', isTel ? 'click_phone' : 'click_email', { link_url: a.getAttribute('href') });
  });
  document.addEventListener('submit', function (e) {
    var f = e.target;
    if (f && f.name) gtag('event', 'contact_form_submit', { form_name: f.name });
  });
})();
