import Phaser from "phaser";

class MainScene extends Phaser.Scene {
  private cursors!: Phaser.Types.Input.Keyboard.CursorKeys;
  private character!: Phaser.Physics.Arcade.Sprite;
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
    map.createLayer("Tile Layer 1", tileset!, 0, 0);
    this.character = this.physics.add.sprite(100, 100, "characters", 0);
    this.cursors = this.input.keyboard!.createCursorKeys();
  }

  update() {
    const speed = 200;

    this.character.setVelocity(0, 0);

    if (this.cursors.up?.isDown) {
      this.character.setVelocityY(-speed);
    } else if (this.cursors.down?.isDown) {
      this.character.setVelocityY(speed);
    }

    if (this.cursors.left?.isDown) {
      this.character.setVelocityX(-speed);
    } else if (this.cursors.right?.isDown) {
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
