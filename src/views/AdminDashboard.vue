<script setup lang="ts">
import { inject, nextTick, onBeforeUnmount, onMounted, ref } from "vue"
import { Chart, registerables } from "chart.js"

import {
    getAdminAnalytics,
    type AnalyticsResponse,
} from "../services/adminApi"

Chart.register(...registerables)

const handleAdminError =
    inject<(err: unknown) => boolean>("handleAdminError")

const analytics = ref<AnalyticsResponse | null>(null)
const loading = ref(true)
const error = ref("")

const gamesOverTimeCanvas = ref<HTMLCanvasElement | null>(null)
const scoreDistCanvas = ref<HTMLCanvasElement | null>(null)
const gamesPerPlayerCanvas = ref<HTMLCanvasElement | null>(null)

let gamesOverTimeChart: Chart | null = null
let scoreDistChart: Chart | null = null
let gamesPerPlayerChart: Chart | null = null

function formatNumber(value: number) {
    return value.toLocaleString("en-GB")
}

function formatPercent(value: number) {
    return `${value.toFixed(1)}%`
}

/*
 * Reads the real design-token values at runtime instead of
 * hardcoding hex duplicates here, Chart.js draws to canvas,
 * which can't reference CSS custom properties directly the
 * way the rest of the app's CSS does, so this stays in sync with App.
 */
function cssVar(name: string, fallback: string) {
    const value = getComputedStyle(document.documentElement)
        .getPropertyValue(name)
        .trim()

    return value || fallback
}

function destroyCharts() {
    gamesOverTimeChart?.destroy()
    scoreDistChart?.destroy()
    gamesPerPlayerChart?.destroy()

    gamesOverTimeChart = null
    scoreDistChart = null
    gamesPerPlayerChart = null
}

function baseChartOptions(textFaint: string, line: string) {
    return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: { display: false },
            tooltip: {
                titleFont: { family: "'JetBrains Mono', monospace", size: 11 },
                bodyFont: { family: "'JetBrains Mono', monospace", size: 11 },
            },
        },
        scales: {
            x: {
                ticks: {
                    color: textFaint,
                    font: { family: "'JetBrains Mono', monospace", size: 9 },
                    autoSkip: true,
                    maxRotation: 0,
                },
                grid: { color: line, drawTicks: false },
            },
            y: {
                beginAtZero: true,
                ticks: {
                    color: textFaint,
                    font: { family: "'JetBrains Mono', monospace", size: 9 },
                    precision: 0,
                },
                grid: { color: line, drawTicks: false },
            },
        },
    }
}

async function renderCharts() {
    if (!analytics.value) {
        return
    }

    // Canvas refs only exist once the v-else-if="analytics"
    // branch has actually rendered, wait a tick so they're
    // attached before Chart.js tries to draw into them?
    await nextTick()

    destroyCharts()

    const volt = cssVar("--volt", "#92c13b")
    const cyan = cssVar("--cyan", "#5bc0c9")
    const textFaint = cssVar("--text-faint", "#54566b")
    const line = cssVar("--line", "rgba(255,255,255,0.08)")

    const options = baseChartOptions(textFaint, line)

    if (gamesOverTimeCanvas.value) {
        gamesOverTimeChart = new Chart(gamesOverTimeCanvas.value, {
            type: "bar",
            data: {
                labels: analytics.value.activity.games_over_time.map(
                    (item) => item.period,
                ),
                datasets: [{
                    data: analytics.value.activity.games_over_time.map(
                        (item) => item.games,
                    ),
                    backgroundColor: volt,
                    borderRadius: 3,
                    maxBarThickness: 22,
                }],
            },
            options,
        })
    }

    if (scoreDistCanvas.value) {
        scoreDistChart = new Chart(scoreDistCanvas.value, {
            type: "bar",
            data: {
                labels: analytics.value.distributions.scores.map(
                    (bucket) => bucket.label,
                ),
                datasets: [{
                    data: analytics.value.distributions.scores.map(
                        (bucket) => bucket.games,
                    ),
                    backgroundColor: cyan,
                    borderRadius: 3,
                    maxBarThickness: 36,
                }],
            },
            options,
        })
    }

    if (gamesPerPlayerCanvas.value) {
        gamesPerPlayerChart = new Chart(gamesPerPlayerCanvas.value, {
            type: "bar",
            data: {
                labels: analytics.value.distributions.games_per_player.map(
                    (item) => `${item.games}`,
                ),
                datasets: [{
                    data: analytics.value.distributions.games_per_player.map(
                        (item) => item.players,
                    ),
                    backgroundColor: volt,
                    borderRadius: 3,
                    maxBarThickness: 36,
                }],
            },
            options,
        })
    }
}

async function loadAnalytics() {
    loading.value = true
    error.value = ""

    try {
        analytics.value = await getAdminAnalytics()

        await renderCharts()
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

onBeforeUnmount(destroyCharts)
</script>

<template>
    <section class="dashboard" :aria-busy="loading">

        <div class="dashboard-heading">
            <div>
                <p class="dashboard-kicker">Performance overview</p>
                <h2>Dashboard</h2>
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

            <!-- PRIMARY OBJECTIVE — the 3 numbers that actually matter for a lead-gen event game -->

            <div class="kpi-primary">
                <article class="kpi-hero kpi-hero--volt">
                    <span>Leaderboard conversion</span>
                    <strong>{{ formatPercent(analytics.leaderboard.conversion_rate) }}</strong>
                    <small>{{ analytics.leaderboard.unique_entries }} contacts captured</small>
                </article>

                <article class="kpi-hero">
                    <span>Unique players</span>
                    <strong>{{ formatNumber(analytics.players.unique_players) }}</strong>
                    <small>reach</small>
                </article>

                <article class="kpi-hero">
                    <span>Games played</span>
                    <strong>{{ formatNumber(analytics.players.total_games) }}</strong>
                    <small>booth volume</small>
                </article>
            </div>

            <!-- SECONDARY OBJECTIVE — supporting detail -->

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

            <!-- 2x2 GRID — uniform height regardless of how many data points exist -->

            <div class="analytics-grid">

                <article class="analytics-panel">
                    <div class="panel-heading">
                        <span>Activity</span>
                        <h3>Games over time</h3>
                    </div>

                    <div v-if="analytics.activity.games_over_time.length === 0" class="panel-empty">
                        No activity data yet.
                    </div>

                    <div v-else class="chart-wrapper">
                        <canvas ref="gamesOverTimeCanvas" role="img"
                            :aria-label="`Games over time, bar chart with ${analytics.activity.games_over_time.length} time periods. See the table below for exact values.`" />
                    </div>

                    <!--
                        TODO: Canvas has no inherent text content for
                        screen readers — this table carries the
                        same data, visually hidden but present
                        in the DOM, so switching from DOM bars
                        to Chart.js isn't an accessibility
                        regression, very important.
                    -->
                    <table v-if="analytics.activity.games_over_time.length > 0" class="sr-only">
                        <caption>Games over time</caption>
                        <thead>
                            <tr>
                                <th scope="col">Period</th>
                                <th scope="col">Games</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in analytics.activity.games_over_time" :key="item.period">
                                <td>{{ item.period }}</td>
                                <td>{{ item.games }}</td>
                            </tr>
                        </tbody>
                    </table>
                </article>

                <article class="analytics-panel">
                    <div class="panel-heading">
                        <span>Scores</span>
                        <h3>Score distribution</h3>
                    </div>

                    <div class="chart-wrapper">
                        <canvas ref="scoreDistCanvas" role="img"
                            aria-label="Score distribution, bar chart. See the table below for exact values." />
                    </div>

                    <table class="sr-only">
                        <caption>Score distribution</caption>
                        <thead>
                            <tr>
                                <th scope="col">Range</th>
                                <th scope="col">Games</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="bucket in analytics.distributions.scores" :key="bucket.label">
                                <td>{{ bucket.label }}</td>
                                <td>{{ bucket.games }}</td>
                            </tr>
                        </tbody>
                    </table>
                </article>

                <article class="analytics-panel">
                    <div class="panel-heading">
                        <span>Engagement</span>
                        <h3>Games per player</h3>
                    </div>

                    <div class="chart-wrapper">
                        <canvas ref="gamesPerPlayerCanvas" role="img"
                            aria-label="Games per player, bar chart. See the table below for exact values." />
                    </div>

                    <table class="sr-only">
                        <caption>Games per player</caption>
                        <thead>
                            <tr>
                                <th scope="col">Games</th>
                                <th scope="col">Players</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr v-for="item in analytics.distributions.games_per_player" :key="item.games">
                                <td>{{ item.games }}</td>
                                <td>{{ item.players }}</td>
                            </tr>
                        </tbody>
                    </table>
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
   PRIMARY KPIs
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
   SECONDARY KPIs
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
   2x2 GRID — fixed, uniform
   panel height regardless of
   data point count
========================= */

.analytics-grid {
    display: grid;

    grid-template-columns: repeat(2, minmax(0, 1fr));
    grid-auto-rows: 300px;
    gap: 14px;
}

.analytics-panel {
    display: flex;
    flex-direction: column;
    min-width: 0;

    padding: 18px;

    border: 1px solid var(--line);
    border-radius: 18px;

    background: var(--surface);
}

.panel-heading {
    flex: 0 0 auto;

    margin-bottom: 14px;
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

.chart-wrapper {
    position: relative;

    flex: 1;
    min-height: 0;
}


/* =========================
   VISUALLY HIDDEN — screen-
   reader-only data tables,
   the text fallback for the
   canvas charts above
========================= */

.sr-only {
    position: absolute;

    width: 1px;
    height: 1px;
    margin: -1px;
    padding: 0;

    overflow: hidden;

    clip: rect(0, 0, 0, 0);
    white-space: nowrap;

    border: 0;
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
        grid-auto-rows: 260px;
    }
}

@media (max-width: 480px) {
    .kpi-secondary {
        grid-template-columns: 1fr;
    }
}
</style>