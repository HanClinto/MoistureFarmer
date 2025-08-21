// entity-detail.js - Entity detail window creation and management

/**
 * Show the entity detail window for a specific entity
 */
function showEntityDetailWindow(entityId) {
    // Create or focus the entity detail window for the given entity ID
    let win = document.getElementById(`entity-detail-window-${entityId}`);
    if (!win) {
        // Create a new window if it doesn't exist
        win = document.createElement('div');
        win.id = `entity-detail-window-${entityId}`;
        win.className = 'window entity-detail-window draggable resizeable';
        win.innerHTML = `
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
        document.body.appendChild(win);

        // Add close button functionality
        const closeButton = win.querySelector('.title-bar-controls button[aria-label="Close"]');
        closeButton.addEventListener('click', function() {
            const win = closeButton.closest('.window');
            if (win) {
                win.classList.add('hidden');
            }
        });

        // Make window interactive
        if (typeof resizeableElement === 'function') resizeableElement(win);
        if (typeof draggableElement === 'function') draggableElement(win);
        if (typeof bringableToFront === 'function') bringableToFront(win);
    }

    updateEntityDetailWindow(entityId);

    // Show the window and bring it to the front
    showWindow(win.id);
    bringToFront(win);
}

/**
 * Update the entity detail window with current entity data
 */
function updateEntityDetailWindow(entityId) {
    // Update the entity detail window for the given entity ID
    let win = document.getElementById(`entity-detail-window-${entityId}`);
    if (!win) {
        return; // If the window doesn't exist, do nothing
    }

    // Populate the entity details
    const entity = window.simulationDataDictionary[entityId];
    const detailBody = document.getElementById(`entity-detail-window-body-${entityId}`);
    if (!entity || !detailBody) return;
    
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
            console.log(`Entity ${entityId} Slot ${slotName} accepts ${slot.accepts}:`, slot);
            
            // Create a specialized view for each slot based on what it can accept
            switch (slot.accepts) {
                case 'DroidAgentSimple':
                    createAgentSlotView(detailBody, entityId, slotName, slot);
                    break;
                case 'PowerPack':
                    createPowerPackSlotView(detailBody, entityId, slotName, slot);
                    break;
                case 'WaterTank':
                    createWaterTankSlotView(detailBody, entityId, slotName, slot);
                    break;
            }
        });
    }
}

/**
 * Create a view for a droid agent slot
 */
function createAgentSlotView(detailBody, entityId, slotName, slot) {
    // Add a progress bar to display the agent context usage vs. capacity
    const progressGroup = document.createElement('fieldset');
    progressGroup.style.width = 'calc(100% - 24px)';
    const progressGroupLabel = document.createElement('legend');
    progressGroupLabel.textContent = `Agent - ${slotName}`;
    progressGroup.appendChild(progressGroupLabel);

    const progressDiv = document.createElement('div');
    progressDiv.className = 'progress-indicator segmented';
    progressDiv.style.width = '100%';
    const contextBar = document.createElement('span');
    contextBar.className = 'progress-indicator-bar';
    contextBar['data-key'] = `${entityId}.${slotName}`;
    
    if (slot.component) {
        contextBar['data-context_size'] = slot.component.last_total_tokens;
        contextBar['data-context_size_max'] = slot.component.tokens_max;

        const pct = (slot.component.last_total_tokens / slot.component.tokens_max) * 100;
        contextBar.title = `Context Size: ${slot.component.last_total_tokens}, Max: ${slot.component.tokens_max} (${pct.toFixed(2)}%)`;
        contextBar.classList.remove('disabled');
        const contextPercentage = (slot.component.last_total_tokens / slot.component.tokens_max) * 100;
        contextBar.style.width = `${contextPercentage}%`;
    } else {
        contextBar.style.width = '0%';
        contextBar.classList.add('disabled');
        contextBar.title = 'No component present';
    }
    
    progressDiv.title = contextBar.title;
    progressGroup.title = contextBar.title;
    progressDiv.appendChild(contextBar);
    progressGroup.appendChild(progressDiv);
    detailBody.appendChild(progressGroup);

    // Add a button to open up a window and chat with the droid agent
    const chatGroup = document.createElement('fieldset');
    chatGroup.style.width = 'calc(100% - 24px)';
    const legend = document.createElement('legend');
    legend.textContent = 'Agent';
    chatGroup.appendChild(legend);

    const btn = document.createElement('button');
    btn.textContent = 'Open Chat';
    btn.addEventListener('click', () => {
        if (typeof openDroidChatWindow === 'function') {
            openDroidChatWindow(entityId);
        }
    });
    chatGroup.appendChild(btn);

    const entity = window.simulationData.world?.entities?.[entityId];
    const isActive = !!entity?.slots?.agent?.component?.is_active;
    const status = document.createElement('span');
    status.style.marginLeft = '8px';
    status.textContent = isActive ? '(Busy)' : '(Idle)';
    chatGroup.appendChild(status);

    detailBody.appendChild(chatGroup);
}

/**
 * Create a view for a power pack slot
 */
function createPowerPackSlotView(detailBody, entityId, slotName, slot) {
    const progressGroup = document.createElement('fieldset');
    progressGroup.style.width = 'calc(100% - 24px)';
    const progressGroupLabel = document.createElement('legend');
    progressGroupLabel.textContent = `Power Pack - ${slotName}`;
    progressGroup.appendChild(progressGroupLabel);

    const progressDiv = document.createElement('div');
    progressDiv.className = 'progress-indicator segmented';
    progressDiv.style.width = '100%';
    const progressBar = document.createElement('span');
    progressBar.className = 'progress-indicator-bar';
    progressBar['data-key'] = `${entityId}.${slotName}`;
    
    if (slot.component) {
        progressBar['data-charge'] = slot.component.charge;
        progressBar['data-charge_max'] = slot.component.charge_max;
        const pct = (slot.component.charge / slot.component.charge_max) * 100;
        progressBar.title = `Charge: ${slot.component.charge}, Capacity: ${slot.component.charge_max}`;
        progressBar.classList.remove('disabled');
        const chargePercentage = (slot.component.charge / slot.component.charge_max) * 100;
        progressBar.style.width = `${chargePercentage}%`;
    } else {
        progressBar.style.width = '0%';
        progressBar.classList.add('disabled');
        progressBar.title = 'No component present';
    }
    
    progressDiv.title = progressBar.title;
    progressGroup.title = progressBar.title;
    progressDiv.appendChild(progressBar);
    progressGroup.appendChild(progressDiv);
    detailBody.appendChild(progressGroup);
}

/**
 * Create a view for a water tank slot
 */
function createWaterTankSlotView(detailBody, entityId, slotName, slot) {
    const progressGroup = document.createElement('fieldset');
    progressGroup.style.width = 'calc(100% - 24px)';
    const progressGroupLabel = document.createElement('legend');
    progressGroupLabel.textContent = `Water Tank - ${slotName}`;
    progressGroup.appendChild(progressGroupLabel);

    const progressDiv = document.createElement('div');
    progressDiv.className = 'progress-indicator segmented';
    progressDiv.style.width = '100%';
    const waterBar = document.createElement('span');
    waterBar.className = 'progress-indicator-bar';
    waterBar['data-key'] = `${entityId}.${slotName}`;
    
    if (slot.component) {
        waterBar['data-fill'] = slot.component.fill;
        waterBar['data-capacity'] = slot.component.capacity;
        waterBar.title = `Fill: ${slot.component.fill}, Capacity: ${slot.component.capacity}`;
        waterBar.classList.remove('disabled');
        const fillPercentage = (slot.component.fill / slot.component.capacity) * 100;
        waterBar.style.width = `${fillPercentage}%`;
    } else {
        waterBar.style.width = '0%';
        waterBar.classList.add('disabled');
        waterBar.title = 'No component present';
    }
    
    progressDiv.title = waterBar.title;
    progressGroup.title = waterBar.title;
    progressDiv.appendChild(waterBar);
    progressGroup.appendChild(progressDiv);
    detailBody.appendChild(progressGroup);
}

// Export functions to global scope
window.showEntityDetailWindow = showEntityDetailWindow;
window.updateEntityDetailWindow = updateEntityDetailWindow;
