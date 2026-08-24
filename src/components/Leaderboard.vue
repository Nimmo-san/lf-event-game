<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import {
    getLeaderboard,
    getPlayerRank,
    type LeaderboardRow,
    type PlayerRank
} from "../services/leaderboardApi";
import { getPlayerSession } from "../services/playerSession";


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

const leaderboard =
    ref<LeaderboardRow[]>([]);

const playerRank = ref<PlayerRank | null>(null);

const loading = ref(true);
const offline = ref(false);
const playerSession = getPlayerSession();

const playerId = computed(() => {
    return playerSession?.playerId ?? null;
});

const playerIsTopTen = computed(() => {
    if (!playerRank.value) {
        return false;
    }

    return playerRank.value.rank <= 10;
})

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

    offline.value = !navigator.onLine;

    // Current leaderboard can't be guranteed while offline
    if (offline.value) {
        loading.value = false;
        return
    }

    try {

        leaderboard.value =
            await getLeaderboard();

        hasLoadedOnce = true;
    } catch (err) {
        console.error(
            "Failed to load Leaderboard:",
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

        loading.value = false;
        return;
    }

    // personal rank is optional.
    if (playerId.value) {
        try {
            playerRank.value = await getPlayerRank(playerId.value);

        } catch (err) {
            console.error("Failed to load player rank:", err);
            playerRank.value = null;
        }
    } else {
        playerRank.value = null;
    }
    loading.value = false;
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


        <!-- INITIAL LOADING -->

        <div v-if="loading" class="leaderboard-state">
            Loading leaderboard...
        </div>


        <!-- OFFLINE -->

        <div v-else-if="offline" class="leaderboard-state">
            <strong>
                Leaderboard unavailable offline
            </strong>

            <span>
                Reconnect to see the latest rankings.
            </span>
        </div>


        <!-- ERROR -->

        <div v-else-if="error" class="leaderboard-state leaderboard-error">
            {{ error }}

            <button type="button" class="retry-button" @click="loadLeaderboard">
                Try again
            </button>
        </div>


        <template v-else>

            <!--
                PERSONAL POSITION

                Only shown when:
                - there is a player session
                - the player has entered the leaderboard

                Public/spectator views won't see this.
            -->

            <section v-if="playerId && playerRank" class="player-position">
                <div class="player-position-main">
                    <span>
                        YOUR POSITION
                    </span>

                    <strong>
                        #{{ playerRank.rank }}
                    </strong>
                </div>

                <div class="player-position-score">
                    <span>
                        BEST SCORE
                    </span>

                    <strong>
                        {{ playerRank.score.toLocaleString() }}
                    </strong>
                </div>
            </section>


            <!--
                PLAYER HAS A SESSION BUT ISN'T ENTERED

                Don't show this to public/spectator visitors.
            -->

            <section v-else-if="playerId && !playerRank" class="player-not-ranked">
                <strong>
                    You're not on the leaderboard yet.
                </strong>

                <span>
                    Enter the leaderboard after your next flight
                    to claim a position.
                </span>
            </section>


            <!-- EMPTY LEADERBOARD -->

            <div v-if="leaderboard.length === 0" class="leaderboard-state">
                No scores yet. Be the first to play.
            </div>


            <!-- TOP 10 -->

            <div v-else class="leaderboard-list">
                <div v-for="player in leaderboard" :key="player.player_id" class="leaderboard-row" :class="{
                    'leaderboard-first':
                        player.rank === 1,

                    'leaderboard-you':
                        playerId === player.player_id,
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

                        <!-- <small>
                            {{ player.company_name }}
                        </small> -->
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


            <!--
                PLAYER IS RANKED BUT OUTSIDE TOP 10
            -->

            <div v-if="
                playerId &&
                playerRank &&
                !playerIsTopTen
            " class="outside-top-ten">
                <div class="rank-divider">
                    <span>•••</span>
                </div>

                <div class="
                        leaderboard-row
                        leaderboard-you
                    ">
                    <div class="leaderboard-rank">
                        #{{ playerRank.rank }}
                    </div>

                    <div class="leaderboard-player">
                        <strong>
                            You
                        </strong>

                        <small>
                            Your current position
                        </small>
                    </div>

                    <div class="leaderboard-score">
                        <strong>
                            {{ playerRank.score.toLocaleString() }}
                        </strong>

                        <small>
                            BEST SCORE
                        </small>
                    </div>
                </div>
            </div>

        </template>

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


/* =========================
   YOUR POSITION (ranked)
========================= */

.player-position {
    display: grid;

    grid-template-columns: 1fr 1fr;
    gap: 10px;

    margin-bottom: 16px;
    padding: 14px 16px;

    border: 1px solid var(--volt-dim);
    border-radius: 16px;

    background: linear-gradient(135deg,
            rgba(var(--volt-rgb), 0.12),
            rgba(var(--cyan-rgb), 0.06));
}

.player-position-main,
.player-position-score {
    display: grid;
    gap: 4px;
}

.player-position-score {
    justify-items: end;
    text-align: right;
}

.player-position span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.56rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.player-position-main strong {
    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 1.6rem;
    font-weight: 700;
}

.player-position-score strong {
    color: var(--text);

    font-family: var(--font-mono);
    font-size: 1.6rem;
    font-weight: 700;
}


/* =========================
   NOT YET RANKED
========================= */

.player-not-ranked {
    display: grid;
    gap: 4px;

    margin-bottom: 16px;
    padding: 14px 16px;

    border: 1px solid var(--line);
    border-radius: 14px;

    background: rgba(255, 255, 255, 0.02);

    text-align: left;
}

.player-not-ranked strong {
    color: var(--text);

    font-family: var(--font-display);
    font-size: 0.85rem;
    font-weight: 700;
}

.player-not-ranked span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.7rem;
    line-height: 1.5;
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


/*
 * "This is you" — an outline ring rather than a
 * background/border override (top of the board AND your own row, at once).
 */
.leaderboard-you {
    outline: 2px solid rgba(var(--cyan-rgb), 0.5);
    outline-offset: 2px;
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


/* =========================
   OUTSIDE TOP 10
========================= */

.outside-top-ten {
    display: grid;
    gap: 8px;

    margin-top: 8px;
}

.rank-divider {
    display: flex;
    justify-content: center;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.3em;
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

.leaderboard-state strong {
    color: var(--text);

    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 700;
}

.leaderboard-state span {
    color: var(--text-faint);

    font-size: 0.75rem;
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

    .player-position {
        padding: 12px 14px;
    }

    .player-position-main strong,
    .player-position-score strong {
        font-size: 1.3rem;
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