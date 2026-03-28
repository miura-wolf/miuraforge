// ─── NAV SCROLL ──────────────────────────────────────────────────────
const nav = document.querySelector('.nav');
window.addEventListener('scroll', () => {
  nav.classList.toggle('scrolled', window.scrollY > 60);
});

// ─── HAMBURGER MENU ──────────────────────────────────────────────────
const hamburger = document.querySelector('.nav__hamburger');
const navLinks  = document.querySelector('.nav__links');
if (hamburger && navLinks) {
  hamburger.addEventListener('click', () => {
    const open = navLinks.style.display === 'flex';
    navLinks.style.display = open ? 'none' : 'flex';
    navLinks.style.flexDirection = 'column';
    navLinks.style.position = 'fixed';
    navLinks.style.top = '60px';
    navLinks.style.left = '0';
    navLinks.style.right = '0';
    navLinks.style.background = 'rgba(10,10,10,0.98)';
    navLinks.style.padding = '2rem';
    navLinks.style.gap = '1.5rem';
    navLinks.style.borderBottom = '1px solid #2A2A2A';
  });
}

// ─── REVEAL ON SCROLL ────────────────────────────────────────────────
const revealEls = document.querySelectorAll('.reveal');
const observer  = new IntersectionObserver((entries) => {
  entries.forEach((entry, i) => {
    if (entry.isIntersecting) {
      setTimeout(() => entry.target.classList.add('visible'), i * 80);
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });

revealEls.forEach(el => observer.observe(el));

// ─── FORM LEAD MAGNET ────────────────────────────────────────────────
const formLead = document.getElementById('form-lead');
if (formLead) {
  formLead.addEventListener('submit', async (e) => {
    e.preventDefault();
    const nombre = document.getElementById('input-nombre')?.value.trim() || '';
    const email  = document.getElementById('input-email')?.value.trim()  || '';
    const btn    = formLead.querySelector('button');

    if (!email || !email.includes('@')) return;

    btn.textContent = 'PROCESANDO...';
    btn.disabled = true;

    // ── CONFIGURACIÓN ──────────────────────────────────────────────
    // Reemplaza esta URL con la que te da Google Apps Script al implementar
    const APPS_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbwgVox-b6T_P_79pjx0Q9zUGAqYk_p7a_uZFaz2alCdHU-ULc3gaRCs_OMBA2LfBzzm/exec';

    const fuente = window.location.pathname.includes('ebook')
      ? 'pagina_libro'
      : window.location.pathname.includes('merch')
      ? 'pagina_merch'
      : 'landing_principal';

    try {
      await fetch(APPS_SCRIPT_URL, {
        method: 'POST',
        // Apps Script requiere text/plain para evitar preflight CORS
        headers: { 'Content-Type': 'text/plain' },
        body: JSON.stringify({ accion: 'capturar', nombre, email, fuente })
      });
    } catch (err) {
      // Si falla la red igual redirigimos — no bloqueamos al usuario
      console.warn('[Leads] Error conectando con Sheets:', err);
    }

    // Redirigir a confirmación con nombre y email
    const params = new URLSearchParams({ nombre, email, url: APPS_SCRIPT_URL });
    window.location.href = `pages/confirmacion.html?${params.toString()}`;
  });
}

// ─── SMOOTH SCROLL PARA ANCLAS ───────────────────────────────────────
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
  anchor.addEventListener('click', (e) => {
    const target = document.querySelector(anchor.getAttribute('href'));
    if (target) {
      e.preventDefault();
      target.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });
});
