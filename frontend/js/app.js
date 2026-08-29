/**
 * app.js — Main application entry point
 * Imports and initialises all page behaviour modules on DOMContentLoaded.
 * Handles file upload from the landing page and navigation to workspace.
 */

import { initScrollEffects } from './scroll-effects.js';
import { initKpiAccordion }  from './kpi-accordion.js';
import { uploadFile } from './api.js';

document.addEventListener('DOMContentLoaded', () => {
  initScrollEffects();
  initKpiAccordion();
  initUploadFlow();
});

/**
 * Wire all upload buttons/CTAs to trigger file selection.
 * On successful upload, navigate to the workspace.
 */
function initUploadFlow() {
  const fileInput = document.getElementById('global-file-input');
  if (!fileInput) return;

  // All elements that should trigger upload
  const triggers = [
    document.getElementById('nav-upload-btn'),
    document.getElementById('hero-cta'),
    document.getElementById('closing-cta'),
  ];

  triggers.forEach(trigger => {
    if (trigger) {
      trigger.addEventListener('click', (e) => {
        e.preventDefault();
        fileInput.click();
      });
    }
  });

  // Handle file selection
  fileInput.addEventListener('change', async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Show uploading state
    const navBtn = document.getElementById('nav-upload-btn');
    if (navBtn) {
      navBtn.style.pointerEvents = 'none';
      navBtn.textContent = 'Uploading...';
    }

    try {
      const result = await uploadFile(file);

      if (result.success) {
        // Store file info in sessionStorage for the workspace to read
        sessionStorage.setItem('docxpert_file_id', result.data.file_id);
        sessionStorage.setItem('docxpert_file_name', result.data.original_name);
        sessionStorage.setItem('docxpert_file_type', result.data.file_type);
        sessionStorage.setItem('docxpert_file_size', result.data.file_size_human);

        // Navigate to workspace
        window.location.href = '/workspace';
      } else {
        alert('Upload failed: ' + (result.error || 'Unknown error'));
        if (navBtn) {
          navBtn.style.pointerEvents = '';
          navBtn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <path d="M17 8l-5-5-5 5"/>
              <path d="M12 3v12"/>
            </svg> Upload`;
        }
      }
    } catch (err) {
      alert('Upload error: ' + err.message);
      if (navBtn) {
        navBtn.style.pointerEvents = '';
        navBtn.innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="14" height="14">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <path d="M17 8l-5-5-5 5"/>
            <path d="M12 3v12"/>
          </svg> Upload`;
      }
    }

    fileInput.value = '';
  });
}
