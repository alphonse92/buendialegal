document.getElementById('copy-year').textContent = new Date().getFullYear();

// Número de WhatsApp en formato internacional sin + ni espacios
const WA_NUMBER = '573177894539';

// Fade-in on scroll
const revealObserver = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add('visible');
        revealObserver.unobserve(entry.target);
      }
    });
  },
  { threshold: 0.15 }
);

document.querySelectorAll('.reveal').forEach((el) => revealObserver.observe(el));

// Navbar scroll effect
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
  navbar.classList.toggle('scrolled', window.scrollY > 60);
}, { passive: true });

// Menu hamburguesa
const navToggle = document.querySelector('.nav-toggle');
const navLinks  = document.querySelectorAll('#nav-links a');

navToggle.addEventListener('click', () => {
  const isOpen = navbar.classList.toggle('nav-open');
  navToggle.setAttribute('aria-expanded', String(isOpen));
});

navLinks.forEach((link) => {
  link.addEventListener('click', () => {
    navbar.classList.remove('nav-open');
    navToggle.setAttribute('aria-expanded', 'false');
  });
});

document.addEventListener('click', (e) => {
  if (!navbar.contains(e.target)) {
    navbar.classList.remove('nav-open');
    navToggle.setAttribute('aria-expanded', 'false');
  }
});

// Formulario → WhatsApp
const form = document.getElementById('contact-form');

form.addEventListener('submit', (e) => {
  e.preventDefault();

  const nombre   = form.nombre.value.trim();
  const email    = form.email.value.trim();
  const telefono = form.telefono.value.trim();
  const area     = form.area.value;
  const caso     = form.mensaje.value.trim();

  // Validar campos obligatorios
  const campos = [
    { el: form.nombre,   val: nombre },
    { el: form.telefono, val: telefono },
    { el: form.area,     val: area },
    { el: form.mensaje,  val: caso },
  ];

  let valido = true;
  campos.forEach(({ el, val }) => {
    if (!val) {
      el.style.borderColor = '#ef4444';
      el.addEventListener('input', () => { el.style.borderColor = ''; }, { once: true });
      valido = false;
    }
  });

  if (!valido) return;

  // Construir mensaje
  const contactoEmail = email ? `\no al correo ${email}` : '';

  const mensaje =
`Hola, soy ${nombre} quisiera hacer la siguiente consulta (${area}):

${caso}

puedes contactarme al siguiente teléfono ${telefono}${contactoEmail}`;

  const url = `https://wa.me/${WA_NUMBER}?text=${encodeURIComponent(mensaje)}`;

  // Mostrar confirmación y abrir WhatsApp
  const submitBtn = form.querySelector('[type="submit"]');
  submitBtn.disabled = true;
  submitBtn.textContent = 'Abriendo WhatsApp…';

  setTimeout(() => {
    window.open(url, '_blank');
    form.reset();
    submitBtn.disabled = false;
    submitBtn.textContent = 'Enviar Consulta';
  }, 500);
});
