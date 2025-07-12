// RandomMover.js
// Moves to random points within 100 squares of spawn, waits, and repeats. Avoids blocked tiles.

class RandomMover extends MobileActor {
    constructor(scene, x, y, spriteKey) {
        super(scene, x, y, spriteKey);
        this.spawnTile = this.getTilePos();
        this.waiting = false;
        this.path = [];
        this.pathIndex = 0;
        this.lastMoveTime = 0;
        this.moveCooldown = 200; // ms between moves
        this.waitAfterArrive = 1000; // ms to wait after reaching a target
        this.maxSpawnDist = 20; // squares for spawn
        this.maxRoamDist = 40; // changed from 100 to 96 for roam
        this.setRandomStart();
        this.blockedRetryCount = 0; // Track retries when blocked
    }

    getTilePos() {
        return {
            x: Math.round(this.sprite.x / 32),
            y: Math.round(this.sprite.y / 32)
        };
    }

    setRandomStart() {
        // Place within 64 squares of spawn
        let tries = 0;
        while (tries < 100) {
            const dx = Math.floor(Math.random() * this.maxSpawnDist * 2) - this.maxSpawnDist;
            const dy = Math.floor(Math.random() * this.maxSpawnDist * 2) - this.maxSpawnDist;
            const tx = this.spawnTile.x + dx;
            const ty = this.spawnTile.y + dy;
            if (!this.isBlocked(tx * 32 + 16, ty * 32 + 16)) {
                this.sprite.x = tx * 32 + 16;
                this.sprite.y = ty * 32 + 16;
                this.targetTile = { x: this.sprite.x, y: this.sprite.y };
                break;
            }
            tries++;
        }
    }

    update() {
        super.update(8 / 4);
        if (this.isMoving) return;
        if (this.isTextBubbleVisible) return; // Prevent movement while bubble is visible
        const now = Date.now();
        if (this.waiting) {
            if (now - this.lastMoveTime > this.waitAfterArrive) {
                this.waiting = false;
                // If just finished waiting after reaching goal, show bubble
                if (this.path && this.path.length === 0 && !this.isMoving) {
                    this.showTextBubble("*beep*");
                }
                this.pickNewTarget();
                this.waiting = true;
                this.lastMoveTime = now;
                return;
            }
            return;
        }
        if (this.path && this.pathIndex < this.path.length) {
            if (now - this.lastMoveTime < this.moveCooldown + (Math.random() * 200 - 100)) return;
            const next = this.path[this.pathIndex];
            this.moveToward(next);
            if (this.isMoving) {
                this.pathIndex++;
                this.lastMoveTime = now;
                this.waiting = true;
                this.waitAfterArrive = Math.random() * 200 + 100; // Short wait between steps
                this.blockedRetryCount = 0; // Reset on successful move
            } else if(this.lastMoveBlocked == true) {
                // Blocked, retry up to 3 times before aborting path
                this.blockedRetryCount = (this.blockedRetryCount || 0) + 1;
                if (this.blockedRetryCount < 3) {
                    // Wait and try again
                    this.waiting = true;
                    this.lastMoveTime = now;
                    this.waitAfterArrive = 200;
                } else {
                    // After 3 tries, abort path and pick a new one
                    this.path = [];
                    this.pathIndex = 0;
                    this.waiting = true;
                    this.lastMoveTime = now;
                    this.waitAfterArrive = 500;
                    this.blockedRetryCount = 0;
                }
            }
        } else if (!this.waiting) {
            // No path, start waiting to retry
            this.waiting = true;
            this.lastMoveTime = now;
            this.waitAfterArrive = 500;
        }
    }

    moveToward(tile) {
        const currentTileX = Math.round(this.sprite.x / 32);
        const currentTileY = Math.round(this.sprite.y / 32);
        const dx = tile.x - currentTileX;
        const dy = tile.y - currentTileY;
        if (dx === 1 && dy === 0) this.moveRight();
        else if (dx === -1 && dy === 0) this.moveLeft();
        else if (dx === 0 && dy === 1) this.moveDown();
        else if (dx === 0 && dy === -1) this.moveUp();
        else if (dx === 0 && dy === 0) console.log("Null move");
        else console.log('moveToward: not moving, not adjacent');
    }

    pickNewTarget() {
        const objects = this.scene.objects;
        let tx, ty;
        var objId = null;
        if (objects && objects.length > 0) {
            const obj = objects[Math.floor(Math.random() * (objects.length -1))];
            objId = obj;
            const objTileX = Math.floor(obj.x / 32);
            const objTileY = Math.floor(obj.y / 32);
            let found = false;
            let minDist = 1;
            while (!found && minDist < 6) {
                for (let dx = -minDist; dx <= minDist; dx++) {
                    for (let dy = -minDist; dy <= minDist; dy++) {
                        if (Math.abs(dx) !== minDist && Math.abs(dy) !== minDist) continue;
                        const txTest = objTileX + dx;
                        const tyTest = objTileY + dy;
                        if (!this.isBlocked(txTest * 32 + 16, tyTest * 32 + 16)) {
                            tx = txTest;
                            ty = tyTest;
                            found = true;
                            break;
                        }
                    }
                    if (found) break;
                }
                minDist++;
            }
            if (!found) {
                let tries = 0;
                while (tries < 100) {
                    const dx = Math.floor(Math.random() * this.maxRoamDist * 2) - this.maxRoamDist;
                    const dy = Math.floor(Math.random() * this.maxRoamDist * 2) - this.maxRoamDist;
                    tx = this.spawnTile.x + dx;
                    ty = this.spawnTile.y + dy;
                    if (!this.isBlocked(tx * 32 + 16, ty * 32 + 16)) break;
                    tries++;
                }
                if (tries >= 100) {
                    console.log("Failed to find unblocked target");
                    return;
                }
            }
        } else {
            let tries = 0;
            while (tries < 100) {
                const dx = Math.floor(Math.random() * this.maxRoamDist * 2) - this.maxRoamDist;
                const dy = Math.floor(Math.random() * this.maxRoamDist * 2) - this.maxRoamDist;
                tx = this.spawnTile.x + dx;
                ty = this.spawnTile.y + dy;
                if (!this.isBlocked(tx * 32 + 16, ty * 32 + 16)) break;
                tries++;
            }
            if (tries >= 100) {
                console.log("Failed to find unblocked target");
                return;
            }
        }
        const start = this.getTilePos();
        const goal = { x: tx, y: ty };
        this.scene.collisionManager.findPathWithEasyStar(start, goal, (path) => {
            this.blockedRetryCount = 0;
            if (path && path.length > 0) {
                this.path = path;
                this.pathIndex = 1;
                this.waiting = false;
                this.waitAfterArrive = 1000;
            } else {
                this.showTextBubble("*boop*");
                this.waiting = true;
                this.lastMoveTime = Date.now();
                this.waitAfterArrive = 500;
                console.log("No path found, waiting to retry");
            }
        });
    }

    isBlocked(tx, ty) {
        return this.scene.collisionManager.isBlocked(this, tx, ty);
    }
}

window.RandomMover = RandomMover;
