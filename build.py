"""Genera el sitio estático de sheriffmotos.com en /public.

Uso: python3 build.py
Datos: data/modelos.json  ·  Fotos: public/img/modelos/<slug>/*.webp
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

def fotos(slug):
    d = PUB / "img/modelos" / slug
    return sorted(f"/img/modelos/{slug}/{p.name}" for p in d.glob("*.webp")) if d.exists() else []

def wa(texto):
    return f"https://wa.me/{WHATSAPP}?text={quote(texto)}"

for m in datos["modelos"]:
    m["fotos"] = fotos(m["slug"])
    m["cat"] = cats[m["categoria"]]
    m["url"] = f"/modelos/{m['slug']}/"
    m["wa"] = wa(f"Hola, quiero información sobre la SHERIFF {m['nombre']}.")

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
<meta name="theme-color" content="#16212A">
<link rel="icon" href="/img/emblema-32.png" type="image/png">
<link rel="apple-touch-icon" href="/img/emblema-180.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700&family=Barlow:wght@400;500&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/site.css?v={{ version }}">
{% block jsonld %}{% endblock %}
</head>
<body>
<a class="saltar" href="#contenido">Ir al contenido</a>
<header class="cabecera">
  <div class="contenedor">
    <a class="marca" href="/"><img src="/img/logo-sheriff.svg" alt="SHERIFF" width="150" height="38"></a>
    <button class="menu-btn" aria-expanded="false" aria-controls="nav">Menú</button>
    <nav class="nav" id="nav" aria-label="Principal">
      <a href="/#modelos" {% if seccion=='modelos' %}aria-current="page"{% endif %}>Modelos</a>
      <a href="/garantia/" {% if seccion=='garantia' %}aria-current="page"{% endif %}>Garantía</a>
      <a href="/red-sheriff/" {% if seccion=='red' %}aria-current="page"{% endif %}>Distribuidores y talleres</a>
      <a href="{{ wa_general }}" rel="noopener">Contacto</a>
    </nav>
  </div>
</header>
<div class="carretera {% if anim %}anim{% endif %}" aria-hidden="true"></div>
<main id="contenido">
{% block contenido %}{% endblock %}
</main>
<footer class="pie">
  <div class="contenedor">
    <div>
      <p class="lema">{{ lema }}</p>
      <p>Motocicletas SHERIFF para la ciudad, la ruta y el trabajo en todo el Perú.</p>
    </div>
    <div>
      <h2>Modelos</h2>
      <ul>{% for m in modelos %}<li><a href="{{ m.url }}">{{ m.nombre }}</a></li>{% endfor %}</ul>
    </div>
    <div>
      <h2>Información</h2>
      <ul>
        <li><a href="/garantia/">Garantía y mantenimiento</a></li>
        <li><a href="/red-sheriff/">Distribuidores y talleres</a></li>
        <li><a href="{{ wa_general }}" rel="noopener">WhatsApp</a></li>
      </ul>
    </div>
    <p class="legal">© {{ anio }} SHERIFF. Importado y distribuido en el Perú por BM3 IMPORT S.R.L., RUC 20600467949.</p>
  </div>
</footer>
<script>
(function(){var b=document.querySelector('.menu-btn'),n=document.getElementById('nav');
if(!b)return;b.addEventListener('click',function(){var a=n.classList.toggle('abierto');b.setAttribute('aria-expanded',a)});})();
</script>
</body>
</html>"""

FICHA = """{% macro ficha(m) %}
<a class="ficha" href="{{ m.url }}">
  <div class="foto">{% if m.fotos %}<img src="{{ m.fotos[0] }}" alt="SHERIFF {{ m.nombre }}" loading="lazy" width="640" height="480">{% else %}<span class="sin-foto">{{ m.nombre }}</span>{% endif %}</div>
  {% if m.estado == 'proximamente' %}<span class="etiqueta" style="margin-top:14px">Próximamente</span>{% endif %}
  <h4>{{ m.nombre }}</h4>
  <ul class="cifras">{% for k, v in m.destacado.items() %}{% if loop.index <= 3 %}<li><b>{{ v }}</b><span>{{ k }}</span></li>{% endif %}{% endfor %}</ul>
</a>
{% endmacro %}"""

INICIO = """{% extends "base" %}{% from "ficha" import ficha %}
{% block contenido %}
<section class="portada">
  <div class="contenedor">
    <h1>Para cada camino, una SHERIFF.</h1>
    <p>Scooters, mini motos, motos de ruta y modelos de tres ruedas pensados para el día a día en el Perú. Conoce cada modelo, su ficha técnica y la garantía que lo respalda.</p>
    <div class="botones">
      <a class="btn" href="#modelos">Ver modelos</a>
      <a class="btn sec" href="/garantia/">Garantía</a>
    </div>
  </div>
</section>

<section class="seccion" id="modelos" aria-labelledby="t-modelos">
  <div class="contenedor">
    <h2 class="titulo" id="t-modelos">Modelos</h2>
    <p class="intro">Toca un modelo para ver su ficha técnica completa.</p>
    {% for c in categorias %}{% set lista = modelos|selectattr('categoria','equalto',c.id)|list %}{% if lista %}
    <div class="categoria">
      <div class="categoria-cab"><h3>{{ c.nombre }}</h3><p>{{ c.descripcion }}</p></div>
      <div class="rejilla">{% for m in lista %}{{ ficha(m) }}{% endfor %}</div>
    </div>{% endif %}{% endfor %}
  </div>
</section>

<section class="seccion gris" aria-labelledby="t-garantia">
  <div class="contenedor garantia-bloque">
    <div class="sello" aria-hidden="true"><span class="n">12</span><span class="u">meses o 10,000 km de garantía</span></div>
    <div>
      <h2 class="titulo" id="t-garantia">Garantía registrada por número de chasis</h2>
      <ul class="lista">
        <li>Cubre defectos de fabricación o de montaje, lo que ocurra primero entre tiempo y kilometraje.</li>
        <li>Mano de obra gratuita en los servicios de 300, 1,500 y 3,000 km.</li>
        <li>No necesitas manual impreso ni cupones: todo queda registrado con el chasis.</li>
      </ul>
      <a class="btn osc" href="/garantia/">Ver condiciones de garantía</a>
    </div>
  </div>
</section>

<section class="seccion" aria-labelledby="t-red">
  <div class="contenedor">
    <h2 class="titulo" id="t-red">Únete a la red SHERIFF</h2>
    <p class="intro">Estamos formando la red de distribuidores y talleres autorizados en las regiones del Perú.</p>
    <div class="red">
      <article><h3>Quiero ser distribuidor</h3><p>Vende motos SHERIFF en tu ciudad con respaldo de importador, repuestos y garantía.</p><a class="btn" href="{{ wa_dist }}" rel="noopener">Postular como distribuidor</a></article>
      <article><h3>Quiero ser taller autorizado</h3><p>Atiende garantías y mantenimientos SHERIFF en tu zona con capacitación técnica.</p><a class="btn" href="{{ wa_taller }}" rel="noopener">Postular como taller</a></article>
    </div>
  </div>
</section>
{% endblock %}"""

MODELO = """{% extends "base" %}
{% block jsonld %}<script type="application/ld+json">{{ jsonld|safe }}</script>{% endblock %}
{% block contenido %}
<section class="modelo-cab">
  <div class="contenedor">
    <p class="migas"><a href="/#modelos">Modelos</a> / {{ m.cat.nombre }}</p>
    <div class="modelo-grid">
      <div>
        {% if m.estado == 'proximamente' %}<span class="etiqueta">Próximamente</span>{% endif %}
        <h1>{{ m.nombre }}</h1>
        <p>{{ m.resumen }}</p>
        <div class="botones" style="margin-bottom:32px">
          <a class="btn" href="{{ m.wa }}" rel="noopener">{% if m.estado == 'proximamente' %}Avísenme cuando llegue{% else %}Consultar por WhatsApp{% endif %}</a>
          {% if m.specs %}<a class="btn sec" href="#ficha">Ficha técnica</a>{% endif %}
        </div>
      </div>
      <div class="modelo-foto">{% if m.fotos %}<img src="{{ m.fotos[0] }}" alt="SHERIFF {{ m.nombre }}" width="900" height="675">{% else %}<span class="sin-foto">{{ m.nombre }}</span>{% endif %}</div>
    </div>
  </div>
  <div class="tablero"><div class="contenedor"><ul>{% for k, v in m.destacado.items() %}<li><b>{{ v }}</b><span>{{ k }}</span></li>{% endfor %}</ul></div></div>
</section>

{% if m.fotos|length > 1 %}
<section class="seccion" style="padding-bottom:0"><div class="contenedor">
  <h2 class="titulo">Galería</h2>
  <div class="galeria">{% for f in m.fotos %}<img src="{{ f }}" alt="SHERIFF {{ m.nombre }}, foto {{ loop.index }}" loading="lazy" width="300" height="300">{% endfor %}</div>
</div></section>
{% endif %}

<section class="seccion" id="ficha"><div class="contenedor dos-col">
  <div>
    {% if m.equipamiento %}<h2 class="titulo">Equipamiento</h2>
    <ul class="equip">{% for e in m.equipamiento %}<li>{{ e }}</li>{% endfor %}</ul>{% endif %}
    {% if m.colores %}<h2 class="titulo" style="margin-top:40px">Colores</h2>
    <ul class="colores">{% for n, h in m.colores %}<li><i {% if h == 'tornasol' %}class="tornasol"{% else %}style="background:{{ h }}"{% endif %}></i>{{ n }}</li>{% endfor %}</ul>
    <p class="pequeno">Disponibilidad de colores sujeta a stock del distribuidor.</p>{% endif %}
  </div>
  <div class="specs">
    <h2 class="titulo">Ficha técnica</h2>
    {% if m.specs %}{% for grupo, filas in m.specs.items() %}
    <h3>{{ grupo }}</h3>
    <table>{% for k, v in filas %}<tr><th scope="row">{{ k }}</th><td>{{ v }}</td></tr>{% endfor %}</table>
    {% endfor %}
    <p class="pequeno">Datos según ficha técnica de homologación. Las especificaciones pueden variar sin previo aviso.</p>
    {% else %}<p class="nota">{{ m.nota_specs }}</p>{% endif %}
  </div>
</div></section>

<section class="seccion gris"><div class="contenedor garantia-bloque">
  <div class="sello" aria-hidden="true"><span class="n">12</span><span class="u">meses o 10,000 km</span></div>
  <div>
    <h2 class="titulo">Respaldada por la garantía SHERIFF</h2>
    <p>Incluye mano de obra gratuita en los tres primeros mantenimientos.</p>
    <a class="btn osc" href="/garantia/">Ver garantía</a>
  </div>
</div></section>
{% endblock %}"""

GARANTIA = """{% extends "base" %}
{% block contenido %}
<section class="portada">
  <div class="contenedor">
    <h1>Garantía SHERIFF</h1>
    <p>12 meses o 10,000 km, lo que ocurra primero, contados desde la entrega. Tu garantía y tus servicios quedan registrados con el número de chasis.</p>
  </div>
</section>

<section class="seccion"><div class="contenedor prosa">
  <h2 class="titulo">Qué cubre</h2>
  <p>La reparación o sustitución sin costo de la pieza con defecto de fabricación o de montaje, incluida la mano de obra, según el informe técnico del servicio técnico autorizado. El diagnóstico y la reparación toman un estimado de 10 días hábiles desde el ingreso del vehículo.</p>
</div>
<div class="contenedor" style="margin-top:32px">
  <h3 class="titulo" style="font-size:1.75rem">Cobertura por componente</h3>
  <div class="tabla-ancha"><table>
    <tr><th>Nivel</th><th>Vigencia</th><th>Componentes</th></tr>
    <tr><td class="nivel">A</td><td>12 meses o 10,000 km</td><td><b>Motor:</b> culata, cilindro, pistón y anillos, cigüeñal, biela, árbol de levas, válvulas y balancines, caja de cambios, bomba de aceite, canasta y campana de embrague, cárter y tapas, empaquetaduras internas. Cuerpo de carburador o inyector.</td></tr>
    <tr><td class="nivel">B</td><td>3 meses o 3,000 km</td><td><b>Estructura:</b> chasis, basculante y soportes soldados del motor. Solo defectos de soldadura o material; no cubre corrosión, golpes ni fisuras por sobrecarga, accidentes o terreno irregular.</td></tr>
    <tr><td class="nivel">C</td><td>30 días o 1,000 km</td><td><b>Sistema eléctrico</b> (batería, tablero, CDI/ECU, bobina, regulador, estator, arranque, ramal, relays, fusibles, comandos, claxon), <b>controles</b> (cables y pedales), <b>suspensión</b> y <b>tanque de combustible</b>.</td></tr>
    <tr><td class="nivel">D</td><td>No aplica</td><td>Piezas de desgaste y consumibles: aceites, bujía, filtros, kit de arrastre, frenos, embrague, faja, neumáticos, aros, plásticos, pintura, espejos, focos, alarmas, pernos y gastos indirectos.</td></tr>
  </table></div>
</div></section>

<section class="seccion gris"><div class="contenedor">
  <h2 class="titulo">Programa de mantenimiento</h2>
  <p class="intro">Cada servicio se hace al llegar al kilometraje o a los 90 días del servicio anterior, lo que ocurra primero. Cumplirlo mantiene vigente la garantía.</p>
  <div class="tabla-ancha"><table>
    <tr><th>Servicio</th><th>Kilometraje</th><th>Tolerancia máxima</th><th>Mano de obra</th></tr>
    {% for s in servicios %}<tr><td>{{ loop.index }}</td><td>{{ s[0] }}</td><td>{{ s[1] }}</td><td>{{ s[2] }}</td></tr>{% endfor %}
  </table></div>
  <p class="pequeno">Los insumos (aceite, filtros, bujía) son de cargo del propietario en todos los servicios. El servicio 8 es una recomendación fuera del período de garantía.</p>
</div></section>

<section class="seccion"><div class="contenedor dos-col">
  <div>
    <h2 class="titulo">Cómo solicitar la garantía</h2>
    <p>Lleva el vehículo, tu comprobante de compra (boleta o factura) y tu documento de identidad. No necesitas manual impreso ni cupones.</p>
  </div>
  <ol class="pasos">
    <li><b>Reporta la falla a tiempo</b>Comunícala dentro de los 15 días de detectada y deja de usar la moto si la falla puede empeorar.</li>
    <li><b>Acude con tu moto</b>A una sede del importador o al distribuidor autorizado donde la compraste.</li>
    <li><b>Verificación por chasis</b>El asesor confirma la fecha de entrega, el kilometraje y los servicios realizados, y abre una orden de servicio.</li>
    <li><b>Diagnóstico técnico</b>El servicio técnico determina si la causa es un defecto de fabricación. Plazo estimado: 10 días hábiles.</li>
    <li><b>Resolución y entrega</b>Si aplica, la reparación es sin costo. Si no, recibes el sustento técnico y un presupuesto que puedes aceptar o rechazar.</li>
  </ol>
</div></section>

<section class="seccion gris"><div class="contenedor dos-col">
  <div>
    <h2 class="titulo">Asentamiento del motor</h2>
    <p>Los primeros 1,000 km definen la vida útil del motor.</p>
  </div>
  <ul class="equip">
    <li>No superes 50 km/h ni 5,500 rpm, y no des más de media vuelta al acelerador.</li>
    <li>Evita llevar pasajero o carga y subir pendientes pronunciadas.</li>
    <li>Calienta el motor de 1 a 3 minutos y no recorras más de 50 km seguidos.</li>
    <li>Varía la velocidad; no mantengas una misma marcha por mucho tiempo.</li>
    <li>Haz el primer cambio de aceite a los 300 km.</li>
    <li>Usa aceite 4T JASO MA o MA2, API SL o superior, y gasolina de 90 octanos o más.</li>
  </ul>
</div></section>

<section class="seccion"><div class="contenedor prosa">
  <h2 class="titulo">Qué no cubre</h2>
  <p>Fallas por no cumplir el programa de mantenimiento o el asentamiento, alteración del odómetro, uso en competencias, sobrecarga (máximo 150 kg), reparaciones o instalaciones eléctricas en talleres no autorizados, piezas no originales, combustible o lubricantes fuera de especificación, accidentes, fenómenos naturales y desgaste normal. El detalle completo está en el Manual de Garantía y Servicios.</p>
  <p class="pequeno">Esta garantía no limita los derechos que te reconoce el Código de Protección y Defensa del Consumidor (Ley N.° 29571). Manual de Garantía y Servicios SHERIFF, versión 2026-01.</p>
  <a class="btn osc" href="{{ wa_garantia }}" rel="noopener">Consultar mi garantía por WhatsApp</a>
</div></section>
{% endblock %}"""

RED = """{% extends "base" %}
{% block contenido %}
<section class="portada">
  <div class="contenedor">
    <h1>Red SHERIFF</h1>
    <p>Buscamos distribuidores y talleres en las regiones del Perú para llevar SHERIFF a más ciudades.</p>
  </div>
</section>
<section class="seccion"><div class="contenedor red">
  <article>
    <h3>Distribuidores</h3>
    <p>Vende la línea completa de scooters, motos y tres ruedas con precio mayorista, abastecimiento desde el importador y garantía respaldada por número de chasis.</p>
    <a class="btn" href="{{ wa_dist }}" rel="noopener">Postular como distribuidor</a>
  </article>
  <article>
    <h3>Talleres autorizados</h3>
    <p>Atiende mantenimientos y garantías SHERIFF en tu zona, con capacitación técnica y acceso a repuestos originales.</p>
    <a class="btn" href="{{ wa_taller }}" rel="noopener">Postular como taller</a>
  </article>
</div>
<div class="contenedor prosa" style="margin-top:40px">
  <p class="pequeno">Al escribirnos, cuéntanos tu ciudad, el nombre de tu negocio y tu experiencia en el rubro. Te responderá el equipo comercial.</p>
</div></section>
{% endblock %}"""

NOENC = """{% extends "base" %}
{% block contenido %}
<section class="portada"><div class="contenedor">
  <h1>Esta página no existe</h1>
  <p>Puede que el enlace haya cambiado. Revisa los modelos desde el inicio.</p>
  <a class="btn" href="/#modelos">Ver modelos</a>
</div></section>
{% endblock %}"""

env = Environment(loader=DictLoader({"base": BASE, "ficha": FICHA, "inicio": INICIO, "modelo": MODELO,
                                     "garantia": GARANTIA, "red": RED, "404": NOENC}),
                  autoescape=select_autoescape(["html"], default=True))

hoy = datetime.date.today()
comun = dict(dominio=DOMINIO, modelos=datos["modelos"], categorias=datos["categorias"], lema=LEMA,
             anio=hoy.year, version=hoy.strftime("%Y%m%d%H%M"), anim=False, og_img=None, seccion="",
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

primera = next((m["fotos"][0] for m in datos["modelos"] if m["fotos"]), None)
escribir("/", "inicio", titulo="SHERIFF Motos Perú | Scooters, motos y tres ruedas",
         descripcion="Modelos SHERIFF en el Perú: scooters 150, motos de 200 y 300 cc y tres ruedas. Fichas técnicas, colores y garantía de 12 meses o 10,000 km.",
         anim=True, og_img=primera)

for m in datos["modelos"]:
    ld = {"@context": "https://schema.org", "@type": "Product", "name": f"SHERIFF {m['nombre']}",
          "brand": {"@type": "Brand", "name": "SHERIFF"}, "description": m["resumen"],
          "category": "Motocicleta", "url": DOMINIO + m["url"]}
    if m["fotos"]:
        ld["image"] = [DOMINIO + f for f in m["fotos"][:3]]
    escribir(m["url"], "modelo", m=m, seccion="modelos", og_img=(m["fotos"] or [None])[0],
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
    + "".join(f"  <url><loc>{DOMINIO}{u}</loc><lastmod>{hoy.isoformat()}</lastmod></url>\n" for u in urls) + "</urlset>\n", encoding="utf-8")
(PUB / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {DOMINIO}/sitemap.xml\n", encoding="utf-8")
(PUB / "_headers").write_text("/img/*\n  Cache-Control: public, max-age=2592000\n/assets/*\n  Cache-Control: public, max-age=604800\n", encoding="utf-8")
print(f"Sitio generado: {len(urls)} páginas")
