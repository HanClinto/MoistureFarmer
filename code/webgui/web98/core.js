// core.js - Core utilities, global state, and helper functions

// Global simulation state
window.simulationData = {};
window.simulationDataDictionary = {};

// Debug logger to prevent noisy console overhead in hot paths
if (typeof window.DEBUG_LOG === 'undefined') {
    window.DEBUG_LOG = false;
}

if (typeof window.DEBUG_LOG_TWEEN === 'undefined') {
    window.DEBUG_LOG_TWEEN = false;
}

/**
 * Debug logger function that respects global DEBUG_LOG setting
 */
function debugLog() {
    if (window.DEBUG_LOG) {
        try { 
            console.log.apply(console, arguments); 
        } catch (e) {}
    }
}

/**
 * Initialize button handlers for window controls
 */
function initializeButtonHandlers() {
    // Handle close buttons for windows with closeable functionality
    const closeButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Close"]');
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const window = button.closest('.window');
            if (window) {
                // Hide any window when its close button is clicked
                window.classList.add('hidden');
            }
        });
    });
}

/**
 * Show a window by removing the hidden class
 */
function showWindow(windowId) {
    const window = document.getElementById(windowId);
    if (window) {
        window.classList.remove('hidden');
    }
}

/**
 * Bring a window to the front by adjusting z-index
 */
function bringToFront(windowElement) {
    // Simple z-index management - could be enhanced for more sophisticated stacking
    const allWindows = document.querySelectorAll('.window');
    let maxZ = 0;
    allWindows.forEach(win => {
        const z = parseInt(getComputedStyle(win).zIndex) || 0;
        if (z > maxZ) maxZ = z;
    });
    windowElement.style.zIndex = maxZ + 1;
}

// Export functions to global scope for compatibility with existing code
window.debugLog = debugLog;
window.initializeButtonHandlers = initializeButtonHandlers;
window.showWindow = showWindow;
window.bringToFront = bringToFront;
