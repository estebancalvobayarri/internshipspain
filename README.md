# INTERNSHIP SPAIN — web estática

Réplica de [internshipspain.com](https://internshipspain.com) (distribución, colores, tipografía y textos) preparada para publicarse con **GitHub Pages** y sustituir a la web de WordPress sin perder posicionamiento.

## Estructura

| Carpeta / archivo | Qué contiene |
|---|---|
| `src/pages/*.html` | Contenido de cada página + sus metadatos SEO (título, ruta, robots…) en la cabecera `<!--meta {...} -->` |
| `src/build.py` | Genera el HTML final (cabecera, menú, pie, SEO, sitemap…) |
| `assets/css/style.css` · `assets/js/main.js` | Estilos e interacciones |
| `wp-content/uploads/…` | Imágenes, **con la misma ruta que tenían en WordPress** |
| `index.html`, `about-us/…`, etc. | HTML generado (no editar a mano) |
| `IMAGENES.md` | Lista de imágenes que faltan y dónde copiarlas |

## Editar y regenerar

```bash
python3 src/build.py
```

Edita los archivos de `src/pages/` y vuelve a ejecutar el comando.

## Imágenes

Mientras falte una foto se muestra un hueco rayado con su nombre. Copia la imagen en la ruta que indica `IMAGENES.md` (por ejemplo `wp-content/uploads/2026/05/rafting-845x684.jpg`), ejecuta `python3 src/build.py` y el hueco se convierte en la foto real.

## SEO conservado

- **Mismas URLs** que la web actual (con barra final) y mismos títulos.
- `canonical`, `robots` (las páginas legales y la de agradecimiento siguen en `noindex`), etiquetas geo y la verificación de Google Search Console.
- Datos estructurados (Organization / LocalBusiness, WebSite, WebPage y migas de pan) y etiquetas Open Graph.
- `sitemap.xml`, `sitemap_index.xml` y `page-sitemap.xml` (los nombres que ya conoce Google) y `robots.txt`.
- Imágenes servidas en sus rutas originales `/wp-content/uploads/…`.
- Redirecciones de URLs antiguas sin contenido (`/home/`, `/entrada-1/`…, `/category/sin-categoria/`, `/contacto/`) y página `404.html` propia.

## Vista previa y puesta en marcha

La web se publica sola con GitHub Actions (`.github/workflows/pages.yml`) en cada cambio de `main`.

1. **Activar GitHub Pages** (una sola vez): *Settings → Pages → Build and deployment → Source: **GitHub Actions***.
   Vista previa: `https://estebancalvobayarri.github.io/internshipspain/` (marcada como `noindex`).
2. **Día del cambio de dominio**:
   - Añade al repositorio un archivo `CNAME` con el texto `internshipspain.com`.
   - *Settings → Pages → Custom domain*: `internshipspain.com`.
   - DNS: registros `A` de `internshipspain.com` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`; registro `CNAME` de `www` → `estebancalvobayarri.github.io`.
   - Marca **Enforce HTTPS** cuando GitHub lo permita.
3. **Google Search Console** (la verificación ya está incluida): envía `https://internshipspain.com/sitemap.xml`.
4. **Formulario de contacto**: usa [FormSubmit](https://formsubmit.co); el primer envío manda un correo de activación a `info@internshipspain.com` que hay que confirmar una vez. Tras enviar, el visitante va a `/thank-you-for-contacting-us/`, como en la web actual.
5. **Banderas EN/ES**: traducen la página con Google Translate, igual que la web actual.
