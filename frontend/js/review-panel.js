/**
 * review-panel.js — Shared review panel component.
 *
 * Renders SuggestedChange[] as interactive cards with accept/reject buttons.
 * Used by spell check, formatting enhancement, settings adjustment, and comparison.
 */

/**
 * Render a review panel with suggestion cards.
 *
 * @param {HTMLElement} container - DOM element to render into.
 * @param {Array} suggestions - Array of SuggestedChange objects from the API.
 * @param {Object} options - { fileId, onApply }
 */
export function renderReviewPanel(container, suggestions, options = {}) {
  if (!suggestions || suggestions.length === 0) {
    container.innerHTML = `
      <div class="ws-empty">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <p>No issues found — your document looks great!</p>
      </div>
    `;
    return;
  }

  // Track statuses
  const statuses = {};
  suggestions.forEach(s => { statuses[s.id] = 'pending'; });

  function getAcceptedCount() {
    return Object.values(statuses).filter(s => s === 'accepted').length;
  }

  function getRejectedCount() {
    return Object.values(statuses).filter(s => s === 'rejected').length;
  }

  function getPendingCount() {
    return Object.values(statuses).filter(s => s === 'pending').length;
  }

  function updateStats() {
    const statsEl = container.querySelector('.review-stats');
    if (statsEl) {
      statsEl.textContent = `${getAcceptedCount()} accepted · ${getRejectedCount()} rejected · ${getPendingCount()} pending`;
    }

    const applyInfo = container.querySelector('.review-apply-info');
    if (applyInfo) {
      applyInfo.innerHTML = `<strong>${getAcceptedCount()}</strong> change(s) will be applied`;
    }

    const applyBtn = container.querySelector('.btn-apply-changes');
    if (applyBtn) {
      applyBtn.disabled = getAcceptedCount() === 0;
    }
  }

  function updateCardUI(cardEl, status) {
    cardEl.classList.remove('accepted', 'rejected');
    if (status !== 'pending') {
      cardEl.classList.add(status);
    }
  }

  // Build HTML
  let html = `
    <div class="review-panel">
      <div class="review-header">
        <div>
          <h3>Review Suggestions</h3>
          <div class="review-stats">${suggestions.length} pending</div>
        </div>
        <div class="review-bulk-actions">
          <button class="review-bulk-btn accept-all" id="bulk-accept-all">✓ Accept All</button>
          <button class="review-bulk-btn reject-all" id="bulk-reject-all">✕ Reject All</button>
        </div>
      </div>
      <div class="suggestion-list">
  `;

  suggestions.forEach((s) => {
    const typeClass = `type-${s.type}`;
    const original = escapeHtml(s.original || '—');
    const suggested = escapeHtml(s.suggested || '—');
    const explanation = escapeHtml(s.explanation || '');
    const context = s.location?.context ? escapeHtml(s.location.context) : '';

    html += `
      <div class="suggestion-card" data-id="${s.id}" id="card-${s.id}">
        <div class="suggestion-top">
          <span class="suggestion-type ${typeClass}">${s.type}</span>
          <div class="suggestion-actions">
            <button class="suggestion-action-btn accept" data-id="${s.id}" title="Accept">✓</button>
            <button class="suggestion-action-btn reject" data-id="${s.id}" title="Reject">✕</button>
          </div>
        </div>
        <div class="suggestion-body">
          <div class="suggestion-diff">
            <span class="diff-original">${original}</span>
            <span class="diff-arrow">→</span>
            <span class="diff-suggested">${suggested}</span>
          </div>
          ${explanation ? `<div class="suggestion-explanation">${explanation}</div>` : ''}
          ${context ? `<div class="suggestion-context">"…${context}…"</div>` : ''}
        </div>
      </div>
    `;
  });

  html += `
      </div>
      <div class="review-apply-bar">
        <div class="review-apply-info"><strong>0</strong> change(s) will be applied</div>
        <button class="ws-btn ws-btn-primary btn-apply-changes" disabled>
          Apply & Download
        </button>
      </div>
    </div>
  `;

  container.innerHTML = html;

  // Event delegation
  container.addEventListener('click', (e) => {
    const acceptBtn = e.target.closest('.suggestion-action-btn.accept');
    const rejectBtn = e.target.closest('.suggestion-action-btn.reject');
    const bulkAccept = e.target.closest('#bulk-accept-all');
    const bulkReject = e.target.closest('#bulk-reject-all');
    const applyBtn = e.target.closest('.btn-apply-changes');

    if (acceptBtn) {
      const id = acceptBtn.dataset.id;
      statuses[id] = statuses[id] === 'accepted' ? 'pending' : 'accepted';
      const card = container.querySelector(`#card-${id}`);
      if (card) updateCardUI(card, statuses[id]);
      updateStats();
    }

    if (rejectBtn) {
      const id = rejectBtn.dataset.id;
      statuses[id] = statuses[id] === 'rejected' ? 'pending' : 'rejected';
      const card = container.querySelector(`#card-${id}`);
      if (card) updateCardUI(card, statuses[id]);
      updateStats();
    }

    if (bulkAccept) {
      suggestions.forEach(s => {
        statuses[s.id] = 'accepted';
        const card = container.querySelector(`#card-${s.id}`);
        if (card) updateCardUI(card, 'accepted');
      });
      updateStats();
    }

    if (bulkReject) {
      suggestions.forEach(s => {
        statuses[s.id] = 'rejected';
        const card = container.querySelector(`#card-${s.id}`);
        if (card) updateCardUI(card, 'rejected');
      });
      updateStats();
    }

    if (applyBtn && !applyBtn.disabled && options.onApply) {
      const acceptedIds = Object.entries(statuses)
        .filter(([, status]) => status === 'accepted')
        .map(([id]) => id);
      options.onApply(acceptedIds, suggestions);
    }
  });
}

/**
 * Show a loading state in a container.
 */
export function showLoading(container, message = 'Analyzing...') {
  container.innerHTML = `
    <div class="ws-loading">
      <div class="ws-spinner"></div>
      <span>${message}</span>
    </div>
  `;
}

/**
 * Show an error state in a container.
 */
export function showError(container, message) {
  container.innerHTML = `
    <div class="ws-card" style="border-color: rgba(255, 95, 86, 0.3);">
      <div class="ws-card-title" style="color: #ff5f56;">⚠ Error</div>
      <p style="color: rgba(255,255,255,0.5); font-size: 0.82rem;">${escapeHtml(message)}</p>
    </div>
  `;
}

/**
 * Show a comparison result with similarity score.
 */
export function renderComparisonHeader(container, data) {
  const score = Math.round((data.similarity_score || 0) * 100);
  const header = document.createElement('div');
  header.className = 'ws-card';
  header.innerHTML = `
    <div class="ws-card-title">Comparison Result</div>
    <div style="display:flex; gap:2rem; margin-bottom:0.5rem;">
      <div style="font-size:0.78rem; color:rgba(255,255,255,0.5);">
        Document A: <strong style="color:#fff;">${data.paragraphs_a} paragraphs</strong>
      </div>
      <div style="font-size:0.78rem; color:rgba(255,255,255,0.5);">
        Document B: <strong style="color:#fff;">${data.paragraphs_b} paragraphs</strong>
      </div>
      <div style="font-size:0.78rem; color:rgba(255,255,255,0.5);">
        Similarity: <strong style="color:#fff;">${score}%</strong>
      </div>
    </div>
    <div class="similarity-bar">
      <div class="similarity-fill" style="width: ${score}%"></div>
    </div>
  `;
  container.prepend(header);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
