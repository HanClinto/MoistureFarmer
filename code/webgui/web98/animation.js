// animation.js - Movement tween and entity animation functionality

// Movement tween configuration & state
if (typeof window.MOVE_TWEEN_MS === 'undefined') window.MOVE_TWEEN_MS = 100; // ms between tile centers
if (typeof window._entityTweenState === 'undefined') window._entityTweenState = {}; // id -> tween state
if (typeof window._entityTweenAnimRunning === 'undefined') window._entityTweenAnimRunning = false;

/**
 * Ensure the tween animation loop is running
 */
function _ensureTweenLoop() {
    if (window._entityTweenAnimRunning) return;
    window._entityTweenAnimRunning = true;
    const step = (now) => {
        try { 
            _updateEntityTweenPositions(now); 
        } catch(e) { 
            /* keep loop alive */ 
        }
        requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

/**
 * Update entity tween positions for smooth movement animation
 * @param {number} nowTs - Current timestamp
 */
function _updateEntityTweenPositions(nowTs) {
    const state = window._entityTweenState;
    for (const id in state) {
        const s = state[id];
        if (!s) continue;
        const dur = window.MOVE_TWEEN_MS || 100;
        const t = Math.min(1, (nowTs - s.moveStart) / dur);
        const ix = s.prevX + (s.targetX - s.prevX) * t;
        const iy = s.prevY + (s.targetY - s.prevY) * t;
        s.interpX = ix;
        s.interpY = iy;
        s.progress = t;
        if (window.DEBUG_LOG_TWEEN && (t === 1 || t === 0)) {
            console.log('[tween]', id, 'progress', t.toFixed(2), 'pos', ix, iy);
        }
    }
    // Re-render world if tilemap exists
    if (window.simulationData && window.simulationData.world && window.simulationData.world.tilemap) {
        try { 
            if (typeof renderWorldTilemap === 'function') {
                renderWorldTilemap(window.simulationData.world.tilemap); 
            }
        } catch(e) {}
    }
}

/**
 * Update entity tween state for smooth movement
 * @param {Object} entity - Entity object with id and location
 */
function updateEntityTweenState(entity) {
    const tweenState = window._entityTweenState;
    const tileSize = 32;
    const targetX = entity.location.x * tileSize;
    const targetY = entity.location.y * tileSize;
    let st = tweenState[entity.id];
    const now = performance.now();
    
    if (!st) {
        // First time: no tween, start at target
        st = tweenState[entity.id] = { 
            prevX: targetX, 
            prevY: targetY, 
            targetX, 
            targetY, 
            moveStart: now, 
            interpX: targetX, 
            interpY: targetY, 
            progress: 1 
        };
    } else {
        // Determine if teleport (delta > 1 tile)
        const dxTiles = Math.abs((targetX - st.targetX) / tileSize);
        const dyTiles = Math.abs((targetY - st.targetY) / tileSize);
        const teleport = dxTiles > 1 || dyTiles > 1;
        
        // Capture in-flight position for smooth chaining
        if (st.progress !== 1) {
            const dur = window.MOVE_TWEEN_MS || 100;
            const t = Math.min(1, (now - st.moveStart) / dur);
            const curX = st.prevX + (st.targetX - st.prevX) * t;
            const curY = st.prevY + (st.targetY - st.prevY) * t;
            st.prevX = curX;
            st.prevY = curY;
        } else {
            // Previous tween completed, start from last target
            st.prevX = st.targetX;
            st.prevY = st.targetY;
        }
        
        st.targetX = targetX;
        st.targetY = targetY;
        st.moveStart = now;
        st.progress = teleport ? 1 : 0;
        
        if (teleport) {
            st.prevX = targetX;
            st.prevY = targetY;
            st.interpX = targetX;
            st.interpY = targetY;
        }
    }
}

/**
 * Start the tween animation loop
 */
function startTweenAnimation() {
    _ensureTweenLoop();
}

// Export functions to global scope for compatibility
window._ensureTweenLoop = _ensureTweenLoop;
window._updateEntityTweenPositions = _updateEntityTweenPositions;
window.updateEntityTweenState = updateEntityTweenState;
window.startTweenAnimation = startTweenAnimation;
