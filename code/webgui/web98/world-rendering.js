// world-rendering.js - Tilemap view state, world canvas rendering, and viewport management

// Insert tilemap view state and rendering utilities
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

// Selection state
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

/**
 * Create the world controls window for zoom and pan controls
 */
function createWorldControlsWindow() {
    if (document.getElementById('world-controls-window')) return;
    const win = document.createElement('div');
    win.id = 'world-controls-window';
    win.className = 'window draggable';
    win.style = 'position:absolute; left:20px; top:20px; width:auto; height:auto;';
    win.innerHTML = `
        <div class="title-bar">
            <div class="title-bar-text">World View</div>
            <div class="title-bar-controls">
                <button aria-label="Close"></button>
            </div>
        </div>
        <div class="window-body" style="padding:4px; display:flex; flex-direction:column; gap:4px;">
            <div style="display:flex; gap:2px;">
                <button id="world-zoom-out" class="btn-compact">-</button>
                <button id="world-zoom-reset" class="btn-compact">Fit</button>
                <button id="world-zoom-in" class="btn-compact">+</button>
                <button id="world-pan-reset" class="btn-compact">Center</button>
            </div>
        </div>`;
    document.body.appendChild(win);
    
    // Position bottom-left after rendering so we know its height
    requestAnimationFrame(() => {
        try {
            win.style.left = '8px';
            win.style.top = (window.innerHeight - win.offsetHeight - 8) + 'px';
        } catch(e) {}
    });

    // Wire close button
    const closeBtn = win.querySelector('.title-bar-controls button[aria-label="Close"]');
    if (closeBtn) closeBtn.addEventListener('click', () => win.classList.add('hidden'));

    // Make it draggable
    try { if (typeof draggableElement === 'function') draggableElement(win); } catch(e) {}
    try { if (typeof bringableToFront === 'function') bringableToFront(win); } catch(e) {}

    // Wire controls
    document.getElementById('world-zoom-in').addEventListener('click', () => adjustWorldZoom(1.1));
    document.getElementById('world-zoom-out').addEventListener('click', () => adjustWorldZoom(1/1.1));
    document.getElementById('world-zoom-reset').addEventListener('click', () => fitWorldToViewport());
    document.getElementById('world-pan-reset').addEventListener('click', () => centerWorldView());
}

/**
 * Adjust world zoom by a multiplier
 */
function adjustWorldZoom(mult) {
    const canvas = document.getElementById('world-canvas');
    if (!canvas) return;
    zoomWorldAtPoint(canvas.width/2, canvas.height/2, mult);
}

/**
 * Zoom the world at a specific point
 */
function zoomWorldAtPoint(px, py, mult) {
    const prevScale = window.tilemapView.scale;
    let newScale = prevScale * mult;
    newScale = Math.max(window.tilemapView.minScale, Math.min(window.tilemapView.maxScale, newScale));
    const scaleChange = newScale / prevScale;

    // Adjust offsets so (px,py) stays put
    window.tilemapView.offsetX = px - scaleChange * (px - window.tilemapView.offsetX);
    window.tilemapView.offsetY = py - scaleChange * (py - window.tilemapView.offsetY);
    window.tilemapView.scale = newScale;

    updateWorldView();
}

/**
 * Fit world to viewport while respecting max scale
 */
function fitWorldToViewport() {
    const canvas = document.getElementById('world-canvas');
    if (!canvas || !window.simulationData.world || !window.simulationData.world.tilemap) return;

    const tm = window.simulationData.world.tilemap;
    const worldWidth = tm.width * 32;
    const worldHeight = tm.height * 32;
    const viewWidth = canvas.width;
    const viewHeight = canvas.height;

    // Calculate scale to fit world in viewport, but never exceed 1.0
    const scaleX = viewWidth / worldWidth;
    const scaleY = viewHeight / worldHeight;
    window.tilemapView.scale = Math.min(1.0, Math.min(scaleX, scaleY));

    // Center the world
    window.tilemapView.offsetX = (viewWidth - worldWidth * window.tilemapView.scale) / 2;
    window.tilemapView.offsetY = (viewHeight - worldHeight * window.tilemapView.scale) / 2;

    updateWorldView();
}

/**
 * Center world view without changing scale
 */
function centerWorldView() {
    const canvas = document.getElementById('world-canvas');
    if (!canvas || !window.simulationData.world || !window.simulationData.world.tilemap) return;

    const tm = window.simulationData.world.tilemap;
    const worldWidth = tm.width * 32;
    const worldHeight = tm.height * 32;
    const viewWidth = canvas.width;
    const viewHeight = canvas.height;

    // Center without changing scale
    window.tilemapView.offsetX = (viewWidth - worldWidth * window.tilemapView.scale) / 2;
    window.tilemapView.offsetY = (viewHeight - worldHeight * window.tilemapView.scale) / 2;

    updateWorldView();
}

/**
 * Update both canvas and entities
 */
function updateWorldView() {
    if (window.simulationData.world && window.simulationData.world.tilemap) {
        renderWorldTilemap(window.simulationData.world.tilemap);
        updateWorldEntitiesTransform();
        saveTimapViewState(); // Save state whenever view changes
    }
}

/**
 * Get visible tile bounds for viewport culling
 */
function getVisibleTileBounds(tilemapView, canvasWidth, canvasHeight, tileSize) {
    const scale = tilemapView.scale;
    const startX = Math.max(0, Math.floor(-tilemapView.offsetX / (tileSize * scale)));
    const startY = Math.max(0, Math.floor(-tilemapView.offsetY / (tileSize * scale)));
    const endX = Math.ceil((canvasWidth - tilemapView.offsetX) / (tileSize * scale));
    const endY = Math.ceil((canvasHeight - tilemapView.offsetY) / (tileSize * scale));
    return { startX, startY, endX, endY };
}

/**
 * Transform entities to match world view
 */
function updateWorldEntitiesTransform() {
    const entitiesContainer = document.getElementById('world-entities');
    if (!entitiesContainer) return;

    const transform = `translate(${window.tilemapView.offsetX}px, ${window.tilemapView.offsetY}px) scale(${window.tilemapView.scale})`;
    entitiesContainer.style.transform = transform;
}

/**
 * Clear entity selection
 */
function clearEntitySelection() {
    window.selectedEntityId = null;
    // You can add visual feedback here later
}

/**
 * Setup world layer interaction for panning and zooming
 */
function setupWorldLayerInteraction() {
    const worldLayer = document.getElementById('world-layer');
    if (!worldLayer) return;
    // Idempotency: don't attach multiple listeners across ticks
    if (window._worldInteractionBound || worldLayer.dataset.listenersAttached === '1') return;

    worldLayer.addEventListener('mousedown', (e) => {
        // Only handle if clicking on the world layer itself (not on entities)
        if (e.target !== worldLayer && !e.target.closest('#world-canvas')) return;

        window.tilemapView.isPanning = true;
        window.tilemapView.panStart = {x: e.clientX, y: e.clientY};
        window.tilemapView.viewStart = {x: window.tilemapView.offsetX, y: window.tilemapView.offsetY};
        window.tilemapView.dragDistance = 0;

        worldLayer.style.cursor = 'grabbing';
        e.preventDefault();
    });

    window.addEventListener('mouseup', () => {
        if (window.tilemapView.isPanning) {
            // If movement was less than threshold, treat as click
            if (window.tilemapView.dragDistance < window.tilemapView.panThreshold) {
                clearEntitySelection();
            }
            window.tilemapView.isPanning = false;
            const worldLayer = document.getElementById('world-layer');
            if (worldLayer) worldLayer.style.cursor = 'grab';
        }
    });

    window.addEventListener('mousemove', (e) => {
        if (!window.tilemapView.isPanning) return;

        const dx = e.clientX - window.tilemapView.panStart.x;
        const dy = e.clientY - window.tilemapView.panStart.y;

        window.tilemapView.dragDistance = Math.sqrt(dx * dx + dy * dy);

        window.tilemapView.offsetX = window.tilemapView.viewStart.x + dx;
        window.tilemapView.offsetY = window.tilemapView.viewStart.y + dy;

        updateWorldView();
    });

    // Wheel zoom on world layer
    worldLayer.addEventListener('wheel', (e) => {
        e.preventDefault();
        // Detect macOS (includes Intel & Apple Silicon variants)
        const isMac = /Macintosh|MacIntel|MacPPC|Mac68K|Mac OS X/i.test(navigator.userAgent) || (navigator.platform && navigator.platform.toUpperCase().indexOf('MAC') >= 0);
        // Base per-notch zoom factor
        const baseZoomIn = 1.1;
        const baseZoomOut = 1 / baseZoomIn;
        let factor = e.deltaY < 0 ? baseZoomIn : baseZoomOut;
        if (isMac) {
            // Make it about 3x less sensitive: take the cubic root of the factor to reduce magnitude
            // rootFactor ~ 1.032 vs 1.1 (since 1.032^3 ≈ 1.10)
            const reduce = (f) => Math.pow(f, 1/3);
            factor = e.deltaY < 0 ? reduce(baseZoomIn) : 1 / reduce(baseZoomIn);
        }
        zoomWorldAtPoint(e.clientX, e.clientY, factor);
    }, { passive: false });

    worldLayer.style.cursor = 'grab';

    // Mark as bound so we don't re-bind every frame
    worldLayer.dataset.listenersAttached = '1';
    window._worldInteractionBound = true;
}

/**
 * Render the world tilemap on canvas
 */
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
    ctx.translate(window.tilemapView.offsetX, window.tilemapView.offsetY);
    ctx.scale(window.tilemapView.scale, window.tilemapView.scale);

    const tileSize = 32;
    const colors = {0:'#C2A060', 1:'#555555', 2:'#88CCFF'};

    // Use viewport culling for large maps
    const shouldCull = tm.width * tm.height > 65536; // 256x256 threshold

    let startX = 0, startY = 0, endX = tm.width, endY = tm.height;

    if (shouldCull) {
        const bounds = getVisibleTileBounds(window.tilemapView, canvas.width, canvas.height, tileSize);
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

    // --- Entity rendering (simple colored rectangles) ---
    try {
        if (window.simulationData.world && window.simulationData.world.entities) {
            // Lazy-init color cache & generator
            if (!window._entityColorCache) window._entityColorCache = {};
            if (!window._entityColorFor) {
                window._entityColorFor = function(id) {
                    if (window._entityColorCache[id]) return window._entityColorCache[id];
                    // Deterministic hash -> hue
                    let h = 0;
                    for (let i = 0; i < id.length; i++) {
                        h = (h * 131 + id.charCodeAt(i)) >>> 0; // simple rolling hash
                    }
                    const hue = h % 360;
                    const color = `hsl(${hue}deg 65% 55%)`;
                    window._entityColorCache[id] = color;
                    return color;
                };
            }

            const entities = Object.values(window.simulationData.world.entities);
            const tweenState = window._entityTweenState || {};
            for (const ent of entities) {
                if (!ent || !ent.location) continue;
                const st = tweenState[ent.id];
                let ex = ent.location.x * tileSize;
                let ey = ent.location.y * tileSize;
                if (st) {
                    // Use interpolated position if tween in progress
                    ex = (typeof st.interpX === 'number') ? st.interpX : ex;
                    ey = (typeof st.interpY === 'number') ? st.interpY : ey;
                }
                const inset = 2;
                const size = tileSize - inset * 2;
                ctx.save();
                ctx.lineWidth = 2;
                ctx.strokeStyle = '#000';
                ctx.fillStyle = window._entityColorFor(ent.id || 'unknown');
                ctx.beginPath();
                ctx.rect(ex + inset, ey + inset, size, size);
                ctx.fill();
                ctx.stroke();
                ctx.restore();
            }
        }
    } catch (e) {
        console.warn('Entity render error', e);
    }

    ctx.restore();
}

/**
 * Save camera view state to localStorage
 */
function saveTimapViewState() {
    // Debounce to avoid frequent blocking localStorage writes during pan/zoom
    if (window._saveViewStateTimer) {
        clearTimeout(window._saveViewStateTimer);
    }
    window._saveViewStateTimer = setTimeout(() => {
        const state = {
            scale: window.tilemapView.scale,
            offsetX: window.tilemapView.offsetX,
            offsetY: window.tilemapView.offsetY
        };
        try {
            localStorage.setItem('moistureFarmer_tilemapView', JSON.stringify(state));
        } catch (e) {
            // Ignore quota or security errors
        }
        window._saveViewStateTimer = null;
    }, 120);
}

/**
 * Load camera view state from localStorage
 */
function loadTimapViewState() {
    try {
        const saved = localStorage.getItem('moistureFarmer_tilemapView');
        if (saved) {
            const state = JSON.parse(saved);
            window.tilemapView.scale = state.scale || 1;
            window.tilemapView.offsetX = state.offsetX || 0;
            window.tilemapView.offsetY = state.offsetY || 0;
            return true;
        }
    } catch (e) {
        console.warn('Failed to load tilemap view state:', e);
    }
    return false;
}

/**
 * Calculate initial view - fit viewport but never exceed 100% scale
 */
function calculateInitialView() {
    // Try to load saved state first
    if (loadTimapViewState()) {
        updateWorldView();
        return;
    }
    saveTimapViewState();
}

/**
 * Initialize world view components
 */
function initializeWorldView() {
    try {
        createWorldControlsWindow();
        setupWorldLayerInteraction();

        if (window.simulationData.world && window.simulationData.world.tilemap) {
            renderWorldTilemap(window.simulationData.world.tilemap);
            updateWorldEntitiesTransform();

            // Initialize view if this is the first render
            if (!window.worldViewInitialized) {
                calculateInitialView();
                window.worldViewInitialized = true;
            }
        }
    } catch (e) { 
        console.error('World render error', e); 
    }
}

// Handle viewport resize for world canvas
window.addEventListener('resize', () => {
    if (window.simulationData.world && window.simulationData.world.tilemap) {
        renderWorldTilemap(window.simulationData.world.tilemap);
    }
});

// Export functions to global scope
window.createWorldControlsWindow = createWorldControlsWindow;
window.adjustWorldZoom = adjustWorldZoom;
window.zoomWorldAtPoint = zoomWorldAtPoint;
window.fitWorldToViewport = fitWorldToViewport;
window.centerWorldView = centerWorldView;
window.updateWorldView = updateWorldView;
window.getVisibleTileBounds = getVisibleTileBounds;
window.updateWorldEntitiesTransform = updateWorldEntitiesTransform;
window.clearEntitySelection = clearEntitySelection;
window.setupWorldLayerInteraction = setupWorldLayerInteraction;
window.renderWorldTilemap = renderWorldTilemap;
window.saveTimapViewState = saveTimapViewState;
window.loadTimapViewState = loadTimapViewState;
window.calculateInitialView = calculateInitialView;
window.initializeWorldView = initializeWorldView;
