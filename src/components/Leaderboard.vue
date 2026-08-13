<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import type { LeaderboardRow } from "../services/leaderboardApi";


const props = withDefaults(
    defineProps<{
        // When set, polls the leaderboard on an interval —
        // for the standalone spectator/TV display, which has
        // no one to tap "Try again" or trigger a reload.
        autoRefreshMs?: number;
    }>(),
    {
        autoRefreshMs: 0,
    },
);

const API_URL =
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000";

const players =
    ref<LeaderboardRow[]>([]);

const loading = ref(true);

const error = ref("");

let hasLoadedOnce = false;

let refreshInterval: ReturnType<typeof setInterval> | null = null;

async function loadLeaderboard() {
    // On background polls (auto-refresh), don't flash the
    // loading state — that'd flicker the whole board on a TV
    // display every interval. Only show it on the first load.
    if (!hasLoadedOnce) {
        loading.value = true;
    }

    error.value = "";

    try {
        const response = await fetch(
            `${API_URL}/leaderboard`,
        );

        if (!response.ok) {
            throw new Error(
                "Failed to load leaderboard.",
            );
        }

        players.value =
            await response.json();

        hasLoadedOnce = true;
    } catch (err) {
        console.error(
            "Leaderboard error:",
            err,
        );

        // Only surface the error state on the first load —
        // a background refresh failure on the TV display
        // should just keep showing the last known standings
        // rather than replacing them with an error screen.
        if (!hasLoadedOnce) {
            error.value =
                "Unable to load the leaderboard.";
        }
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    loadLeaderboard();

    if (props.autoRefreshMs > 0) {
        refreshInterval = setInterval(() => {
            loadLeaderboard();
        }, props.autoRefreshMs);
    }
});

onBeforeUnmount(() => {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
});
</script>

<template>
    <section class="leaderboard-card">

        <header class="leaderboard-header">
            <div>
                <p class="section-kicker">
                    <i class="kicker-bolt">⚡</i>
                    LIGHTNING FLIGHT
                </p>

                <h2>
                    Leaderboard
                </h2>
            </div>

            <span class="leaderboard-icon">
                🏆
            </span>
        </header>

        <div v-if="loading" class="leaderboard-state">
            Loading leaderboard...
        </div>

        <div v-else-if="error" class="leaderboard-state leaderboard-error">
            {{ error }}

            <button type="button" class="retry-button" @click="loadLeaderboard">
                Try again
            </button>
        </div>

        <div v-else-if="players.length === 0" class="leaderboard-state">
            No scores yet. Be the first to play.
        </div>

        <div v-else class="leaderboard-list">
            <div v-for="player in players" :key="player.rank" class="leaderboard-row" :class="{
                'leaderboard-first':
                    player.rank === 1,
            }">
                <div class="leaderboard-rank">
                    <span v-if="player.rank === 1">
                        🏆
                    </span>

                    <span v-else>
                        #{{ player.rank }}
                    </span>
                </div>

                <div class="leaderboard-player">
                    <strong>
                        {{ player.player_name }}
                    </strong>

                    <small>
                        {{ player.company_name }}
                    </small>
                </div>

                <div class="leaderboard-score">
                    <strong>
                        {{ player.score.toLocaleString() }}
                    </strong>

                    <small>
                        ⚡
                        {{ player.lightning_collected }}
                    </small>
                </div>
            </div>
        </div>

    </section>
</template>

<style scoped>
.leaderboard-card {
    width: 100%;
    max-width: 620px;
    margin: 0 auto;
    padding: 20px;

    border: 1px solid var(--line);
    border-radius: 24px;

    background: linear-gradient(165deg, var(--surface), var(--surface-2));

    color: var(--text);

    box-sizing: border-box;
}

.leaderboard-header {
    display: flex;
    align-items: center;
    justify-content: space-between;

    margin-bottom: 18px;
}

.section-kicker {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    margin: 0;

    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.kicker-bolt {
    font-style: normal;
}

.leaderboard-header h2 {
    margin: 6px 0 0;

    color: var(--text);

    font-family: var(--font-display);
    font-size: 1.7rem;
    font-weight: 700;
    letter-spacing: -0.02em;
}

.leaderboard-icon {
    display: grid;

    width: 46px;
    height: 46px;

    place-items: center;

    border: 1px solid var(--volt-dim);
    border-radius: 14px;

    background: rgba(var(--volt-rgb), 0.1);

    font-size: 1.3rem;
}

.leaderboard-list {
    display: grid;
    gap: 8px;
}

.leaderboard-row {
    display: grid;

    grid-template-columns: 44px minmax(0, 1fr) auto;

    gap: 12px;

    align-items: center;

    padding: 13px 12px;

    border: 1px solid var(--line);
    border-radius: 16px;

    background: rgba(255, 255, 255, 0.02);
}

.leaderboard-first {
    border-color: var(--volt-dim);

    background: linear-gradient(135deg,
            rgba(var(--volt-rgb), 0.14),
            rgba(var(--cyan-rgb), 0.08));
}

.leaderboard-rank {
    display: grid;

    min-width: 44px;

    justify-items: center;

    color: var(--cyan);

    font-family: var(--font-mono);
    font-size: 0.78rem;
    font-weight: 700;
}

.leaderboard-first .leaderboard-rank {
    font-size: 1.25rem;
}

.leaderboard-player {
    display: grid;
    gap: 3px;

    min-width: 0;
}

.leaderboard-player strong {
    overflow: hidden;

    color: var(--text);

    font-family: var(--font-display);
    font-size: 0.88rem;
    font-weight: 700;

    text-overflow: ellipsis;
    white-space: nowrap;
}

.leaderboard-player small {
    overflow: hidden;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.66rem;

    text-overflow: ellipsis;
    white-space: nowrap;
}

.leaderboard-score {
    display: grid;

    justify-items: end;

    gap: 3px;
}

.leaderboard-score strong {
    color: var(--text);

    font-family: var(--font-mono);
    font-size: 0.95rem;
    font-weight: 700;
}

.leaderboard-score small {
    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.64rem;
    font-weight: 700;
}

.leaderboard-state {
    display: grid;

    min-height: 180px;

    place-content: center;

    gap: 12px;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.85rem;
    text-align: center;
}

.retry-button {
    justify-self: center;

    padding: 10px 18px;

    border: 0;
    border-radius: 10px;

    color: var(--ink);
    background: linear-gradient(100deg, var(--volt), var(--volt-light));

    font-family: var(--font-display);
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.02em;
    text-transform: uppercase;

    cursor: pointer;

    transition: filter 120ms ease;
}

.retry-button:hover {
    filter: brightness(1.06);
}

.retry-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 3px;
}

@media (max-width: 480px) {
    .leaderboard-card {
        padding: 15px;

        border-radius: 20px;
    }

    .leaderboard-row {
        grid-template-columns: 34px minmax(0, 1fr) auto;

        gap: 8px;

        padding: 11px 9px;
    }

    .leaderboard-rank {
        min-width: 34px;
    }

    .leaderboard-score strong {
        font-size: 0.82rem;
    }

    .leaderboard-score small {
        font-size: 0.58rem;
    }
}
</style>