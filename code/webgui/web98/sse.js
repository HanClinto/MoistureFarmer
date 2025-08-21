// sse.js - Server-Sent Events communication module

/**
 * Initialize Server-Sent Events connection for real-time simulation updates
 */
function initializeSSE() {
    // Check if EventSource is supported
    if (typeof(EventSource) === "undefined") {
        console.error("SSE not supported by this browser");
        return;
    }
    
    const eventSource = new EventSource('/events');
    
    eventSource.onmessage = function(event) {
        try {
            debugLog('On tick: Received SSE data ' + event.data.length + ' bytes');
            window.simulationData = JSON.parse(event.data);
            if (typeof updateSimulationDisplay === 'function') {
                updateSimulationDisplay();
            }
        } catch (error) {
            console.error('Error parsing SSE data:', error);
        }
    };
    
    eventSource.onerror = function(event) {
        console.error('SSE connection error:', event);
        debugLog('SSE readyState:', eventSource.readyState);
        
        // Firefox specific: Check readyState and attempt reconnection if needed
        if (eventSource.readyState === EventSource.CLOSED) {
            console.log('SSE connection closed, attempting to reconnect in 5 seconds...');
            setTimeout(() => {
                initializeSSE();
            }, 5000);
        }
    };
    
    eventSource.onopen = function(event) {
        debugLog('SSE connection opened');
    };
    
    // Store reference globally for debugging
    window.sseConnection = eventSource;
}

/**
 * Initialize SSE with a small delay for Firefox compatibility
 */
function startSSE() {
    setTimeout(() => {
        initializeSSE();
    }, 100);
}

// Export functions to global scope
window.initializeSSE = initializeSSE;
window.startSSE = startSSE;
