// MobileActor.js
// Base class for mobile actors (player, NPCs) with tile movement and blocker logic

class MobileActor {
    constructor(scene, x, y, spriteKey) {
        this.scene = scene;
        this.sprite = scene.add.sprite(x, y, spriteKey, 0);
        this.sprite.setOrigin(0.5, 0.5);
        this.sprite.setDepth(5);
        this.direction = 0; // 0: down, 1: right, 2: left, 3: up
        this.isMoving = false;
        this.targetTile = { x, y };
        this.isBumping = false;
        this.lastMoveBlocked = false; // Track if last move was blocked
        this.textBubble = null;
        this.textBubbleTimer = null;
        this.isTextBubbleVisible = false;
        this.onBump = () => { this.showTextBubble("*beep boop*"); };
        this.onBumpedByOther = () => { this.showTextBubble("*awooow*"); };
    }

    moveLeft() {
        this._tryMove(-32, 0, 2);
    }
    moveRight() {
        this._tryMove(32, 0, 1);
    }
    moveUp() {
        this._tryMove(0, -32, 3);
    }
    moveDown() {
        this._tryMove(0, 32, 0);
    }

    _tryMove(dx, dy, dir) {
        if (this.isMoving || this.isBumping) return;
        const tx = this.sprite.x + dx;
        const ty = this.sprite.y + dy;
        const blockingActor = this.scene.collisionManager.getBlockingActor(this, tx, ty);
        if (this.isBlocked(tx, ty)) {
            this.lastMoveBlocked = true;
            this._bump(dir, dx, dy, blockingActor);
            return;
        }
        this.lastMoveBlocked = false;
        this.direction = dir;
        this.sprite.setFrame(dir);
        this.targetTile = { x: tx, y: ty };
        this.isMoving = true;
    }

    isBlocked(tx, ty) {
        // Use collision manager and pass self to ignore self in collision checks
        return this.scene.collisionManager.isBlocked(this, tx, ty);
    }

    showTextBubble(message) {
        if (this.textBubble) {
            this.textBubble.destroy();
            this.textBubble = null;
        }
        // Create a Phaser text object above the sprite
        this.textBubble = this.scene.add.text(
            this.sprite.x,
            this.sprite.y - this.sprite.height / 2 - 16, // above head
            message,
            {
                font: '8px Arial',
                fill: '#fff',
                backgroundColor: 'rgba(0,0,0,0.7)',
                padding: { x: 6, y: 2 },
                align: 'center',
                borderRadius: 6,
                wordWrap: { width: 120, useAdvancedWrap: true }
            }
        ).setOrigin(0.5, 1);
        this.textBubble.setDepth(1000); // Ensure above all layers
        this.isTextBubbleVisible = true;
        // Hide after 250ms
        if (this.textBubbleTimer) clearTimeout(this.textBubbleTimer);
        this.textBubbleTimer = setTimeout(() => {
            if (this.textBubble) {
                this.textBubble.destroy();
                this.textBubble = null;
            }
            this.isTextBubbleVisible = false;
        }, 1000);
    }

    update(speed = 8) {
        // Prevent movement while text bubble is visible
        if (this.isTextBubbleVisible) return;
        if (this.isMoving) {
            const dx = this.targetTile.x - this.sprite.x;
            const dy = this.targetTile.y - this.sprite.y;
            if (Math.abs(dx) <= speed && Math.abs(dy) <= speed) {
                this.sprite.x = this.targetTile.x;
                this.sprite.y = this.targetTile.y;
                this.isMoving = false;
            } else {
                this.sprite.x += Math.sign(dx) * Math.min(Math.abs(dx), speed);
                this.sprite.y += Math.sign(dy) * Math.min(Math.abs(dy), speed);
            }
            if (this.textBubble) {
                // Keep bubble above head as we move
                this.textBubble.x = this.sprite.x;
                this.textBubble.y = this.sprite.y - this.sprite.height / 2 - 16;
            }
        }
    }

    _bump(dir, dx, dy, blockingActor = null) {
        if (this.isBumping) return;
        this.isBumping = true;
        this.direction = dir;
        this.sprite.setFrame(dir);
        const bumpDistance = 8;
        let bumpX = 0, bumpY = 0;
        if (dir === 0) bumpY = bumpDistance;
        else if (dir === 1) bumpX = bumpDistance;
        else if (dir === 2) bumpX = -bumpDistance;
        else if (dir === 3) bumpY = -bumpDistance;
        const originalX = this.sprite.x;
        const originalY = this.sprite.y;
        this.scene.tweens.add({
            targets: this.sprite,
            x: originalX + bumpX,
            y: originalY + bumpY,
            duration: 60,
            yoyo: true,
            repeat: 0,
            onComplete: () => {
                this.isBumping = false;
                this.sprite.x = originalX;
                this.sprite.y = originalY;
            }
        });
        if (blockingActor) {
            if (typeof this.onBump === 'function') this.onBump(blockingActor);
            if (typeof blockingActor.onBumpedByOther === 'function') blockingActor.onBumpedByOther(this);
        } else {
            if (typeof this.onBump === 'function') this.onBump();
        }
    }
}

window.MobileActor = MobileActor;
