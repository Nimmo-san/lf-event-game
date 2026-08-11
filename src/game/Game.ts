import { Player } from "./Player";

import { RowManager } from "./RowManager";

import { getPlayerSession } from "../services/playerSession";
import { saveGameResult } from "../storage/gameSessions";

import { detectRowCollision } from "./CollisionSystem";

import { type GameSizes } from "./SpriteSizing";
import { syncGameResults } from "../storage/syncGameResults";

export type GameStatus = "ready" | "playing" | "gameover";
export type GameEffect = "none" | "lightning" | "collision";
export type GameEndReason = "collision" | "timeout" | null;

export interface GameFeedback {
  effect: GameEffect;
  timer: number;
}

// Round length — imported by StartScreen/GameCanvas so copy and
// countdowns stay in sync with what's actually enforced here.
export const ROUND_DURATION = 120; // seconds

const COLLISION_EFFECT_DURATION = 120;
const LIGHTNING_EFFECT_DURATION = 250;

// Scoring
const SURVIVAL_RATE = 12; // points per second alive
const LIGHTNING_BASE_SCORE = 50; // points per bolt before combo
const COMBO_STEP = 0.25; // multiplier gained per consecutive bolt
const COMBO_MAX_MULTIPLIER = 3; // multiplier ceiling

// Difficulty ramp
const BASE_ROW_SPEED = 250; // must match RowManager's own default
const DIFFICULTY_RAMP_INTERVAL = 7; // seconds between speed increases
const DIFFICULTY_RAMP_FACTOR = 1.12; // multiplier growth per tick
const DIFFICULTY_MAX_MULTIPLIER = 3; // ceiling so it doesn't spiral
const PATTERN_DIFFICULTY_MAX = 3; // matches RowManager/PatternGenerator's top tier

export class Game {
  readonly player = new Player();

  readonly rowManager = new RowManager();

  status: GameStatus = "ready";

  score = 0;
  elapsedTime = 0;

  lightning = 0;

  // Set in finishGame() — the ID of the result just
  // saved, so the UI can reference this exact round
  // (e.g. for a leaderboard submission) without
  // regenerating or guessing an ID.
  resultId: string | null = null;

  // Why the round ended — lets the UI show a different message
  // for "you survived the full 120s" vs "you crashed".
  endReason: GameEndReason = null;

  // Consecutive bolts collected this run (never resets mid-run,
  // since a collision ends the run outright).
  combo = 0;
  comboMultiplier = 1;

  // Difficulty ramp — grows every DIFFICULTY_RAMP_INTERVAL seconds,
  // pushed into RowManager.
  speedMultiplier = 1;
  patternDifficulty = 1;
  private timeSinceLastRamp = 0;
  private rampTickCount = 0;

  feedback: GameFeedback = {
    effect: "none",
    timer: 0,
  };

  start() {
    this.score = 0;
    this.elapsedTime = 0;

    this.lightning = 0;

    this.resultId = null;
    this.endReason = null;

    this.combo = 0;
    this.comboMultiplier = 1;

    this.speedMultiplier = 1;
    this.patternDifficulty = 1;
    this.timeSinceLastRamp = 0;
    this.rampTickCount = 0;

    this.feedback = {
      effect: "none",
      timer: 0,
    };

    this.player.lane = 2;
    this.player.x = 50;

    this.rowManager.initialize();

    // RowManager is reused across rounds — without this, a
    // replay would silently inherit whatever speed/difficulty
    // the previous round had ramped up to.
    this.rowManager.setSpeed(BASE_ROW_SPEED);
    this.rowManager.setDifficulty(1);

    this.status = "playing";
  }

  update(
    deltaTime: number,
    canvasWidth: number,
    canvasHeight: number,
    sizes: GameSizes,
  ) {
    // Always update visual effects
    if (this.feedback.timer > 0) {
      this.feedback.timer -= deltaTime;

      if (this.feedback.timer <= 0) {
        this.feedback = {
          effect: "none",
          timer: 0,
        };
      }
    }

    // Stop game logic after game over
    if (this.status !== "playing") {
      return;
    }

    this.elapsedTime += deltaTime;

    if (this.elapsedTime >= ROUND_DURATION) {
      this.elapsedTime = ROUND_DURATION;

      this.finishGame("timeout");

      return;
    }

    // Survival trickle — score climbs just for staying alive.
    this.score += SURVIVAL_RATE * deltaTime;

    // Difficulty ramp — every DIFFICULTY_RAMP_INTERVAL seconds,
    // bump speedMultiplier and push it into RowManager
    this.timeSinceLastRamp += deltaTime;

    if (this.timeSinceLastRamp >= DIFFICULTY_RAMP_INTERVAL) {
      this.timeSinceLastRamp -= DIFFICULTY_RAMP_INTERVAL;
      this.rampTickCount += 1;

      this.speedMultiplier = Math.min(
        DIFFICULTY_MAX_MULTIPLIER,
        this.speedMultiplier * DIFFICULTY_RAMP_FACTOR,
      );

      this.rowManager.setSpeed(BASE_ROW_SPEED * this.speedMultiplier);

      // Pattern complexity escalates slower than speed — only
      // every other ramp tick, since it's a discrete 1/2/3 tier
      // system rather than a smooth multiplier.
      if (
        this.rampTickCount % 2 === 0 &&
        this.patternDifficulty < PATTERN_DIFFICULTY_MAX
      ) {
        this.patternDifficulty += 1;

        this.rowManager.setDifficulty(this.patternDifficulty);
      }
    }

    this.player.update(deltaTime);
    this.rowManager.update(deltaTime);

    this.checkCollisions(canvasWidth, canvasHeight, sizes);
  }

  private checkCollisions(
    canvasWidth: number,
    canvasHeight: number,
    sizes: GameSizes,
  ) {
    const playerHitbox = this.player.getHitbox(
      canvasWidth,
      canvasHeight,
      sizes.sprites.plane,
      sizes.hitboxes.plane,
    );

    const rows = this.rowManager.getRows();

    for (const row of rows) {
      const collision = detectRowCollision(
        playerHitbox,
        row.cells,
        row.y,
        canvasWidth,
        sizes.hitboxes.obstacle,
        sizes.hitboxes.lightning,
      );

      if (collision.type === "obstacle") {
        this.triggerEffect("collision", COLLISION_EFFECT_DURATION);
        this.finishGame("collision");

        return;
      }

      if (collision.type === "lightning") {
        this.lightning += 1;

        this.combo += 1;
        this.comboMultiplier = Math.min(
          COMBO_MAX_MULTIPLIER,
          1 + this.combo * COMBO_STEP,
        );

        this.score += LIGHTNING_BASE_SCORE * this.comboMultiplier;

        this.triggerEffect("lightning", LIGHTNING_EFFECT_DURATION);

        // remove the lightning so it cant be collected multiple times
        if (collision.lane !== null) {
          row.cells[collision.lane] = "empty";
        }
      }
    }
  }

  private finishGame(reason: "collision" | "timeout") {
    const session = getPlayerSession();

    if (!session) {
      console.error("No player session found.");
      return;
    }
    const result = {
      id: crypto.randomUUID(),

      playerId: session.playerId,
      playerName: session.playerName,
      companyName: session.companyName,

      score: Math.round(this.score),

      lightning: this.lightning,

      duration: this.elapsedTime,

      createdAt: Date.now(),

      synced: false,
    };

    this.resultId = result.id;
    this.endReason = reason;

    void saveGameResult(result);
    void syncGameResults();
    this.status = "gameover";
  }

  private triggerEffect(effect: GameEffect, duration: number) {
    this.feedback = {
      effect,
      timer: duration,
    };
  }
}
