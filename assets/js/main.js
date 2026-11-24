/* INTERNSHIP SPAIN — interacciones de la web */
(function () {
  'use strict';
  var body = document.body;
  var BASE = body.getAttribute('data-base') || '';

  /* ---------- Cabecera que se encoge al hacer scroll + botón "volver arriba" ---------- */
  var toTop = document.querySelector('.to-top');
  function onScroll() {
    var y = window.scrollY || window.pageYOffset;
    body.classList.toggle('is-scrolled', y > 40);
    if (toTop) toTop.classList.toggle('show', y > 400);
  }
  window.addEventListener('scroll', onScroll, { passive: true });
  onScroll();

  /* ---------- Animación de entrada de los iconos de la portada ---------- */
  var revealEls = document.querySelectorAll('.icon-strip');
  if (revealEls.length && 'IntersectionObserver' in window) {
    document.documentElement.classList.add('js-reveal');
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add('in-view'); io.unobserve(en.target); }
      });
    }, { threshold: 0.3 });
    revealEls.forEach(function (el) { io.observe(el); });
  }

  /* ---------- Menú móvil ---------- */
  var nav = document.querySelector('.main-nav');
  var toggle = document.querySelector('.menu-toggle');
  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
  }

  /* ---------- Banderas EN / ES (Google Translate, como en la web original) ---------- */
  function setGoogTrans(lang) {
    var v = lang === 'en' ? '' : '/en/' + lang;
    var host = location.hostname;
    var exp = v ? '' : '; expires=Thu, 01 Jan 1970 00:00:00 GMT';
    document.cookie = 'googtrans=' + v + '; path=/' + exp;
    document.cookie = 'googtrans=' + v + '; path=/; domain=' + host + exp;
    document.cookie = 'googtrans=' + v + '; path=/; domain=.' + host.replace(/^www\./, '') + exp;
  }
  function loadTranslate() {
    if (window.__gtLoaded) return;
    window.__gtLoaded = true;
    var holder = document.createElement('div');
    holder.id = 'google_translate_element';
    body.appendChild(holder);
    window.googleTranslateElementInit = function () {
      /* global google */
      new google.translate.TranslateElement({ pageLanguage: 'en', includedLanguages: 'en,es', autoDisplay: false }, 'google_translate_element');
    };
    var s = document.createElement('script');
    s.src = 'https://translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    s.async = true;
    document.head.appendChild(s);
  }
  document.querySelectorAll('.flags [data-lang]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      var lang = a.getAttribute('data-lang');
      setGoogTrans(lang);
      location.reload();
    });
  });
  if (/googtrans=\/en\/es/.test(document.cookie)) loadTranslate();

  /* ---------- Cookies: solo técnicas por defecto; mapas tras aceptar ---------- */
  var KEY = 'is_cookie_consent';
  function getConsent() { try { return localStorage.getItem(KEY); } catch (e) { return null; } }
  function setConsent(v) { try { localStorage.setItem(KEY, v); } catch (e) {} }
  var bar = document.querySelector('.cookie-bar');

  function loadMaps() {
    document.querySelectorAll('[data-map-src]').forEach(function (box) {
      var f = document.createElement('iframe');
      f.src = box.getAttribute('data-map-src');
      f.className = 'map-frame';
      f.style.height = box.offsetHeight ? box.offsetHeight + 'px' : '150px';
      f.loading = 'lazy';
      f.title = 'Map of Valencia';
      f.referrerPolicy = 'no-referrer-when-downgrade';
      box.replaceWith(f);
    });
  }
  function applyConsent() { if (getConsent() === 'all') loadMaps(); }
  if (bar) {
    if (!getConsent()) bar.classList.add('show');
    bar.querySelector('.cb-accept').addEventListener('click', function () { setConsent('all'); bar.classList.remove('show'); applyConsent(); });
    bar.querySelector('.cb-reject').addEventListener('click', function () { setConsent('essential'); bar.classList.remove('show'); });
  }
  document.querySelectorAll('.cookie-lock').forEach(function (b) {
    b.addEventListener('click', function () { if (bar) bar.classList.add('show'); });
  });
  document.querySelectorAll('[data-accept-cookies]').forEach(function (b) {
    b.addEventListener('click', function () { setConsent('all'); if (bar) bar.classList.remove('show'); applyConsent(); });
  });
  applyConsent();

  /* ---------- Buscador ---------- */
  var overlay = document.querySelector('.search-overlay');
  var index = null;
  function norm(s) { return (s || '').toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, ''); }
  function openSearch() {
    if (!overlay) return;
    overlay.classList.add('show');
    var input = overlay.querySelector('input');
    input.focus();
    if (!index) {
      fetch(BASE + '/search-index.json').then(function (r) { return r.json(); }).then(function (d) { index = d; runSearch(); }).catch(function () { index = []; });
    }
  }
  function runSearch() {
    var input = overlay.querySelector('input');
    var list = overlay.querySelector('.search-results');
    var q = norm(input.value.trim());
    list.innerHTML = '';
    if (!q || !index) return;
    var words = q.split(/\s+/);
    var hits = index.filter(function (p) {
      var hay = norm(p.title + ' ' + p.description + ' ' + p.text);
      return words.every(function (w) { return hay.indexOf(w) !== -1; });
    });
    if (!hits.length) { list.innerHTML = '<li><p>Nothing found. Sorry, but nothing matched your search terms.</p></li>'; return; }
    hits.forEach(function (p) {
      var li = document.createElement('li');
      var a = document.createElement('a'); a.href = BASE + p.url; a.textContent = p.title;
      var d = document.createElement('p');
      var i = norm(p.text).indexOf(words[0]);
      d.textContent = p.description || (i > -1 ? '…' + p.text.substr(Math.max(0, i - 60), 180) + '…' : p.text.substr(0, 180) + '…');
      li.appendChild(a); li.appendChild(d); list.appendChild(li);
    });
  }
  document.querySelectorAll('.search-btn').forEach(function (b) { b.addEventListener('click', function (e) { e.preventDefault(); openSearch(); }); });
  if (overlay) {
    overlay.querySelector('.so-close').addEventListener('click', function () { overlay.classList.remove('show'); });
    overlay.querySelector('input').addEventListener('input', runSearch);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape') overlay.classList.remove('show'); });
    var params = new URLSearchParams(location.search);
    if (params.get('s')) { overlay.querySelector('input').value = params.get('s'); openSearch(); }
  }

  /* ---------- Formulario de contacto ---------- */
  var form = document.querySelector('#contact-form');
  if (form) {
    var msg = form.querySelector('.form-msg');
    var q = form.querySelector('[data-captcha]');
    var a1 = Math.floor(Math.random() * 6), a2 = 1 + Math.floor(Math.random() * 8);
    if (q) q.textContent = a1 + ' + ' + a2 + ' = ?';
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      msg.className = 'form-msg';
      if (!form.checkValidity()) {
        msg.textContent = 'Found errors in the following field(s): please fill in all required fields.';
        msg.classList.add('err');
        form.reportValidity();
        return;
      }
      if (form.elements['verification'].value.trim() !== String(a1 + a2)) {
        msg.textContent = 'Please prove that you are human by solving the equation correctly.';
        msg.classList.add('err');
        return;
      }
      var btn = form.querySelector('[type="submit"]');
      btn.disabled = true; btn.textContent = 'Sending…';
      var data = new FormData(form);
      data.delete('verification');
      fetch(form.getAttribute('data-endpoint'), { method: 'POST', body: data, headers: { 'Accept': 'application/json' } })
        .then(function (r) { if (!r.ok) throw new Error(); return r.json(); })
        .then(function () {
          form.reset();
          location.href = BASE + (form.getAttribute('data-redirect') || '/');
        })
        .catch(function () {
          msg.innerHTML = 'Your message could not be sent. Please write to <a href="mailto:info@internshipspain.com">info@internshipspain.com</a> or WhatsApp (+34) 672 852 975.';
          msg.classList.add('err');
          btn.disabled = false; btn.textContent = 'Submit';
        });
    });
  }
})();
