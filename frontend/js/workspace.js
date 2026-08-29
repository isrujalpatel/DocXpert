/**
 * workspace.js — DocXpert Workspace Controller.
 *
 * Handles tab switching, feature forms, API calls, rendering results,
 * and coordinating the review panel for accept/reject flows.
 */

import * as api from './api.js';
import { renderReviewPanel, showLoading, showError, renderComparisonHeader } from './review-panel.js';

// ── State ────────────────────────────────────────────────────
let state = {
  fileId: null,
  fileName: null,
  fileType: null,
  fileSize: null,
  activePanel: 'convert',
  compareFile: null,
};

// ── Initialization ───────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  // Check if a file was passed via URL params or sessionStorage
  const params = new URLSearchParams(window.location.search);
  const storedFileId = params.get('file_id') || sessionStorage.getItem('docxpert_file_id');
  const storedFileName = params.get('file_name') || sessionStorage.getItem('docxpert_file_name');
  const storedFileType = params.get('file_type') || sessionStorage.getItem('docxpert_file_type');
  const storedFileSize = params.get('file_size') || sessionStorage.getItem('docxpert_file_size');

  if (storedFileId) {
    state.fileId = storedFileId;
    state.fileName = storedFileName || 'document';
    state.fileType = storedFileType || 'docx';
    state.fileSize = storedFileSize || '';
    updateFileInfo();
  } else {
    // No file — prompt upload
    promptUpload();
  }

  initNavigation();
  initConvert();
  initFindReplace();
  initSpellCheck();
  initFormatEnhance();
  initCompare();
  initAdjustSettings();
  initSidebarActions();
});

// ── File Info ────────────────────────────────────────────────
function updateFileInfo() {
  const nameEl = document.getElementById('ws-file-name-text');
  const badgeEl = document.getElementById('ws-file-badge');
  const metaEl = document.getElementById('ws-file-meta');

  if (nameEl) nameEl.textContent = state.fileName || 'No file loaded';

  if (badgeEl && state.fileType) {
    badgeEl.textContent = state.fileType.toUpperCase();
    badgeEl.className = `file-type-badge badge-${state.fileType}`;
    badgeEl.style.display = 'inline';
  }

  if (metaEl && state.fileSize) {
    metaEl.textContent = state.fileSize;
  }
}

function promptUpload() {
  const input = document.getElementById('ws-new-file-input');
  if (input) {
    input.click();
  }
}

// ── Navigation ───────────────────────────────────────────────
function initNavigation() {
  const navItems = document.querySelectorAll('.ws-nav-item');

  navItems.forEach(item => {
    item.addEventListener('click', () => {
      const panel = item.dataset.panel;
      if (!panel) return;

      // Update nav
      navItems.forEach(n => n.classList.remove('active'));
      item.classList.add('active');

      // Update panels
      document.querySelectorAll('.ws-panel').forEach(p => p.classList.remove('active'));
      const targetPanel = document.getElementById(`panel-${panel}`);
      if (targetPanel) targetPanel.classList.add('active');

      // Update topbar title
      const topTitle = document.getElementById('ws-topbar-title');
      if (topTitle) topTitle.textContent = item.textContent.trim();

      state.activePanel = panel;
    });
  });
}

// ── Sidebar Actions ──────────────────────────────────────────
function initSidebarActions() {
  // Download button
  const downloadBtn = document.getElementById('ws-download-btn');
  if (downloadBtn) {
    downloadBtn.addEventListener('click', async () => {
      if (!state.fileId) {
        showToast('No file to download', 'error');
        return;
      }
      try {
        await api.downloadFile(state.fileId, state.fileName);
        showToast('Download started!', 'success');
      } catch (e) {
        showToast(e.message, 'error');
      }
    });
  }

  // New file button
  const newBtn = document.getElementById('ws-new-btn');
  const newInput = document.getElementById('ws-new-file-input');

  if (newBtn && newInput) {
    newBtn.addEventListener('click', () => newInput.click());

    newInput.addEventListener('change', async (e) => {
      const file = e.target.files[0];
      if (!file) return;

      showToast('Uploading...', 'info');

      try {
        const result = await api.uploadFile(file);
        if (result.success) {
          state.fileId = result.data.file_id;
          state.fileName = result.data.original_name;
          state.fileType = result.data.file_type;
          state.fileSize = result.data.file_size_human;

          // Persist to sessionStorage
          sessionStorage.setItem('docxpert_file_id', state.fileId);
          sessionStorage.setItem('docxpert_file_name', state.fileName);
          sessionStorage.setItem('docxpert_file_type', state.fileType);
          sessionStorage.setItem('docxpert_file_size', state.fileSize);

          updateFileInfo();
          showToast(`Uploaded: ${state.fileName}`, 'success');
        } else {
          showToast(result.error || 'Upload failed', 'error');
        }
      } catch (e) {
        showToast('Upload failed: ' + e.message, 'error');
      }

      newInput.value = '';
    });
  }
}

// ── Convert ──────────────────────────────────────────────────
function initConvert() {
  const options = document.querySelectorAll('.convert-option');
  let targetFormat = 'pdf';

  options.forEach(opt => {
    opt.addEventListener('click', () => {
      options.forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      targetFormat = opt.dataset.format;
    });
  });

  const btn = document.getElementById('btn-convert');
  const resultContainer = document.getElementById('convert-result');

  if (btn) {
    btn.addEventListener('click', async () => {
      if (!state.fileId) {
        showToast('Upload a file first', 'error');
        return;
      }

      btn.disabled = true;
      btn.textContent = 'Converting...';
      showLoading(resultContainer, 'Converting document...');

      try {
        const result = await api.convertFile(state.fileId, targetFormat);

        if (result.success) {
          // Update state with the converted file
          state.fileId = result.data.file_id;
          state.fileType = result.data.file_type;
          state.fileName = state.fileName.replace(/\.\w+$/, `.${result.data.file_type}`);
          state.fileSize = result.data.file_size_human;

          sessionStorage.setItem('docxpert_file_id', state.fileId);
          sessionStorage.setItem('docxpert_file_name', state.fileName);
          sessionStorage.setItem('docxpert_file_type', state.fileType);
          sessionStorage.setItem('docxpert_file_size', state.fileSize);

          updateFileInfo();

          resultContainer.innerHTML = `
            <div class="ws-card" style="border-color: rgba(39, 201, 63, 0.3);">
              <div class="ws-card-title" style="color: #27c93f;">✓ Conversion Complete</div>
              <p style="color: rgba(255,255,255,0.5); font-size: 0.82rem;">
                ${result.message} — ${result.data.file_size_human}
              </p>
              <div class="ws-btn-row">
                <button class="ws-btn ws-btn-primary" onclick="document.getElementById('ws-download-btn').click()">
                  Download Converted File
                </button>
              </div>
            </div>
          `;

          showToast('Conversion complete!', 'success');
        } else {
          showError(resultContainer, result.error);
        }
      } catch (e) {
        showError(resultContainer, e.message);
      }

      btn.disabled = false;
      btn.innerHTML = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" width="15" height="15"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><path d="M14 2v6h6"/></svg> Convert Now`;
    });
  }
}

// ── Find & Replace ───────────────────────────────────────────
function initFindReplace() {
  const btn = document.getElementById('btn-replace');
  const resultContainer = document.getElementById('replace-result');

  if (btn) {
    btn.addEventListener('click', async () => {
      if (!state.fileId) {
        showToast('Upload a file first', 'error');
        return;
      }

      const findText = document.getElementById('find-text').value;
      const replaceText = document.getElementById('replace-text').value;
      const useRegex = document.getElementById('use-regex').checked;
      const caseSensitive = document.getElementById('case-sensitive').checked;

      if (!findText) {
        showToast('Enter text to find', 'error');
        return;
      }

      btn.disabled = true;
      showLoading(resultContainer, 'Replacing...');

      try {
        const result = await api.findReplace(state.fileId, findText, replaceText, useRegex, caseSensitive);

        if (result.success) {
          state.fileId = result.data.file_id;
          sessionStorage.setItem('docxpert_file_id', state.fileId);

          resultContainer.innerHTML = `
            <div class="ws-card" style="border-color: rgba(39, 201, 63, 0.3);">
              <div class="ws-card-title" style="color: #27c93f;">✓ Replace Complete</div>
              <p style="color: rgba(255,255,255,0.5); font-size: 0.82rem;">
                ${result.message}
              </p>
            </div>
          `;

          showToast(`${result.data.replacements_made} replacement(s) made`, 'success');
        } else {
          showError(resultContainer, result.error);
        }
      } catch (e) {
        showError(resultContainer, e.message);
      }

      btn.disabled = false;
    });
  }
}

// ── Spell Check ──────────────────────────────────────────────
function initSpellCheck() {
  const btn = document.getElementById('btn-spell-check');
  const resultContainer = document.getElementById('spell-check-results');

  if (btn) {
    btn.addEventListener('click', async () => {
      if (!state.fileId) {
        showToast('Upload a file first', 'error');
        return;
      }

      btn.disabled = true;
      showLoading(resultContainer, 'Running spell check...');

      try {
        const result = await api.spellCheck(state.fileId);

        if (result.success) {
          renderReviewPanel(resultContainer, result.data.suggestions, {
            fileId: state.fileId,
            onApply: handleApplyChanges,
          });

          if (result.data.total === 0) {
            showToast('No issues found!', 'success');
          } else {
            showToast(`Found ${result.data.total} issue(s)`, 'info');
          }
        } else {
          showError(resultContainer, result.error);
        }
      } catch (e) {
        showError(resultContainer, e.message);
      }

      btn.disabled = false;
    });
  }
}

// ── Format Enhancement ───────────────────────────────────────
function initFormatEnhance() {
  const btn = document.getElementById('btn-format-enhance');
  const resultContainer = document.getElementById('format-enhance-results');

  if (btn) {
    btn.addEventListener('click', async () => {
      if (!state.fileId) {
        showToast('Upload a file first', 'error');
        return;
      }

      btn.disabled = true;
      showLoading(resultContainer, 'Analyzing formatting...');

      try {
        const result = await api.formatEnhance(state.fileId);

        if (result.success) {
          renderReviewPanel(resultContainer, result.data.suggestions, {
            fileId: state.fileId,
            onApply: handleApplyChanges,
          });

          showToast(`Found ${result.data.total} formatting suggestion(s)`, 'info');
        } else {
          showError(resultContainer, result.error);
        }
      } catch (e) {
        showError(resultContainer, e.message);
      }

      btn.disabled = false;
    });
  }
}

// ── Compare ──────────────────────────────────────────────────
function initCompare() {
  const dropzone = document.getElementById('compare-dropzone');
  const fileInput = document.getElementById('compare-file-input');
  const fileNameEl = document.getElementById('compare-file-name');
  const btn = document.getElementById('btn-compare');
  const resultContainer = document.getElementById('compare-results');

  if (dropzone && fileInput) {
    dropzone.addEventListener('click', () => fileInput.click());

    dropzone.addEventListener('dragover', (e) => {
      e.preventDefault();
      dropzone.style.borderColor = 'rgba(59, 76, 202, 0.5)';
    });

    dropzone.addEventListener('dragleave', () => {
      dropzone.style.borderColor = '';
    });

    dropzone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropzone.style.borderColor = '';
      const file = e.dataTransfer.files[0];
      if (file) {
        state.compareFile = file;
        fileNameEl.textContent = file.name;
        dropzone.classList.add('has-file');
        btn.disabled = false;
      }
    });

    fileInput.addEventListener('change', (e) => {
      const file = e.target.files[0];
      if (file) {
        state.compareFile = file;
        fileNameEl.textContent = file.name;
        dropzone.classList.add('has-file');
        btn.disabled = false;
      }
    });
  }

  if (btn) {
    btn.addEventListener('click', async () => {
      if (!state.fileId) {
        showToast('Upload a primary file first', 'error');
        return;
      }
      if (!state.compareFile) {
        showToast('Select a comparison file', 'error');
        return;
      }

      btn.disabled = true;
      showLoading(resultContainer, 'Comparing documents...');

      try {
        const result = await api.compareDocuments(state.fileId, state.compareFile);

        if (result.success) {
          resultContainer.innerHTML = '';
          renderComparisonHeader(resultContainer, result.data);
          const reviewDiv = document.createElement('div');
          resultContainer.appendChild(reviewDiv);

          renderReviewPanel(reviewDiv, result.data.suggestions, {
            fileId: state.fileId,
            onApply: handleApplyChanges,
          });

          showToast(`Found ${result.data.total} difference(s)`, 'info');
        } else {
          showError(resultContainer, result.error);
        }
      } catch (e) {
        showError(resultContainer, e.message);
      }

      btn.disabled = false;
    });
  }
}

// ── Adjust Settings ──────────────────────────────────────────
function initAdjustSettings() {
  const btn = document.getElementById('btn-adjust-settings');
  const resultContainer = document.getElementById('adjust-settings-results');

  if (btn) {
    btn.addEventListener('click', async () => {
      if (!state.fileId) {
        showToast('Upload a file first', 'error');
        return;
      }

      const intent = document.getElementById('doc-intent').value;

      btn.disabled = true;
      showLoading(resultContainer, 'Analyzing settings...');

      try {
        const result = await api.adjustSettings(state.fileId, intent);

        if (result.success) {
          renderReviewPanel(resultContainer, result.data.suggestions, {
            fileId: state.fileId,
            onApply: handleApplyChanges,
          });

          showToast(`Found ${result.data.total} suggestion(s)`, 'info');
        } else {
          showError(resultContainer, result.error);
        }
      } catch (e) {
        showError(resultContainer, e.message);
      }

      btn.disabled = false;
    });
  }
}

// ── Apply Changes (shared callback) ──────────────────────────
async function handleApplyChanges(acceptedIds, allChanges) {
  if (!state.fileId) return;

  showToast('Applying changes...', 'info');

  try {
    const result = await api.applyChanges(state.fileId, acceptedIds, allChanges);

    if (result.success) {
      state.fileId = result.data.file_id;
      state.fileSize = result.data.file_size_human;

      sessionStorage.setItem('docxpert_file_id', state.fileId);
      sessionStorage.setItem('docxpert_file_size', state.fileSize);

      updateFileInfo();

      showToast(`Applied ${result.data.changes_applied} change(s). Downloading...`, 'success');

      // Auto-download the result
      await api.downloadFile(state.fileId, state.fileName);
    } else {
      showToast(result.error || 'Failed to apply changes', 'error');
    }
  } catch (e) {
    showToast('Error applying changes: ' + e.message, 'error');
  }
}

// ── Toast Notification ───────────────────────────────────────
function showToast(message, type = 'info') {
  // Remove existing toasts
  document.querySelectorAll('.ws-toast').forEach(t => t.remove());

  const toast = document.createElement('div');
  toast.className = `ws-toast ${type}`;
  toast.textContent = message;
  document.body.appendChild(toast);

  setTimeout(() => toast.remove(), 3200);
}
