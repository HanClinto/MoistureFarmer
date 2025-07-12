class CameraController {
    constructor(scene, camera) {
        this.scene = scene;
        this.camera = camera;
        this.isDragging = false;
        this.dragStart = { x: 0, y: 0 };
        this.cameraStart = { x: 0, y: 0 };
        this.zoomLevels = [1, 2, 3, 4, 5];
        this.currentZoomIndex = this.zoomLevels.indexOf(Math.round(camera.zoom)) || 2;
        this.lastZoomTime = 0;
        this.enable();
    }
    enable() {
        const input = this.scene.input;
        input.mouse.enabled = true;
        input.on('pointerdown', this.onPointerDown, this);
        input.on('pointerup', this.onPointerUp, this);
        input.on('pointermove', this.onPointerMove, this);
        input.on('wheel', this.onWheel, this);
    }
    onPointerDown(pointer) {
        if (pointer.rightButtonDown()) {
            this.isDragging = true;
            this.dragStart.x = pointer.x;
            this.dragStart.y = pointer.y;
            this.cameraStart.x = this.camera.scrollX;
            this.cameraStart.y = this.camera.scrollY;
        }
    }
    onPointerUp(pointer) {
        if (pointer.rightButtonReleased()) {
            this.isDragging = false;
        }
    }
    onPointerMove(pointer) {
        if (this.isDragging) {
            const dx = (pointer.x - this.dragStart.x) / this.camera.zoom;
            const dy = (pointer.y - this.dragStart.y) / this.camera.zoom;
            this.camera.scrollX = this.cameraStart.x - dx;
            this.camera.scrollY = this.cameraStart.y - dy;
        }
    }
    onWheel(pointer, gameObjects, deltaX, deltaY, deltaZ) {
        const now = this.scene.time.now;
        if (now - this.lastZoomTime < 200) return;
        this.lastZoomTime = now;
        if (deltaY > 0) {
            this.currentZoomIndex = Math.max(0, this.currentZoomIndex - 1);
        } else if (deltaY < 0) {
            this.currentZoomIndex = Math.min(this.zoomLevels.length - 1, this.currentZoomIndex + 1);
        }
        this.camera.setZoom(this.zoomLevels[this.currentZoomIndex]);
    }
}

// Export for browser global usage
window.CameraController = CameraController;
