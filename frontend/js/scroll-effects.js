/**
 * scroll-effects.js
 * Feature cards staggered entrance animation using IntersectionObserver.
 */

export function initScrollEffects() {
  const cards = document.querySelectorAll('.feature-card');
  if (!cards.length) return;

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.style.opacity = '1';
        entry.target.style.transform = 'translateY(0)';
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.15 });

  cards.forEach((card, i) => {
    card.style.opacity = '0';
    card.style.transform = 'translateY(24px)';
    card.style.transition = `opacity 0.5s ease ${i * 0.08}s, transform 0.5s ease ${i * 0.08}s, border-color 0.25s ease, box-shadow 0.25s ease`;
    observer.observe(card);
  });
}
