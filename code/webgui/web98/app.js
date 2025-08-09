simulationData = {};
simulationDataDictionary = {};

// Debug logger to prevent noisy console overhead in hot paths
if (typeof window.DEBUG_LOG === 'undefined') {
    window.DEBUG_LOG = false;
}
function debugLog() {
    if (window.DEBUG_LOG) {
        try { console.log.apply(console, arguments); } catch (e) {}
    }
}

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

    // Add button click handlers
    initializeButtonHandlers();

    // Initialize SSE connection with a small delay for Firefox compatibility
    setTimeout(() => {
        initializeSSE();
    }, 100);

    // Fetch the initial simulation state and populate the display to reduce GUI loading lag
    fetch('/simulation')
        .then(response => response.json())
        .then(data => {
            debugLog('Initial simulation state:', data);
            simulationData = data;
            updateSimulationDisplay(data);
        })
        .catch(error => {
            console.error('Error fetching initial simulation state:', error);
        });
});

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
            simulationData = JSON.parse(event.data);
            updateSimulationDisplay();
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

function updateSimulationDisplay() {
    // For each entity in the simulation data, populate the simulationDataDictionary
    if (simulationData.world && simulationData.world.entities) {
        Object.keys(simulationData.world.entities).forEach(entityId => {
            const entity = simulationData.world.entities[entityId];
            simulationDataDictionary[entityId] = entity;

            // For each entity's slots, populate the simulationDataDictionary
            if (entity.slots) {
                Object.keys(entity.slots).forEach(slotName => {
                    const slot = entity.slots[slotName];
                    if (slot.component) {
                        // If the slot has a component, add it to the dictionary
                        simulationDataDictionary[`${entityId}.${slotName}`] = slot;
                        simulationDataDictionary[slot.component.id] = slot.component;
                    }
                });
            }
        });
    }

    // Update tick count
    const tickCountElement = document.getElementById('simulation-tick-count');
    if (tickCountElement && simulationData.tick_count !== undefined) {
        tickCountElement.textContent = simulationData.tick_count;
    }

    // Update entities display if needed
    if (simulationData.world && simulationData.world.entities) {
        const windowBodyEntities = document.getElementById('simulation-detail-window-body-entities');
        if (windowBodyEntities) {
            updateJsonTreeviewHtmlIncrementally(windowBodyEntities, simulationData, 'Entities', 'entities');
        }
    }

    const simulationStatusPausedElement = document.getElementById('simulation-status-paused');
    if (simulationStatusPausedElement) {
        simulationStatusPausedElement.textContent = simulationData.paused ? 'Paused' : 'Running';
    }
    
    // Update button text based on the new state
    const pauseButton = document.getElementById('simulation-pause');
    if (pauseButton) {
        if (simulationData.paused) {
            pauseButton.textContent = 'Resume';
        } else {
            pauseButton.textContent = 'Pause';
        }
    }

    // Update the simulation delay buttons
    const buttons = document.querySelectorAll('.simulation-delay-button');
    buttons.forEach(button => {
        if (button.id === `simulation-delay-${simulationData.simulation_delay}`) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Add / update icons on the desktop for each entity in the World
    // Each entity should use /resources/sprites/{entity.model}.png as its icon
    // Then position the icon based on the entity's location, with 0,0 as the center of the desktop, and each unit of location counting for 32 pixels.
    // Each icon should use the class 'entity-icon' and have a data-entity-id attribute set to the entity's ID
    // Each icon should have a caption that is the entity.name or entity.id if name is not set

    const entitiesContainer = document.getElementById('world-entities');
    if (entitiesContainer) {
        // Clear existing icons
        const existingIcons = entitiesContainer.querySelectorAll('.entity-icon');
        existingIcons.forEach(icon => icon.remove());

    debugLog('Entities snapshot', simulationData.world && simulationData.world.entities);

        // simulationData.world.entities is a dictionary of entities where the key is the entity ID

        // Add new icons for each entity, with a caption centered underneath like an icon's name in Windows 98
        Object.values(simulationData.world.entities).forEach(entity => {
            // If there is a window attached to this entity, update it
            updateEntityDetailWindow(entity.id);

            // Create a group entity to hold both the icon and caption
            const group = document.createElement('div');
            group.className = 'entity-icon';
            group.style.position = 'absolute';
            group.style.left = `${entity.location.x * 32}px`;
            group.style.top = `${entity.location.y * 32}px`;
            group.setAttribute('data-entity-id', entity.id);

            // Create the icon image element
            const icon = document.createElement('img');
            icon.src = `/resources/sprites/${entity.model}.png`; // Use the model name for the sprite
            icon.className = 'entity-icon-sprite';
            group.appendChild(icon);

            // Create the caption element
            const caption = document.createElement('div');
            caption.className = 'entity-icon-caption';
            caption.textContent = entity.name || entity.id; // Use name if available, otherwise use ID
            group.appendChild(caption);

            // When mouse-down on the anything in the group, open the entity detail window
            // TODO: Why doesn't this work?
            icon.addEventListener("click", function() {
                debugLog(`Opening entity detail for ${entity.id}`);
                showEntityDetailWindow(entity.id);
                window.selectedEntityId = entity.id; // Update selection
            });

            entitiesContainer.appendChild(group);
            debugLog(`Added icon for entity ${entity.id} at (${entity.location.x}, ${entity.location.y})`);

            // TODO: Add drop-down menu items for entities
        });
    }
}

function updateJsonTreeviewHtmlIncrementally(containerElement, json, title, id_path, depth = 0) {
    // Get or create the root container
    let rootContainer = containerElement;

    // If this is the first call (depth 0), ensure we have the proper structure
    if (depth === 0) {
        let treeView = containerElement.querySelector('ul.tree-view');
        if (!treeView) {
            // Create initial structure if it doesn't exist
            containerElement.innerHTML = jsonToTreeviewHtml(json, title, id_path, depth);
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

        // TODO: Arrays don't seem to be handled correctly here -- need to fix this better
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
                updateJsonTreeviewHtmlIncrementally(nestedList, value, key, elementId, depth + 1);
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
function jsonToTreeviewHtml(json, title, id_path, depth = 0) {
    // Take JSON data and convert it to HTML in the following format:
    //  https://jdan.github.io/98.css/#tree-view

    // If a value is an object or an array, it should be displayed as a nested list
    // If a nested list has more than two items, it should be displayed as a details element with a summary
    // If a value is a string or number, it should be displayed as a list item with the key and value
    // If a value is a boolean, it should be displayed as a list item with the key and value
    let added_details = false;
    let html = '';
    if (json && depth > 0 && (typeof json === 'object' || Array.isArray(json))) {
        added_details = true;
        // Count the number of keys in the object, if more than 2, default to open
        const keysCount = Object.keys(json).length;
        const isOpen = keysCount > 2; // Default to open if more than 2 keys
        const detailsOpen = isOpen ? ' open' : '';
        // Create a details element with a summary
        html += '<details' + detailsOpen + '><summary>' + title + '</summary>';
    }
    html += depth === 0 ? '<ul class="tree-view">' : '<ul>';
    for (const key in json) {
        if (json.hasOwnProperty(key)) {
            if (typeof json[key] === 'object' || Array.isArray(json[key])) {
                html += `<li id="${id_path + '.' + key}" data-key="${key}">${jsonToTreeviewHtml(json[key], key, id_path + '.' + key, depth + 1)}</li>`;
            } else {
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

function showEntityDetailWindow(entityId) {
    // Create or focus the entity detail window for the given entity ID
    let window = document.getElementById(`entity-detail-window-${entityId}`);
    if (!window) {
        // Create a new window if it doesn't exist
        window = document.createElement('div');
        window.id = `entity-detail-window-${entityId}`;
        window.className = 'window entity-detail-window draggable resizeable';
        window.innerHTML = `
            <div class="title-bar">
                <div class="title-bar-text">Entity Detail - ${entityId}</div>
                <div class="title-bar-controls">
                    <button aria-label="Close"></button>
                </div>
            </div>
            <div class="window-body">
                <div id="entity-detail-window-body-${entityId}" class="entity-detail-body">
                    <p>Loading entity details...</p>
                </div>
            </div>
        `;
        document.body.appendChild(window);
        // Add close button functionality

        const closeButton = window.querySelector('.title-bar-controls button[aria-label="Close"]');
        closeButton.addEventListener('click', function() {
            const window = closeButton.closest('.window');
            if (window) {
                // Hide any window when its close button is clicked
                window.classList.add('hidden');
            }
        });

        resizeableElement(window);
        draggableElement(window);
        bringableToFront(window);
    }

    updateEntityDetailWindow(entityId);

    // Show the window and bring it to the front
    showWindow(window.id);
    bringToFront(window);
}

function updateEntityDetailWindow(entityId) {
    // Update the entity detail window for the given entity ID
    let window = document.getElementById(`entity-detail-window-${entityId}`);
    if (!window) {
        return; // If the window doesn't exist, do nothing
    }

    // Populate the entity details
    const entity = simulationDataDictionary[entityId];
    const detailBody = document.getElementById(`entity-detail-window-body-${entityId}`);
    detailBody.innerHTML = ''; // Clear existing content
    detailBody.style.width = '100%'; // Ensure it takes full width

    // Add the Name, ID, and Model of the entity
    const entityInfo = document.createElement('fieldset');
    entityInfo.className = 'entity-info';
    entityInfo.style.width = 'calc(100% - 24px)';
    entityInfo.innerHTML = `
        <strong>Name:</strong> ${entity.name || 'Unknown'}<br>
        <strong>ID:</strong> ${entity.id}<br>
        <strong>Model:</strong> ${entity.model || 'Unknown'}<br>
    `;
    detailBody.appendChild(entityInfo);

    // Loop through the component slots and create specialized views if needed.
    if (entity.slots) {
        Object.keys(entity.slots).forEach(slotName => {
            const slot = entity.slots[slotName];
            // Create a specialized view for each slot based on what it can accept
            switch (slot.accepts) {
                case 'PowerPack':
                    // Add a progress bar to display the power pack charge and capacity
                    // <div class="progress-indicator segmented">
                    //     <span class="progress-indicator-bar" style="width: 40%;" />
                    // </div>
                    progressGroup = document.createElement('fieldset');
                    progressGroup.style.width = 'calc(100% - 24px)';
                    progressGroupLabel = document.createElement('legend');
                    progressGroupLabel.textContent = `Power Pack - ${slotName}`;
                    progressGroup.appendChild(progressGroupLabel);

                    progressDiv = document.createElement('div');
                    progressDiv.className = 'progress-indicator segmented';
                    progressDiv.style.width = '100%'; // Ensure it takes full width
                    const progressBar = document.createElement('span');
                    progressBar.className = 'progress-indicator-bar';
                    progressBar['data-key'] = `${entityId}.${slotName}`;
                    if (slot.component) {
                        progressBar['data-charge'] = slot.component.charge;
                        progressBar['data-charge_max'] = slot.component.charge_max;
                        progressBar['data-capacity'] = slot.component.capacity;
                        progressBar['data-capacity_max'] = slot.component.capacity_max;
                        // progressBar.textContent = `${slotName}: ${slot.component.charge}/${slot.component.charge_max}`;
                        // Add a tooltip with the charge and capacity
                        progressBar.title = `Charge: ${slot.component.charge}, Capacity: ${slot.component.charge_max}`;
                        // Remove the disabled class if it exists
                        progressBar.classList.remove('disabled');
                        // Set the width based on the charge percentage
                        const chargePercentage = (slot.component.charge / slot.component.charge_max) * 100;
                        progressBar.style.width = `${chargePercentage}%`;
                    } else {
                        // Otherwise, set it to 0% width and grey it out as disabled
                        progressBar.style.width = '0%';
                        progressBar.classList.add('disabled');
                        // progressBar.textContent = `${slotName}: 0/0`;
                        // Add a tooltip indicating no component is present
                        progressBar.title = 'No component present';
                    }
                    progressDiv.title = progressBar.title;
                    progressGroup.title = progressBar.title;
                    progressDiv.appendChild(progressBar);
                    progressGroup.appendChild(progressDiv);
                    detailBody.appendChild(progressGroup);
                    break;
                case 'WaterTank':
                    // Add a progress bar to display the water tank level and capacity
                    progressGroup = document.createElement('fieldset');
                    progressGroup.style.width = 'calc(100% - 24px)';
                    progressGroupLabel = document.createElement('legend');
                    progressGroupLabel.textContent = `Water Tank - ${slotName}`;
                    progressGroup.appendChild(progressGroupLabel);

                    progressDiv = document.createElement('div');
                    progressDiv.className = 'progress-indicator segmented';
                    progressDiv.style.width = '100%'; // Ensure it takes full width
                    const waterBar = document.createElement('span');
                    waterBar.className = 'progress-indicator-bar';
                    waterBar['data-key'] = `${entityId}.${slotName}`;
                    if (slot.component) {
                        waterBar['data-fill'] = slot.component.fill;
                        waterBar['data-capacity'] = slot.component.capacity;
                        // waterBar.textContent = `${slotName}: ${slot.component.fill}/${slot.component.capacity}`;
                        // Add a tooltip with the fill and capacity
                        waterBar.title = `Fill: ${slot.component.fill}, Capacity: ${slot.component.capacity}`;
                        // Remove the disabled class if it exists
                        waterBar.classList.remove('disabled');
                        // Set the width based on the fill percentage
                        const fillPercentage = (slot.component.fill / slot.component.capacity) * 100;
                        waterBar.style.width = `${fillPercentage}%`;
                    } else {
                        // Otherwise, set it to 0% width and grey it out as disabled
                        waterBar.style.width = '0%';
                        waterBar.classList.add('disabled');
                        // waterBar.textContent = `${slotName}: 0/0`;
                        // Add a tooltip indicating no component is present
                        waterBar.title = 'No component present';
                    }
                    progressDiv.title = waterBar.title;
                    progressGroup.title = waterBar.title;
                    progressDiv.appendChild(waterBar);
                    progressGroup.appendChild(progressDiv);
                    detailBody.appendChild(progressGroup);

                    break;
            }
        });
    }
}

function doFullscreen(enable) {
    // Request or exit fullscreen mode
    const doc = document.documentElement;
    if (enable) {
        if (doc.requestFullscreen) {
            doc.requestFullscreen();
        } else if (doc.mozRequestFullScreen) { // Firefox
            doc.mozRequestFullScreen();
        } else if (doc.webkitRequestFullscreen) { // Chrome, Safari and Opera
            doc.webkitRequestFullscreen();
        } else if (doc.msRequestFullscreen) { // IE/Edge
            doc.msRequestFullscreen();
        }
        // Find all Maximize buttons and hide them
        const maximizeButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Maximize"]');
        maximizeButtons.forEach(button => {
            button.classList.add('hidden');
        });
        // Show Restore button
        const restoreButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Restore"]');
        restoreButtons.forEach(button => {
            button.classList.remove('hidden');
        });
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        } else if (document.mozCancelFullScreen) { // Firefox
            document.mozCancelFullScreen();
        } else if (document.webkitExitFullscreen) { // Chrome, Safari and Opera
            document.webkitExitFullscreen();
        } else if (document.msExitFullscreen) { // IE/Edge
            document.msExitFullscreen();
        }

        // Find all Maximize buttons and show them
        const maximizeButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Maximize"]');
        maximizeButtons.forEach(button => {
            button.classList.remove('hidden');
        });
        // Hide Restore buttons
        const restoreButtons = document.querySelectorAll('.title-bar-controls button[aria-label="Restore"]');
        restoreButtons.forEach(button => {
            button.classList.add('hidden');
        });

    }
}

function navigateTo(url) {
    // Navigate to the specified URL
    console.log('Navigating to:', url);
    window.location.href = url;
}

function setSimulationDelay(simulation_delay) {
    // Set the simulation delay
    console.log('Setting simulation delay to:', simulation_delay);
    fetch(`/simulation/simulation_delay/${simulation_delay}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Simulation delay set:', data);
    })
    .catch(error => {
        console.error('Error setting simulation delay:', error);
    });

    simulationData.simulation_delay = simulation_delay; // Update the local state

    // Update view based on new data
    updateSimulationDisplay();
}

function toggleSimulationPaused() {
    // Toggle the simulation pause state
    console.log('Toggling simulation pause');
    fetch(`/simulation/paused/${simulationData.paused ? false : true}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
    })
    .then(response => response.json())
    .then(data => {
        console.log('Simulation paused:', data);
    })
    .catch(error => {
        console.error('Error setting simulation pause:', error);
    });

    simulationData.paused = !simulationData.paused; // Toggle the local state

    updateSimulationDisplay(); // Update the display to reflect the new state
}
// --- Scenario Management ---
function createNewScenario() {
    // Create a new scenario on the server by resetting the simulation
    fetch('/simulation', { method: 'GET' })
        .then(response => response.json())
        .then(data => {
            // Optionally, POST to /scenario/load with a blank scenario structure
            const blankScenario = {
                name: "New Scenario",
                description: "A new scenario.",
                simulation_settings: {},
                entities: []
            };
            fetch('/scenario/load', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(blankScenario)
            })
            .then(resp => resp.json())
            .then(result => {
                if (result.status === 'success') {
                    alert('New scenario created.');
                } else {
                    alert('Error creating scenario: ' + (result.error || 'Unknown error'));
                }
            });
        });
}

function openScenarioFile() {
    // Create a hidden file input
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json,application/json';
    input.style.display = 'none';
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const scenarioData = JSON.parse(event.target.result);
                fetch('/scenario/load', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(scenarioData)
                })
                .then(resp => resp.json())
                .then(result => {
                    if (result.status === 'success') {
                        alert('Scenario loaded: ' + (scenarioData.name || 'Unnamed'));
                    } else {
                        alert('Error loading scenario: ' + (result.error || 'Unknown error'));
                    }
                });
            } catch (err) {
                alert('Error loading scenario: ' + err);
            }
        };
        reader.readAsText(file);
    };
    document.body.appendChild(input);
    input.click();
    document.body.removeChild(input);
}

function saveScenarioFile() {
    // Prompt for scenario name/description if desired
    const name = prompt('Enter scenario name:', simulationData.name || 'Scenario');
    const description = prompt('Enter scenario description:', simulationData.description || '');
    fetch('/scenario/save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, description })
    })
    .then(response => {
        if (!response.ok) throw new Error('Failed to save scenario');
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = (name || 'scenario') + '.json';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    })
    .catch(error => {
        alert('Error saving scenario: ' + error);
    });
}

// Insert tilemap view state and rendering utilities near top-level (after global vars)
if (typeof window.tilemapView === 'undefined') {
  window.tilemapView = {
    scale: 1,
    minScale: 0.1,
    maxScale: 1.0,  // Never upscale beyond 100%
    offsetX: 0,
    offsetY: 0,
    isPanning: false,
    panStart: {x: 0, y: 0},
    viewStart: {x: 0, y: 0},
    panThreshold: 4,  // pixels
    dragDistance: 0
  };
}

// NEW: Selection state
if (typeof window.selectedEntityId === 'undefined') {
  window.selectedEntityId = null;
}

// Internal guards to prevent duplicate bindings / heavy writes
if (typeof window._worldInteractionBound === 'undefined') {
    window._worldInteractionBound = false;
}
if (typeof window._saveViewStateTimer === 'undefined') {
    window._saveViewStateTimer = null;
}

function createWorldControlsWindow() {
  if (document.getElementById('world-controls-window')) return;
  const win = document.createElement('div');
  win.id = 'world-controls-window';
  win.className = 'window draggable';
  win.style = 'position:absolute; left:20px; top:20px; width:160px; height:120px;';
  win.innerHTML = `
    <div class="title-bar">
      <div class="title-bar-text">World View</div>
      <div class="title-bar-controls">
        <button aria-label="Close"></button>
      </div>
    </div>
    <div class="window-body" style="padding:4px; display:flex; flex-direction:column; gap:4px;">
      <div style="display:flex; gap:2px;">
        <button id="world-zoom-out" style="flex:1;">-</button>
        <button id="world-zoom-reset" style="flex:1;">Fit</button>
        <button id="world-zoom-in" style="flex:1;">+</button>
      </div>
      <div style="display:flex; gap:2px;">
        <button id="world-pan-reset" style="flex:1;">Center</button>
      </div>
    </div>`;
  document.body.appendChild(win);
  
  // Wire close button
  const closeBtn = win.querySelector('.title-bar-controls button[aria-label="Close"]');
  if (closeBtn) closeBtn.addEventListener('click', ()=>win.classList.add('hidden'));
  
  // Make it draggable
  try { draggableElement(win); } catch(e) {}
  try { bringableToFront(win); } catch(e) {}
  
  // Wire controls
  document.getElementById('world-zoom-in').addEventListener('click', ()=> adjustWorldZoom(1.1));
  document.getElementById('world-zoom-out').addEventListener('click', ()=> adjustWorldZoom(1/1.1));
  document.getElementById('world-zoom-reset').addEventListener('click', ()=> fitWorldToViewport());
  document.getElementById('world-pan-reset').addEventListener('click', ()=> centerWorldView());
}

function adjustWorldZoom(mult) {
  const canvas = document.getElementById('world-canvas');
  if (!canvas) return;
  zoomWorldAtPoint(canvas.width/2, canvas.height/2, mult);
}

function zoomWorldAtPoint(px, py, mult) {
  const prevScale = tilemapView.scale;
  let newScale = prevScale * mult;
  newScale = Math.max(tilemapView.minScale, Math.min(tilemapView.maxScale, newScale));
  const scaleChange = newScale / prevScale;
  
  // Adjust offsets so (px,py) stays put
  tilemapView.offsetX = px - scaleChange * (px - tilemapView.offsetX);
  tilemapView.offsetY = py - scaleChange * (py - tilemapView.offsetY);
  tilemapView.scale = newScale;
  
  updateWorldView();
}

function fitWorldToViewport() {
  const canvas = document.getElementById('world-canvas');
  if (!canvas || !simulationData.world || !simulationData.world.tilemap) return;
  
  const tm = simulationData.world.tilemap;
  const worldWidth = tm.width * 32;
  const worldHeight = tm.height * 32;
  const viewWidth = canvas.width;
  const viewHeight = canvas.height;
  
  // Calculate scale to fit world in viewport, but never exceed 1.0
  const scaleX = viewWidth / worldWidth;
  const scaleY = viewHeight / worldHeight;
  tilemapView.scale = Math.min(1.0, Math.min(scaleX, scaleY));
  
  // Center the world
  tilemapView.offsetX = (viewWidth - worldWidth * tilemapView.scale) / 2;
  tilemapView.offsetY = (viewHeight - worldHeight * tilemapView.scale) / 2;
  
  updateWorldView();
}

function centerWorldView() {
  const canvas = document.getElementById('world-canvas');
  if (!canvas || !simulationData.world || !simulationData.world.tilemap) return;
  
  const tm = simulationData.world.tilemap;
  const worldWidth = tm.width * 32;
  const worldHeight = tm.height * 32;
  const viewWidth = canvas.width;
  const viewHeight = canvas.height;
  
  // Center without changing scale
  tilemapView.offsetX = (viewWidth - worldWidth * tilemapView.scale) / 2;
  tilemapView.offsetY = (viewHeight - worldHeight * tilemapView.scale) / 2;
  
  updateWorldView();
}

// Helper function to update both canvas and entities
function updateWorldView() {
  if (simulationData.world && simulationData.world.tilemap) {
    renderWorldTilemap(simulationData.world.tilemap);
    updateWorldEntitiesTransform();
    saveTimapViewState(); // Save state whenever view changes
  }
}

// Viewport culling for large tilemaps
function getVisibleTileBounds(tilemapView, canvasWidth, canvasHeight, tileSize) {
  const scale = tilemapView.scale;
  const startX = Math.max(0, Math.floor(-tilemapView.offsetX / (tileSize * scale)));
  const startY = Math.max(0, Math.floor(-tilemapView.offsetY / (tileSize * scale)));
  const endX = Math.ceil((canvasWidth - tilemapView.offsetX) / (tileSize * scale));
  const endY = Math.ceil((canvasHeight - tilemapView.offsetY) / (tileSize * scale));
  return { startX, startY, endX, endY };
}

// Transform entities to match world view
function updateWorldEntitiesTransform() {
  const entitiesContainer = document.getElementById('world-entities');
  if (!entitiesContainer) return;
  
  const transform = `translate(${tilemapView.offsetX}px, ${tilemapView.offsetY}px) scale(${tilemapView.scale})`;
  entitiesContainer.style.transform = transform;
}

// Clear entity selection
function clearEntitySelection() {
  window.selectedEntityId = null;
  // You can add visual feedback here later
}

// Setup world layer interaction
function setupWorldLayerInteraction() {
  const worldLayer = document.getElementById('world-layer');
  if (!worldLayer) return;
    // Idempotency: don't attach multiple listeners across ticks
    if (window._worldInteractionBound || worldLayer.dataset.listenersAttached === '1') return;
  
  worldLayer.addEventListener('mousedown', (e) => {
    // Only handle if clicking on the world layer itself (not on entities)
    if (e.target !== worldLayer && !e.target.closest('#world-canvas')) return;
    
    tilemapView.isPanning = true;
    tilemapView.panStart = {x: e.clientX, y: e.clientY};
    tilemapView.viewStart = {x: tilemapView.offsetX, y: tilemapView.offsetY};
    tilemapView.dragDistance = 0;
    
    worldLayer.style.cursor = 'grabbing';
    e.preventDefault();
  });
  
  window.addEventListener('mouseup', () => {
    if (tilemapView.isPanning) {
      // If movement was less than threshold, treat as click
      if (tilemapView.dragDistance < tilemapView.panThreshold) {
        clearEntitySelection();
      }
      tilemapView.isPanning = false;
      const worldLayer = document.getElementById('world-layer');
      if (worldLayer) worldLayer.style.cursor = 'grab';
    }
  });
  
  window.addEventListener('mousemove', (e) => {
    if (!tilemapView.isPanning) return;
    
    const dx = e.clientX - tilemapView.panStart.x;
    const dy = e.clientY - tilemapView.panStart.y;
    
    tilemapView.dragDistance = Math.sqrt(dx * dx + dy * dy);
    
    tilemapView.offsetX = tilemapView.viewStart.x + dx;
    tilemapView.offsetY = tilemapView.viewStart.y + dy;
    
    updateWorldView();
  });
  
  // Wheel zoom on world layer
  worldLayer.addEventListener('wheel', (e) => {
    e.preventDefault();
    const factor = e.deltaY < 0 ? 1.1 : 1/1.1;
    zoomWorldAtPoint(e.clientX, e.clientY, factor);
  }, { passive: false });
  
  worldLayer.style.cursor = 'grab';

    // Mark as bound so we don't re-bind every frame
    worldLayer.dataset.listenersAttached = '1';
    window._worldInteractionBound = true;
}

// NEW: World tilemap rendering function (replaces old window-based version)
function renderWorldTilemap(tm) {
  if (!tm) return;
  
  // Ensure we have the world canvas
  const canvas = document.getElementById('world-canvas');
  if (!canvas) return;
  
  // Set canvas size to viewport
  const viewWidth = window.innerWidth;
  const viewHeight = window.innerHeight;
  
  if (canvas.width !== viewWidth || canvas.height !== viewHeight) {
    canvas.width = viewWidth;
    canvas.height = viewHeight;
  }
  
    const ctx = canvas.getContext('2d');
    ctx.reset();
  ctx.save();
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  
  // Apply transform
  ctx.translate(tilemapView.offsetX, tilemapView.offsetY);
  ctx.scale(tilemapView.scale, tilemapView.scale);
  
  const tileSize = 32;
  const colors = {0:'#C2A060', 1:'#555555', 2:'#88CCFF'};
  
  // Use viewport culling for large maps
  const shouldCull = tm.width * tm.height > 65536; // 256x256 threshold
  
  let startX = 0, startY = 0, endX = tm.width, endY = tm.height;
  
  if (shouldCull) {
    const bounds = getVisibleTileBounds(tilemapView, canvas.width, canvas.height, tileSize);
    startX = Math.max(0, bounds.startX);
    startY = Math.max(0, bounds.startY);
    endX = Math.min(tm.width, bounds.endX);
    endY = Math.min(tm.height, bounds.endY);
  }
  
  // Render visible tiles
  for (let y = startY; y < endY && y < tm.tiles.length; y++) {
    const row = tm.tiles[y];
    for (let x = startX; x < endX && x < row.length; x++) {
      const id = row[x];
      ctx.fillStyle = colors[id] || '#FF00FF';
      ctx.fillRect(x * tileSize, y * tileSize, tileSize, tileSize);
    }
  }
  
  ctx.restore();
}

// Camera state persistence
function saveTimapViewState() {
    // Debounce to avoid frequent blocking localStorage writes during pan/zoom
    if (window._saveViewStateTimer) {
        clearTimeout(window._saveViewStateTimer);
    }
    window._saveViewStateTimer = setTimeout(() => {
        const state = {
            scale: tilemapView.scale,
            offsetX: tilemapView.offsetX,
            offsetY: tilemapView.offsetY
        };
        try {
            localStorage.setItem('moistureFarmer_tilemapView', JSON.stringify(state));
        } catch (e) {
            // Ignore quota or security errors
        }
        window._saveViewStateTimer = null;
    }, 120);
}

function loadTimapViewState() {
  try {
    const saved = localStorage.getItem('moistureFarmer_tilemapView');
    if (saved) {
      const state = JSON.parse(saved);
      tilemapView.scale = state.scale || 1;
      tilemapView.offsetX = state.offsetX || 0;
      tilemapView.offsetY = state.offsetY || 0;
      return true;
    }
  } catch (e) {
    console.warn('Failed to load tilemap view state:', e);
  }
  return false;
}

// Calculate initial view - fit viewport but never exceed 100% scale
function calculateInitialView() {
  // Try to load saved state first
  if (loadTimapViewState()) {
    updateWorldView();
    return;
  }
  
  // Otherwise, fit to viewport
  fitWorldToViewport();
  
  // Save the initial state
  saveTimapViewState();
}

// Hook into existing updateSimulationDisplay to also render tilemap
const _origUpdateSimulationDisplay = updateSimulationDisplay;
updateSimulationDisplay = function() {
  _origUpdateSimulationDisplay();
  try {
    // Initialize world view components if needed
    createWorldControlsWindow();
    setupWorldLayerInteraction();
    
    if (simulationData.world && simulationData.world.tilemap) {
      // Use new world rendering instead of old tilemap window
      renderWorldTilemap(simulationData.world.tilemap);
      updateWorldEntitiesTransform();
      
      // Initialize view if this is the first render
      if (!window.worldViewInitialized) {
        calculateInitialView();
        window.worldViewInitialized = true;
      }
    }
  } catch (e) { console.error('World render error', e); }
};

// Handle viewport resize for world canvas
window.addEventListener('resize', () => {
  if (simulationData.world && simulationData.world.tilemap) {
    renderWorldTilemap(simulationData.world.tilemap);
  }
});