<script setup lang="ts">
import {
    onMounted,
    onBeforeUnmount,
    ref,
} from "vue"

import { Game, ROUND_DURATION } from "../game/Game"

import {
    PLAYER_BOTTOM_MARGIN_MULTIPLIER,
} from "../game/Player"

import {
    SpriteRenderer,
} from "../game/SpriteRenderer"

import {
    getGameSizes,
    getSpriteSizes,
} from "../game/SpriteSizing"

import {
    getPlayerSession,
} from "../services/playerSession"

import LeaderboardEntry from "./LeaderboardEntry.vue"

const canvas =
    ref<HTMLCanvasElement | null>(
        null,
    )

let resizeObserver:
    ResizeObserver | null =
    null

const spriteRenderer = new SpriteRenderer()

const playerSession = getPlayerSession()

const gameOver =
    ref(false)

const showLeaderboard =
    ref(false)

const score =
    ref(0)

const lightning =
    ref(0)

const comboMultiplier =
    ref(1)

const timeRemaining =
    ref(ROUND_DURATION)

const game = new Game()

let animationFrame = 0

let lastTime = 0

let running = false

const shakeAmount =
    ref(0)

const shakeX =
    ref(0)

const shakeY =
    ref(0)

// Reflects the device's primary input mechanism, not just
// raw touch hardware — a laptop with a touchscreen still
// reports false here, which is the right call for a "which
// controls apply" decision, not just "is touch possible".
const isTouchDevice =
    window.matchMedia(
        "(pointer: coarse)",
    ).matches

function resizeCanvas() {
    const element =
        canvas.value

    if (!element) {
        return
    }

    const rect =
        element.getBoundingClientRect()

    const width =
        Math.max(
            1,
            Math.floor(
                rect.width,
            ),
        )

    const height =
        Math.max(
            1,
            Math.floor(
                rect.height,
            ),
        )

    const pixelRatio =
        Math.min(
            window.devicePixelRatio ||
            1,
            2,
        )

    element.width =
        Math.floor(
            width *
            pixelRatio,
        )

    element.height =
        Math.floor(
            height *
            pixelRatio,
        )

    const context =
        element.getContext(
            "2d",
        )

    if (!context) {
        return
    }

    context.setTransform(
        pixelRatio,
        0,
        0,
        pixelRatio,
        0,
        0,
    )
}

function draw(
    context: CanvasRenderingContext2D,
    width: number,
    height: number,
) {

    const spriteSizes =
        getSpriteSizes(
            width,
            height,
        )
    /*
     * Background
     */
    context.clearRect(
        0,
        0,
        width,
        height,
    )

    const gradient =
        context.createLinearGradient(
            0,
            0,
            0,
            height,
        )

    gradient.addColorStop(
        0,
        "#12131f",
    )

    gradient.addColorStop(
        1,
        "#07070c",
    )

    context.fillStyle =
        gradient

    context.fillRect(
        0,
        0,
        width,
        height,
    )

    /*
     * Game dimensions
     */
    const laneWidth =
        width / 5

    /*
     * Subtle lane guides
     */
    context.strokeStyle =
        "rgba(255,255,255,0.05)"

    context.lineWidth = 1

    for (
        let i = 1;
        i < 5;
        i++
    ) {
        const x =
            laneWidth * i

        context.beginPath()

        context.moveTo(
            x,
            0,
        )

        context.lineTo(
            x,
            height,
        )

        context.stroke()
    }

    /*
     * Rows
     */
    const rows =
        game.rowManager.getRows()

    for (
        const row of rows
    ) {
        drawRow(
            context,
            row,
            laneWidth,
            height,
            spriteSizes,
        )
    }

    /*
     * Player
     */
    drawPlayer(
        context,
        width,
        height,
        spriteSizes,
    )
}

function drawRow(
    context: CanvasRenderingContext2D,
    row: any,
    laneWidth: number,
    height: number,
    spriteSizes: any,
) {
    /*
     * Convert our game-space Y
     * into canvas space.
     */
    const y =
        row.y

    if (
        y < -100 ||
        y > height + 100
    ) {
        return
    }

    for (
        let lane = 0;
        lane < 5;
        lane++
    ) {
        const cell =
            row.cells[lane]

        const x =
            lane *
            laneWidth +
            laneWidth /
            2

        if (
            cell ===
            "obstacle"
        ) {
            spriteRenderer.draw(
                context,
                "obstacle",
                x,
                y,
                spriteSizes.obstacle,
                spriteSizes.obstacle,
            )
        }

        if (
            cell ===
            "lightning"
        ) {
            spriteRenderer.draw(
                context,
                "lightning",
                x,
                y,
                spriteSizes.lightning,
                spriteSizes.lightning,
            )
        }
    }
}

function drawPlayer(
    context: CanvasRenderingContext2D,
    width: number,
    height: number,
    spriteSizes: any,
) {
    const x =
        (
            game.player.x /
            100
        ) *
        width

    const y =
        height -
        spriteSizes.plane *
        PLAYER_BOTTOM_MARGIN_MULTIPLIER
    const collisionActive =
        game.feedback.effect ===
        "collision"

    if (
        collisionActive
    ) {
        const progress =
            game.feedback.timer /
            650

        context.save()

        context.globalAlpha =
            Math.min(
                0.75,
                progress,
            )

        context.fillStyle =
            "#ff5c6c"

        context.beginPath()

        context.arc(
            x,
            y,
            spriteSizes.plane *
            0.55,
            0,
            Math.PI * 2,
        )

        context.fill()

        context.restore()
    }

    if (
        collisionActive
    ) {
        context.save()

        context.shadowColor =
            "rgba(255, 92, 108, 0.95)"

        context.shadowBlur = 25

        context.globalAlpha =
            0.9
    }

    spriteRenderer.draw(
        context,
        "plane",
        x,
        y,
        spriteSizes.plane,
        spriteSizes.plane,
    )

    if (
        collisionActive
    ) {
        context.restore()
    }

    if (
        game.feedback.effect ===
        "lightning"
    ) {
        const progress =
            1 -
            game.feedback.timer /
            450

        const radius =
            spriteSizes.plane *
            (
                0.5 +
                progress
            )

        context.save()

        context.globalAlpha =
            1 - progress

        context.strokeStyle =
            "#92c13b"

        context.lineWidth = 3

        context.beginPath()

        context.arc(
            x,
            y,
            radius,
            0,
            Math.PI * 2,
        )

        context.stroke()

        context.restore()
    }

    // debugging lines for collision
    // context.strokeStyle =
    //     "#ff4444"

    // context.lineWidth = 2

    // const hitboxSize =
    //     sizes.hitboxes.plane

    // context.strokeRect(
    //     -hitboxSize / 2,
    //     -hitboxSize / 2,
    //     hitboxSize,
    //     hitboxSize,
    // )
}

function update(
    deltaTime: number,
) {
    const element =
        canvas.value

    if (!element) {
        return
    }

    const rect =
        canvas.value
            ?.getBoundingClientRect()

    if (!rect) {
        return
    }

    const width =
        rect.width

    const height =
        rect.height

    const sizes =
        getGameSizes(
            width,
            height,
        )

    game.update(
        deltaTime,
        width,
        height,
        sizes,
    )
}

function gameLoop(
    timestamp: number,
) {
    if (!running) {
        return
    }

    const deltaTime =
        Math.min(
            (
                timestamp -
                lastTime
            ) /
            1000,
            0.05,
        )

    lastTime =
        timestamp

    update(
        deltaTime,
    )

    gameOver.value =
        game.status ===
        "gameover"

    score.value =
        Math.round(
            game.score,
        )

    lightning.value =
        game.lightning

    comboMultiplier.value =
        game.comboMultiplier

    timeRemaining.value =
        Math.max(
            0,
            Math.ceil(
                ROUND_DURATION -
                game.elapsedTime,
            ),
        )
    const element =
        canvas.value

    if (element) {
        const context =
            element.getContext(
                "2d",
            )

        if (context) {
            const rect =
                element.getBoundingClientRect()

            draw(
                context,
                rect.width,
                rect.height,
            )
        }
    }

    if (
        game.feedback.effect ===
        "collision"
    ) {
        const progress =
            game.feedback.timer /
            650

        shakeAmount.value =
            Math.max(
                0,
                progress,
            ) * 8
    } else {
        shakeAmount.value = 0
    }

    if (
        game.feedback.effect ===
        "collision"
    ) {
        const intensity =
            Math.min(
                8,
                game.feedback.timer /
                650 *
                8,
            )

        shakeX.value =
            (
                Math.random() -
                0.5
            ) *
            intensity

        shakeY.value =
            (
                Math.random() -
                0.5
            ) *
            intensity
    } else {
        shakeX.value = 0
        shakeY.value = 0
    }

    animationFrame =
        requestAnimationFrame(
            gameLoop,
        )
}

function moveLeft() {
    game.player.moveLeft()
}

function moveRight() {
    game.player.moveRight()
}

function handleKeyDown(
    event: KeyboardEvent,
) {
    if (
        event.key ===
        "ArrowLeft"
    ) {
        moveLeft()
    }

    if (
        event.key ===
        "ArrowRight"
    ) {
        moveRight()
    }
}

function handleTouchStart(
    event: TouchEvent,
) {
    const element =
        canvas.value

    if (!element) {
        return
    }

    const touch =
        event.touches[0]

    if (!touch) {
        return
    }

    // Prevents this from also firing a synthetic mouse/click
    // event afterward, and blocks any default gesture the
    // browser might otherwise try (double-tap zoom, etc.) —
    // "touch-action: none" on the canvas handles most of this.
    event.preventDefault()

    const rect =
        element.getBoundingClientRect()

    const tapX =
        touch.clientX -
        rect.left

    if (
        tapX <
        rect.width / 2
    ) {
        moveLeft()
    } else {
        moveRight()
    }
}

onMounted(async () => {
    await spriteRenderer.preload()

    game.start()

    resizeCanvas()

    const element =
        canvas.value

    if (element) {
        resizeObserver =
            new ResizeObserver(
                () => {
                    resizeCanvas()
                },
            )

        resizeObserver.observe(
            element,
        )
    }

    window.addEventListener(
        "keydown",
        handleKeyDown,
    )

    if (element && isTouchDevice) {
        // passive: false is required — the handler calls
        // preventDefault(), which browsers ignore on passive
        // listeners (the default for touchstart).
        element.addEventListener(
            "touchstart",
            handleTouchStart,
            { passive: false },
        )
    }

    running = true

    lastTime =
        performance.now()

    animationFrame =
        requestAnimationFrame(
            gameLoop,
        )
})

onBeforeUnmount(() => {
    running = false

    cancelAnimationFrame(
        animationFrame,
    )

    resizeObserver?.disconnect()

    window.removeEventListener(
        "keydown",
        handleKeyDown,
    )

    canvas.value?.removeEventListener(
        "touchstart",
        handleTouchStart,
    )
})

function restart() {
    game.start()

    gameOver.value =
        false

    showLeaderboard.value =
        false

    timeRemaining.value =
        ROUND_DURATION
}
</script>

<template>
    <div class="game-wrapper" :class="{
        'collision-active':
            game.feedback.effect ===
            'collision',

        'lightning-active':
            game.feedback.effect ===
            'lightning',
    }" :style="{
        '--shake-x': `${shakeX}px`,
        '--shake-y': `${shakeY}px`,
    }">
        <canvas ref="canvas" class="game-canvas" />

        <div class="hud-readout" aria-hidden="true">
            <div class="hud-readout-group">

                <span class="hud-readout-item">
                    <i class="hud-dot"></i>
                    SCORE
                    <strong>{{ score }}</strong>
                </span>

                <span class="hud-readout-item" :class="{ 'hud-readout-item--urgent': timeRemaining <= 10 }">
                    ⏱
                    <strong>{{ timeRemaining }}s</strong>
                </span>

            </div>

            <div class="hud-readout-group">

                <span v-if="comboMultiplier > 1" class="hud-readout-item hud-readout-item--cyan">
                    COMBO
                    <strong>×{{ comboMultiplier.toFixed(2) }}</strong>
                </span>

                <span class="hud-readout-item hud-readout-item--volt">
                    ⚡
                    <strong>{{ lightning }}</strong>
                </span>

            </div>
        </div>

        <div v-if="gameOver" class="game-over">

            <div class="game-over-panel">

                <LeaderboardEntry v-if="showLeaderboard" :game-id="game.resultId!" :player-id="playerSession!.playerId"
                    :score="score" @submitted="showLeaderboard = false" @skipped="showLeaderboard = false"
                    @play-again="restart" />

                <template v-else>

                    <span class="game-over-label">
                        <i class="label-bolt">⚡</i>
                        {{
                            game.endReason === "timeout"
                                ? "Flight complete"
                                : "Run ended"
                        }}
                    </span>

                    <strong class="game-over-title">
                        {{
                            game.endReason === "timeout"
                                ? "TIME'S UP"
                                : "GAME OVER"
                        }}
                    </strong>

                    <div class="game-over-stats">

                        <div class="stat-block">
                            <strong>{{ score }}</strong>
                            <span>Score</span>
                        </div>

                        <div class="stat-block stat-block--volt">
                            <strong>⚡ {{ lightning }}</strong>
                            <span>Collected</span>
                        </div>

                    </div>

                    <button type="button" class="restart-button" @click="showLeaderboard = true">
                        <span>
                            <i class="btn-bolt">🏆</i>
                            Join leaderboard
                        </span>

                        <span class="restart-button-arrow">
                            →
                        </span>
                    </button>

                    <button type="button" class="secondary-button" @click="restart">
                        Play again
                    </button>

                    <RouterLink to="/leaderboard" class="text-link">
                        View leaderboard
                    </RouterLink>

                </template>

            </div>

        </div>
    </div>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@500;700&display=swap');

.game-wrapper {
    position: relative;

    width: 100%;
    height: 100%;
    min-height: 0;

    overflow: hidden;

    flex: 1;
    isolation: isolate;

    background: var(--ink);

    transform:
        translate3d(var(--shake-x, 0px),
            var(--shake-y, 0px),
            0);

    transition:
        box-shadow 80ms ease;
}

.game-wrapper::after {
    content: "";

    position: absolute;

    inset: 0;

    z-index: 2;

    pointer-events: none;

    border:
        0 solid transparent;

    opacity: 0;
}

/*
 * OBSTACLE HIT
 */
.game-wrapper.collision-active {
    box-shadow:
        inset 0 0 0 3px rgba(255,
            92,
            108,
            0.95),
        inset 0 0 45px rgba(255,
            50,
            60,
            0.32),
        0 0 35px rgba(255,
            80,
            90,
            0.28);
}

.game-wrapper.collision-active::after {
    border:
        3px solid rgba(255,
            92,
            108,
            0.85);

    opacity: 1;

    box-shadow:
        inset 0 0 30px rgba(255,
            50,
            60,
            0.24);
}

/*
 * LIGHTNING COLLECTION
 */
.game-wrapper.lightning-active {
    box-shadow:
        inset 0 0 0 2px rgba(var(--volt-rgb),
            0.8),
        inset 0 0 35px rgba(var(--volt-rgb),
            0.16);
}

.game-canvas {
    display: block;

    width: 100%;
    height: 100%;

    min-width: 0;
    min-height: 0;

    touch-action: none;
    user-select: none;

    /*
     * Prevent the browser from treating
     * the canvas as an inline/replaced
     * element with unexpected sizing.
     */
    object-fit: fill;
}

/*
 * LIVE HUD READOUT
 */
.hud-readout {
    position: absolute;

    top: calc(14px + env(safe-area-inset-top));
    left: 14px;
    right: 14px;

    z-index: 5;

    display: flex;

    align-items: center;
    justify-content: space-between;

    pointer-events: none;
}

.hud-readout-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.hud-readout-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    padding: 6px 12px;

    border: 1px solid var(--line);
    border-radius: 10px;

    color: var(--text-dim);

    background: rgba(7, 7, 12, 0.55);
    backdrop-filter: blur(6px);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.hud-readout-item strong {
    color: var(--text);

    font-size: 0.72rem;
    letter-spacing: 0;
}

.hud-readout-item--volt {
    color: var(--volt);
    border-color: var(--volt-dim);
}

.hud-readout-item--volt strong {
    color: var(--volt);
}

.hud-readout-item--cyan {
    color: var(--cyan);
    border-color: rgba(var(--cyan-rgb), 0.28);
}

.hud-readout-item--cyan strong {
    color: var(--cyan);
}

.hud-readout-item--urgent {
    color: var(--coral);
    border-color: rgba(var(--coral-rgb), 0.3);

    animation: urgent-pulse 1s ease-in-out infinite;
}

.hud-readout-item--urgent strong {
    color: var(--coral);
}

@keyframes urgent-pulse {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.55;
    }
}

.hud-dot {
    width: 5px;
    height: 5px;

    border-radius: 50%;

    background: var(--cyan);

    box-shadow: 0 0 6px 1px rgba(var(--cyan-rgb), 0.5);
}

/*
 * GAME OVER
 */
.game-over {
    position: absolute;

    inset: 0;

    z-index: 10;

    display: grid;

    width: 100%;
    height: 100%;

    place-content: center;
    justify-items: center;

    padding:
        clamp(20px,
            6vw,
            40px);

    box-sizing: border-box;

    overflow-y: auto;

    background:
        rgba(7, 7, 12, 0.86);

    backdrop-filter:
        blur(10px);

    -webkit-backdrop-filter:
        blur(10px);
}

.game-over-panel {
    display: grid;
    justify-items: center;

    gap: clamp(10px, 2.5vw, 14px);

    width: min(100%, 340px);

    padding: clamp(22px, 5vw, 30px) clamp(20px, 5vw, 26px);

    border: 1px solid var(--line);
    border-radius: 18px;

    background: linear-gradient(165deg, var(--surface), var(--surface-2));

    text-align: center;

    color: var(--text);
}

.game-over-label {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.label-bolt {
    font-style: normal;
}

.game-over-title {
    font-family: var(--font-display);
    font-size:
        clamp(1.9rem,
            8vw,
            2.5rem);
    font-weight: 700;
    letter-spacing: -0.01em;
    text-transform: uppercase;
    line-height: 1;
}

.game-over-stats {
    display: grid;

    grid-template-columns: 1fr 1fr;
    gap: 10px;

    width: 100%;
    margin: 6px 0 4px;
}

.stat-block {
    display: grid;
    justify-items: center;
    gap: 4px;

    padding: 12px 6px;

    border: 1px solid var(--line);
    border-radius: 12px;

    background: rgba(255, 255, 255, 0.02);
}

.stat-block strong {
    font-family: var(--font-mono);
    font-size:
        clamp(1.15rem,
            5vw,
            1.4rem);
    font-weight: 700;
    color: var(--text);
}

.stat-block span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.54rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.stat-block--volt strong {
    color: var(--volt);
}

.restart-button {
    display: flex;

    width: min(100%, 260px);
    min-height: 54px;

    margin-top: 4px;
    padding: 0 8px 0 20px;

    align-items: center;
    justify-content: space-between;

    border: 0;
    clip-path: polygon(0 0, 100% 0, 100% 70%, 96% 100%, 0 100%);

    color: var(--ink);
    background: linear-gradient(100deg, var(--volt), var(--volt-light));

    font-family: var(--font-display);
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    text-transform: uppercase;

    cursor: pointer;

    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;

    transition: transform 120ms ease, filter 120ms ease;
}

.restart-button span {
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.btn-bolt {
    font-style: normal;
}

.restart-button:hover {
    filter: brightness(1.06);
}

.restart-button:active {
    transform: scale(0.97);
}

.restart-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 3px;
}

.restart-button-arrow {
    display: grid;

    width: 30px;
    height: 30px;

    place-items: center;

    border-radius: 8px;

    background: rgba(7, 7, 12, 0.14);

    font-size: 1rem;
}

.secondary-button {
    width: min(100%, 260px);
    min-height: 40px;

    margin-top: -2px;
    padding: 8px 12px;

    border: 0;
    border-radius: 10px;

    color: var(--text-faint);
    background: transparent;

    font-family: var(--font-mono);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;

    cursor: pointer;

    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;

    transition: color 120ms ease, background 120ms ease;
}

.secondary-button:hover {
    color: var(--text-dim);
    background: rgba(255, 255, 255, 0.03);
}

.secondary-button:active {
    color: var(--text);
}

.secondary-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.text-link {
    margin-top: 2px;
    padding: 4px;

    border: 0;
    background: transparent;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-decoration: underline;
    text-underline-offset: 3px;
    text-transform: uppercase;

    cursor: pointer;

    transition: color 120ms ease;
}

.text-link:hover {
    color: var(--text-dim);
}

.text-link:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}



/*
 * Smaller phones
 */
@media (max-width: 480px) {
    .game-wrapper {
        min-height: 0;
    }

    .game-over {
        padding:
            20px 16px;
    }

    .hud-readout {
        top: calc(10px + env(safe-area-inset-top));
        left: 10px;
        right: 10px;
    }

    .hud-readout-item {
        padding: 5px 9px;
        font-size: 0.54rem;
    }
}

/*
 * Short screens, such as:
 * landscape phones or Chrome
 * device emulation.
 */
@media (max-height: 600px) {
    .game-over-panel {
        gap: 8px;
        padding: 18px 20px;
    }

    .game-over-title {
        font-size: 1.6rem;
    }

    .restart-button {
        min-height: 46px;
    }
}

/*
 * Landscape mobile
 */
@media (orientation: landscape) and (max-height: 500px) {
    .game-over-panel {
        width: min(100%, 460px);
    }

    .game-over-stats {
        grid-template-columns: 1fr 1fr;
    }
}

/*
 * Reduced motion — nothing animates in this
 * component beyond built-in transitions, but
 * keep transforms instant for shake feedback.
 */
@media (prefers-reduced-motion: reduce) {
    .game-wrapper {
        transition: none;
    }

    .hud-readout-item--urgent {
        animation: none;
    }
}
</style>