// CollisionManager.js
// Handles collision logic between mobile actors (player, NPCs, etc.)

class CollisionManager {
    constructor(scene, options = {}) {
        this.scene = scene;
        this.blockTileIds = options.blockTileIds || [];
        this.layers = options.layers || [];
        this.easyStar = null;
        this.easyStarGrid = null;
    }

    // Returns true if any actor would block movement to (tx, ty) for the given actor
    isBlocked(actor, tx, ty) {
        // Check for tile-based blocking
        if (this.isTileBlocked(tx, ty)) return true;

        // Check for other mobile actors
        let actors = [this.scene.player];
        if (Array.isArray(this.scene.randomMovers)) {
            actors = actors.concat(this.scene.randomMovers);
        } else if (this.scene.randomMover) {
            actors.push(this.scene.randomMover);
        }
        for (const other of actors) {
            if (!other || other === actor) continue;
            // Block if other actor is at or moving to the target tile
            const ox = Math.round(other.sprite.x);
            const oy = Math.round(other.sprite.y);
            const otx = Math.round(other.targetTile.x);
            const oty = Math.round(other.targetTile.y);
            if ((Math.round(tx) === ox && Math.round(ty) === oy) ||
                (other.isMoving && Math.round(tx) === otx && Math.round(ty) === oty)) {
                return true;
            }
            // Block if other actor is blocked by this actor and is trying to move into this actor's tile
            if (!other.isMoving && Math.round(tx) === otx && Math.round(ty) === oty) {
                return true;
            }
        }
        return false;
   }

    // Returns the actor blocking movement to (tx, ty), or null if none. Ignores self.
    getBlockingActor(actor, tx, ty) {
        let actors = [this.scene.player];
        if (Array.isArray(this.scene.randomMovers)) {
            actors = actors.concat(this.scene.randomMovers);
        } else if (this.scene.randomMover) {
            actors.push(this.scene.randomMover);
        }
        for (const other of actors) {
            if (!other || other === actor) continue;
            const ox = Math.round(other.sprite.x);
            const oy = Math.round(other.sprite.y);
            const otx = Math.round(other.targetTile.x);
            const oty = Math.round(other.targetTile.y);
            if ((Math.round(tx) === ox && Math.round(ty) === oy) ||
                (other.isMoving && Math.round(tx) === otx && Math.round(ty) === oty)) {
                return other;
            }
            if (!other.isMoving && Math.round(tx) === otx && Math.round(ty) === oty) {
                return other;
            }
        }
        return null;
    }

    // Checks if a tile is blocked by any of the configured layers and blockTileIds
    isTileBlocked(tx, ty) {
        const tileX = Math.ceil(tx / 32) - 1;
        const tileY = Math.ceil(ty / 32) - 1;
        for (const layer of this.layers) {
            if (!layer) continue;
            const tile = layer.getTileAt(tileX, tileY);
            if (tile && this.blockTileIds.includes(parseInt(tile.index) - 1)) {
                return true;
            }
        }
        return false;
    }

    setupEasyStar() {
        if (this.easyStar) return;
        const layers = this.layers;
        const width = layers[0].layer.width;
        const height = layers[0].layer.height;
        const grid = [];
        for (let y = 0; y < height; y++) {
            const row = [];
            for (let x = 0; x < width; x++) {
                let blocked = false;
                for (const layer of layers) {
                    if (!layer) continue;
                    const tile = layer.getTileAt(x, y);
                    if (tile && this.blockTileIds.includes(parseInt(tile.index) - 1)) {
                        blocked = true;
                        break;
                    }
                }
                row.push(blocked ? 1 : 0);
            }
            grid.push(row);
        }
        this.easyStarGrid = grid;
        this.easyStar = new EasyStar.js();
        this.easyStar.setGrid(grid);
        this.easyStar.setAcceptableTiles([0]);
    }

    findPathWithEasyStar(start, goal, callback) {
        this.setupEasyStar();
        this.easyStar.findPath(start.x, start.y, goal.x, goal.y, callback);
        this.easyStar.calculate();
    }
}

window.CollisionManager = CollisionManager;
