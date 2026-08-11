<script setup lang="ts">
import GameCanvas from "../components/GameCanvas.vue"

// Same check as GameCanvas.vue — reflects the device's
// primary input mechanism, used here to decide which
// control hint to show in the footer.
const isTouchDevice =
    window.matchMedia(
        "(pointer: coarse)",
    ).matches

</script>

<template>
    <main class="game-page">

        <header class="game-header">

            <span class="game-header-brand">
                <i class="brand-bolt">⚡</i>
                LIGHTNING FLIGHT
            </span>

        </header>


        <section class="game-container">
            <GameCanvas />
        </section>


        <footer class="controls-hint">

            <template v-if="isTouchDevice">
                <span class="hint-text">
                    Tap left or right to steer
                </span>
            </template>

            <template v-else>
                <kbd>←</kbd>
                <kbd>→</kbd>
                <span class="hint-text">
                    to steer
                </span>
            </template>

        </footer>

    </main>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@500;700&display=swap');

.game-page {
    display: flex;

    width: 100%;
    height: 100%;

    flex-direction: column;

    overflow: hidden;

    background: var(--ink);

    color: var(--text);

    font-family: var(--font-mono);
}


/* =========================
   HEADER
========================= */

.game-header {
    display: flex;

    align-items: center;

    padding: 16px 20px;

    border-bottom: 1px solid var(--line);
}


.game-header-brand {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.14em;
}


.brand-bolt {
    font-style: normal;
    color: var(--volt);
}


/* =========================
   GAME CANVAS AREA
========================= */

.game-container {
    position: relative;

    width: 100%;
    flex: 1 1 auto;

    min-width: 0;
    min-height: 0;

    overflow: hidden;
}


/* =========================
   CONTROL HINT
========================= */

.controls-hint {
    display: flex;

    align-items: center;
    justify-content: center;
    gap: 8px;

    padding: 12px 16px calc(12px + env(safe-area-inset-bottom));

    border-top: 1px solid var(--line);
}


.controls-hint kbd {
    display: grid;

    min-width: 34px;
    height: 34px;

    place-items: center;

    border: 1px solid var(--volt-dim);
    border-radius: 8px;

    background: rgba(var(--volt-rgb), 0.06);

    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 1rem;
    font-weight: 700;

    box-shadow: 0 0 0 1px rgba(255, 255, 255, 0.02) inset;
}


.hint-text {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}


/* =========================
   RESERVED: LIVE STAT BLOCKS
   (see script comment above)
========================= */

.stat-block {
    display: grid;
    justify-items: center;
    gap: 2px;
}


.stat-block strong {
    font-family: var(--font-mono);
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text);
}


.stat-block span {
    color: var(--text-faint);

    font-size: 0.55rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}


.stat-block--volt strong {
    color: var(--volt);
}


/* =========================
   MOBILE
========================= */

@media (max-width: 480px) {

    .game-header {
        padding: 13px 16px;
    }


    .controls-hint {
        gap: 6px;

        padding: 10px 14px calc(10px + env(safe-area-inset-bottom));
    }


    .controls-hint kbd {
        min-width: 30px;
        height: 30px;

        font-size: 0.9rem;
    }


    .hint-text {
        font-size: 0.56rem;
    }
}
</style>