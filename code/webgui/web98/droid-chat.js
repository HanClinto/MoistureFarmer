// droid-chat.js - Droid chat functionality and window management

// Simple in-memory chat state per droid
const droidChats = {}; // { [entityId]: { messages: Array<{role:string,text:string}>, pending: boolean } }

/**
 * Check if a droid agent is currently active/busy
 */
function isDroidAgentActive(entityId) {
    try {
        const entity = window.simulationData.world?.entities?.[entityId];
        const agent = entity?.slots?.agent?.component;
        return !!agent?.is_active;
    } catch (e) { 
        return false; 
    }
}

/**
 * Open a chat window for the specified droid
 */
function openDroidChatWindow(entityId) {
    ensureDroidChatWindow(entityId);
    const win = document.getElementById(`droid-chat-window-${entityId}`);
    if (win) { 
        showWindow(win.id); 
        bringToFront(win); 
    }
}

/**
 * Ensure a chat window exists for the specified droid
 */
function ensureDroidChatWindow(entityId) {
    if (!droidChats[entityId]) {
        droidChats[entityId] = { messages: [], pending: false };
    }

    let win = document.getElementById(`droid-chat-window-${entityId}`);
    if (win) return; // already exists

    win = document.createElement('div');
    win.id = `droid-chat-window-${entityId}`;
    win.className = 'window droid-chat-window draggable resizeable';
    win.style.width = '360px';
    win.style.height = '300px';
    win.innerHTML = `
        <div class="title-bar">
            <div class="title-bar-text">Droid Chat - ${entityId}</div>
            <div class="title-bar-controls">
                <button aria-label="Close"></button>
            </div>
        </div>
        <div class="window-body chat-body">
            <div id="droid-chat-log-${entityId}" class="chat-log"></div>
        </div>
        <div class="status-bar chat-input-bar">
            <div class="status-bar-field chat-input-wrapper">
                <input id="droid-chat-input-${entityId}" class="chat-input" type="text" placeholder="Type a message..." />
            </div>
            <div class="status-bar-field chat-send-wrapper">
                <button id="droid-chat-send-${entityId}" class="chat-send">Send</button>
            </div>
        </div>
    `;
    document.body.appendChild(win);

    // Wire behaviors
    const closeButton = win.querySelector('.title-bar-controls button[aria-label="Close"]');
    if (closeButton) closeButton.addEventListener('click', () => win.classList.add('hidden'));
    
    // Make window draggable and resizeable
    if (typeof resizeableElement === 'function') resizeableElement(win);
    if (typeof draggableElement === 'function') draggableElement(win);
    if (typeof bringableToFront === 'function') bringableToFront(win);

    const input = document.getElementById(`droid-chat-input-${entityId}`);
    const sendBtn = document.getElementById(`droid-chat-send-${entityId}`);

    const doSend = () => {
        const text = input.value.trim();
        if (!text) return;
        if (isDroidAgentActive(entityId)) return; // guard

        // Append <user> message locally
        addChatMessage(entityId, 'user', text);
        input.value = '';

        // Mark pending and disable send
        droidChats[entityId].pending = true;
        updateDroidChatWindow(entityId, /*syncOnly*/ true);

        fetch(`/droid/chat/${entityId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
        .then(r => r.json())
        .then(resp => {
            if (resp.error) {
                addChatMessage(entityId, 'system', `Error: ${resp.error}`);
                droidChats[entityId].pending = false;
                updateDroidChatWindow(entityId, /*syncOnly*/ true);
            }
        })
        .catch(err => {
            addChatMessage(entityId, 'system', `Error: ${err}`);
            droidChats[entityId].pending = false;
            updateDroidChatWindow(entityId, /*syncOnly*/ true);
        });
    };

    sendBtn.addEventListener('click', doSend);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            doSend();
        }
    });

    // Initial sync
    updateDroidChatWindow(entityId, /*syncOnly*/ true);
}

/**
 * Add a message to the chat log for a specific droid
 */
function addChatMessage(entityId, role, text) {
    if (!droidChats[entityId]) droidChats[entityId] = { messages: [], pending: false };
    droidChats[entityId].messages.push({ role, text });
    updateDroidChatWindow(entityId);
}

/**
 * Update the chat window display for a specific droid
 */
function updateDroidChatWindow(entityId, syncOnly = false) {
    const logEl = document.getElementById(`droid-chat-log-${entityId}`);
    const sendBtn = document.getElementById(`droid-chat-send-${entityId}`);
    const input = document.getElementById(`droid-chat-input-${entityId}`);
    if (!sendBtn || !input) return;

    const active = isDroidAgentActive(entityId);
    // Disable send when active
    sendBtn.disabled = active;
    input.disabled = active;

    // When we detect agent finished after a pending send, add a simple done line
    if (!active && droidChats[entityId]?.pending) {
        droidChats[entityId].pending = false;
    }

    //if (syncOnly || !logEl) return;

    // Render messages
    logEl.innerHTML = '';
    
    // See if we can find this entity's agent component
    agent_slot = simulationDataDictionary[`${entityId}.agent`];
    if (agent_slot && agent_slot.component) {
        // For each message in the agent's context, add it to the chat log
        messages = agent_slot.component.context.messages;
        console.log(`Agent messages for ${entityId}:`);
        console.log(messages);

        (messages || []).forEach(msg => {
            const prefix = `<${msg.role}>`
            if (msg.content){
                // TODO: Add a checkbox that will optionally let us show / hide messages with "Current world state: {" in them.
                const hide_world_state_messages = true;
                if (hide_world_state_messages && msg.content.includes("Current world state: {")) {
                    // Skip rendering this message
                    return;
                }
                const div = document.createElement('div');
                div.className = `chat-line chat-${msg.role}`;
                div.textContent = `${prefix} ${msg.content}`;
                logEl.appendChild(div);
            }
            if (msg.tool_calls && Array.isArray(msg.tool_calls)) {
                // Structure tool calls as if they are IRC commands, such as "/kick <username>" or "/move_to_entity <identifier>"
                msg.tool_calls.forEach(toolCall => {
                    const toolDiv = document.createElement('div');
                    toolDiv.className = `chat-line chat-toolcall`;
                    // For now, just append the arguments as-is:
                    toolDiv.textContent = `${prefix} /${toolCall.function.name} ${toolCall.function.arguments}`;

                    // Append each argument as " identifier=value"
                    //const args = JSON.parse(toolCall.arguments);
                    //toolDiv.textContent = `${prefix} /${toolCall.function.name} ${Object.entries(args).map(([key, value]) => `${key}=${value}`).join(' ')}`;
                    logEl.appendChild(toolDiv);
                });
            }
        });
    } else {
        // If no agent component is found, display a message
        const div = document.createElement('div');
        div.className = `chat-line chat-system`;
        div.textContent = `<system> No agent component found for this entity.`;
        logEl.appendChild(div);
    }
    // Auto-scroll
    logEl.scrollTop = logEl.scrollHeight;
}

/**
 * Update all open droid chat windows
 */
function updateAllDroidChatWindows() {
    Object.keys(droidChats).forEach(entityId => {
        updateDroidChatWindow(entityId, /*syncOnly*/ true);
    });
}

// Export functions to global scope
window.isDroidAgentActive = isDroidAgentActive;
window.openDroidChatWindow = openDroidChatWindow;
window.ensureDroidChatWindow = ensureDroidChatWindow;
window.addChatMessage = addChatMessage;
window.updateDroidChatWindow = updateDroidChatWindow;
window.updateAllDroidChatWindows = updateAllDroidChatWindows;
