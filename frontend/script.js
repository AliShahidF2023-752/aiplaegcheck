/**
 * Plagiarism Checker Frontend Logic
 */

// DOM Elements
const textInput = document.getElementById('text-input');
const pdfUpload = document.getElementById('pdf-upload');
const fileName = document.getElementById('file-name');
const checkBtn = document.getElementById('check-btn');
const rephraseBtn = document.getElementById('rephrase-btn');
const loadingSection = document.getElementById('loading');
const resultsSection = document.getElementById('results');
const summaryContent = document.getElementById('summary-content');
const plagiarismResults = document.getElementById('plagiarism-results');
const aiResults = document.getElementById('ai-results');
const rephrasedSection = document.getElementById('rephrased-section');
const rephrasedText = document.getElementById('rephrased-text');
const copyRephrasedBtn = document.getElementById('copy-rephrased');
const errorSection = document.getElementById('error');
const errorMessage = document.getElementById('error-message');

// State
let currentText = '';
let lastCheckResults = null;

// Event Listeners
pdfUpload.addEventListener('change', handleFileSelect);
checkBtn.addEventListener('click', handleCheck);
rephraseBtn.addEventListener('click', handleRephrase);
copyRephrasedBtn.addEventListener('click', copyToClipboard);

/**
 * Handle file selection
 */
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        fileName.textContent = file.name;
        // Clear text input when file is selected
        textInput.value = '';
    } else {
        fileName.textContent = 'No file chosen';
    }
}

/**
 * Handle check button click
 */
async function handleCheck() {
    hideError();
    hideResults();
    
    const text = textInput.value.trim();
    const file = pdfUpload.files[0];
    
    if (!text && !file) {
        showError('Please enter text or upload a PDF file.');
        return;
    }
    
    showLoading();
    
    try {
        const formData = new FormData();
        
        if (file) {
            formData.append('file', file);
        } else {
            formData.append('text', text);
        }
        
        const response = await fetch('/check', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to check text');
        }
        
        const data = await response.json();
        lastCheckResults = data;
        currentText = data.original_text;
        
        displayResults(data);
        rephraseBtn.disabled = false;
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Handle rephrase button click
 */
async function handleRephrase() {
    if (!currentText) {
        showError('No text to rephrase. Please run a check first.');
        return;
    }
    
    hideError();
    showLoading();
    
    try {
        const formData = new FormData();
        formData.append('text', currentText);
        
        const response = await fetch('/rephrase', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to rephrase text');
        }
        
        const data = await response.json();
        
        displayResults(data);
        displayRephrasedText(data.rephrased_text);
        
        // Update current text to rephrased version
        currentText = data.rephrased_text;
        textInput.value = data.rephrased_text;
        
    } catch (error) {
        showError(error.message);
    } finally {
        hideLoading();
    }
}

/**
 * Display check/rephrase results
 */
function displayResults(data) {
    // Display summary
    summaryContent.innerHTML = formatSummary(data.summary);
    
    // Display plagiarism results
    plagiarismResults.innerHTML = formatServiceResults(data.plagiarism_results);
    
    // Display AI detection results
    aiResults.innerHTML = formatServiceResults(data.ai_detection_results);
    
    resultsSection.classList.remove('hidden');
}

/**
 * Format summary text with basic markdown support
 */
function formatSummary(summary) {
    if (!summary) return '<p>No summary available.</p>';
    
    // Convert markdown-style headers
    let formatted = summary
        .replace(/^### (.+)$/gm, '<h4>$1</h4>')
        .replace(/^## (.+)$/gm, '<h3>$1</h3>')
        .replace(/^# (.+)$/gm, '<h2>$1</h2>')
        // Bold text
        .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
        // Italic text
        .replace(/\*(.+?)\*/g, '<em>$1</em>')
        // Line breaks
        .replace(/\n/g, '<br>');
    
    return formatted;
}

/**
 * Format service results for display
 */
function formatServiceResults(results) {
    if (!results || results.length === 0) {
        return '<p class="no-results">No services were enabled for this check.</p>';
    }
    
    return results.map(result => {
        const statusClass = result.success ? 'success' : 'error';
        const statusText = result.success ? 'Completed' : `Error: ${result.error}`;
        const details = result.success && result.result 
            ? `<div class="service-details">${JSON.stringify(result.result, null, 2)}</div>`
            : '';
        
        return `
            <div class="service-result ${statusClass}">
                <div class="service-name">${escapeHtml(result.service_name)}</div>
                <div class="service-status">${escapeHtml(statusText)}</div>
                ${details}
            </div>
        `;
    }).join('');
}

/**
 * Display rephrased text
 */
function displayRephrasedText(text) {
    rephrasedText.textContent = text;
    rephrasedSection.classList.remove('hidden');
}

/**
 * Copy rephrased text to clipboard
 */
async function copyToClipboard() {
    const text = rephrasedText.textContent;
    
    try {
        await navigator.clipboard.writeText(text);
        copyRephrasedBtn.textContent = '✓ Copied!';
        setTimeout(() => {
            copyRephrasedBtn.textContent = '📋 Copy to Clipboard';
        }, 2000);
    } catch (error) {
        // Fallback for older browsers
        const textarea = document.createElement('textarea');
        textarea.value = text;
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand('copy');
        document.body.removeChild(textarea);
        copyRephrasedBtn.textContent = '✓ Copied!';
        setTimeout(() => {
            copyRephrasedBtn.textContent = '📋 Copy to Clipboard';
        }, 2000);
    }
}

/**
 * Show loading state
 */
function showLoading() {
    loadingSection.classList.remove('hidden');
    checkBtn.disabled = true;
    rephraseBtn.disabled = true;
}

/**
 * Hide loading state
 */
function hideLoading() {
    loadingSection.classList.add('hidden');
    checkBtn.disabled = false;
}

/**
 * Show error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorSection.classList.remove('hidden');
}

/**
 * Hide error message
 */
function hideError() {
    errorSection.classList.add('hidden');
}

/**
 * Hide results section
 */
function hideResults() {
    resultsSection.classList.add('hidden');
    rephrasedSection.classList.add('hidden');
}

/**
 * Escape HTML to prevent XSS
 */
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}
