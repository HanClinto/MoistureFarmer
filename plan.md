# MoistureFarmer - Tilemap Background Integration Plan

## Overview
Convert the existing popup tilemap window to a full-viewport background with synchronized entity positioning and a compact floating control window for zoom/pan operations.

## Final Requirements (User Clarified)

### Core Functionality
1. **World Extent**: Tilemap dimensions (width × height × 32px) define full world bounds; entities always within
2. **Future Graphics**: Design for upcoming tile spritesheet replacement (swap fillRect → drawImage)
3. **Camera Persistence**: Preserve zoom/pan state across page reloads (localStorage)
4. **Interaction Model**: 
   - Background click (< 4px movement) clears entity selection
   - Background drag pans the view
   - Entity icons remain clickable
5. **Control Window**: Small draggable Win98-style "World View" window with zoom controls
6. **Initial View**: Fill viewport but never exceed 100% scale (no upscaling)
7. **Performance**: Implement viewport culling for large maps (support 1000s of pixels)
8. **Platform**: Desktop-only (no touch/pinch support needed)
9. **Legacy Cleanup**: Remove existing tilemap popup window completely
10. **Z-Layering**: Background < entities < windows < control window
11. **Default Size**: Expand mock grid to 128×128 tiles (4096×4096 pixels)

### Entity State Management
- No existing `selectedEntity` variable found in web98 codebase
- Will introduce `window.selectedEntityId` for selection tracking
- Pan threshold: 4px movement before treating mousedown as drag vs. click

## Technical Architecture

### DOM Structure Changes
```html
<body id="desktop">
  <!-- NEW: Full-viewport world layer -->
  <div id="world-layer">
    <canvas id="world-canvas"></canvas>
    <div id="world-entities"></div>
  </div>
  
  <!-- EXISTING: All Windows 98 windows (higher z-index) -->
  <div id="simulation-control-window" class="window">...</div>
  <div id="droid-window" class="window">...</div>
  
  <!-- NEW: Floating camera controls -->
  <div id="world-controls-window" class="window draggable">...</div>
</body>
```

### CSS Architecture
```css
body#desktop { 
  position: relative; 
  overflow: hidden; 
}

#world-layer { 
  position: absolute; 
  inset: 0; 
  z-index: 0; 
}

#world-canvas { 
  position: absolute; 
  left: 0; 
  top: 0; 
  image-rendering: pixelated; 
}

#world-entities { 
  position: absolute; 
  left: 0; 
  top: 0; 
  transform-origin: 0 0; 
  pointer-events: none; 
}

.entity-icon { 
  pointer-events: auto; 
}

.window { 
  z-index: 10; 
}

#world-controls-window { 
  z-index: 20; 
  width: 160px; 
  height: 120px; 
}
```

### Camera System
```javascript
// Enhanced tilemapView state
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

// NEW: Selection state
window.selectedEntityId = null;
```

### Viewport Culling Strategy
For large tilemaps (> 256×256 tiles), implement efficient rendering:

1. **Visible Tile Calculation**:
   ```javascript
   function getVisibleTileBounds(tilemapView, canvasWidth, canvasHeight, tileSize) {
     const scale = tilemapView.scale;
     const startX = Math.floor(-tilemapView.offsetX / (tileSize * scale));
     const startY = Math.floor(-tilemapView.offsetY / (tileSize * scale));
     const endX = Math.ceil((canvasWidth - tilemapView.offsetX) / (tileSize * scale));
     const endY = Math.ceil((canvasHeight - tilemapView.offsetY) / (tileSize * scale));
     return { startX, startY, endX, endY };
   }
   ```

2. **Canvas Sizing Strategy**:
   - Canvas size = viewport dimensions (not full tilemap)
   - Render only visible tiles plus small buffer
   - Entity positions calculated relative to visible area

3. **Performance Threshold**:
   - If `tilemap.width * tilemap.height > 65536` (256×256), enable culling
   - Otherwise use full-canvas approach for simplicity

## Implementation Steps

### Phase 1: DOM/CSS Foundation
1. Add world-layer container to HTML body start
2. Add CSS rules for layering and transform behavior
3. Update entity icon creation to target #world-entities
4. Remove pointer-events: none from entity icons individually

### Phase 2: Camera Integration
1. Create `createWorldControlsWindow()` function
2. Add zoom/pan/fit controls to floating window
3. Implement viewport culling logic
4. Port existing pan/zoom handlers to world-layer
5. Add selection state management

### Phase 3: Rendering Pipeline
1. Replace `ensureTilemapWindow()` calls with direct canvas operations
2. Implement `updateWorldEntitiesTransform()` for synchronized positioning
3. Add `renderTilemap()` with culling support
4. Hook into existing `updateSimulationDisplay()` pipeline

### Phase 4: Persistence & Polish
1. Add localStorage for camera state persistence
2. Implement initial view calculation (fill without upscaling)
3. Clean up legacy tilemap window code
4. Add click vs. drag detection for selection clearing

### Phase 5: Testing & Optimization
1. Test with various tilemap sizes (small, medium, large)
2. Verify entity positioning accuracy across zoom levels
3. Validate memory usage with large maps
4. Confirm Win98 UI consistency

## Code Changes Required

### Files to Modify
- `index.html`: Add world-layer DOM structure
- `app.css`: Add layering and transform CSS
- `app.js`: Major refactoring of tilemap and entity systems

### Functions to Remove
- `ensureTilemapWindow()`
- `resizeTilemapCanvas()`
- Tilemap window resize observer code

### Functions to Add
- `createWorldControlsWindow()`
- `updateWorldEntitiesTransform()`
- `getVisibleTileBounds()`
- `saveTimapViewState()` / `loadTimapViewState()`
- `clearEntitySelection()`
- `calculateInitialView()`

### Functions to Modify
- `renderTilemap()`: Add culling support, target #world-canvas
- `updateSimulationDisplay()`: Add entity transform updates
- Entity icon creation: Target #world-entities, remove per-icon transforms
- Pan/zoom handlers: Attach to world-layer, add selection logic

## Risk Mitigation

### Performance Risks
- **Large Canvas Memory**: Mitigated by viewport culling
- **Transform Repaints**: Minimized by single container transform
- **Entity Count**: Existing entity limit should scale fine

### UX Risks  
- **Zoom Disorientation**: Mitigated by preserving camera state
- **Click vs. Drag**: 4px threshold provides good balance
- **Control Discoverability**: Draggable window maintains Win98 consistency

### Technical Risks
- **Entity Click Detection**: Careful pointer-events management
- **Z-Order Conflicts**: Clear layering strategy defined
- **Legacy Code Dependencies**: Systematic removal of tilemap window refs

## Success Criteria
- [ ] Tilemap renders as full viewport background
- [ ] Entity icons move/scale with background smoothly  
- [ ] Small control window provides zoom/pan functionality
- [ ] Camera state persists across reloads
- [ ] Large maps (128×128+) render efficiently
- [ ] Entity selection/clicking works as before
- [ ] No legacy tilemap window code remains
- [ ] Win98 aesthetic maintained throughout

## Future Enhancements
- Tile spritesheet integration (replace color fills)
- Mini-map overlay for large worlds
- Smooth zoom/pan animations
- Entity selection highlighting
- Keyboard shortcuts for camera operations
