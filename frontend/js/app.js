/**
 * app.js — Main application entry point
 * Imports and initialises all page behaviour modules on DOMContentLoaded.
 */

import { initScrollEffects } from './scroll-effects.js';
import { initKpiAccordion }  from './kpi-accordion.js';

document.addEventListener('DOMContentLoaded', () => {
  initScrollEffects();
  initKpiAccordion();
});
