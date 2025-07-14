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
        const windowBodyEntities = document.getElementById('window-body-entities');
        if (windowBodyEntities) {
            updateJsonHtmlIncrementally(windowBodyEntities, simulationData, 'Entities', 'entities');
        }
    }
}


function updateJsonHtmlIncrementally(containerElement, json, title, id_path, depth = 0) {
    // Get or create the root container
    let rootContainer = containerElement;

    // If this is the first call (depth 0), ensure we have the proper structure
    if (depth === 0) {
        let treeView = containerElement.querySelector('ul.tree-view');
        if (!treeView) {
            // Create initial structure if it doesn't exist
            containerElement.innerHTML = jsonToHtml(json, title, id_path, depth);
            return;
        }
        rootContainer = treeView;
    }

    // Get existing child elements mapped by their data-key attribute
    const existingElements = new Map();
    const existingItems = rootContainer.querySelectorAll(':scope > li[data-key]');
    existingItems.forEach(item => {
        const key = item.getAttribute('data-key');
        if (key) {
            existingElements.set(key, item);
        }
    });

    // Track which keys we've processed
    const processedKeys = new Set();

    // Process each key in the JSON
    for (const key in json) {
        if (!json.hasOwnProperty(key)) continue;

        processedKeys.add(key);
        const value = json[key];
        const elementId = `${id_path}.${key}`;

        if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
            // Handle object values
            let listItem = existingElements.get(key);

            if (!listItem) {
                // Create new list item for object
                listItem = document.createElement('li');
                listItem.setAttribute('data-key', key);
                listItem.id = elementId;

                const details = document.createElement('details');
                const summary = document.createElement('summary');
                summary.textContent = key;
                details.appendChild(summary);

                const nestedList = document.createElement('ul');
                details.appendChild(nestedList);
                listItem.appendChild(details);

                rootContainer.appendChild(listItem);
            }

            // Recursively update the nested object
            const nestedList = listItem.querySelector('details > ul');
            if (nestedList) {
                updateJsonHtmlIncrementally(nestedList, value, key, elementId, depth + 1);
            }
        } else {
            // Handle primitive values (string, number, boolean)
            let listItem = existingElements.get(key);
            const displayValue = `${key}: ${value}`;

            if (!listItem) {
                // Create new list item for primitive value
                listItem = document.createElement('li');
                listItem.setAttribute('data-key', key);
                listItem.id = elementId;
                listItem.textContent = displayValue;
                rootContainer.appendChild(listItem);
            } else {
                // Update existing item's content if it has changed
                if (listItem.textContent !== displayValue) {
                    listItem.textContent = displayValue;
                }
            }
        }
    }

    // Remove elements that are no longer present in the JSON
    existingElements.forEach((element, key) => {
        if (!processedKeys.has(key)) {
            element.remove();
        }
    });
}

// Keep the original function for initial rendering when needed
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
                //html += `<li id="${id_path + '.' + key}">${jsonToHtml(json[key], key, id_path + '.' + key, depth + 1)}</li>`;
                //html += `<li id="${id_path + '.' + key}" data-key="${id_path + '.' + key}">${jsonToHtml(json[key], key, id_path + '.' + key, depth + 1)}</li>`;
                html += `<li id="${id_path + '.' + key}" data-key="${key}">${jsonToHtml(json[key], key, id_path + '.' + key, depth + 1)}</li>`;
            } else {
                //html += `<li id="${id_path + '.' + key}">${key}: ${json[key]}</li>`;
                html += `<li id="${id_path + '.' + key}" data-key="${key}">${key}: ${json[key]}</li>`;
            }
        }
    }
    html += '</ul>';
    if (added_details) {
        html += '</details>';
    }
    return html;
}

