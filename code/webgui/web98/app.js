// app.js - Main application initialization and coordination
// This file coordinates all the modular components and handles initial setup

/**
 * Enhanced updateSimulationDisplay that coordinates all modules
 */
function updateSimulationDisplay() {
    // Call the core simulation display update from simulation-display.js
    if (typeof updateSimulationDisplayCore === 'function') {
        updateSimulationDisplayCore();
    }

    // Initialize world view components if needed
    if (typeof initializeWorldView === 'function') {
        initializeWorldView();
    }
}

/**
 * Main application initialization
 */
document.addEventListener('DOMContentLoaded', function () {
    // Loop through all elements and find those with the 'draggable' class
    const draggableElements = document.querySelectorAll('.draggable');
    draggableElements.forEach(el => {
        if (typeof draggableElement === 'function') {
            draggableElement(el);
        }
    });

    // Loop through all elements and ensure all windows are bringable to the front
    const windows = document.querySelectorAll('.window');
    windows.forEach(el => {
        if (typeof bringableToFront === 'function') {
            bringableToFront(el);
        }
    });

    // Loop through all elements and find those with the 'resizeable' class
    const resizeableElements = document.querySelectorAll('.resizeable');
    resizeableElements.forEach(el => {
        if (typeof resizeableElement === 'function') {
            resizeableElement(el);
        }
    });

    // Add button click handlers
    if (typeof initializeButtonHandlers === 'function') {
        initializeButtonHandlers();
    }

    // Initialize SSE connection with a small delay for Firefox compatibility
    if (typeof startSSE === 'function') {
        startSSE();
    }

    // Fetch the initial simulation state and populate the display to reduce GUI loading lag
    fetch('/simulation')
        .then(response => response.json())
        .then(data => {
            if (typeof debugLog === 'function') {
                debugLog('Initial simulation state:', data);
            }
            window.simulationData = data;
            updateSimulationDisplay();
        })
        .catch(error => {
            console.error('Error fetching initial simulation state:', error);
        });
});

// Set up the enhanced updateSimulationDisplay function in the global scope
// This ensures compatibility with SSE and other modules that call it
window.updateSimulationDisplay = updateSimulationDisplay;