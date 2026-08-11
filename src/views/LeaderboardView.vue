<script setup lang="ts">
import { computed } from "vue"
import { useRouter } from "vue-router"

import Leaderboard from "../components/Leaderboard.vue"

const router = useRouter()

/*
 * Vue Router sets window.history.state.back to the previous
 * route's path when navigated to in-app (e.g. from the
 * game-over screen's "View leaderboard" link) — and leaves it
 * null on a direct URL load, which is exactly how the TV/booth
 * display always arrives here. So this naturally shows "Back"
 * for the phone case and hides it for the spectator case,
 * without needing to pass a prop or track it manually.
 */
const canGoBack =
    computed(() => !!window.history.state?.back)

function goBack() {
    router.back()
}
</script>

<template>
    <main class="leaderboard-page">

        <header class="leaderboard-page-header">
            <div class="leaderboard-page-header-left">

                <button v-if="canGoBack" type="button" class="back-link" @click="goBack">
                    ← Back
                </button>

                <span class="brand-mark">
                    <i class="brand-bolt">⚡</i>
                    LIGHTNING FIBRE
                </span>

            </div>

            <span class="live-tag">
                <i class="live-dot"></i>
                LIVE STANDINGS
            </span>
        </header>

        <div class="leaderboard-page-content">
            <!--
                30s poll — frequent enough that a TV display
                feels live, infrequent enough not to hammer
                the API with a screen that never closes.
            -->
            <Leaderboard :auto-refresh-ms="30000" />
        </div>

    </main>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=JetBrains+Mono:wght@500;700&display=swap');

.leaderboard-page {
    display: flex;

    width: 100%;
    height: 100%;

    flex-direction: column;

    overflow: hidden;

    background: var(--ink);
}

.leaderboard-page-header {
    display: flex;

    align-items: center;
    justify-content: space-between;

    padding: 24px 32px;

    border-bottom: 1px solid var(--line);
}

.leaderboard-page-header-left {
    display: flex;
    align-items: center;
    gap: 16px;
}

.back-link {
    padding: 6px 10px;

    border: 1px solid var(--line);
    border-radius: 8px;

    background: transparent;

    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;

    cursor: pointer;

    transition: color 120ms ease, border-color 120ms ease;
}

.back-link:hover {
    color: var(--text);
    border-color: var(--volt-dim);
}

.back-link:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.brand-mark {
    display: inline-flex;
    align-items: center;
    gap: 8px;

    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.16em;
}

.brand-bolt {
    font-style: normal;
    color: var(--volt);
}

.live-tag {
    display: inline-flex;
    align-items: center;
    gap: 7px;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
}

.live-dot {
    width: 7px;
    height: 7px;

    border-radius: 50%;

    background: var(--volt);

    box-shadow: 0 0 8px 1px var(--volt-dim);

    animation: pulse 1.8s ease-in-out infinite;
}

@keyframes pulse {

    0%,
    100% {
        opacity: 1;
    }

    50% {
        opacity: 0.35;
    }
}

.leaderboard-page-content {
    display: grid;

    flex: 1;
    min-height: 0;

    place-items: center;

    padding: 32px;

    overflow-y: auto;
}

@media (prefers-reduced-motion: reduce) {
    .live-dot {
        animation: none;
    }
}
</style>