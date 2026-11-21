(function () {
  var reducido = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* Cabecera: fondo sólido al hacer scroll */
  var cab = document.querySelector('[data-cab]');
  function alScroll() { if (cab) cab.classList.toggle('solida', window.scrollY > 40); }
  window.addEventListener('scroll', alScroll, { passive: true }); alScroll();

  /* Menú móvil */
  var mb = document.querySelector('.menu-btn'), nav = document.getElementById('nav');
  if (mb) mb.addEventListener('click', function () {
    var a = document.body.classList.toggle('menu-abierto');
    mb.setAttribute('aria-expanded', a);
  });
  if (nav) nav.addEventListener('click', function (e) {
    if (e.target.closest('a')) { document.body.classList.remove('menu-abierto'); if (mb) mb.setAttribute('aria-expanded', false); }
  });

  /* Carrusel de portada */
  var hero = document.querySelector('[data-hero]');
  if (hero) {
    var slides = hero.querySelectorAll('[data-slide]'), btns = hero.querySelectorAll('[data-ir]'), i = 0, t;
    function ir(n) {
      slides[i].classList.remove('activo'); slides[i].setAttribute('aria-hidden', 'true'); btns[i].removeAttribute('aria-current');
      i = (n + slides.length) % slides.length;
      slides[i].classList.add('activo'); slides[i].removeAttribute('aria-hidden'); btns[i].setAttribute('aria-current', 'true');
      hero.style.setProperty('--ciclo', '0'); void hero.offsetWidth; hero.style.removeProperty('--ciclo');
    }
    function auto() { clearInterval(t); if (!reducido && slides.length > 1) t = setInterval(function () { ir(i + 1); }, 6500); }
    btns.forEach(function (b) { b.addEventListener('click', function () { ir(+b.dataset.ir); auto(); }); });
    hero.addEventListener('mouseenter', function () { clearInterval(t); hero.classList.add('pausa'); });
    hero.addEventListener('mouseleave', function () { hero.classList.remove('pausa'); auto(); });
    var x0 = null;
    hero.addEventListener('touchstart', function (e) { x0 = e.touches[0].clientX; }, { passive: true });
    hero.addEventListener('touchend', function (e) {
      if (x0 === null) return; var dx = e.changedTouches[0].clientX - x0;
      if (Math.abs(dx) > 50) { ir(i + (dx < 0 ? 1 : -1)); auto(); } x0 = null;
    });
    auto();
  }

  /* Filtros del catálogo */
  var rejilla = document.querySelector('[data-rejilla]');
  function filtrar(f) {
    document.querySelectorAll('[data-f]').forEach(function (b) { b.setAttribute('aria-pressed', b.dataset.f === f); });
    if (rejilla) rejilla.querySelectorAll('.tarjeta').forEach(function (c) { c.hidden = !(f === 'todas' || c.dataset.cat === f); });
  }
  document.querySelectorAll('[data-f]').forEach(function (b) { b.addEventListener('click', function () { filtrar(b.dataset.f); }); });
  document.querySelectorAll('[data-filtrar]').forEach(function (a) { a.addEventListener('click', function () { filtrar(a.dataset.filtrar); }); });

  /* Puntos de color en tarjetas */
  document.querySelectorAll('.tarjeta .puntos button').forEach(function (b) {
    function cambiar() {
      var card = b.closest('.tarjeta'), img = card.querySelector('[data-foto]');
      if (img) img.src = b.dataset.img;
      card.querySelectorAll('.puntos button').forEach(function (o) { o.setAttribute('aria-pressed', o === b); });
    }
    b.addEventListener('click', cambiar); b.addEventListener('mouseenter', cambiar);
  });

  /* Visor de la página de modelo */
  var gal = document.getElementById('galeria'), visor = document.querySelector('[data-visor]');
  if (gal && visor) {
    var g = JSON.parse(gal.textContent), c = 0, v = 0;
    var vistas = document.querySelector('[data-vistas]'), nombre = document.querySelector('[data-color-nombre]');
    function mostrar() {
      visor.classList.remove('entra'); void visor.offsetWidth;
      visor.src = g[c].fotos[v]; visor.classList.add('entra');
    }
    function pintarVistas() {
      if (!vistas) return;
      vistas.innerHTML = g[c].fotos.map(function (f, k) {
        return '<button type="button" data-v="' + k + '" aria-pressed="' + (k === v) + '"><img src="' + f + '" alt="" width="120" height="90"><span>' + g[c].vistas[k] + '</span></button>';
      }).join('');
    }
    document.querySelectorAll('[data-color]').forEach(function (b) {
      b.addEventListener('click', function () {
        c = +b.dataset.color; v = Math.min(v, g[c].fotos.length - 1);
        document.querySelectorAll('[data-color]').forEach(function (o) { o.setAttribute('aria-pressed', o === b); });
        if (nombre) nombre.textContent = g[c].nombre;
        mostrar(); pintarVistas();
      });
    });
    if (vistas) vistas.addEventListener('click', function (e) {
      var b = e.target.closest('[data-v]'); if (!b) return;
      v = +b.dataset.v; vistas.querySelectorAll('[data-v]').forEach(function (o) { o.setAttribute('aria-pressed', o === b); });
      mostrar();
    });
  }

  /* Ficha técnica: en celular solo el primer grupo abierto */
  if (window.matchMedia('(max-width:760px)').matches) document.querySelectorAll('.spec').forEach(function (d, k) { if (k) d.open = false; });

  /* Aparición suave al hacer scroll */
  var rev = document.querySelectorAll('.revela');
  if ('IntersectionObserver' in window && !reducido) {
    var io = new IntersectionObserver(function (es) {
      es.forEach(function (e) { if (e.isIntersecting) { e.target.classList.add('visto'); io.unobserve(e.target); } });
    }, { rootMargin: '0px 0px -8% 0px' });
    rev.forEach(function (el) { io.observe(el); });
  } else rev.forEach(function (el) { el.classList.add('visto'); });
})();
