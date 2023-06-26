import Phaser from "phaser";

class MainScene extends Phaser.Scene {
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private character!: Phaser.Physics.Arcade.Sprite;
  private mapLayer!: Phaser.Tilemaps.TilemapLayer;

  constructor() {
    super({ key: "main" });
  }

  preload() {
    this.load.tilemapTiledJSON("map", "assets/map.json"); // loading the map
    this.load.image("tiles", "assets/tilemap.png"); // loading the tileset
    this.load.spritesheet("characters", "assets/characters.png", {
      frameWidth: 16,
    });
  }

  create() {
    const map = this.make.tilemap({ key: "map" });
    const tileset = map.addTilesetImage("tilemap-separated-test", "tiles");
    this.mapLayer = map.createLayer("Tile Layer 1", tileset!, 0, 0)!;
    this.character = this.physics.add.sprite(350, 100, "characters", 0);
    this.cursors = this.input.keyboard!.createCursorKeys();
  }

  private isOnLandTile(tileX: number, tileY: number): boolean {
    const tile = this.mapLayer.getTileAt(tileX, tileY);
    if (tile) {
      // Assuming "normal land" tiles have an index of 1.
      // Change this depending on your map data.
      return tile.index === 43;
    }
    return false;
  }

  update() {
    const speed = 200;

    this.character.setVelocity(0, 0);

    const nextTileX = Math.floor(this.character.x / 16); // assuming each tile is 16 pixels
    const nextTileY = Math.floor(this.character.y / 16); // adjust this if your tiles are a different size

    if (
      this.cursors.up?.isDown &&
      this.isOnLandTile(nextTileX, nextTileY - 1)
    ) {
      this.character.setVelocityY(-speed);
    } else if (
      this.cursors.down?.isDown &&
      this.isOnLandTile(nextTileX, nextTileY + 1)
    ) {
      this.character.setVelocityY(speed);
    }

    if (
      this.cursors.left?.isDown &&
      this.isOnLandTile(nextTileX - 1, nextTileY)
    ) {
      this.character.setVelocityX(-speed);
    } else if (
      this.cursors.right?.isDown &&
      this.isOnLandTile(nextTileX + 1, nextTileY)
    ) {
      this.character.setVelocityX(speed);
    }

    this.character.body!.velocity.normalize().scale(speed);
  }
}

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 640,
  height: 640,
  physics: {
    default: "arcade",
    arcade: {
      gravity: { y: 0 },
    },
  },
  scene: [MainScene],
};

const game = new Phaser.Game(config);
