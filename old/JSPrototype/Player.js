// Player.js
// Player class for handling player logic abstraction

class Player extends MobileActor {
    constructor(scene, x, y, spriteKey) {
        super(scene, x, y, spriteKey);
    }

    // Optionally override isBlocked to block on squareMover
    isBlocked(tx, ty) {
        return this.scene.collisionManager.isBlocked(this, tx, ty);
    }
}
// Make Player available globally for index.html
window.Player = Player;
