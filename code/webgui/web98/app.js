document.addEventListener('DOMContentLoaded', function () {
    // Loop through all elements and find those with the 'draggable' class
    const draggableElements = document.querySelectorAll('.draggable');
    draggableElements.forEach(el => draggableElement(el));

    // Loop through all elements and ensure all windows are bringable to the front
    const windows = document.querySelectorAll('.window');
    windows.forEach(el => bringableToFront(el));

    // Loop through all elements and find those with the 'resizeable' class
    const resizeableElements = document.querySelectorAll('.resizeable');
    resizeableElements.forEach(el => resizeableElement(el));

//    dragElement(document.getElementById('main-window'));
//    resizeElement(document.getElementById('main-window'));

    // Initialize SSE connection with a small delay for Firefox compatibility
    setTimeout(() => {
        initializeSSE();
    }, 100);

});

function initializeSSE() {
    // Check if EventSource is supported
    if (typeof(EventSource) === "undefined") {
        console.error("SSE not supported by this browser");
        return;
    }
    
    const eventSource = new EventSource('/events');
    
    eventSource.onmessage = function(event) {
        try {
            console.log('On tick: Received SSE data ' + event.data.length + ' bytes');
            const simulationData = JSON.parse(event.data);
            updateSimulationDisplay(simulationData);
        } catch (error) {
            console.error('Error parsing SSE data:', error);
        }
    };
    
    eventSource.onerror = function(event) {
        console.error('SSE connection error:', event);
        console.log('SSE readyState:', eventSource.readyState);
        
        // Firefox specific: Check readyState and attempt reconnection if needed
        if (eventSource.readyState === EventSource.CLOSED) {
            console.log('SSE connection closed, attempting to reconnect in 5 seconds...');
            setTimeout(() => {
                initializeSSE();
            }, 5000);
        }
    };
    
    eventSource.onopen = function(event) {
        console.log('SSE connection opened');
    };
    
    // Store reference globally for debugging
    window.sseConnection = eventSource;
}

function updateSimulationDisplay(simulationData) {
    // Update tick count
    const tickCountElement = document.getElementById('simulation-tick-count');
    if (tickCountElement && simulationData.tick_count !== undefined) {
        tickCountElement.textContent = simulationData.tick_count;
    }
    
    // Update entities display if needed
    if (simulationData.world && simulationData.world.entities) {
        const html = jsonToHtml(simulationData.world, 'Entities', 'entities');
        const windowBodyEntities = document.getElementById('window-body-entities');
        if (windowBodyEntities) {
            windowBodyEntities.innerHTML = html;
        }
    }
}


function jsonToHtml(json, title, id_path, depth = 0) {
// Take JSON data and convert it to HTML in the following format:

/* Output style:
<ul class="tree-view">
  <li>Table of Contents</li>
  <li>What is web development?</li>
  <li>
    CSS
    <ul>
      <li>Selectors</li>
      <li>Specificity</li>
      <li>Properties</li>
    </ul>
  </li>
  <li>
    <details open>
      <summary>JavaScript</summary>
      <ul>
        <li>Avoid at all costs</li>
        <li>
          <details>
            <summary>Unless</summary>
            <ul>
              <li>Avoid</li>
              <li>
                <details>
                  <summary>At</summary>
                  <ul>
                    <li>Avoid</li>
                    <li>At</li>
                    <li>All</li>
                    <li>Cost</li>
                  </ul>
                </details>
              </li>
              <li>All</li>
              <li>Cost</li>
            </ul>
          </details>
        </li>
      </ul>
    </details>
  </li>
  <li>HTML</li>
  <li>Special Thanks</li>
</ul>
*/

    // If a value is an object or an array, it should be displayed as a nested list
    // If a nested list has more than two items, it should be displayed as a details element with a summary
    // If a value is a string or number, it should be displayed as a list item with the key and value
    // If a value is a boolean, it should be displayed as a list item with the key and value
    let added_details = false;
    let html = '';
    if (json && (typeof json === 'object' || Array.isArray(json))) {
        added_details = true;
        html += '<details><summary>' + title + '</summary>';
    }
    html += depth === 0 ? '<ul class="tree-view">' : '<ul>';
    for (const key in json) {
        if (json.hasOwnProperty(key)) {
            if (typeof json[key] === 'object' || Array.isArray(json[key])) {
                html += `<li id="${id_path + '.' + key}">${jsonToHtml(json[key], key, id_path + '.' + key, depth + 1)}</li>`;
            } else {
                html += `<li id="${id_path + '.' + key}">${key}: ${json[key]}</li>`;
            }
        }
    }
    html += '</ul>';
    if (added_details) {
        html += '</details>';
    }
    return html;
}
