<script setup lang="ts">
import { computed, onMounted, ref } from "vue";

const API_URL =
    import.meta.env.VITE_API_URL ||
    "/api";

interface AdminEntry {
    id: string;
    email: string;
    player_name: string;
    company_name: string;
    score: number;
    lightning_collected: number;
    entered_at: string;
}

interface AnalyticsResponse {
    players: {
        unique_players: number;
        total_games: number;
        repeat_players: number;
        average_games_per_player: number;
        replay_rate: number;
    };

    gameplay: {
        average_score: number;
        highest_score: number;
        average_lightning: number;
        average_duration: number;
    };

    leaderboard: {
        unique_entries: number;
        conversion_rate: number;
    };

    activity: {
        games_over_time: Array<{
            period: string;
            games: number;
        }>;
    };

    distributions: {
        scores: Array<{
            label: string;
            minimum: number;
            maximum: number;
            games: number;
        }>;

        games_per_player: Array<{
            games: number;
            players: number;
        }>;
    };

    companies: Array<{
        company: string;
        players: number;
        games: number;
        best_score: number;
        average_score: number;
    }>;
}

const authenticated = ref(false);

const adminKey = ref("");
const loginError = ref("");

const loading = ref(false);
const exportLoading = ref(false);

const error = ref("");

const entries = ref<AdminEntry[]>([]);

const search = ref("");
const name = ref("");
const email = ref("");
const company = ref("");

const analytics =
    ref<AnalyticsResponse | null>(
        null,
    );

const analyticsLoading =
    ref(false);

const analyticsError =
    ref("");

const excludedIds = ref<Set<string>>(
    new Set(),
);

const filtersActive = computed(() => {
    return Boolean(
        search.value.trim() ||
        name.value.trim() ||
        email.value.trim() ||
        company.value.trim()
    );
});

const resultCount = computed(
    () => entries.value.length,
);

const exportCount = computed(() => {
    return entries.value.filter(
        (entry) =>
            !excludedIds.value.has(
                entry.id,
            ),
    ).length;
});

const excludedVisibleCount =
    computed(() => {
        return entries.value.filter(
            (entry) =>
                excludedIds.value.has(
                    entry.id,
                ),
        ).length;
    });

const maxGamesOverTime =
    computed(() => {
        if (!analytics.value) {
            return 1;
        }

        return Math.max(
            1,
            ...analytics.value.activity.games_over_time.map(
                item => item.games,
            ),
        );
    });


const maxScoreBucket =
    computed(() => {
        if (!analytics.value) {
            return 1;
        }

        return Math.max(
            1,
            ...analytics.value.distributions.scores.map(
                item => item.games,
            ),
        );
    });


const maxReplayPlayers =
    computed(() => {
        if (!analytics.value) {
            return 1;
        }

        return Math.max(
            1,
            ...analytics.value.distributions.games_per_player.map(
                item => item.players,
            ),
        );
    });


function formatNumber(
    value: number,
) {
    return value.toLocaleString(
        "en-GB",
    );
}


function formatPercent(
    value: number,
) {
    return `${value.toFixed(1)}%`;
}

function toggleExcluded(
    id: string,
) {
    const updated = new Set(excludedIds.value);

    if (updated.has(id)) {
        updated.delete(id);
    } else {
        updated.add(id);
    }

    excludedIds.value = updated;
}

function resetExclusions() {
    excludedIds.value =
        new Set();
}

function buildParams() {
    const params =
        new URLSearchParams();

    if (search.value.trim()) {
        params.set(
            "search",
            search.value.trim(),
        );
    }

    if (name.value.trim()) {
        params.set(
            "name",
            name.value.trim(),
        );
    }

    if (email.value.trim()) {
        params.set(
            "email",
            email.value.trim(),
        );
    }

    if (company.value.trim()) {
        params.set(
            "company",
            company.value.trim(),
        );
    }

    return params;
}

async function checkSession() {
    try {
        const response = await fetch(`${API_URL}/admin/session`,
            {
                credentials: "include",
            },
        );

        if (!response.ok) {
            authenticated.value = false;
            return
        }

        authenticated.value = true;

        await loadEntries();
        await loadAnalytics();
    } catch {
        authenticated.value = false;
    }
}

async function login() {
    loginError.value = "";
    error.value = "";

    if (!adminKey.value.trim()) {
        loginError.value =
            "Enter the admin key.";

        return;
    }

    try {
        const response =
            await fetch(
                `${API_URL}/admin/login`,
                {
                    method: "POST",

                    credentials:
                        "include",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        key:
                            adminKey.value,
                    }),
                },
            );

        if (!response.ok) {
            loginError.value =
                "Invalid admin key.";

            return;
        }

        authenticated.value =
            true;

        adminKey.value =
            "";

        await loadEntries();

    } catch (err) {
        console.error(
            "Admin login failed:",
            err,
        );

        loginError.value =
            "Unable to sign in.";
    }
}

async function loadEntries() {
    loading.value = true;
    error.value = "";

    try {
        const params =
            buildParams();

        const query =
            params.toString();

        const response =
            await fetch(
                `${API_URL}/admin/entries${query
                    ? `?${query}`
                    : ""
                }`,
                {
                    credentials:
                        "include",
                },
            );

        if (
            response.status === 401
        ) {
            authenticated.value =
                false;

            entries.value = [];

            return;
        }

        if (!response.ok) {
            throw new Error(
                "Unable to load entries.",
            );
        }

        entries.value =
            await response.json();

        authenticated.value =
            true;

    } catch (err) {
        console.error(
            "Failed to load admin entries:",
            err,
        );

        error.value =
            "Unable to load entries.";

    } finally {
        loading.value = false;
    }
}

async function exportCsv() {
    exportLoading.value = true;
    error.value = "";

    try {
        const response =
            await fetch(
                `${API_URL}/admin/export/marketing`,
                {
                    method: "POST",

                    credentials:
                        "include",

                    headers: {
                        "Content-Type":
                            "application/json",
                    },

                    body: JSON.stringify({
                        search:
                            search.value.trim()
                            || null,

                        name:
                            name.value.trim()
                            || null,

                        email:
                            email.value.trim()
                            || null,

                        company:
                            company.value.trim()
                            || null,

                        excluded_ids:
                            Array.from(
                                excludedIds.value,
                            ),
                    }),
                },
            );

        if (response.status === 401) {
            authenticated.value = false;

            entries.value = [];

            return;
        }

        if (!response.ok) {
            throw new Error(
                "Export failed.",
            );
        }

        const blob =
            await response.blob();

        const url =
            URL.createObjectURL(
                blob,
            );

        const link =
            document.createElement(
                "a",
            );

        link.href = url;

        link.download =
            "lightning-flight-marketing.csv";

        document.body.appendChild(
            link,
        );

        link.click();

        link.remove();

        URL.revokeObjectURL(
            url,
        );

    } catch (err) {
        console.error(
            "CSV export failed:",
            err,
        );

        error.value =
            "Unable to export data.";

    } finally {
        exportLoading.value =
            false;
    }
}

async function logout() {
    try {
        await fetch(
            `${API_URL}/admin/logout`,
            {
                method: "POST",

                credentials:
                    "include",
            },
        );
    } finally {
        authenticated.value =
            false;

        entries.value = [];

        clearFilters();
    }
}

async function loadAnalytics() {
    analyticsLoading.value = true;
    analyticsError.value = "";

    try {
        const response =
            await fetch(
                `${API_URL}/admin/analytics`,
                {
                    credentials:
                        "include",
                },
            );

        if (response.status === 401) {
            authenticated.value =
                false;

            analytics.value =
                null;

            return;
        }

        if (!response.ok) {
            throw new Error(
                "Unable to load analytics.",
            );
        }

        analytics.value =
            await response.json();

    } catch (err) {
        console.error(
            "Failed to load analytics:",
            err,
        );

        analyticsError.value =
            "Unable to load analytics.";

    } finally {
        analyticsLoading.value =
            false;
    }
}

function clearFilters() {
    search.value = "";
    name.value = "";
    email.value = "";
    company.value = "";

    if (authenticated.value) {
        void loadEntries();
    }
}

function formatDate(
    value: string,
) {
    return new Intl.DateTimeFormat(
        "en-GB",
        {
            dateStyle: "medium",
            timeStyle: "short",
        },
    ).format(
        new Date(value),
    );
}

onMounted(() => {
    void checkSession();
});
</script>

<template>
    <main class="admin-page">

        <section v-if="!authenticated" class="admin-login-card">
            <p class="section-kicker">
                <i class="kicker-bolt">⚡</i>
                LIGHTNING FLIGHT
            </p>

            <h1>
                Admin
            </h1>

            <p class="admin-intro">
                Sign in to view, filter and export
                leaderboard entry data.
            </p>

            <form class="admin-login-form" @submit.prevent="login">
                <label for="admin-key">
                    ADMIN KEY
                </label>

                <input id="admin-key" v-model="adminKey" type="password" autocomplete="current-password"
                    placeholder="Enter admin key" />

                <p v-if="loginError" class="form-error">
                    {{ loginError }}
                </p>

                <button class="primary-button" type="submit">
                    Sign in
                </button>
            </form>
        </section>

        <section v-else class="admin-dashboard">
            <header class="admin-header">
                <section class="analytics-section">

                    <div class="analytics-heading">

                        <div>
                            <span class="analytics-kicker">
                                EVENT ANALYTICS
                            </span>

                            <h2>
                                Performance overview
                            </h2>
                        </div>

                        <button class="secondary-button" type="button" :disabled="analyticsLoading"
                            @click="loadAnalytics">
                            {{
                                analyticsLoading
                                    ? "Refreshing..."
                                    : "Refresh"
                            }}
                        </button>

                    </div>


                    <div v-if="analyticsLoading && !analytics" class="analytics-state">
                        Loading analytics...
                    </div>


                    <div v-else-if="analyticsError && !analytics" class="analytics-state analytics-error">
                        {{ analyticsError }}
                    </div>


                    <template v-else-if="analytics">

                        <div class="analytics-kpis">

                            <article class="analytics-card">
                                <span>
                                    UNIQUE PLAYERS
                                </span>

                                <strong>
                                    {{
                                        formatNumber(
                                            analytics.players.unique_players
                                        )
                                    }}
                                </strong>
                            </article>


                            <article class="analytics-card">
                                <span>
                                    GAMES PLAYED
                                </span>

                                <strong>
                                    {{
                                        formatNumber(
                                            analytics.players.total_games
                                        )
                                    }}
                                </strong>
                            </article>


                            <article class="analytics-card">
                                <span>
                                    REPLAY RATE
                                </span>

                                <strong>
                                    {{
                                        formatPercent(
                                            analytics.players.replay_rate
                                        )
                                    }}
                                </strong>

                                <small>
                                    {{
                                        analytics.players.repeat_players
                                    }}
                                    repeat players
                                </small>
                            </article>


                            <article class="analytics-card">
                                <span>
                                    LEADERBOARD CONVERSION
                                </span>

                                <strong>
                                    {{
                                        formatPercent(
                                            analytics.leaderboard.conversion_rate
                                        )
                                    }}
                                </strong>

                                <small>
                                    {{
                                        analytics.leaderboard.unique_entries
                                    }}
                                    unique contacts
                                </small>
                            </article>


                            <article class="analytics-card">
                                <span>
                                    HIGHEST SCORE
                                </span>

                                <strong>
                                    {{
                                        formatNumber(
                                            analytics.gameplay.highest_score
                                        )
                                    }}
                                </strong>
                            </article>


                            <article class="analytics-card">
                                <span>
                                    AVG SCORE
                                </span>

                                <strong>
                                    {{
                                        Math.round(
                                            analytics.gameplay.average_score
                                        ).toLocaleString()
                                    }}
                                </strong>
                            </article>


                            <article class="analytics-card">
                                <span>
                                    AVG LIGHTNING
                                </span>

                                <strong>
                                    {{
                                        analytics.gameplay.average_lightning
                                            .toFixed(1)
                                    }}
                                </strong>
                            </article>


                            <article class="analytics-card">
                                <span>
                                    AVG GAME TIME
                                </span>

                                <strong>
                                    {{
                                        analytics.gameplay.average_duration
                                            .toFixed(1)
                                    }}s
                                </strong>
                            </article>

                        </div>


                        <div class="analytics-grid">

                            <!-- GAMES OVER TIME -->

                            <article class="analytics-panel">

                                <div class="panel-heading">
                                    <div>
                                        <span>
                                            ACTIVITY
                                        </span>

                                        <h3>
                                            Games over time
                                        </h3>
                                    </div>
                                </div>


                                <div v-if="
                                    analytics.activity.games_over_time.length === 0
                                " class="panel-empty">
                                    No activity data yet.
                                </div>


                                <div v-else class="bar-chart">
                                    <div v-for="item in analytics.activity.games_over_time" :key="item.period"
                                        class="bar-row">
                                        <span class="bar-label">
                                            {{ item.period }}
                                        </span>

                                        <div class="bar-track">
                                            <div class="bar-fill" :style="{
                                                width:
                                                    `${(
                                                        item.games /
                                                        maxGamesOverTime
                                                    ) * 100
                                                    }%`,
                                            }" />
                                        </div>

                                        <strong>
                                            {{ item.games }}
                                        </strong>
                                    </div>
                                </div>

                            </article>


                            <!-- SCORE DISTRIBUTION -->

                            <article class="analytics-panel">

                                <div class="panel-heading">
                                    <div>
                                        <span>
                                            SCORES
                                        </span>

                                        <h3>
                                            Score distribution
                                        </h3>
                                    </div>
                                </div>


                                <div class="bar-chart">
                                    <div v-for="bucket in analytics.distributions.scores" :key="bucket.label"
                                        class="bar-row">
                                        <span class="bar-label">
                                            {{ bucket.label }}
                                        </span>

                                        <div class="bar-track">
                                            <div class="bar-fill" :style="{
                                                width:
                                                    `${(
                                                        bucket.games /
                                                        maxScoreBucket
                                                    ) * 100
                                                    }%`,
                                            }" />
                                        </div>

                                        <strong>
                                            {{ bucket.games }}
                                        </strong>
                                    </div>
                                </div>

                            </article>


                            <!-- REPLAY DISTRIBUTION -->

                            <article class="analytics-panel">

                                <div class="panel-heading">
                                    <div>
                                        <span>
                                            ENGAGEMENT
                                        </span>

                                        <h3>
                                            Games per player
                                        </h3>
                                    </div>
                                </div>


                                <div class="bar-chart">
                                    <div v-for="item in analytics.distributions.games_per_player" :key="item.games"
                                        class="bar-row">
                                        <span class="bar-label">
                                            {{ item.games }}
                                            {{
                                                item.games === 1
                                                    ? "game"
                                                    : "games"
                                            }}
                                        </span>

                                        <div class="bar-track">
                                            <div class="bar-fill" :style="{
                                                width:
                                                    `${(
                                                        item.players /
                                                        maxReplayPlayers
                                                    ) * 100
                                                    }%`,
                                            }" />
                                        </div>

                                        <strong>
                                            {{ item.players }}
                                        </strong>
                                    </div>
                                </div>

                            </article>


                            <!-- COMPANIES -->

                            <article class="analytics-panel">

                                <div class="panel-heading">
                                    <div>
                                        <span>
                                            COMPANIES
                                        </span>

                                        <h3>
                                            Top companies
                                        </h3>
                                    </div>
                                </div>


                                <div v-if="analytics.companies.length === 0" class="panel-empty">
                                    No company data yet.
                                </div>


                                <div v-else class="company-list">
                                    <div v-for="company in analytics.companies" :key="company.company"
                                        class="company-row">
                                        <div>
                                            <strong>
                                                {{ company.company }}
                                            </strong>

                                            <span>
                                                {{ company.players }}
                                                players ·
                                                {{ company.games }}
                                                games
                                            </span>
                                        </div>


                                        <div class="company-score">
                                            <strong>
                                                {{
                                                    company.best_score
                                                        .toLocaleString()
                                                }}
                                            </strong>

                                            <span>
                                                best
                                            </span>
                                        </div>
                                    </div>
                                </div>

                            </article>

                        </div>

                    </template>

                </section>
                <div>
                    <p class="section-kicker">
                        <i class="kicker-bolt">⚡</i>
                        LIGHTNING FLIGHT
                    </p>

                    <h1>
                        Event Admin
                    </h1>

                    <p>
                        Filter and export leaderboard entry data.
                    </p>
                </div>

                <button class="logout-button" type="button" @click="logout">
                    Logout
                </button>
            </header>

            <section class="admin-filters">

                <div class="filter-heading">
                    <div>
                        <span>
                            DATA FILTERS
                        </span>

                        <strong>
                            Find the records you need
                        </strong>
                    </div>

                    <span class="record-count">
                        {{ resultCount }}
                        results
                    </span>
                </div>

                <div class="filter-grid">

                    <div class="filter-field filter-field--wide">
                        <label for="admin-search">
                            SEARCH ALL
                        </label>

                        <input id="admin-search" v-model="search" type="search" placeholder="Name, email or company"
                            @keyup.enter="loadEntries" />
                    </div>

                    <div class="filter-field">
                        <label for="filter-name">
                            NAME
                        </label>

                        <input id="filter-name" v-model="name" type="text" placeholder="e.g. Sarah"
                            @keyup.enter="loadEntries" />
                    </div>

                    <div class="filter-field">
                        <label for="filter-email">
                            EMAIL
                        </label>

                        <input id="filter-email" v-model="email" type="text" placeholder="e.g. @gmail.com"
                            @keyup.enter="loadEntries" />
                    </div>

                    <div class="filter-field">
                        <label for="filter-company">
                            COMPANY
                        </label>

                        <input id="filter-company" v-model="company" type="text" placeholder="e.g. Lightning"
                            @keyup.enter="loadEntries" />
                    </div>

                </div>

                <div class="filter-actions">

                    <button class="primary-button" type="button" :disabled="loading" @click="loadEntries">
                        {{
                            loading
                                ? "Loading..."
                                : "Apply filters"
                        }}
                    </button>


                    <button class="secondary-button" type="button" :disabled="!filtersActive" @click="clearFilters">
                        Clear filters
                    </button>


                    <button v-if="excludedIds.size > 0" class="secondary-button" type="button" @click="resetExclusions">
                        Include all
                    </button>


                    <span v-if="excludedVisibleCount > 0" class="excluded-count">
                        {{ excludedVisibleCount }}
                        excluded
                    </span>


                    <button class="export-button" type="button" :disabled="exportLoading ||
                        exportCount === 0
                        " @click="exportCsv">
                        {{
                            exportLoading
                                ? "Exporting..."
                                : `Export ${exportCount} records`
                        }}
                    </button>

                </div>

            </section>

            <p v-if="error" class="admin-error">
                {{ error }}
            </p>

            <section class="admin-results">

                <div v-if="loading && entries.length === 0" class="admin-state">
                    Loading entries...
                </div>

                <div v-else-if="entries.length === 0" class="admin-state">
                    No matching records.
                </div>

                <div v-else class="admin-table-wrapper">
                    <table class="admin-table">
                        <thead>
                            <tr>
                                <th class="exclude-column">
                                    Export
                                </th>

                                <th>
                                    Name
                                </th>

                                <th>
                                    Company
                                </th>

                                <th>
                                    Email
                                </th>

                                <th>
                                    Score
                                </th>

                                <th>
                                    ⚡
                                </th>

                                <th>
                                    Entered
                                </th>
                            </tr>
                        </thead>

                        <tbody>
                            <tr v-for="entry in entries" :key="entry.id" :class="{
                                'entry-excluded':
                                    excludedIds.has(entry.id),
                            }">
                                <td class="exclude-column">
                                    <input type="checkbox" :checked="!excludedIds.has(entry.id,)"
                                        :aria-label="`Include ${entry.player_name} in export`"
                                        @change="toggleExcluded(entry.id,)" />
                                </td>
                                <td>
                                    <strong>
                                        {{ entry.player_name }}
                                    </strong>
                                </td>

                                <td>
                                    {{ entry.company_name }}
                                </td>

                                <td>
                                    <a :href="`mailto:${entry.email}`">
                                        {{ entry.email }}
                                    </a>
                                </td>

                                <td>
                                    {{ entry.score.toLocaleString() }}
                                </td>

                                <td>
                                    {{ entry.lightning_collected }}
                                </td>

                                <td>
                                    {{ formatDate(entry.entered_at) }}
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>

            </section>
        </section>

    </main>
</template>

<style scoped>
.admin-page {
    width: 100%;
    min-height: 100dvh;

    padding: 28px;

    overflow-y: auto;

    color: var(--text);

    background:
        radial-gradient(circle at 50% 0%,
            rgba(var(--volt-rgb), .08),
            transparent 34%),
        var(--ink);

    font-family: var(--font-body);
}


/* =========================
   LOGIN
========================= */

.admin-login-card {
    width: min(100%, 430px);

    margin: 8vh auto 0;

    padding: 28px;

    border: 1px solid var(--line);
    border-radius: 20px;

    background:
        linear-gradient(165deg,
            var(--surface),
            var(--surface-2));
}


.admin-login-card h1 {
    margin: 8px 0 10px;

    font-family: var(--font-display);
    font-size: 2.3rem;
}

.section-kicker {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    margin: 0;

    color: var(--volt);

    font-family: var(--font-mono);
    font-size: .6rem;
    font-weight: 700;
    letter-spacing: .14em;
    text-transform: uppercase;
}

.kicker-bolt {
    font-style: normal;
}


.admin-intro {
    margin: 0 0 26px;

    color: var(--text-dim);

    font-size: .85rem;
    line-height: 1.6;
}


.admin-login-form {
    display: grid;
    gap: 12px;
}


.admin-login-form label,
.filter-field label {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: .58rem;
    font-weight: 700;

    letter-spacing: .12em;
}


.admin-login-form input,
.filter-field input {
    width: 100%;

    padding: 13px 14px;

    border: 1px solid var(--line);
    border-radius: 12px;

    outline: none;

    color: var(--text);

    background:
        rgba(255, 255, 255, .035);

    font: inherit;
}


.admin-login-form input:focus,
.filter-field input:focus {
    border-color:
        rgba(var(--volt-rgb), .55);
}


/* =========================
   DASHBOARD
========================= */

.admin-dashboard {
    width: min(100%, 1180px);

    margin: 0 auto;
}


.admin-header {
    display: flex;

    justify-content: space-between;
    align-items: flex-start;

    gap: 20px;

    margin-bottom: 24px;
}


.admin-header h1 {
    margin: 7px 0;

    font-family: var(--font-display);
    font-size: clamp(2rem, 5vw, 3rem);
}


.admin-header p:last-child {
    margin: 0;

    color: var(--text-dim);
}

/* =========================
   ANALYTICS
========================= */

.analytics-section {
    margin-bottom: 22px;
}


.analytics-heading {
    display: flex;

    align-items: flex-end;
    justify-content: space-between;

    gap: 20px;

    margin-bottom: 16px;
}


.analytics-kicker,
.panel-heading span {
    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.56rem;
    font-weight: 700;

    letter-spacing: 0.12em;
}


.analytics-heading h2,
.panel-heading h3 {
    margin: 5px 0 0;

    color: var(--text);

    font-family: var(--font-display);
}


.analytics-heading h2 {
    font-size: 1.45rem;
}


.analytics-kpis {
    display: grid;

    grid-template-columns:
        repeat(4, minmax(0, 1fr));

    gap: 12px;

    margin-bottom: 14px;
}


.analytics-card {
    display: grid;

    min-width: 0;

    gap: 7px;

    padding: 16px;

    border: 1px solid var(--line);
    border-radius: 16px;

    background:
        linear-gradient(155deg,
            rgba(255, 255, 255, 0.035),
            rgba(255, 255, 255, 0.015));
}


.analytics-card>span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.54rem;
    font-weight: 700;

    letter-spacing: 0.1em;
}


.analytics-card>strong {
    color: var(--text);

    font-family: var(--font-display);
    font-size: clamp(1.35rem,
            3vw,
            2rem);

    letter-spacing: -0.03em;
}


.analytics-card>small {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.58rem;
}


.analytics-grid {
    display: grid;

    grid-template-columns:
        repeat(2, minmax(0, 1fr));

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


.panel-heading h3 {
    font-size: 1rem;
}


.bar-chart {
    display: grid;
    gap: 11px;
}


.bar-row {
    display: grid;

    grid-template-columns:
        minmax(90px, 0.9fr) minmax(100px, 2fr) 36px;

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

    background:
        rgba(255, 255, 255, 0.06);
}


.bar-fill {
    height: 100%;

    min-width: 2px;

    border-radius: inherit;

    background:
        linear-gradient(90deg,
            var(--volt),
            var(--cyan));
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

    border-bottom:
        1px solid var(--line);
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


.analytics-state,
.panel-empty {
    display: grid;

    min-height: 120px;

    place-content: center;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.7rem;

    text-align: center;
}


.analytics-error {
    color: var(--coral);
}


@media (max-width: 900px) {

    .analytics-kpis {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));
    }


    .analytics-grid {
        grid-template-columns: 1fr;
    }

}


@media (max-width: 520px) {

    .analytics-heading {
        align-items: center;
    }


    .analytics-kpis {
        grid-template-columns:
            repeat(2, minmax(0, 1fr));

        gap: 8px;
    }


    .analytics-card {
        padding: 13px;
    }


    .bar-row {
        grid-template-columns:
            minmax(72px, 0.8fr) minmax(80px, 1.8fr) 30px;

        gap: 7px;
    }

}

/* =========================
   FILTERS
========================= */

.admin-filters {
    margin-bottom: 20px;
    padding: 20px;

    border: 1px solid var(--line);
    border-radius: 18px;

    background: var(--surface);
}


.filter-heading {
    display: flex;

    justify-content: space-between;
    align-items: flex-end;

    gap: 20px;

    margin-bottom: 18px;
}


.filter-heading>div {
    display: grid;
    gap: 4px;
}


.filter-heading span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: .58rem;
    font-weight: 700;

    letter-spacing: .1em;
}


.filter-heading strong {
    font-family: var(--font-display);
    font-size: 1.05rem;
}


.record-count {
    white-space: nowrap;

    color: var(--volt) !important;
}


.filter-grid {
    display: grid;

    grid-template-columns:
        repeat(3, minmax(0, 1fr));

    gap: 14px;
}


.filter-field {
    display: grid;
    gap: 7px;
}


.filter-field--wide {
    grid-column: 1 / -1;
}


.filter-actions {
    display: flex;

    flex-wrap: wrap;

    gap: 10px;

    margin-top: 18px;
}


/* =========================
   BUTTONS
========================= */

.primary-button,
.secondary-button,
.export-button,
.logout-button {
    min-height: 42px;

    padding: 0 16px;

    border-radius: 11px;

    font-family: var(--font-display);
    font-size: .76rem;
    font-weight: 700;

    cursor: pointer;
}


.primary-button {
    border: 0;

    color: var(--ink);

    background:
        linear-gradient(100deg,
            var(--volt),
            var(--volt-light));
}


.secondary-button,
.logout-button {
    border: 1px solid var(--line);

    color: var(--text-dim);

    background:
        rgba(255, 255, 255, .03);
}


.export-button {
    margin-left: auto;

    border: 1px solid rgba(var(--cyan-rgb), .3);

    color: var(--cyan);

    background:
        rgba(var(--cyan-rgb), .08);
}


button:disabled {
    opacity: .45;

    cursor: not-allowed;
}


/* =========================
   RESULTS
========================= */

.admin-results {
    border: 1px solid var(--line);
    border-radius: 18px;

    overflow: hidden;

    background: var(--surface);
}


.admin-table-wrapper {
    width: 100%;

    overflow-x: auto;
}


.admin-table {
    width: 100%;

    border-collapse: collapse;
}


.admin-table th {
    padding: 12px 14px;

    color: var(--text-faint);

    background:
        rgba(255, 255, 255, .025);

    font-family: var(--font-mono);
    font-size: .56rem;

    letter-spacing: .09em;

    text-align: left;
    text-transform: uppercase;
}


.admin-table td {
    padding: 14px;

    border-top: 1px solid var(--line);

    color: var(--text-dim);

    font-size: .76rem;

    white-space: nowrap;
}

.entry-excluded {
    opacity: .4;
}

.entry-excluded td:not(.exclude-column) {
    filter: grayscale(.8);
}

.entry-excluded:hover {
    opacity: .5;
}

.exclude-column {
    width: 64px;

    text-align: center !important;
}

.exclude-column input {
    width: 17px;
    height: 17px;

    accent-color: var(--volt);

    cursor: pointer;
}

.excluded-count {
    display: inline-flex;

    align-items: center;

    color: var(--coral);

    font-family: var(--font-mono);
    font-size: .64rem;
    font-weight: 700;

    white-space: nowrap;
}


.admin-table td strong {
    color: var(--text);
}


.admin-table a {
    color: var(--cyan);

    text-decoration: none;
}


.admin-table a:hover {
    text-decoration: underline;
}


.admin-state {
    display: grid;

    min-height: 220px;

    place-content: center;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: .78rem;
}


/* =========================
   MESSAGES
========================= */

.form-error,
.admin-error {
    color: var(--coral);

    font-family: var(--font-mono);
    font-size: .7rem;
}


.admin-error {
    margin: 0 0 14px;
}


/* =========================
   MOBILE
========================= */

@media (max-width: 760px) {
    .admin-page {
        padding: 16px;
    }

    .admin-header {
        align-items: center;
    }

    .filter-grid {
        grid-template-columns: 1fr;
    }

    .filter-field--wide {
        grid-column: auto;
    }

    .export-button {
        width: 100%;

        margin-left: 0;
    }
}
</style>