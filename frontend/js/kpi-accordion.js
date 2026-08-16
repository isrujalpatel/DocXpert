/**
 * kpi-accordion.js
 * Three-dots button click handler: toggles expanded state on KPI/feature cards.
 * Clicking the ⋯ button reveals the `.expanded-details` panel inside each card.
 */

export function initKpiAccordion() {
  const dotsBtns = document.querySelectorAll('.card-dots-btn');

  dotsBtns.forEach((btn) => {
    btn.addEventListener('click', (e) => {
      e.stopPropagation();
      const card = btn.closest('.feature-card');
      if (card) {
        card.classList.toggle('expanded');
      }
    });
  });
}
