"""Genera el sitio estático de sheriffmotos.com en /public.

Uso: python3 build.py
Datos: data/modelos.json
Fotos: public/img/modelos/<slug>/<color>/<NN-vista>.webp  (o, sin colores, public/img/modelos/<slug>/*.webp)
Banners opcionales: public/img/banners/<slug>-escritorio.webp (1920×800) y <slug>-movil.webp (1080×1350)
"""
import json, shutil, datetime
from pathlib import Path
from urllib.parse import quote
from jinja2 import Environment, DictLoader, select_autoescape

RAIZ = Path(__file__).parent
PUB = RAIZ / "public"
DOMINIO = "https://sheriffmotos.com"
WHATSAPP = "51967470547"
LEMA = "Para cada camino, una SHERIFF"

datos = json.loads((RAIZ / "data/modelos.json").read_text(encoding="utf-8"))
cats = {c["id"]: c for c in datos["categorias"]}


def wa(texto):
    return f"https://wa.me/{WHATSAPP}?text={quote(texto)}"


def vista_nombre(archivo):
    n = archivo.rsplit("/", 1)[-1].split(".")[0]
    n = n.split("-", 1)[1] if n[:2].isdigit() else n
    return {"tres-cuartos": "Tres cuartos", "perfil": "Perfil", "posterior": "Posterior", "frontal": "Frontal",
            "tres-cuartos-izq": "Tres cuartos izq.", "frontal-izq": "Frontal izq.",
            "perfil-alternativa": "Perfil 2"}.get(n, "Detalle" if n.startswith("detalle") else n.replace("-", " ").capitalize())


def galeria(m):
    base = PUB / "img/modelos" / m["slug"]
    colores = []
    for cid, nombre, hexa in m.get("fotos_color", []):
        d = base / cid
        if not d.exists():
            continue
        todas = sorted(d.glob("*.webp"))
        vistas = [f"/img/modelos/{m['slug']}/{cid}/{p.name}" for p in todas if "detalle" not in p.name]
        detalles = [f"/img/modelos/{m['slug']}/{cid}/{p.name}" for p in todas if "detalle" in p.name]
        if vistas:
            colores.append({"id": cid, "nombre": nombre, "hex": hexa, "fotos": vistas, "detalles": detalles,
                            "vistas": [vista_nombre(v) for v in vistas]})
    if not colores and base.exists():
        sueltas = sorted(f"/img/modelos/{m['slug']}/{p.name}" for p in base.glob("*.webp"))
        if sueltas:
            colores.append({"id": "unico", "nombre": "", "hex": "", "fotos": sueltas, "detalles": [],
                            "vistas": [f"Vista {i+1}" for i in range(len(sueltas))]})
    return colores


for m in datos["modelos"]:
    m["galeria"] = galeria(m)
    m["foto"] = m["galeria"][0]["fotos"][0] if m["galeria"] else None
    m["detalles"] = [f for c in m["galeria"] for f in c["detalles"]]
    m["cat"] = cats[m["categoria"]]
    m["url"] = f"/modelos/{m['slug']}/"
    m["wa"] = wa(f"Hola, quiero información sobre la SHERIFF {m['nombre']}.")
    m["cifras"] = list(m["destacado"].items())

por_slug = {m["slug"]: m for m in datos["modelos"]}

portada = []
for p in datos.get("portada", []):
    m = por_slug[p["modelo"]]
    col = next((c for c in m["galeria"] if c["id"] == p.get("color")), m["galeria"][0] if m["galeria"] else None)
    esc = PUB / f"img/banners/{m['slug']}-escritorio.webp"
    mov = PUB / f"img/banners/{m['slug']}-movil.webp"
    portada.append({**p, "m": m, "foto": col["fotos"][0] if col else m["foto"],
                    "banner_esc": f"/img/banners/{esc.name}" if esc.exists() else None,
                    "banner_mov": f"/img/banners/{mov.name}" if mov.exists() else None})

ICONO_WA = '<svg viewBox="0 0 24 24" aria-hidden="true" width="18" height="18"><path fill="currentColor" d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.2-.3-.3-.6-.4zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4c-1-1.6-1.5-3.4-1.5-5.2C2.2 6.6 6.6 2.2 12 2.2c2.6 0 5.1 1 6.9 2.9 1.8 1.8 2.9 4.3 2.9 6.9 0 5.4-4.4 9.8-9.8 9.8zm8.4-18.2C18.2 1.3 15.2 0 12 0 5.4 0 .1 5.3.1 11.9c0 2.1.5 4.1 1.6 5.9L0 24l6.3-1.7c1.7.9 3.7 1.4 5.7 1.4 6.6 0 11.9-5.3 11.9-11.9 0-3.2-1.2-6.2-3.5-8.4z"/></svg>'

BASE = """<!doctype html>
<html lang="es-PE">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ titulo }}</title>
<meta name="description" content="{{ descripcion }}">
<link rel="canonical" href="{{ dominio }}{{ ruta }}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="SHERIFF Motos">
<meta property="og:title" content="{{ titulo }}">
<meta property="og:description" content="{{ descripcion }}">
<meta property="og:url" content="{{ dominio }}{{ ruta }}">
{% if og_img %}<meta property="og:image" content="{{ dominio }}{{ og_img }}">{% endif %}
<meta name="theme-color" content="#0B0C0E">
<link rel="icon" href="/img/emblema-32.png" type="image/png">
<link rel="apple-touch-icon" href="/img/emblema-180.png">
<link rel="preload" href="/fonts/archivo-wdth.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="/assets/site.css?v={{ version }}">
{% if precarga %}<link rel="preload" as="image" href="{{ precarga }}">{% endif %}
{% block jsonld %}{% endblock %}
</head>
<body class="{{ clase_body }}">
<a class="saltar" href="#contenido">Ir al contenido</a>
<header class="cab" data-cab>
  <div class="cab-in">
    <a class="marca" href="/" aria-label="SHERIFF, inicio"><img src="/img/logo-sheriff.svg" alt="SHERIFF" width="132" height="34"></a>
    <nav class="nav" id="nav" aria-label="Principal">
      <a href="/#modelos" {% if seccion=='modelos' %}aria-current="page"{% endif %}>Modelos</a>
      <a href="/garantia/" {% if seccion=='garantia' %}aria-current="page"{% endif %}>Garantía</a>
      <a href="/red-sheriff/" {% if seccion=='red' %}aria-current="page"{% endif %}>Red SHERIFF</a>
      <a class="nav-wa" href="{{ wa_general }}" rel="noopener">{{ icono_wa|safe }} WhatsApp</a>
    </nav>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav"><span></span><span></span><span class="sr">Menú</span></button>
  </div>
</header>
<main id="contenido">
{% block contenido %}{% endblock %}
</main>
<footer class="pie">
  <div class="pie-marca"><span>SHERIFF</span></div>
  <div class="contenedor pie-grid">
    <div class="pie-lema">
      <img src="/img/logo-sheriff.svg" alt="SHERIFF" width="150" height="38" loading="lazy">
      <p>{{ lema }}.</p>
      <a class="btn" href="{{ wa_general }}" rel="noopener">{{ icono_wa|safe }} Escríbenos</a>
    </div>
    <div>
      <h2>Modelos</h2>
      <ul>{% for m in modelos %}<li><a href="{{ m.url }}">{{ m.nombre }}</a></li>{% endfor %}</ul>
    </div>
    <div>
      <h2>SHERIFF</h2>
      <ul>
        <li><a href="/garantia/">Garantía y mantenimiento</a></li>
        <li><a href="/red-sheriff/">Ser distribuidor</a></li>
        <li><a href="/red-sheriff/">Ser taller autorizado</a></li>
      </ul>
    </div>
  </div>
  <div class="contenedor legal">© {{ anio }} SHERIFF. Importado y distribuido en el Perú por BM3 IMPORT S.R.L., RUC 20600467949.</div>
</footer>
{% block barra %}{% endblock %}
<script src="/assets/site.js?v={{ version }}" defer></script>
</body>
</html>"""

TARJETA = """{% macro tarjeta(m) %}
<article class="tarjeta" data-cat="{{ m.categoria }}">
  <a href="{{ m.url }}" class="tarjeta-enl" aria-label="SHERIFF {{ m.nombre }}">
    <div class="tarjeta-foto">
      {% if m.foto %}<img src="{{ m.foto }}" alt="SHERIFF {{ m.nombre }}" loading="lazy" width="800" height="600" data-foto>
      {% else %}<span class="silueta">{{ m.nombre.split(' ')[0] }}</span>{% endif %}
      {% if m.estado == 'proximamente' %}<span class="chip">Próximamente</span>{% endif %}
    </div>
    <div class="tarjeta-txt">
      <p class="tarjeta-cat">{{ m.cat.nombre }}</p>
      <h3>{{ m.nombre }}</h3>
      <ul class="mini">{% for k, v in m.cifras[:3] %}<li><b>{{ v }}</b><span>{{ k }}</span></li>{% endfor %}</ul>
    </div>
  </a>
  {% if m.galeria|length > 1 %}<div class="puntos" aria-label="Colores">{% for c in m.galeria %}<button type="button" style="--c:{{ c.hex }}" data-img="{{ c.fotos[0] }}" aria-label="{{ c.nombre }}" {% if loop.first %}aria-pressed="true"{% else %}aria-pressed="false"{% endif %}></button>{% endfor %}</div>{% endif %}
</article>
{% endmacro %}"""

INICIO = """{% extends "base" %}{% from "tarjeta" import tarjeta %}
{% block contenido %}
<section class="hero" data-hero aria-roledescription="carrusel" aria-label="Modelos destacados">
  {% for s in portada %}
  <div class="slide {% if loop.first %}activo{% endif %}{% if s.banner_esc %} con-banner{% endif %}" data-slide aria-roledescription="diapositiva" aria-label="{{ loop.index }} de {{ portada|length }}" {% if not loop.first %}aria-hidden="true"{% endif %}>
    {% if s.banner_esc %}
    <picture class="slide-banner">{% if s.banner_mov %}<source media="(max-width:760px)" srcset="{{ s.banner_mov }}">{% endif %}<img src="{{ s.banner_esc }}" alt="" {% if not loop.first %}loading="lazy"{% endif %}></picture>
    {% else %}
    <span class="slide-fondo" aria-hidden="true" style="--fs:{{ (92 / (s.m.nombre.split(' ')[0]|length * 0.8))|round(1) }}vw">{{ s.m.nombre.split(' ')[0] }}</span>
    <div class="slide-moto"><img src="{{ s.foto }}" alt="SHERIFF {{ s.m.nombre }}" width="1200" height="1000" {% if not loop.first %}loading="lazy"{% endif %}></div>
    {% endif %}
    <div class="slide-txt contenedor">
      <p class="ante">{{ s.antetitulo }}</p>
      <h2 class="slide-tit"><span>{{ s.m.nombre }}</span>{{ s.titular }}</h2>
      <div class="botones">
        <a class="btn" href="{{ s.m.url }}">Conocer la {{ s.m.nombre.split(' ')[0]|title }}</a>
        <a class="btn fant" href="{{ s.m.wa }}" rel="noopener">{{ icono_wa|safe }} Consultar</a>
      </div>
    </div>
  </div>
  {% endfor %}
  <div class="hero-ctrl contenedor">
    {% for s in portada %}<button type="button" data-ir="{{ loop.index0 }}" aria-label="{{ s.m.nombre }}" {% if loop.first %}aria-current="true"{% endif %}><i></i><span>{{ s.m.nombre }}</span></button>{% endfor %}
  </div>
</section>

<section class="manifiesto">
  <div class="contenedor manifiesto-grid">
    <h1>Para cada camino,<br><em>una SHERIFF.</em></h1>
    <p>Scooters, mini motos, motos de ruta y modelos de tres ruedas, pensados para el día a día en el Perú. Cada SHERIFF llega con garantía registrada por número de chasis y servicios con mano de obra gratuita.</p>
  </div>
  <div class="contenedor accesos">
    {% for c in categorias %}{% set rep = modelos|selectattr('categoria','equalto',c.id)|selectattr('foto')|list %}
    <a class="acceso" href="#modelos" data-filtrar="{{ c.id }}">
      <span class="acceso-n">0{{ loop.index }}</span>
      <h2>{{ c.nombre }}</h2>
      <p>{{ c.descripcion }}</p>
      {% if rep %}<img src="{{ rep[0].foto }}" alt="" loading="lazy" width="600" height="450">{% endif %}
      <span class="flecha" aria-hidden="true">→</span>
    </a>{% endfor %}
  </div>
</section>

<section class="seccion hueso" id="modelos" aria-labelledby="t-modelos">
  <div class="contenedor">
    <div class="sec-cab">
      <div><p class="ante osc">La línea</p><h2 class="tit" id="t-modelos">Modelos</h2></div>
      <div class="filtros" role="group" aria-label="Filtrar por tipo">
        <button type="button" data-f="todas" aria-pressed="true">Todas</button>
        {% for c in categorias %}<button type="button" data-f="{{ c.id }}" aria-pressed="false">{{ c.nombre }}</button>{% endfor %}
      </div>
    </div>
    <div class="rejilla" data-rejilla>{% for m in modelos %}{{ tarjeta(m) }}{% endfor %}</div>
  </div>
</section>

{% if foco %}
<section class="foco" aria-labelledby="t-foco">
  <div class="contenedor foco-grid">
    <div class="foco-txt revela">
      <p class="ante">La más potente de la línea</p>
      <h2 class="tit" id="t-foco">{{ foco.nombre }}</h2>
      <p>{{ foco.resumen }}</p>
      <dl class="foco-cifras">
        {% for k, v in foco.cifras %}<div><dt>{{ k }}</dt><dd>{{ v }}</dd></div>{% endfor %}
      </dl>
      <a class="btn" href="{{ foco.url }}">Ver ficha técnica</a>
    </div>
    <div class="mosaico revela">
      {% for f in foco.detalles[:3] %}<figure class="m{{ loop.index }}"><img src="{{ f }}" alt="Detalle de la SHERIFF {{ foco.nombre }}" loading="lazy" width="800" height="800"></figure>{% endfor %}
    </div>
  </div>
</section>
{% endif %}

<section class="seccion garantia" aria-labelledby="t-garantia">
  <div class="contenedor">
    <div class="sec-cab"><div><p class="ante osc">Respaldo</p><h2 class="tit" id="t-garantia">Garantía SHERIFF</h2></div>
      <a class="enl" href="/garantia/">Ver condiciones →</a></div>
    <div class="cifras-g revela">
      <div><b>12</b><span>meses de garantía de motor</span></div>
      <div><b>10,000</b><span>kilómetros, lo que ocurra primero</span></div>
      <div><b>3</b><span>servicios con mano de obra gratuita, registrados por número de chasis</span></div>
    </div>
  </div>
</section>

<section class="red-home" aria-labelledby="t-red">
  {% set tr = modelos|selectattr('slug','equalto','trooper-200')|first %}
  <div class="contenedor red-grid">
    <div class="revela">
      <p class="ante">Red SHERIFF</p>
      <h2 class="tit" id="t-red">Lleva SHERIFF a tu ciudad.</h2>
      <p>Estamos formando la red de distribuidores y talleres autorizados en las regiones del Perú.</p>
      <div class="botones">
        <a class="btn" href="{{ wa_dist }}" rel="noopener">Quiero ser distribuidor</a>
        <a class="btn fant" href="{{ wa_taller }}" rel="noopener">Quiero ser taller</a>
      </div>
    </div>
    {% if tr and tr.galeria %}<img class="red-moto revela" src="{{ tr.galeria[0].fotos[-1] }}" alt="SHERIFF {{ tr.nombre }}" loading="lazy" width="1200" height="800">{% endif %}
  </div>
</section>
{% endblock %}"""

MODELO = """{% extends "base" %}{% from "tarjeta" import tarjeta %}
{% block jsonld %}<script type="application/ld+json">{{ jsonld|safe }}</script>{% endblock %}
{% block contenido %}
<section class="mod-hero">
  <div class="contenedor">
    <p class="migas"><a href="/#modelos">Modelos</a><span>/</span>{{ m.cat.nombre }}</p>
  </div>
  <div class="contenedor mod-grid">
    <div class="mod-txt">
      {% if m.estado == 'proximamente' %}<span class="chip">Próximamente</span>{% endif %}
      <h1>{{ m.nombre }}</h1>
      <p>{{ m.resumen }}</p>
      {% if m.galeria|length > 1 %}
      <div class="selector" role="group" aria-label="Color">
        <p class="selector-tit">Color: <b data-color-nombre>{{ m.galeria[0].nombre }}</b></p>
        <div class="puntos grandes">{% for c in m.galeria %}<button type="button" style="--c:{{ c.hex }}" data-color="{{ loop.index0 }}" aria-label="{{ c.nombre }}" aria-pressed="{{ 'true' if loop.first else 'false' }}"></button>{% endfor %}</div>
      </div>
      {% elif m.galeria and m.galeria[0].nombre %}<p class="selector-tit">Color: <b>{{ m.galeria[0].nombre }}</b></p>{% endif %}
      <div class="botones">
        <a class="btn" href="{{ m.wa }}" rel="noopener">{{ icono_wa|safe }} {% if m.estado == 'proximamente' %}Avísenme cuando llegue{% else %}Consultar por WhatsApp{% endif %}</a>
        <a class="btn fant osc" href="#ficha">Ficha técnica</a>
      </div>
    </div>
    <div class="visor">
      <span class="visor-fondo" aria-hidden="true" style="--fs:{{ (96 / (m.nombre.split(' ')[0]|length * 0.8))|round(1) }}cqw">{{ m.nombre.split(' ')[0] }}</span>
      {% if m.foto %}<img src="{{ m.foto }}" alt="SHERIFF {{ m.nombre }}" width="1200" height="900" data-visor>
      {% else %}<span class="silueta">{{ m.nombre.split(' ')[0] }}</span>{% endif %}
      {% if m.galeria and m.galeria[0].fotos|length > 1 %}
      <div class="vistas" data-vistas>{% for f in m.galeria[0].fotos %}<button type="button" data-v="{{ loop.index0 }}" aria-pressed="{{ 'true' if loop.first else 'false' }}"><img src="{{ f }}" alt="" loading="lazy" width="120" height="90"><span>{{ m.galeria[0].vistas[loop.index0] }}</span></button>{% endfor %}</div>
      {% endif %}
    </div>
  </div>
  <div class="tablero"><div class="contenedor"><dl>{% for k, v in m.cifras %}<div><dd>{{ v }}</dd><dt>{{ k }}</dt></div>{% endfor %}</dl></div></div>
</section>
<script type="application/json" id="galeria">{{ galeria_json|safe }}</script>

{% if m.equipamiento %}
<section class="seccion">
  <div class="contenedor equip-grid">
    <div><p class="ante osc">Equipamiento</p><h2 class="tit">Lo que trae de serie</h2></div>
    <ol class="equip">{% for e in m.equipamiento %}<li class="revela"><span>{{ '%02d'|format(loop.index) }}</span>{{ e }}</li>{% endfor %}</ol>
  </div>
</section>
{% endif %}

{% if m.detalles %}
<section class="detalles" aria-label="Detalles">
  <div class="carril">{% for f in m.detalles %}<figure><img src="{{ f }}" alt="Detalle de la SHERIFF {{ m.nombre }}" loading="lazy" width="900" height="900"></figure>{% endfor %}</div>
</section>
{% endif %}

<section class="seccion hueso" id="ficha">
  <div class="contenedor">
    <div class="sec-cab"><div><p class="ante osc">Datos de homologación</p><h2 class="tit">Ficha técnica</h2></div></div>
    {% if m.specs %}
    <div class="specs">{% for grupo, filas in m.specs.items() %}
      <details class="spec" open>
        <summary>{{ grupo }}</summary>
        <table>{% for k, v in filas %}<tr><th scope="row">{{ k }}</th><td>{{ v }}</td></tr>{% endfor %}</table>
      </details>{% endfor %}
    </div>
    <p class="pequeno">Datos según ficha técnica de homologación. Las especificaciones pueden variar sin previo aviso.</p>
    {% else %}<p class="nota">{{ m.nota_specs }}</p>{% endif %}
    {% if m.colores %}
    <div class="colores-disp">
      <h3>Colores disponibles</h3>
      <ul>{% for n, h in m.colores %}<li><i {% if h == 'tornasol' %}class="tornasol"{% else %}style="background:{{ h }}"{% endif %}></i>{{ n }}</li>{% endfor %}</ul>
      <p class="pequeno">Disponibilidad de colores sujeta a stock del distribuidor.</p>
    </div>{% endif %}
  </div>
</section>

<section class="banda-g">
  <div class="contenedor banda-g-in">
    <p><b>12 meses o 10,000 km</b> de garantía y mano de obra gratuita en los servicios de 300, 1,500 y 3,000 km.</p>
    <a class="btn" href="/garantia/">Ver garantía</a>
  </div>
</section>

<section class="seccion">
  <div class="contenedor">
    <div class="sec-cab"><div><p class="ante osc">Sigue explorando</p><h2 class="tit">Otros modelos</h2></div><a class="enl" href="/#modelos">Ver todos →</a></div>
    <div class="rejilla">{% for o in otros %}{{ tarjeta(o) }}{% endfor %}</div>
  </div>
</section>
{% endblock %}
{% block barra %}<div class="barra-movil"><span>{{ m.nombre }}</span><a class="btn" href="{{ m.wa }}" rel="noopener">{{ icono_wa|safe }} Consultar</a></div>{% endblock %}"""

CAB_INTERNA = """<section class="int-hero">
  <div class="contenedor">
    <p class="ante">{{ ante }}</p>
    <h1>{{ h1 }}</h1>
    <p class="int-lead">{{ lead }}</p>
  </div>
</section>"""

GARANTIA = """{% extends "base" %}
{% block contenido %}
{% with ante="Respaldo SHERIFF", h1="Garantía", lead="12 meses o 10,000 km, lo que ocurra primero, contados desde la entrega. Tu garantía y tus servicios quedan registrados con el número de chasis." %}{% include "cab_interna" %}{% endwith %}

<section class="seccion">
  <div class="contenedor">
    <div class="cifras-g">
      <div><b>12</b><span>meses o 10,000 km en motor</span></div>
      <div><b>3</b><span>servicios con mano de obra gratuita</span></div>
      <div><b>10</b><span>días hábiles estimados de diagnóstico</span></div>
      <div><b>0</b><span>cupones ni manual impreso</span></div>
    </div>
  </div>
</section>

<section class="seccion hueso"><div class="contenedor">
  <div class="sec-cab"><div><p class="ante osc">Qué cubre</p><h2 class="tit">Cobertura por componente</h2></div></div>
  <p class="intro">La reparación o sustitución sin costo de la pieza con defecto de fabricación o de montaje, incluida la mano de obra, según el informe técnico del servicio técnico autorizado.</p>
  <div class="niveles">
    <article><span class="nivel">A</span><h3>12 meses o 10,000 km</h3><p><b>Motor:</b> culata, cilindro, pistón y anillos, cigüeñal, biela, árbol de levas, válvulas y balancines, caja de cambios, bomba de aceite, canasta y campana de embrague, cárter y tapas, empaquetaduras internas. Cuerpo de carburador o inyector.</p></article>
    <article><span class="nivel">B</span><h3>3 meses o 3,000 km</h3><p><b>Estructura:</b> chasis, basculante y soportes soldados del motor. Solo defectos de soldadura o material; no cubre corrosión, golpes ni fisuras por sobrecarga, accidentes o terreno irregular.</p></article>
    <article><span class="nivel">C</span><h3>30 días o 1,000 km</h3><p><b>Sistema eléctrico</b> (batería, tablero, CDI/ECU, bobina, regulador, estator, arranque, ramal, relays, fusibles, comandos, claxon), <b>controles</b> (cables y pedales), <b>suspensión</b> y <b>tanque de combustible</b>.</p></article>
    <article class="sin"><span class="nivel">D</span><h3>No aplica</h3><p>Piezas de desgaste y consumibles: aceites, bujía, filtros, kit de arrastre, frenos, embrague, faja, neumáticos, aros, plásticos, pintura, espejos, focos, alarmas, pernos y gastos indirectos.</p></article>
  </div>
</div></section>

<section class="seccion"><div class="contenedor">
  <div class="sec-cab"><div><p class="ante osc">Mantenimiento</p><h2 class="tit">Programa de servicios</h2></div></div>
  <p class="intro">Cada servicio se hace al llegar al kilometraje o a los 90 días del servicio anterior, lo que ocurra primero. Cumplirlo mantiene vigente la garantía.</p>
  <ol class="ruta">
    {% for s in servicios %}<li class="{{ 'gratis' if s[2] == 'Gratuita' else '' }}"><span class="ruta-n">{{ loop.index }}</span><b>{{ s[0] }}</b><small>Tolerancia {{ s[1] }}</small><em>{{ s[2] }}</em></li>{% endfor %}
  </ol>
  <p class="pequeno">Los insumos (aceite, filtros, bujía) son de cargo del propietario en todos los servicios. El servicio 8 es una recomendación fuera del período de garantía.</p>
</div></section>

<section class="seccion oscura"><div class="contenedor dos-col">
  <div>
    <p class="ante">Paso a paso</p>
    <h2 class="tit">Cómo solicitar la garantía</h2>
    <p>Lleva el vehículo, tu comprobante de compra (boleta o factura) y tu documento de identidad. No necesitas manual impreso ni cupones.</p>
    <a class="btn" href="{{ wa_garantia }}" rel="noopener">{{ icono_wa|safe }} Consultar mi garantía</a>
  </div>
  <ol class="pasos">
    <li><b>Reporta la falla a tiempo</b>Comunícala dentro de los 15 días de detectada y deja de usar la moto si la falla puede empeorar.</li>
    <li><b>Acude con tu moto</b>A una sede del importador o al distribuidor autorizado donde la compraste.</li>
    <li><b>Verificación por chasis</b>El asesor confirma la fecha de entrega, el kilometraje y los servicios realizados, y abre una orden de servicio.</li>
    <li><b>Diagnóstico técnico</b>El servicio técnico determina si la causa es un defecto de fabricación. Plazo estimado: 10 días hábiles.</li>
    <li><b>Resolución y entrega</b>Si aplica, la reparación es sin costo. Si no, recibes el sustento técnico y un presupuesto que puedes aceptar o rechazar.</li>
  </ol>
</div></section>

<section class="seccion hueso"><div class="contenedor dos-col">
  <div>
    <p class="ante osc">Primeros 1,000 km</p>
    <h2 class="tit">Asentamiento del motor</h2>
    <p>Los primeros 1,000 km definen la vida útil del motor.</p>
  </div>
  <ol class="equip">
    <li><span>01</span>No superes 50 km/h ni 5,500 rpm, y no des más de media vuelta al acelerador.</li>
    <li><span>02</span>Evita llevar pasajero o carga y subir pendientes pronunciadas.</li>
    <li><span>03</span>Calienta el motor de 1 a 3 minutos y no recorras más de 50 km seguidos.</li>
    <li><span>04</span>Varía la velocidad; no mantengas una misma marcha por mucho tiempo.</li>
    <li><span>05</span>Haz el primer cambio de aceite a los 300 km.</li>
    <li><span>06</span>Usa aceite 4T JASO MA o MA2, API SL o superior, y gasolina de 90 octanos o más.</li>
  </ol>
</div></section>

<section class="seccion"><div class="contenedor prosa">
  <p class="ante osc">Exclusiones</p>
  <h2 class="tit">Qué no cubre</h2>
  <p>Fallas por no cumplir el programa de mantenimiento o el asentamiento, alteración del odómetro, uso en competencias, sobrecarga (máximo 150 kg), reparaciones o instalaciones eléctricas en talleres no autorizados, piezas no originales, combustible o lubricantes fuera de especificación, accidentes, fenómenos naturales y desgaste normal. El detalle completo está en el Manual de Garantía y Servicios.</p>
  <p class="pequeno">Esta garantía no limita los derechos que te reconoce el Código de Protección y Defensa del Consumidor (Ley N.° 29571). Manual de Garantía y Servicios SHERIFF, versión 2026-01.</p>
</div></section>
{% endblock %}"""

RED = """{% extends "base" %}
{% block contenido %}
{% with ante="Red SHERIFF", h1="Únete a la red", lead="Buscamos distribuidores y talleres en las regiones del Perú para llevar SHERIFF a más ciudades." %}{% include "cab_interna" %}{% endwith %}
<section class="seccion"><div class="contenedor red-cards">
  <article>
    <span class="acceso-n">01</span>
    <h2>Distribuidores</h2>
    <p>Vende la línea completa de scooters, motos y tres ruedas con precio mayorista, abastecimiento desde el importador y garantía respaldada por número de chasis.</p>
    <a class="btn" href="{{ wa_dist }}" rel="noopener">{{ icono_wa|safe }} Postular como distribuidor</a>
  </article>
  <article>
    <span class="acceso-n">02</span>
    <h2>Talleres autorizados</h2>
    <p>Atiende mantenimientos y garantías SHERIFF en tu zona, con capacitación técnica y acceso a repuestos originales.</p>
    <a class="btn" href="{{ wa_taller }}" rel="noopener">{{ icono_wa|safe }} Postular como taller</a>
  </article>
</div>
<div class="contenedor prosa" style="margin-top:32px">
  <p class="pequeno">Al escribirnos, cuéntanos tu ciudad, el nombre de tu negocio y tu experiencia en el rubro. Te responderá el equipo comercial.</p>
</div></section>
{% endblock %}"""

NOENC = """{% extends "base" %}
{% block contenido %}
{% with ante="Error 404", h1="Te saliste del camino", lead="Puede que el enlace haya cambiado. Revisa los modelos desde el inicio." %}{% include "cab_interna" %}{% endwith %}
<section class="seccion"><div class="contenedor"><a class="btn osc" href="/#modelos">Ver modelos</a></div></section>
{% endblock %}"""

env = Environment(loader=DictLoader({"base": BASE, "tarjeta": TARJETA, "inicio": INICIO, "modelo": MODELO,
                                     "cab_interna": CAB_INTERNA, "garantia": GARANTIA, "red": RED, "404": NOENC}),
                  autoescape=select_autoescape(["html"], default=True))

hoy = datetime.datetime.now()
comun = dict(dominio=DOMINIO, modelos=datos["modelos"], categorias=datos["categorias"], lema=LEMA,
             anio=hoy.year, version=hoy.strftime("%Y%m%d%H%M"), og_img=None, seccion="", precarga=None,
             clase_body="", icono_wa=ICONO_WA,
             wa_general=wa("Hola, quiero información sobre las motos SHERIFF."),
             wa_dist=wa("Hola, quiero ser distribuidor SHERIFF. Mi ciudad es: "),
             wa_taller=wa("Hola, quiero ser taller autorizado SHERIFF. Mi ciudad es: "),
             wa_garantia=wa("Hola, quiero consultar la garantía de mi SHERIFF. Mi número de chasis es: "))


def escribir(ruta, plantilla, **kw):
    destino = PUB / ruta.lstrip("/") / "index.html" if ruta.endswith("/") else PUB / ruta.lstrip("/")
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(env.get_template(plantilla).render(**{**comun, "ruta": ruta, **kw}), encoding="utf-8")


# Limpia páginas generadas (no toca /img)
for d in ["modelos", "garantia", "red-sheriff"]:
    shutil.rmtree(PUB / d, ignore_errors=True)
(PUB / "assets").mkdir(parents=True, exist_ok=True)
shutil.copy(RAIZ / "src/site.css", PUB / "assets/site.css")
shutil.copy(RAIZ / "src/site.js", PUB / "assets/site.js")

foco = por_slug.get("destroyer-300")
escribir("/", "inicio", titulo="SHERIFF Motos Perú | Scooters, motos y tres ruedas",
         descripcion="Modelos SHERIFF en el Perú: scooters 150, motos de 200 y 300 cc y tres ruedas. Fichas técnicas, colores y garantía de 12 meses o 10,000 km.",
         portada=portada, foco=foco if foco and foco["detalles"] else None, clase_body="cab-sobre",
         og_img=portada[0]["foto"] if portada else None,
         precarga=portada[0]["banner_esc"] or portada[0]["foto"] if portada else None)

for m in datos["modelos"]:
    ld = {"@context": "https://schema.org", "@type": "Product", "name": f"SHERIFF {m['nombre']}",
          "brand": {"@type": "Brand", "name": "SHERIFF"}, "description": m["resumen"],
          "category": "Motocicleta", "url": DOMINIO + m["url"]}
    if m["foto"]:
        ld["image"] = [DOMINIO + f for f in m["galeria"][0]["fotos"][:3]]
    otros = [o for o in datos["modelos"] if o["slug"] != m["slug"] and o["categoria"] == m["categoria"]]
    otros += [o for o in datos["modelos"] if o["slug"] != m["slug"] and o not in otros]
    gal = [{"nombre": c["nombre"], "fotos": c["fotos"], "vistas": c["vistas"]} for c in m["galeria"]]
    escribir(m["url"], "modelo", m=m, seccion="modelos", og_img=m["foto"], precarga=m["foto"], otros=otros[:3],
             galeria_json=json.dumps(gal, ensure_ascii=False).replace("</", "<\\/"),
             titulo=f"SHERIFF {m['nombre']} | Ficha técnica y colores",
             descripcion=f"{m['resumen']} Conoce la ficha técnica y la garantía de la SHERIFF {m['nombre']}.",
             jsonld=json.dumps(ld, ensure_ascii=False))

servicios = [("300 km", "350 km", "Gratuita"), ("1,500 km", "1,650 km", "Gratuita"), ("3,000 km", "3,150 km", "Gratuita"),
             ("4,500 km", "4,650 km", "Con costo"), ("6,000 km", "6,150 km", "Con costo"), ("7,500 km", "7,650 km", "Con costo"),
             ("9,000 km", "9,150 km", "Con costo"), ("10,500 km", "10,650 km", "Con costo (recomendado)")]
escribir("/garantia/", "garantia", seccion="garantia", servicios=servicios,
         titulo="Garantía SHERIFF | 12 meses o 10,000 km",
         descripcion="Condiciones de garantía de las motos SHERIFF: cobertura por componente, mantenimientos gratuitos de 300, 1,500 y 3,000 km y cómo solicitarla.")
escribir("/red-sheriff/", "red", seccion="red",
         titulo="Distribuidores y talleres SHERIFF | Únete a la red",
         descripcion="Postula como distribuidor o taller autorizado de motos SHERIFF en tu región del Perú.")
escribir("/404.html", "404", titulo="Página no encontrada | SHERIFF", descripcion="Página no encontrada.")

urls = ["/", "/garantia/", "/red-sheriff/"] + [m["url"] for m in datos["modelos"]]
(PUB / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    + "".join(f"  <url><loc>{DOMINIO}{u}</loc><lastmod>{hoy.date().isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
(PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
(PUB / "_headers").write_text("/img/*\n  Cache-Control: public, max-age=2592000\n/fonts/*\n  Cache-Control: public, max-age=31536000, immutable\n/assets/*\n  Cache-Control: public, max-age=604800\n", encoding="utf-8")
print(f"Sitio generado: {len(urls)} páginas")
