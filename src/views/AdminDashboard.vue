<script setup lang="ts">
import { computed, inject, onMounted, ref } from "vue"

import {
    type AnalyticsResponse,
    getAdminAnalytics
} from "../services/adminApi"

const handleAdminError =
    inject<(err: unknown) => boolean>("handleAdminError")

const analytics = ref<AnalyticsResponse | null>(null)
const loading = ref(true)
const error = ref("")

const maxGamesOverTime = computed(() => {
    if (!analytics.value) {
        return 1
    }

    return Math.max(
        1,
        ...analytics.value.activity.games_over_time.map(
            (item) => item.games,
        ),
    )
})

const maxScoreBucket = computed(() => {
    if (!analytics.value) {
        return 1
    }

    return Math.max(
        1,
        ...analytics.value.distributions.scores.map(
            (item) => item.games,
        ),
    )
})

const maxReplayPlayers = computed(() => {
    if (!analytics.value) {
        return 1
    }

    return Math.max(
        1,
        ...analytics.value.distributions.games_per_player.map(
            (item) => item.players,
        ),
    )
})

function formatNumber(value: number) {
    return value.toLocaleString("en-GB")
}

function formatPercent(value: number) {
    return `${value.toFixed(1)}%`
}

async function loadAnalytics() {
    loading.value = true
    error.value = ""

    try {
        analytics.value = await getAdminAnalytics()
    } catch (err) {
        if (handleAdminError?.(err)) {
            return
        }

        console.error("Failed to load analytics:", err)

        error.value = "Unable to load analytics."
    } finally {
        loading.value = false
    }
}

onMounted(loadAnalytics)
</script>

<template>
    <section class="dashboard" :aria-busy="loading">

        <div class="dashboard-heading">
            <div>
                <p class="dashboard-kicker">
                    Performance overview
                </p>

                <h2>
                    Dashboard
                </h2>
            </div>

            <button class="refresh-button" type="button" :disabled="loading" @click="loadAnalytics">
                {{ loading ? "Refreshing..." : "Refresh" }}
            </button>
        </div>


        <div v-if="loading && !analytics" class="dashboard-state" aria-live="polite">
            Loading analytics...
        </div>


        <div v-else-if="error && !analytics" class="dashboard-state dashboard-error" role="alert">
            {{ error }}
        </div>


        <template v-else-if="analytics">

            <!--
                PRIMARY OBJECTIVE, the business metrics.
            -->

            <div class="kpi-primary">

                <article class="kpi-hero kpi-hero--volt">
                    <span>Leaderboard conversion</span>

                    <strong>
                        {{ formatPercent(analytics.leaderboard.conversion_rate) }}
                    </strong>

                    <small>
                        {{ analytics.leaderboard.unique_entries }} contacts captured
                    </small>
                </article>

                <article class="kpi-hero">
                    <span>Unique players</span>

                    <strong>
                        {{ formatNumber(analytics.players.unique_players) }}
                    </strong>

                    <small>reach</small>
                </article>

                <article class="kpi-hero">
                    <span>Games played</span>

                    <strong>
                        {{ formatNumber(analytics.players.total_games) }}
                    </strong>

                    <small>booth volume</small>
                </article>

            </div>


            <!--
                SECONDARY OBJECTIVE, engagement depth.
            -->

            <div class="kpi-secondary">

                <div class="kpi-chip">
                    <span>Replay rate</span>
                    <strong>{{ formatPercent(analytics.players.replay_rate) }}</strong>
                    <small>{{ analytics.players.repeat_players }} repeat players</small>
                </div>

                <div class="kpi-chip">
                    <span>Avg game time</span>
                    <strong>{{ analytics.gameplay.average_duration.toFixed(1) }}s</strong>
                </div>

                <div class="kpi-chip">
                    <span>Highest score</span>
                    <strong>{{ formatNumber(analytics.gameplay.highest_score) }}</strong>
                </div>

                <div class="kpi-chip">
                    <span>Avg score</span>
                    <strong>{{ Math.round(analytics.gameplay.average_score).toLocaleString() }}</strong>
                </div>

                <div class="kpi-chip">
                    <span>Avg lightning</span>
                    <strong>{{ analytics.gameplay.average_lightning.toFixed(1) }}</strong>
                </div>

            </div>

            <div class="analytics-grid">

                <article class="analytics-panel">
                    <div class="panel-heading">
                        <span>Activity</span>
                        <h3>Games over time</h3>
                    </div>

                    <div v-if="analytics.activity.games_over_time.length === 0" class="panel-empty">
                        No activity data yet.
                    </div>

                    <div v-else class="bar-chart">
                        <div v-for="item in analytics.activity.games_over_time" :key="item.period" class="bar-row">
                            <span class="bar-label">{{ item.period }}</span>

                            <div class="bar-track" aria-hidden="true">
                                <div class="bar-fill" :style="{
                                    width: `${(item.games / maxGamesOverTime) * 100}%`,
                                }" />
                            </div>

                            <strong>{{ item.games }}</strong>
                        </div>
                    </div>
                </article>

                <article class="analytics-panel">
                    <div class="panel-heading">
                        <span>Companies</span>
                        <h3>Top companies</h3>
                    </div>

                    <div v-if="analytics.companies.length === 0" class="panel-empty">
                        No company data yet.
                    </div>

                    <div v-else class="company-list">
                        <div v-for="company in analytics.companies" :key="company.company" class="company-row">
                            <div>
                                <strong>{{ company.company }}</strong>
                                <span>{{ company.players }} players · {{ company.games }} games</span>
                            </div>

                            <div class="company-score">
                                <strong>{{ company.best_score.toLocaleString() }}</strong>
                                <span>best</span>
                            </div>
                        </div>
                    </div>
                </article>

                <article class="analytics-panel">
                    <div class="panel-heading">
                        <span>Engagement</span>
                        <h3>Games per player</h3>
                    </div>

                    <div class="bar-chart">
                        <div v-for="item in analytics.distributions.games_per_player" :key="item.games" class="bar-row">
                            <span class="bar-label">
                                {{ item.games }} {{ item.games === 1 ? "game" : "games" }}
                            </span>

                            <div class="bar-track" aria-hidden="true">
                                <div class="bar-fill" :style="{
                                    width: `${(item.players / maxReplayPlayers) * 100}%`,
                                }" />
                            </div>

                            <strong>{{ item.players }}</strong>
                        </div>
                    </div>
                </article>

                <article class="analytics-panel">
                    <div class="panel-heading">
                        <span>Scores</span>
                        <h3>Score distribution</h3>
                    </div>

                    <div class="bar-chart">
                        <div v-for="bucket in analytics.distributions.scores" :key="bucket.label" class="bar-row">
                            <span class="bar-label">{{ bucket.label }}</span>

                            <div class="bar-track" aria-hidden="true">
                                <div class="bar-fill" :style="{
                                    width: `${(bucket.games / maxScoreBucket) * 100}%`,
                                }" />
                            </div>

                            <strong>{{ bucket.games }}</strong>
                        </div>
                    </div>
                </article>

            </div>

        </template>

    </section>
</template>

<style scoped>
.dashboard-heading {
    display: flex;

    align-items: flex-end;
    justify-content: space-between;

    gap: 20px;

    margin-bottom: 20px;
}

.dashboard-kicker {
    margin: 0 0 5px;

    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.dashboard-heading h2 {
    margin: 0;

    color: var(--text);

    font-family: var(--font-display);
    font-size: clamp(1.6rem, 3.5vw, 2.2rem);
}

.refresh-button {
    min-height: 40px;

    padding: 0 14px;

    border: 1px solid var(--line);
    border-radius: 10px;

    color: var(--text-dim);
    background: rgba(255, 255, 255, 0.03);

    font-family: var(--font-display);
    font-size: 0.72rem;
    font-weight: 700;

    cursor: pointer;
}

.refresh-button:hover:not(:disabled) {
    color: var(--text);
}

.refresh-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.refresh-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}


/* =========================
   PRIMARY KPIs — the "3 hero numbers"
========================= */

.kpi-primary {
    display: grid;

    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;

    margin-bottom: 14px;
}

.kpi-hero {
    display: grid;
    gap: 8px;

    padding: 22px;

    border: 1px solid var(--line);
    border-radius: 18px;

    background: linear-gradient(155deg, rgba(255, 255, 255, 0.04), rgba(255, 255, 255, 0.015));
}

.kpi-hero--volt {
    border-color: var(--volt-dim);

    background: linear-gradient(155deg, rgba(var(--volt-rgb), 0.14), rgba(var(--cyan-rgb), 0.06));
}

.kpi-hero span {
    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}

.kpi-hero strong {
    color: var(--text);

    font-family: var(--font-display);
    font-size: clamp(1.8rem, 4vw, 2.6rem);
    letter-spacing: -0.03em;
}

.kpi-hero--volt strong {
    color: var(--volt);
}

.kpi-hero small {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.62rem;
}


/* =========================
   SECONDARY KPIs — quieter, smaller, supporting detail
========================= */

.kpi-secondary {
    display: grid;

    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 10px;

    margin-bottom: 26px;
}

.kpi-chip {
    display: grid;

    min-width: 0;
    gap: 4px;

    padding: 12px 14px;

    border: 1px solid var(--line);
    border-radius: 12px;

    background: rgba(255, 255, 255, 0.02);
}

.kpi-chip span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.52rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

.kpi-chip strong {
    color: var(--text-dim);

    font-family: var(--font-display);
    font-size: 1.05rem;
}

.kpi-chip small {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.54rem;
}


/* =========================
   CHARTS
========================= */

.analytics-grid {
    display: grid;

    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 14px;
}

.analytics-panel {
    min-width: 0;

    padding: 18px;

    border: 1px solid var(--line);
    border-radius: 18px;

    background: var(--surface);
}

.panel-heading {
    margin-bottom: 18px;
}

.panel-heading span {
    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.56rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.panel-heading h3 {
    margin: 5px 0 0;

    color: var(--text);

    font-family: var(--font-display);
    font-size: 1rem;
}

.bar-chart {
    display: grid;
    gap: 11px;
}

.bar-row {
    display: grid;

    grid-template-columns: minmax(90px, 0.9fr) minmax(100px, 2fr) 36px;
    gap: 10px;

    align-items: center;
}

.bar-label {
    overflow: hidden;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.58rem;

    text-overflow: ellipsis;
    white-space: nowrap;
}

.bar-track {
    height: 7px;

    overflow: hidden;

    border-radius: 999px;

    background: rgba(255, 255, 255, 0.06);
}

.bar-fill {
    height: 100%;
    min-width: 2px;

    border-radius: inherit;

    background: linear-gradient(90deg, var(--volt), var(--cyan));
}

.bar-row>strong {
    color: var(--text);

    font-family: var(--font-mono);
    font-size: 0.68rem;
    text-align: right;
}

.company-list {
    display: grid;
}

.company-row {
    display: flex;

    align-items: center;
    justify-content: space-between;

    gap: 18px;

    padding: 11px 0;

    border-bottom: 1px solid var(--line);
}

.company-row:last-child {
    border-bottom: 0;
}

.company-row>div:first-child {
    display: grid;
    gap: 4px;

    min-width: 0;
}

.company-row strong {
    overflow: hidden;

    color: var(--text);

    font-family: var(--font-display);
    font-size: 0.78rem;

    text-overflow: ellipsis;
    white-space: nowrap;
}

.company-row span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.57rem;
}

.company-score {
    display: grid;

    flex: 0 0 auto;

    justify-items: end;
    gap: 2px;
}

.company-score strong {
    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.82rem;
}


/* =========================
   STATES
========================= */

.dashboard-state,
.panel-empty {
    display: grid;

    min-height: 120px;

    place-content: center;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.75rem;
    text-align: center;
}

.dashboard-error {
    color: var(--coral);
}


/* =========================
   RESPONSIVE
========================= */

@media (max-width: 900px) {
    .kpi-primary {
        grid-template-columns: 1fr;
    }

    .kpi-secondary {
        grid-template-columns: repeat(2, minmax(0, 1fr));
    }

    .analytics-grid {
        grid-template-columns: 1fr;
    }
}

@media (max-width: 480px) {
    .kpi-secondary {
        grid-template-columns: 1fr;
    }

    .bar-row {
        grid-template-columns: minmax(72px, 0.8fr) minmax(80px, 1.8fr) 30px;
        gap: 7px;
    }
}
</style>