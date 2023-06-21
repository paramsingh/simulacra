import Phaser from "phaser";

class MainScene extends Phaser.Scene {
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
    this.add.sprite(300, 100, "characters", 0); // the last parameter is the index of the character in the spritesheet
  }
}

const config: Phaser.Types.Core.GameConfig = {
  type: Phaser.AUTO,
  width: 640,
  height: 640,
  physics: {
    default: "arcade",
    arcade: {
      gravity: { y: 200 },
    },
  },
  scene: [MainScene],
};

const game = new Phaser.Game(config);
