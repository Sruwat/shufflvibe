const openingIntro = document.createElement('div');
openingIntro.className = 'opening-intro';
openingIntro.setAttribute('aria-label', 'SHFFL opening animation');
openingIntro.innerHTML = '<img src="assets/SHFFL_opening.gif" alt="SHFFL opening animation" />';
document.body.prepend(openingIntro);
document.documentElement.classList.add('intro-lock');
document.body.classList.add('intro-lock');

const finishOpening = () => {
  openingIntro.classList.add('is-done');
  document.documentElement.classList.remove('intro-lock');
  document.body.classList.remove('intro-lock');
  window.setTimeout(() => openingIntro.remove(), 650);
};

if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
  finishOpening();
} else {
  window.setTimeout(finishOpening, 1850);
}

const reveals = document.querySelectorAll('.reveal');
const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) { entry.target.classList.add('visible'); observer.unobserve(entry.target); }
  });
}, { threshold: 0.12 });
reveals.forEach((el) => observer.observe(el));

const glow = document.querySelector('.cursor-glow');
if (glow && matchMedia('(pointer:fine)').matches) {
  addEventListener('pointermove', (event) => {
    glow.style.transform = `translate(${event.clientX - 120}px, ${event.clientY - 120}px)`;
  }, { passive: true });
}

const header = document.querySelector('[data-header]');
addEventListener('scroll', () => header?.classList.toggle('scrolled', scrollY > 20), { passive: true });

const menuToggle = document.querySelector('[data-menu-toggle]');
menuToggle?.addEventListener('click', () => {
  const open = header.classList.toggle('menu-open');
  menuToggle.setAttribute('aria-expanded', String(open));
});

const heroSlider = document.querySelector('[data-hero-slider]');
if (heroSlider) {
  const slides = [...heroSlider.querySelectorAll('.hero-slide')];
  const dots = [...heroSlider.querySelectorAll('.hero-dots button')];
  let active = 0;
  let timer;
  const showSlide = (index) => {
    active = index;
    slides.forEach((slide, i) => slide.classList.toggle('is-active', i === active));
    dots.forEach((dot, i) => dot.classList.toggle('is-active', i === active));
  };
  const start = () => { timer = setInterval(() => showSlide((active + 1) % slides.length), 5200); };
  dots.forEach((dot, i) => dot.addEventListener('click', () => { clearInterval(timer); showSlide(i); start(); }));
  start();
}
