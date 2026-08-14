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
        const params =
            buildParams();

        const query =
            params.toString();

        const response =
            await fetch(
                `${API_URL}/admin/export/marketing${query
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
                        Clear
                    </button>

                    <button class="export-button" type="button" :disabled="exportLoading ||
                        entries.length === 0
                        " @click="exportCsv">
                        {{
                            exportLoading
                                ? "Exporting..."
                                : `Export ${resultCount} records`
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
                            <tr v-for="entry in entries" :key="entry.id">
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
            rgba(var(--volt-rgb), 0.08),
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
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.kicker-bolt {
    font-style: normal;
}


.admin-intro {
    margin: 0 0 26px;

    color: var(--text-dim);

    font-size: 0.85rem;
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
    font-size: 0.58rem;
    font-weight: 700;

    letter-spacing: 0.12em;
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
        rgba(255, 255, 255, 0.035);

    font: inherit;
}


.admin-login-form input:focus,
.filter-field input:focus {
    border-color:
        rgba(var(--volt-rgb), 0.55);
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
    font-size: 0.58rem;
    font-weight: 700;

    letter-spacing: 0.1em;
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
    font-size: 0.76rem;
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
        rgba(255, 255, 255, 0.03);
}


.export-button {
    margin-left: auto;

    border: 1px solid rgba(var(--cyan-rgb), 0.3);

    color: var(--cyan);

    background:
        rgba(var(--cyan-rgb), 0.08);
}


button:disabled {
    opacity: 0.45;

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
        rgba(255, 255, 255, 0.025);

    font-family: var(--font-mono);
    font-size: 0.56rem;

    letter-spacing: 0.09em;

    text-align: left;
    text-transform: uppercase;
}


.admin-table td {
    padding: 14px;

    border-top: 1px solid var(--line);

    color: var(--text-dim);

    font-size: 0.76rem;

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
    font-size: 0.78rem;
}


/* =========================
   MESSAGES
========================= */

.form-error,
.admin-error {
    color: var(--coral);

    font-family: var(--font-mono);
    font-size: 0.7rem;
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