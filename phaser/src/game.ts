import Phaser from "phaser";

class MainScene extends Phaser.Scene {
  constructor() {
    super({ key: "main" });
  }

  preload() {
    this.load.tilemapTiledJSON("map", "assets/map.json"); // loading the map
    this.load.image("tiles", "assets/tilemap.png"); // loading the tileset
  }

  create() {
    const map = this.make.tilemap({ key: "map" });
    const tileset = map.addTilesetImage("tilemap-separated-test", "tiles");
    const worldLayer = map.createLayer("Tile Layer 1", tileset!, 0, 0);
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
