/**
 * api.js — DocXpert API client module.
 *
 * All API calls return { success, data?, error?, message? }.
 * Base URL defaults to current origin (Flask serves both frontend and API).
 */

const API_BASE = window.location.origin;

/**
 * Upload a file to the server.
 * @param {File} file - The file to upload.
 * @returns {Promise<Object>} Upload response with file_id.
 */
export async function uploadFile(file) {
  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: 'POST',
    body: formData,
  });
  return res.json();
}

/**
 * Get file metadata.
 * @param {string} fileId - UUID of the file.
 */
export async function getFileMetadata(fileId) {
  const res = await fetch(`${API_BASE}/api/files/${fileId}`);
  return res.json();
}

/**
 * Download a file.
 * @param {string} fileId - UUID of the file.
 * @param {string} [name] - Optional download filename.
 */
export async function downloadFile(fileId, name) {
  const url = name
    ? `${API_BASE}/api/files/${fileId}/download?name=${encodeURIComponent(name)}`
    : `${API_BASE}/api/files/${fileId}/download`;

  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.error || 'Download failed');
  }

  const blob = await res.blob();
  const a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = name || `document-${fileId}`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(a.href);
}

/**
 * Convert a document.
 * @param {string} fileId
 * @param {string} targetFormat - 'pdf' or 'docx'
 */
export async function convertFile(fileId, targetFormat) {
  const res = await fetch(`${API_BASE}/api/convert`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_id: fileId, target_format: targetFormat }),
  });
  return res.json();
}

/**
 * Find and replace text.
 */
export async function findReplace(fileId, findText, replaceText, useRegex = false, caseSensitive = true) {
  const res = await fetch(`${API_BASE}/api/find-replace`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_id: fileId,
      find_text: findText,
      replace_text: replaceText,
      use_regex: useRegex,
      case_sensitive: caseSensitive,
    }),
  });
  return res.json();
}

/**
 * Run AI spell check.
 */
export async function spellCheck(fileId) {
  const res = await fetch(`${API_BASE}/api/ai/spell-check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_id: fileId }),
  });
  return res.json();
}

/**
 * Run AI formatting enhancement.
 */
export async function formatEnhance(fileId) {
  const res = await fetch(`${API_BASE}/api/ai/format-enhance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_id: fileId }),
  });
  return res.json();
}

/**
 * Compare two documents.
 * @param {string} fileIdA - First file UUID.
 * @param {string|File} fileB - Second file UUID or File object.
 */
export async function compareDocuments(fileIdA, fileB) {
  if (typeof fileB === 'string') {
    // Both are file IDs
    const res = await fetch(`${API_BASE}/api/ai/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ file_id_a: fileIdA, file_id_b: fileB }),
    });
    return res.json();
  } else {
    // fileB is a File object — upload first, then compare
    const uploadResult = await uploadFile(fileB);
    if (!uploadResult.success) return uploadResult;

    const res = await fetch(`${API_BASE}/api/ai/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        file_id_a: fileIdA,
        file_id_b: uploadResult.data.file_id,
      }),
    });
    return res.json();
  }
}

/**
 * Get AI settings suggestions.
 */
export async function adjustSettings(fileId, intent = '') {
  const res = await fetch(`${API_BASE}/api/ai/adjust-settings`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ file_id: fileId, intent }),
  });
  return res.json();
}

/**
 * Apply accepted AI changes to a document.
 */
export async function applyChanges(fileId, acceptedChangeIds, allChanges) {
  const res = await fetch(`${API_BASE}/api/ai/apply-changes`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      file_id: fileId,
      accepted_change_ids: acceptedChangeIds,
      all_changes: allChanges,
    }),
  });
  return res.json();
}
