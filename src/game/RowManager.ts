import { type CellType } from "./types";

import { generateValidRow } from "./PatternGenerator";

export interface ActiveRow {
  id: number;
  y: number;
  cells: CellType[];
  patternName: string;
}

export class RowManager {
  private rows: ActiveRow[] = [];

  private nextId = 0;

  private rowSpacing = 180;

  // TODO increase difficulty based on speed
  private speed = 180;
  private difficulty = 1;

  private safeLanes = [0, 1, 2, 3, 4];

  initialize() {
    this.rows = [];

    this.safeLanes = [0, 1, 2, 3, 4];

    /*
    * Generate enough rows to
    * fill the initial game world.
    */
    for (let i = 0; i < 8; i++) {
      this.spawnRow(-100 - (i * this.rowSpacing));
    }
  }

  update(deltaTime: number) {
    for (const row of this.rows) {
      row.y += this.speed * deltaTime;
    }

    this.removeOldRows();

    this.spawnMissingRows();
  }

  private spawnRow(y: number) {
    const generated = generateValidRow(this.safeLanes, this.difficulty);

    const safeLanes = generated.cells
      .map((cell, index) => (cell !== "obstacle" ? index : -1))
      .filter((lane) => lane !== -1);

    this.rows.push({
      id: this.nextId++,

      y,

      cells: generated.cells,

      patternName: generated.patternName,
    });

    this.safeLanes = safeLanes;
  }

  private removeOldRows() {
    this.rows = this.rows.filter((row) => row.y < 900);
  }

  private spawnMissingRows() {
    if (this.rows.length === 0) {
      this.spawnRow(-this.rowSpacing);

      return;
    }

    let highestY = Math.min(...this.rows.map((row) => row.y));

    while (highestY > -this.rowSpacing * 2) {
      highestY -= this.rowSpacing;

      this.spawnRow(highestY);
    }
  }

  getRows() {
    return [...this.rows];
  }

  setDifficulty(difficulty: number) {
    this.difficulty = difficulty;
  }

  setSpeed(speed: number) {
    this.speed = speed;
  }
}
