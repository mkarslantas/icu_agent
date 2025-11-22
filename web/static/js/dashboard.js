/**
 * ICU Agent Dashboard - Common JavaScript Functions
 */

// Configuration
const CONFIG = {
    refreshInterval: 30000, // 30 seconds
    apiBaseUrl: '/api',
};

// Global state
const state = {
    autoRefresh: true,
    refreshTimer: null,
};

/**
 * Fetch JSON from API endpoint
 * @param {string} endpoint - API endpoint path
 * @returns {Promise<Object>} - Parsed JSON response
 */
async function fetchAPI(endpoint) {
    try {
        const response = await fetch(`${CONFIG.apiBaseUrl}${endpoint}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error(`API fetch error for ${endpoint}:`, error);
        throw error;
    }
}

/**
 * Format date string for display
 * @param {string} dateStr - Date string (YYYY-MM-DD)
 * @returns {string} - Formatted date
 */
function formatDate(dateStr) {
    if (!dateStr) return '--';

    try {
        const date = new Date(dateStr);
        return date.toLocaleDateString('tr-TR', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    } catch (error) {
        return dateStr;
    }
}

/**
 * Format timestamp for display
 * @param {string} timestamp - ISO timestamp
 * @returns {string} - Formatted timestamp
 */
function formatTimestamp(timestamp) {
    if (!timestamp) return '--';

    try {
        const date = new Date(timestamp);
        return date.toLocaleString('tr-TR', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (error) {
        return timestamp;
    }
}

/**
 * Get urgency badge HTML
 * @param {string} urgency - Urgency level (immediate, urgent, monitor)
 * @returns {string} - Badge HTML
 */
function getUrgencyBadge(urgency) {
    const badges = {
        immediate: '<span class="badge bg-danger">ACİL</span>',
        urgent: '<span class="badge bg-warning">ÖNEMLİ</span>',
        monitor: '<span class="badge bg-info">TAKİP</span>',
    };

    return badges[urgency] || `<span class="badge bg-secondary">${urgency}</span>`;
}

/**
 * Get SOFA score badge HTML
 * @param {number} score - SOFA score (0-24)
 * @returns {string} - Badge HTML
 */
function getSofaBadge(score) {
    if (score < 0) return '--';

    let badgeClass = 'bg-success';
    if (score >= 15) badgeClass = 'bg-danger';
    else if (score >= 10) badgeClass = 'bg-warning';
    else if (score >= 5) badgeClass = 'bg-info';

    return `<span class="badge ${badgeClass}">${score}/24</span>`;
}

/**
 * Get patient status badge
 * @param {Object} patient - Patient object
 * @returns {string} - Status badge HTML
 */
function getStatusBadge(patient) {
    if (patient.status !== 'active') {
        return '<span class="badge bg-secondary">No Data</span>';
    }

    if (patient.immediate_alerts > 0) {
        return '<span class="badge bg-danger"><i class="bi bi-exclamation-triangle-fill"></i> Critical</span>';
    } else if (patient.critical_count > 0) {
        return '<span class="badge bg-warning">Warning</span>';
    } else {
        return '<span class="badge bg-success">Stable</span>';
    }
}

/**
 * Show loading spinner in element
 * @param {HTMLElement} element - Target element
 */
function showLoading(element) {
    element.innerHTML = `
        <div class="text-center p-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading...</span>
            </div>
        </div>
    `;
}

/**
 * Show error message in element
 * @param {HTMLElement} element - Target element
 * @param {string} message - Error message
 */
function showError(element, message = 'Error loading data') {
    element.innerHTML = `
        <div class="alert alert-danger text-center" role="alert">
            <i class="bi bi-exclamation-triangle-fill"></i> ${message}
        </div>
    `;
}

/**
 * Show empty state in element
 * @param {HTMLElement} element - Target element
 * @param {string} message - Empty state message
 */
function showEmpty(element, message = 'No data available') {
    element.innerHTML = `
        <p class="text-center text-muted p-4">${message}</p>
    `;
}

/**
 * Debounce function
 * @param {Function} func - Function to debounce
 * @param {number} wait - Wait time in milliseconds
 * @returns {Function} - Debounced function
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Copy text to clipboard
 * @param {string} text - Text to copy
 * @returns {Promise<void>}
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showToast('Copied to clipboard', 'success');
    } catch (error) {
        console.error('Failed to copy:', error);
        showToast('Failed to copy', 'danger');
    }
}

/**
 * Show toast notification
 * @param {string} message - Toast message
 * @param {string} type - Toast type (success, danger, warning, info)
 */
function showToast(message, type = 'info') {
    // Simple toast implementation
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed bottom-0 end-0 m-3`;
    toast.style.zIndex = '9999';
    toast.textContent = message;

    document.body.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

/**
 * Initialize auto-refresh
 * @param {Function} refreshCallback - Function to call on refresh
 * @param {number} interval - Refresh interval in milliseconds
 */
function initAutoRefresh(refreshCallback, interval = CONFIG.refreshInterval) {
    if (state.refreshTimer) {
        clearInterval(state.refreshTimer);
    }

    state.refreshTimer = setInterval(() => {
        if (state.autoRefresh) {
            refreshCallback();
        }
    }, interval);
}

/**
 * Stop auto-refresh
 */
function stopAutoRefresh() {
    if (state.refreshTimer) {
        clearInterval(state.refreshTimer);
        state.refreshTimer = null;
    }
}

/**
 * Toggle auto-refresh
 */
function toggleAutoRefresh() {
    state.autoRefresh = !state.autoRefresh;
    return state.autoRefresh;
}

/**
 * Format number with thousands separator
 * @param {number} num - Number to format
 * @returns {string} - Formatted number
 */
function formatNumber(num) {
    if (num === null || num === undefined) return '--';
    return num.toLocaleString('tr-TR');
}

/**
 * Sanitize HTML to prevent XSS
 * @param {string} html - HTML string
 * @returns {string} - Sanitized HTML
 */
function sanitizeHTML(html) {
    const div = document.createElement('div');
    div.textContent = html;
    return div.innerHTML;
}

/**
 * Update all timestamps on the page
 */
function updateTimestamps() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('tr-TR');
    const dateStr = now.toLocaleDateString('tr-TR');

    document.querySelectorAll('.timestamp').forEach(el => {
        el.textContent = timeStr;
    });

    document.querySelectorAll('.datestamp').forEach(el => {
        el.textContent = dateStr;
    });
}

/**
 * Initialize common dashboard features
 */
function initDashboard() {
    // Update timestamps every second
    setInterval(updateTimestamps, 1000);
    updateTimestamps();

    // Handle refresh button if present
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
        refreshBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const icon = refreshBtn.querySelector('i');
            if (icon) {
                icon.classList.add('rotate');
                setTimeout(() => icon.classList.remove('rotate'), 1000);
            }
        });
    }

    // Handle visibility change (pause refresh when tab is hidden)
    document.addEventListener('visibilitychange', () => {
        if (document.hidden) {
            state.autoRefresh = false;
        } else {
            state.autoRefresh = true;
        }
    });

    // Cleanup on unload
    window.addEventListener('beforeunload', () => {
        stopAutoRefresh();
    });
}

// Initialize on DOM ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initDashboard);
} else {
    initDashboard();
}

// Export functions for use in templates
window.Dashboard = {
    fetchAPI,
    formatDate,
    formatTimestamp,
    getUrgencyBadge,
    getSofaBadge,
    getStatusBadge,
    showLoading,
    showError,
    showEmpty,
    debounce,
    copyToClipboard,
    showToast,
    initAutoRefresh,
    stopAutoRefresh,
    toggleAutoRefresh,
    formatNumber,
    sanitizeHTML,
    updateTimestamps,
};
