// simulation-display.js - Simulation data processing and display updates

/**
 * Update the simulation display with current data
 */
function updateSimulationDisplayCore() {
    // For each entity in the simulation data, populate the simulationDataDictionary
    if (window.simulationData.world && window.simulationData.world.entities) {
        Object.keys(window.simulationData.world.entities).forEach(entityId => {
            const entity = window.simulationData.world.entities[entityId];
            window.simulationDataDictionary[entityId] = entity;

            // For each entity's slots, populate the simulationDataDictionary
            if (entity.slots) {
                Object.keys(entity.slots).forEach(slotName => {
                    const slot = entity.slots[slotName];
                    if (slot.component) {
                        // If the slot has a component, add it to the dictionary
                        window.simulationDataDictionary[`${entityId}.${slotName}`] = slot;
                        window.simulationDataDictionary[slot.component.id] = slot.component;
                    }
                });
            }
        });
    }

    // Update tick count
    const tickCountElement = document.getElementById('simulation-tick-count');
    if (tickCountElement && window.simulationData.tick_count !== undefined) {
        tickCountElement.textContent = window.simulationData.tick_count;
    }

    // Update entities display if needed
    if (window.simulationData.world && window.simulationData.world.entities) {
        const windowBodyEntities = document.getElementById('simulation-detail-window-body-entities');
        if (windowBodyEntities) {
            updateJsonTreeviewHtmlIncrementally(windowBodyEntities, window.simulationData, 'Entities', 'entities');
        }
    }

    // Update simulation status
    const simulationStatusPausedElement = document.getElementById('simulation-status-paused');
    if (simulationStatusPausedElement) {
        simulationStatusPausedElement.textContent = window.simulationData.paused ? 'Paused' : 'Running';
    }
    
    // Update button text based on the new state
    const pauseButton = document.getElementById('simulation-pause');
    if (pauseButton) {
        if (window.simulationData.paused) {
            pauseButton.textContent = 'Resume';
        } else {
            pauseButton.textContent = 'Pause';
        }
    }

    // Update the simulation delay buttons
    const buttons = document.querySelectorAll('.simulation-delay-button');
    buttons.forEach(button => {
        if (button.id === `simulation-delay-${window.simulationData.simulation_delay}`) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });

    // Handle entity animations and display
    const entitiesContainer = document.getElementById('world-entities');
    if (entitiesContainer) {
        // Clear existing icons (canvas rendering used now)
        const existingIcons = entitiesContainer.querySelectorAll('.entity-icon');
        existingIcons.forEach(icon => icon.remove());
        debugLog('Entities snapshot', window.simulationData.world && window.simulationData.world.entities);

        // Update entity tween states for smooth movement
        if (window.simulationData.world && window.simulationData.world.entities) {
            Object.values(window.simulationData.world.entities).forEach(entity => {
                if (typeof updateEntityDetailWindow === 'function') {
                    updateEntityDetailWindow(entity.id);
                }
                if (typeof updateEntityTweenState === 'function') {
                    updateEntityTweenState(entity);
                }
            });
            // Start animation loop once we have entities
            if (typeof startTweenAnimation === 'function') {
                startTweenAnimation();
            }
        }
    }

    // Keep any open chat windows in sync
    if (typeof updateAllDroidChatWindows === 'function') {
        updateAllDroidChatWindows();
    }

    // Update the Entities menu
    if (typeof updateEntitiesMenu === 'function') {
        updateEntitiesMenu();
    }
}

/**
 * Update the Entities menu with current entities from the simulation
 */
function updateEntitiesMenu() {
    const entitiesMenu = document.getElementById('entities-menu');
    if (!entitiesMenu) return;

    // Get current entities
    const entities = window.simulationData.world && window.simulationData.world.entities 
        ? Object.values(window.simulationData.world.entities) 
        : [];

    // Clear existing menu items
    entitiesMenu.innerHTML = '';

    // Add menu item for each entity
    entities.forEach(entity => {
        const li = document.createElement('li');
        li.setAttribute('onmousedown', `showEntityDetailWindow('${entity.id}')`);
        
        // Add sprite icon if model is available
        if (entity.model) {
            const img = document.createElement('img');
            img.src = `/resources/sprites/${entity.model}.png`;
            li.appendChild(img);
        }
        
        // Add entity name/id
        const span = document.createElement('span');
        span.textContent = entity.name || entity.id;
        li.appendChild(span);
        
        entitiesMenu.appendChild(li);
    });

    // If no entities, show a placeholder
    if (entities.length === 0) {
        const li = document.createElement('li');
        li.className = 'disabled';
        li.textContent = 'No entities';
        entitiesMenu.appendChild(li);
    }
}

/**
 * Update JSON treeview HTML incrementally to avoid full re-renders
 */
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

/**
 * Convert JSON data to HTML tree view format
 */
function jsonToTreeviewHtml(json, title, id_path, depth = 0) {
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

// Export functions to global scope
window.updateSimulationDisplayCore = updateSimulationDisplayCore;
window.updateJsonTreeviewHtmlIncrementally = updateJsonTreeviewHtmlIncrementally;
window.jsonToTreeviewHtml = jsonToTreeviewHtml;
window.updateEntitiesMenu = updateEntitiesMenu;
