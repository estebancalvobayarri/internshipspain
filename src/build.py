#!/usr/bin/env python3
"""
Generador de la web estática de Internship Spain.

Uso:  python3 src/build.py

Lee cada página de src/pages/*.html (contenido + metadatos SEO en la cabecera
<!--meta {...} -->) y genera el HTML final en la raíz del repositorio con la
MISMA estructura de URLs que internshipspain.com (p. ej. /about-us/).

Imágenes: se referencian con su ruta original de WordPress
(/wp-content/uploads/AAAA/MM/archivo.ext). Si el archivo todavía no existe en
el repositorio se muestra un hueco señalizado con el nombre de la foto; en
cuanto se copia la imagen a esa ruta y se vuelve a ejecutar este script, el
hueco se sustituye por la foto real (con la misma URL que en la web antigua).
"""
import datetime
import hashlib
import html
import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
PAGES = SRC / "pages"
SITE = "https://internshipspain.com"
# Versión de CSS/JS = huella de su contenido (evita copias antiguas en caché).
BUILD_VERSION = hashlib.md5(b"".join((ROOT / f).read_bytes()
                                     for f in ("assets/css/style.css", "assets/js/main.js"))).hexdigest()[:10]
# Prefijo de ruta: vacío en el dominio definitivo; /internshipspain en la vista previa de github.io
BASE = os.environ.get("BASE_PATH", "").rstrip("/")
ROOT_LINK_RE = re.compile(r'((?:href|src|action|data-src|data-map-src|data-bg-pending)=")/(?!/)')


def with_base(doc):
    """Antepone BASE a los enlaces internos que empiezan por "/"."""
    if not BASE:
        return doc
    doc = ROOT_LINK_RE.sub(lambda m: m.group(1) + BASE + "/", doc)
    doc = doc.replace("url('/", "url('" + BASE + "/")
    doc = doc.replace('content="0; url=/', 'content="0; url=' + BASE + "/")
    doc = doc.replace('location.replace("/', 'location.replace("' + BASE + "/")
    return doc


# ---------------------------------------------------------------------------
# Datos generales
# ---------------------------------------------------------------------------
BUSINESS = {
    "name": "INTERNSHIP SPAIN",
    "legal": "Move Abroad Experience S.L.",
    "oid": "E10410987",
    "phone_display": "(+34) 672 852 975",
    "phone": "+34672852975",
    "whatsapp": "https://api.whatsapp.com/send?phone=34672852975",
    "email": "info@internshipspain.com",
    "address": "Valencia, Comunidad Valenciana, España",
    "hours": "Monday-Friday: 8:00-14:00, 15:00-19:00",
    "lat": "39.469907",
    "lng": "-0.376288",
}
LOGO = "/wp-content/uploads/2015/07/logo-web.png"
FAVICON = "/wp-content/uploads/2020/05/favicon-top.png"
OG_IMAGE = "/wp-content/uploads/2026/05/Calderona_web.jpeg"
MAP_SRC = "https://maps.google.com/maps?q=Valencia%2C%20Espa%C3%B1a&t=&z=10&ie=UTF8&iwloc=&output=embed"
GOOGLE_VERIFICATION = "-LZbq31QLDWI3CKeuiOXjdQPXT_WSyzTRP3g48HsPKM"

MENU = [
    ("home", "Home", "/"),
    ("internship", "Internship in Spain", "/your-internship-in-spain/"),
    ("mobility", "Mobility", "/mobility-organisation-step-by-step/"),
    ("resources", "Resources", "/erasmus-resources-and-documentation/"),
    ("about", "About us", "/about-us/"),
]

FOOTER_PAGES = [
    ("Home", "/"),
    ("Internship in Spain", "/your-internship-in-spain/"),
    ("Mobility Organisation Step by Step", "/mobility-organisation-step-by-step/"),
    ("Erasmus+ Resources and Documentation", "/erasmus-resources-and-documentation/"),
    ("About us", "/about-us/"),
    ("Contact", "/contact/"),
    ("Legal Notice", "/legal-notice/"),
    ("Privacy Policy", "/privacy-policy/"),
    ("Data Protection", "/data-protection/"),
    ("Cookie Policy", "/cookie-policy/"),
    ("Accessibility", "/accessibility/"),
]

# URLs antiguas de WordPress que conviene redirigir (GitHub Pages no admite 301;
# se usa canonical + meta refresh, que Google trata como redirección permanente).
REDIRECTS = {
    "/home/": "/",
    "/entrada-1/": "/",
    "/entrada-2/": "/",
    "/entrada-3/": "/",
    "/category/sin-categoria/": "/",
    "/contacto/": "/contact/",
}

# ---------------------------------------------------------------------------
# Iconos SVG (los mismos de la web original: Entypo Fontello)
# ---------------------------------------------------------------------------
ICONS = {
    "direction": '<svg viewBox="0 0 28 32" aria-hidden="true"><path d="M27.136 2.624q0.256 0.256 0.352 0.512t-0.064 0.704-0.32 0.832-0.608 1.248-0.768 1.568q-1.728 3.584-4.704 9.152t-5.024 9.344l-2.112 3.776-1.728-12.16-12.16-1.792q14.144-7.872 22.272-11.776 0.64-0.32 1.536-0.8t1.248-0.64 0.8-0.288 0.736-0.032 0.544 0.352zM24.192 5.696l-9.728 8.96 0.896 7.488z"/></svg>',
    "flight": '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M8.576 31.040l3.968-12.8h-5.76l-3.584 3.2h-3.2l2.56-5.44-2.56-5.44h3.2l3.584 3.2h5.76l-3.968-12.8h3.2l7.168 12.8h8.768t1.152 0.128 1.472 0.352 1.152 0.672 0.512 1.088q0 1.024-1.216 1.568t-2.368 0.608l-1.216 0.064h-8.256l-7.168 12.8h-3.2z"/></svg>',
    "attach": '<svg viewBox="0 0 30 32" aria-hidden="true"><path d="M7.808 31.68q-3.264 0-5.44-2.304-2.304-2.24-2.368-5.312t2.688-6.080l15.872-15.872q2.56-2.56 5.568-1.728 1.408 0.384 2.528 1.504t1.504 2.528q0.832 3.072-1.728 5.632l-15.168 15.168q-1.28 1.28-2.816 1.472-1.536 0.128-2.56-0.896-0.96-0.768-0.864-2.368t1.504-2.944l10.624-10.688q0.768-0.832 1.6 0t0 1.6l-10.624 10.624q-1.408 1.408-0.64 2.24 0.384 0.256 0.768 0.192 0.768-0.128 1.472-0.832l15.168-15.168q1.6-1.6 1.088-3.456-0.512-1.92-2.432-2.432-1.728-0.448-3.456 1.152l-15.808 15.808q-2.112 2.432-2.048 4.576t1.664 3.744q1.6 1.536 3.744 1.6t4.512-1.984l15.872-15.808q0.768-0.768 1.6 0 0.832 0.704 0 1.536l-15.872 15.872q-2.624 2.624-5.952 2.624z"/></svg>',
    "users": '<svg viewBox="0 0 32 32" aria-hidden="true"><path d="M32 30.080h-7.168v-4.8q0-1.728-0.96-2.592t-4.928-2.848q1.28-0.96 1.28-2.688 0-0.512-0.416-1.056t-0.608-1.632q-0.064-0.256-0.448-0.512t-0.448-1.344q0-0.768 0.384-0.96-0.192-1.088-0.256-1.92-0.128-1.216 0.736-2.496t3.040-1.28 3.072 1.28 0.768 2.496l-0.256 1.92q0.384 0.192 0.384 0.96-0.064 1.088-0.448 1.344t-0.448 0.512q-0.192 1.088-0.608 1.632t-0.416 1.056q0 1.344 0.672 2.112t2.464 1.536q3.584 1.472 4.16 2.56 0.192 0.256 0.288 1.952t0.16 3.232v1.536zM16.384 21.696q5.824 2.496 5.824 3.968v4.416h-22.208v-5.888q0-1.408 2.688-2.496 2.432-1.024 3.328-2.048t0.896-2.816q0-0.64-0.608-1.408t-0.8-2.176q-0.064-0.32-0.576-0.704t-0.64-1.792q0-0.448 0.096-0.736t0.224-0.416l0.128-0.064q-0.192-1.472-0.32-2.624-0.128-1.6 1.056-3.296t4.064-1.696 4.064 1.696 1.056 3.296l-0.32 2.624q0.448 0.256 0.448 1.216-0.128 1.408-0.64 1.792t-0.576 0.704q-0.192 1.408-0.8 2.176t-0.608 1.408q0 1.792 0.896 2.816t3.328 2.048z"/></svg>',
    "mobile": '<svg viewBox="0 0 20 32" aria-hidden="true"><path d="M15.5 0h-11C2.6 0 1 1.6 1 3.5v25C1 30.4 2.6 32 4.5 32h11c1.9 0 3.5-1.6 3.5-3.5v-25C19 1.6 17.4 0 15.5 0zM10 30.2c-.9 0-1.6-.7-1.6-1.6S9.1 27 10 27s1.6.7 1.6 1.6-.7 1.6-1.6 1.6zM16.4 25H3.6V4h12.8v21z"/></svg>',
    "check": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 16.2 4.8 12l-1.4 1.4L9 19 21 7l-1.4-1.4z"/></svg>',
    "phone": '<svg viewBox="0 0 512 512" aria-hidden="true"><path d="M497.4 361.8 385.4 313.8a24 24 0 0 0-28 6.9l-49.6 60.6A370.7 370.7 0 0 1 130.6 204.1l60.6-49.6a23.9 23.9 0 0 0 6.9-28l-48-112A24.2 24.2 0 0 0 122.6.6l-104 24A24 24 0 0 0 0 48c0 256.5 207.9 464 464 464a24 24 0 0 0 23.4-18.6l24-104a24.3 24.3 0 0 0-14-27.6z"/></svg>',
    "whatsapp": '<svg viewBox="0 0 448 512" aria-hidden="true"><path d="M380.9 97.1A223.9 223.9 0 0 0 224.1 32c-123.5 0-224 100.5-224 224 0 39.5 10.3 78 29.9 112L0 480l117.7-30.9a223.2 223.2 0 0 0 106.3 27c123.4 0 226-100.5 226-224 0-59.8-25.4-116-69.1-155zM224.1 438.7a185.9 185.9 0 0 1-94.8-25.9l-6.8-4.1-69.8 18.3 18.6-68.1-4.4-7a184.5 184.5 0 0 1-28.3-98.5c0-102.6 83.5-186.1 186.2-186.1a184.4 184.4 0 0 1 131.6 54.5 185.3 185.3 0 0 1 56.5 131.7c0 102.7-85.7 186.2-188.8 186.2zm101.6-139.4c-5.5-2.8-32.8-16.2-37.9-18-5.1-1.9-8.8-2.8-12.5 2.8s-14.3 18-17.6 21.8c-3.2 3.7-6.5 4.2-12 1.4-32.6-16.3-54-29.1-75.5-66-5.7-9.8 5.7-9.1 16.3-30.3 1.8-3.7.9-6.9-.5-9.7s-12.5-30.1-17.1-41.2c-4.5-10.8-9.1-9.3-12.5-9.5-3.2-.2-6.9-.2-10.6-.2s-9.7 1.4-14.8 6.9c-5.1 5.6-19.4 19-19.4 46.3s19.9 53.7 22.6 57.4c2.8 3.7 39.1 59.7 94.8 83.8 35.2 15.2 49 16.5 66.6 13.9 10.7-1.6 32.8-13.4 37.4-26.4s4.6-24.1 3.2-26.4c-1.3-2.5-5-3.9-10.5-6.6z"/></svg>',
    "mail": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 5h20v14H2zm2 2v.5l8 5 8-5V7zm16 2.9-8 5-8-5V17h16z"/></svg>',
    "search": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M10 2a8 8 0 0 1 6.3 12.9l5.4 5.4-1.4 1.4-5.4-5.4A8 8 0 1 1 10 2zm0 2a6 6 0 1 0 0 12 6 6 0 0 0 0-12z"/></svg>',
    "menu": '<svg viewBox="0 0 24 24" aria-hidden="true" fill="currentColor"><path d="M3 6h18v2H3zm0 5h18v2H3zm0 5h18v2H3z"/></svg>',
    "up": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 7l-7 7 1.4 1.4L12 9.8l5.6 5.6L19 14z"/></svg>',
    "lock": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M17 9h-1V7a4 4 0 0 0-8 0v2H7a2 2 0 0 0-2 2v9a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2v-9a2 2 0 0 0-2-2zm-7-2a2 2 0 0 1 4 0v2h-4z"/></svg>',
    "flag-en": '<svg viewBox="0 0 60 30" aria-hidden="true"><clipPath id="fe"><path d="M0 0v30h60V0z"/></clipPath><clipPath id="ft"><path d="M30 15h30v15zv15H0zH0V0zV0h30z"/></clipPath><g clip-path="url(#fe)"><path d="M0 0v30h60V0z" fill="#012169"/><path d="M0 0l60 30m0-30L0 30" stroke="#fff" stroke-width="6"/><path d="M0 0l60 30m0-30L0 30" clip-path="url(#ft)" stroke="#C8102E" stroke-width="4"/><path d="M30 0v30M0 15h60" stroke="#fff" stroke-width="10"/><path d="M30 0v30M0 15h60" stroke="#C8102E" stroke-width="6"/></g></svg>',
    "flag-es": '<svg viewBox="0 0 750 500" aria-hidden="true"><path fill="#c60b1e" d="M0 0h750v500H0z"/><path fill="#ffc400" d="M0 125h750v250H0z"/></svg>',
}


def icon(name):
    return ICONS[name]


# ---------------------------------------------------------------------------
# Imágenes: hueco o foto real
# ---------------------------------------------------------------------------
IMG_RE = re.compile(r"<img\b([^>]*?)\s*/?>", re.S)
ATTR_RE = re.compile(r'([\w:-]+)="([^"]*)"')
BG_RE = re.compile(r'data-bg="([^"]+)"')
missing_images = set()
present_images = set()


def img_exists(src):
    return src.startswith("/") and (ROOT / src.lstrip("/")).is_file()


def real_size(src):
    try:
        from PIL import Image
        with Image.open(ROOT / src.lstrip("/")) as im:
            return im.size
    except Exception:
        return None


def replace_img(m):
    attrs = dict(ATTR_RE.findall(m.group(1)))
    src = attrs.get("src", "")
    if not src.startswith("/wp-content/") or img_exists(src):
        tag = m.group(0)
        if src.startswith("/wp-content/"):
            present_images.add(src)
            dims = real_size(src)
            if dims:
                tag = re.sub(r'width="\d+"', f'width="{dims[0]}"', tag)
                tag = re.sub(r'height="\d+"', f'height="{dims[1]}"', tag)
        if "loading=" not in tag and "data-eager" not in tag:
            tag = tag.replace("<img", '<img loading="lazy" decoding="async"', 1)
        return tag.replace(" data-eager", "")
    missing_images.add(src)
    w, h = attrs.get("width"), attrs.get("height")
    style = f' style="aspect-ratio:{w}/{h}"' if w and h else ""
    cls = ("img-ph " + attrs.get("class", "")).strip()
    alt = attrs.get("alt", "")
    label = html.escape(src.rsplit("/", 1)[-1])
    aria = f' role="img" aria-label="{html.escape(alt)}"' if alt else ' aria-hidden="true"'
    return f'<div class="{cls}"{style}{aria} data-src="{html.escape(src)}"><span>Imagen pendiente:<br>{label}</span></div>'


def replace_bg(content):
    """Convierte data-bg="..." en background-image o en un fondo provisional."""

    def repl(m):
        src = m.group(1)
        if img_exists(src):
            present_images.add(src)
            return f'style="background-image:url(\'{src}\')"'
        missing_images.add(src)
        return f'data-bg-pending="{src}"'

    out = BG_RE.sub(repl, content)

    def tag_repl(m):
        tag = m.group(0)
        src = re.search(r'data-bg-pending="([^"]+)"', tag).group(1)
        tag = re.sub(r'class="', 'class="bg-ph ', tag, count=1)
        return tag + f'<span class="bg-label">Fondo pendiente: {html.escape(src.rsplit("/", 1)[-1])}</span>'

    return re.sub(r'<(section|div)\b[^>]*data-bg-pending="[^"]+"[^>]*>', tag_repl, out)


# ---------------------------------------------------------------------------
# Plantilla
# ---------------------------------------------------------------------------
def nav_html(active):
    items = []
    for key, label, url in MENU:
        cur = key == active
        c = ' class="current"' if cur else ""
        aria = ' aria-current="page"' if cur else ""
        items.append(f'<li{c}><a href="{url}"{aria}>{label}</a></li>')
    cur = active == "contact"
    items.append(f'<li class="nav-cta{" current" if cur else ""}"><a href="/contact/"'
                 f'{" aria-current=\"page\"" if cur else ""}>Contact</a></li>')
    items.append(f'<li><a class="search-btn" href="/?s=" aria-label="Search">{icon("search")}</a></li>')
    return "".join(items)


def header_html(active):
    logo = f'<img src="{LOGO}" alt="INTERNSHIP SPAIN" width="253" height="116" data-eager fetchpriority="high">'
    return f"""<a class="skip-link" href="#main">Skip to content</a>
<header class="site-header">
  <div class="topbar"><div class="container">
    <span class="tb-text">Powered by Move Abroad Experience S.L. - OID: {BUSINESS["oid"]} – Organisation registered in the Erasmus+ Programme</span>
    <span class="flags notranslate"><a href="#" data-lang="en" title="English" aria-label="English">{icon("flag-en")}</a><a href="#" data-lang="es" title="Spanish" aria-label="Español">{icon("flag-es")}</a></span>
  </div></div>
  <div class="header-main">
    <div class="container">
      <a class="logo" href="/" aria-label="INTERNSHIP SPAIN - Home">{logo}</a>
      <nav class="main-nav" aria-label="Main menu">
        <button class="menu-toggle" type="button" aria-label="Menu" aria-expanded="false">{icon("menu")}</button>
        <ul>{nav_html(active)}</ul>
      </nav>
    </div>
  </div>
</header>"""


def footer_html():
    pages = "".join(f'<li><a href="{u}">{t}</a></li>' for t, u in FOOTER_PAGES)
    b = BUSINESS
    return f"""<footer class="site-footer">
  <div class="container footer-grid">
    <section class="f-pages" aria-label="Pages">
      <h3>Pages</h3>
      <ul>{pages}</ul>
    </section>
    <section class="f-contact" aria-label="Contact details">
      <h3><a href="/">INTERNSHIP SPAIN</a></h3>
      <ul>
        <li>{b["address"]}</li>
        <li>Tel. <a href="tel:{b["phone"]}">{b["phone_display"]}</a></li>
        <li>Opening hours:<br>&nbsp; {b["hours"]}</li>
        <li><a href="mailto:{b["email"]}">{b["email"]}</a></li>
      </ul>
    </section>
    <section class="f-map" aria-label="Map">
      <div class="map-consent" data-map-src="{MAP_SRC}">
        <span>Para la correcta visualización, debe aceptar las cookies.</span>
        <button type="button" data-accept-cookies>Accept and show the map</button>
      </div>
      <p class="f-credit"><a href="https://ecwebdesign.es/" target="_blank" rel="noopener">Web design by <img src="/assets/img/ecwebdesign.png" alt="EC Web Design" width="94" height="12" loading="lazy"></a></p>
    </section>
  </div>
</footer>
<div class="socket"><div class="container"></div></div>
<a class="to-top" href="#top" aria-label="Back to top">{icon("up")}</a>
<button class="cookie-lock" type="button" aria-label="Cookie settings">{icon("lock")}</button>
<div class="cookie-bar" role="dialog" aria-label="Cookie notice">
  <div class="cb-inner">
    <p>A cookie is a small information file that is stored each time you visit our website. Some cookies are our own, and others belong to third-party companies that provide services for our website.</p>
    <p>Cookies can be of different types: technical cookies are necessary for our website to function. Other cookies are used to improve our website, personalize it or show you advertising tailored to your searches and interests. You can accept all these cookies by clicking the <strong>ACCEPT</strong> button or reject their use by clicking <strong>REJECT</strong>.</p>
    <p>If you want more information, please consult the <a href="/cookie-policy/">Cookie Policy</a> of our website.</p>
    <div class="cb-actions"><button type="button" class="cb-accept">Accept</button><button type="button" class="cb-reject">Reject</button></div>
  </div>
</div>
<div class="search-overlay" role="dialog" aria-label="Search">
  <button class="so-close" type="button" aria-label="Close">×</button>
  <div class="so-inner">
    <label class="sr-only" for="search-input">Search</label>
    <input id="search-input" type="search" placeholder="Search…" autocomplete="off">
    <ul class="search-results"></ul>
  </div>
</div>"""


def jsonld(meta, url):
    b = BUSINESS
    org = {
        "@type": ["Organization", "LocalBusiness"],
        "@id": SITE + "/#organization",
        "name": b["name"],
        "legalName": b["legal"],
        "url": SITE + "/",
        "logo": SITE + LOGO,
        "image": SITE + OG_IMAGE,
        "telephone": b["phone"],
        "email": b["email"],
        "address": {"@type": "PostalAddress", "streetAddress": "Conde Salvatierra 21, Pta. 4", "postalCode": "46004",
                    "addressLocality": "Valencia", "addressRegion": "Comunidad Valenciana", "addressCountry": "ES"},
        "geo": {"@type": "GeoCoordinates", "latitude": float(b["lat"]), "longitude": float(b["lng"])},
        "openingHoursSpecification": [
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "opens": "08:00", "closes": "14:00"},
            {"@type": "OpeningHoursSpecification", "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
             "opens": "15:00", "closes": "19:00"}],
        "areaServed": "EU",
    }
    website = {"@type": "WebSite", "@id": SITE + "/#website", "url": SITE + "/", "name": "INTERNSHIP SPAIN",
               "description": "INTERNSHIP SPAIN", "publisher": {"@id": SITE + "/#organization"}, "inLanguage": "en-US",
               "potentialAction": {"@type": "SearchAction", "target": SITE + "/?s={search_term_string}",
                                   "query-input": "required name=search_term_string"}}
    webpage = {"@type": "WebPage", "@id": url + "#webpage", "url": url, "name": meta["title"],
               "isPartOf": {"@id": SITE + "/#website"}, "inLanguage": "en-US"}
    if meta.get("description"):
        webpage["description"] = meta["description"]
    if meta.get("published"):
        webpage["datePublished"] = meta["published"]
    if meta.get("lastmod"):
        webpage["dateModified"] = meta["lastmod"]
    graph = [org, website, webpage]
    crumbs = meta.get("breadcrumb")
    if crumbs:
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(crumbs)
        ]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False)


def page_html(meta, content):
    path = meta["path"]
    url = SITE + path
    robots = meta.get("robots", "index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1")
    if BASE:  # vista previa en github.io: que Google no la indexe
        robots = "noindex, nofollow"
    desc = meta.get("description", "")
    og_image = SITE + meta.get("og_image", OG_IMAGE)
    title = html.escape(meta["title"])
    desc_tags = ""
    if desc:
        d = html.escape(desc)
        desc_tags = (f'<meta name="description" content="{d}">\n'
                     f'<meta property="og:description" content="{d}">\n')
    canonical = f'<link rel="canonical" href="{url}">\n' if meta.get("canonical", True) else ""
    reading = (f'<meta name="twitter:label1" content="Est. reading time">\n'
               f'<meta name="twitter:data1" content="{meta["reading"]}">\n') if meta.get("reading") else ""
    modified = f'<meta property="article:modified_time" content="{meta["lastmod"]}">\n' if meta.get("lastmod") else ""
    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
{desc_tags}<meta name="robots" content="{robots}">
{canonical}<meta name="google-site-verification" content="{GOOGLE_VERIFICATION}">
<meta name="geo.region" content="ES-VC">
<meta name="geo.placename" content="Valencia">
<meta name="geo.position" content="{BUSINESS['lat']};{BUSINESS['lng']}">
<meta name="ICBM" content="{BUSINESS['lat']}, {BUSINESS['lng']}">
<meta property="og:locale" content="en_US">
<meta property="og:type" content="{meta.get('og_type', 'article')}">
<meta property="og:title" content="{title}">
<meta property="og:url" content="{url}">
<meta property="og:site_name" content="INTERNSHIP SPAIN">
{modified}<meta property="og:image" content="{og_image}">
<meta name="twitter:card" content="summary_large_image">
{reading}<meta name="theme-color" content="#104844">
<link rel="icon" href="{FAVICON}" type="image/png">
<link rel="apple-touch-icon" href="{FAVICON}">
<link rel="stylesheet" href="/assets/css/style.css?v={BUILD_VERSION}">
<script type="application/ld+json">{jsonld(meta, url)}</script>
</head>
<body class="{meta.get('body', '')}" id="top" data-base="{BASE}">
{header_html(meta.get("nav", ""))}
<main id="main">
{content}
</main>
{footer_html()}
<script src="/assets/js/main.js?v={BUILD_VERSION}" defer></script>
</body>
</html>
"""


def redirect_html(new):
    url = SITE + new
    return f"""<!DOCTYPE html>
<html lang="en-US">
<head>
<meta charset="UTF-8">
<title>INTERNSHIP SPAIN</title>
<meta name="robots" content="noindex, follow">
<link rel="canonical" href="{url}">
<meta http-equiv="refresh" content="0; url={new}">
<script>location.replace("{new}" + location.hash);</script>
</head>
<body><p>This page has moved to <a href="{new}">{url}</a>.</p></body>
</html>
"""


# ---------------------------------------------------------------------------
# Construcción
# ---------------------------------------------------------------------------
META_RE = re.compile(r"\A\s*<!--\s*meta\s*(\{.*?\})\s*-->", re.S)


def strip_tags(s):
    s = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", s, flags=re.S)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def out_path(path):
    if path == "/404.html":
        return ROOT / "404.html"
    return ROOT / path.strip("/") / "index.html" if path != "/" else ROOT / "index.html"


def main():
    sitemap, search = [], []
    pages = sorted(PAGES.glob("*.html"))
    for f in pages:
        raw = f.read_text(encoding="utf-8")
        m = META_RE.match(raw)
        if not m:
            raise SystemExit(f"Falta la cabecera <!--meta {{...}} --> en {f}")
        meta = json.loads(m.group(1))
        content = raw[m.end():].strip()
        content = re.sub(r"\{\{icon:([\w-]+)\}\}", lambda mm: icon(mm.group(1)), content)
        content = replace_bg(content)
        target = out_path(meta["path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(with_base(IMG_RE.sub(replace_img, page_html(meta, content))), encoding="utf-8")
        if meta.get("sitemap", True) and "noindex" not in meta.get("robots", ""):
            sitemap.append((meta["path"], meta.get("lastmod"), meta.get("priority", "0.8")))
        if meta["path"] != "/404.html" and "noindex" not in meta.get("robots", "") or meta.get("searchable"):
            search.append({"title": meta["title"].replace(" - INTERNSHIP SPAIN", ""), "url": meta["path"],
                           "description": meta.get("description", ""), "text": strip_tags(content)[:4000]})
        print("✔", meta["path"])

    for old, new in REDIRECTS.items():
        t = out_path(old)
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(with_base(redirect_html(new)), encoding="utf-8")
        print("↪", old, "→", new)

    # sitemap.xml (+ los nombres de sitemap que usaba Yoast en la web antigua)
    today = datetime.date.today().isoformat()
    urls = "".join(
        f"  <url>\n    <loc>{SITE}{p}</loc>\n    <lastmod>{lm or today}</lastmod>\n    <priority>{pr}</priority>\n  </url>\n"
        for p, lm, pr in sorted(sitemap, key=lambda x: (x[0] != "/", x[0]))
    )
    xml = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n'
    (ROOT / "sitemap.xml").write_text(xml, encoding="utf-8")
    (ROOT / "page-sitemap.xml").write_text(xml, encoding="utf-8")
    index_xml = (f'<?xml version="1.0" encoding="UTF-8"?>\n<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                 f'  <sitemap>\n    <loc>{SITE}/page-sitemap.xml</loc>\n    <lastmod>{today}</lastmod>\n  </sitemap>\n</sitemapindex>\n')
    (ROOT / "sitemap_index.xml").write_text(index_xml, encoding="utf-8")
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap_index.xml\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    (ROOT / "search-index.json").write_text(json.dumps(search, ensure_ascii=False), encoding="utf-8")

    lines = ["# Imágenes pendientes", "",
             "Copia cada imagen en la ruta indicada (respetando carpetas y nombre) y ejecuta `python3 src/build.py`.",
             "Así las fotos conservan exactamente la misma URL que tenían en la web antigua.", ""]
    for s in sorted(missing_images):
        lines.append(f"- [ ] `{s.lstrip('/')}`")
    if present_images:
        lines += ["", "## Ya incluidas", ""] + [f"- [x] `{s.lstrip('/')}`" for s in sorted(present_images)]
    (ROOT / "IMAGENES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"\n{len(pages)} páginas · {len(missing_images)} imágenes pendientes · {len(present_images)} imágenes presentes")


if __name__ == "__main__":
    main()
