<script setup lang="ts">
import { computed, inject, onMounted, ref } from "vue"

import {
    type AdminEntry,
    getAdminEntries,
    exportMarketingCsv,
} from "../services/adminApi"

const handleAdminError =
    inject<(err: unknown) => boolean>("handleAdminError")

const loading = ref(true)
const exportLoading = ref(false)
const error = ref("")

const entries = ref<AdminEntry[]>([])

const search = ref("")
const name = ref("")
const email = ref("")
const company = ref("")

const excludedIds = ref<Set<string>>(new Set())

const filtersActive = computed(() => {
    return Boolean(
        search.value.trim() ||
        name.value.trim() ||
        email.value.trim() ||
        company.value.trim(),
    )
})

const resultCount = computed(() => entries.value.length)

const exportCount = computed(() => {
    return entries.value.filter(
        (entry) => !excludedIds.value.has(entry.id),
    ).length
})

const excludedVisibleCount = computed(() => {
    return entries.value.filter(
        (entry) => excludedIds.value.has(entry.id),
    ).length
})

function toggleExcluded(id: string) {
    const updated = new Set(excludedIds.value)

    if (updated.has(id)) {
        updated.delete(id)
    } else {
        updated.add(id)
    }

    excludedIds.value = updated
}

function resetExclusions() {
    excludedIds.value = new Set()
}

function currentFilters() {
    return {
        search: search.value,
        name: name.value,
        email: email.value,
        company: company.value,
    }
}

async function loadEntries() {
    loading.value = true
    error.value = ""

    try {
        entries.value = await getAdminEntries(currentFilters())
    } catch (err) {
        if (handleAdminError?.(err)) {
            return
        }

        console.error("Failed to load admin entries:", err)

        error.value = "Unable to load entries."
    } finally {
        loading.value = false
    }
}

async function exportCsv() {
    exportLoading.value = true
    error.value = ""

    try {
        const blob = await exportMarketingCsv(
            currentFilters(),
            Array.from(excludedIds.value),
        )

        const url = URL.createObjectURL(blob)
        const link = document.createElement("a")

        link.href = url
        link.download = "lightning-flight-marketing.csv"

        document.body.appendChild(link)
        link.click()
        link.remove()

        URL.revokeObjectURL(url)
    } catch (err) {
        if (handleAdminError?.(err)) {
            return
        }

        console.error("CSV export failed:", err)

        error.value = "Unable to export data."
    } finally {
        exportLoading.value = false
    }
}

function clearFilters() {
    search.value = ""
    name.value = ""
    email.value = ""
    company.value = ""

    void loadEntries()
}

function formatDate(value: string) {
    return new Intl.DateTimeFormat("en-GB", {
        dateStyle: "medium",
        timeStyle: "short",
    }).format(new Date(value))
}

onMounted(loadEntries)
</script>

<template>
    <section class="export-tab">

        <div class="export-heading">
            <p class="export-kicker">
                Leaderboard entries
            </p>

            <h2>
                Export data
            </h2>
        </div>

        <section class="admin-filters">

            <div class="filter-heading">
                <div>
                    <span>Data filters</span>
                    <strong>Find the records you need</strong>
                </div>

                <span class="record-count" aria-live="polite">
                    {{ resultCount }} results
                </span>
            </div>

            <div class="filter-grid">
                <div class="filter-field filter-field--wide">
                    <label for="admin-search">Search all</label>
                    <input id="admin-search" v-model="search" type="search" placeholder="Name, email or company"
                        @keyup.enter="loadEntries" />
                </div>

                <div class="filter-field">
                    <label for="filter-name">Name</label>
                    <input id="filter-name" v-model="name" type="text" placeholder="e.g. Sarah"
                        @keyup.enter="loadEntries" />
                </div>

                <div class="filter-field">
                    <label for="filter-email">Email</label>
                    <input id="filter-email" v-model="email" type="text" placeholder="e.g. @gmail.com"
                        @keyup.enter="loadEntries" />
                </div>

                <div class="filter-field">
                    <label for="filter-company">Company</label>
                    <input id="filter-company" v-model="company" type="text" placeholder="e.g. Lightning"
                        @keyup.enter="loadEntries" />
                </div>
            </div>

            <div class="filter-actions">
                <button class="primary-button" type="button" :disabled="loading" @click="loadEntries">
                    {{ loading ? "Loading..." : "Apply filters" }}
                </button>

                <button class="secondary-button" type="button" :disabled="!filtersActive" @click="clearFilters">
                    Clear filters
                </button>

                <button v-if="excludedIds.size > 0" class="secondary-button" type="button" @click="resetExclusions">
                    Include all
                </button>

                <span v-if="excludedVisibleCount > 0" class="excluded-count" aria-live="polite">
                    {{ excludedVisibleCount }} excluded
                </span>

                <button class="export-button" type="button" :disabled="exportLoading || exportCount === 0"
                    @click="exportCsv">
                    {{ exportLoading ? "Exporting..." : `Export ${exportCount} records` }}
                </button>
            </div>

        </section>

        <p v-if="error" class="admin-error" role="alert">
            {{ error }}
        </p>

        <section class="admin-results">

            <div v-if="loading && entries.length === 0" class="admin-state" aria-live="polite">
                Loading entries...
            </div>

            <div v-else-if="entries.length === 0" class="admin-state">
                No matching records.
            </div>

            <div v-else class="admin-table-wrapper">
                <table class="admin-table">
                    <thead>
                        <tr>
                            <th scope="col" class="exclude-column">Export</th>
                            <th scope="col">Name</th>
                            <th scope="col">Company</th>
                            <th scope="col">Email</th>
                            <th scope="col">Score</th>
                            <th scope="col">⚡</th>
                            <th scope="col">Entered</th>
                        </tr>
                    </thead>

                    <tbody>
                        <tr v-for="entry in entries" :key="entry.id" :class="{
                            'entry-excluded': excludedIds.has(entry.id),
                        }">
                            <td class="exclude-column">
                                <input type="checkbox" :checked="!excludedIds.has(entry.id)"
                                    :aria-label="`Include ${entry.player_name} in export`"
                                    @change="toggleExcluded(entry.id)" />
                            </td>

                            <td>
                                <strong>{{ entry.player_name }}</strong>
                            </td>

                            <td>{{ entry.company_name }}</td>

                            <td>
                                <a :href="`mailto:${entry.email}`">{{ entry.email }}</a>
                            </td>

                            <td>{{ entry.score.toLocaleString() }}</td>

                            <td>{{ entry.lightning_collected }}</td>

                            <td>{{ formatDate(entry.entered_at) }}</td>
                        </tr>
                    </tbody>
                </table>
            </div>

        </section>

    </section>
</template>

<style scoped>
.export-heading {
    margin-bottom: 20px;
}

.export-kicker {
    margin: 0 0 5px;

    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}

.export-heading h2 {
    margin: 0;

    color: var(--text);

    font-family: var(--font-display);
    font-size: clamp(1.6rem, 3.5vw, 2.2rem);
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
    text-transform: uppercase;
}

.filter-heading strong {
    font-family: var(--font-display);
    font-size: 1.05rem;
}

.filter-heading .record-count {
    white-space: nowrap;

    color: var(--volt);
}

.filter-grid {
    display: grid;

    grid-template-columns: repeat(3, minmax(0, 1fr));
    gap: 14px;
}

.filter-field {
    display: grid;
    gap: 7px;
}

.filter-field--wide {
    grid-column: 1 / -1;
}

.filter-field label {
    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.filter-field input {
    width: 100%;

    padding: 13px 14px;

    border: 1px solid var(--line);
    border-radius: 12px;

    outline: none;

    color: var(--text);
    background: rgba(255, 255, 255, 0.035);

    font: inherit;
}

.filter-field input:focus {
    border-color: rgba(var(--volt-rgb), 0.55);
}

.filter-field input:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.filter-actions {
    display: flex;

    flex-wrap: wrap;
    align-items: center;

    gap: 10px;

    margin-top: 18px;
}


/* =========================
   BUTTONS
========================= */

.primary-button,
.secondary-button,
.export-button {
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
    background: linear-gradient(100deg, var(--volt), var(--volt-light));
}

.secondary-button {
    border: 1px solid var(--line);

    color: var(--text-dim);
    background: rgba(255, 255, 255, 0.03);
}

.secondary-button:hover:not(:disabled) {
    color: var(--text);
}

.export-button {
    margin-left: auto;

    border: 1px solid rgba(var(--cyan-rgb), 0.3);

    color: var(--cyan);
    background: rgba(var(--cyan-rgb), 0.08);
}

button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.primary-button:focus-visible,
.secondary-button:focus-visible,
.export-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.excluded-count {
    display: inline-flex;
    align-items: center;

    color: var(--coral);

    font-family: var(--font-mono);
    font-size: 0.64rem;
    font-weight: 700;

    white-space: nowrap;
}


/* =========================
   RESULTS TABLE
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

    background: rgba(255, 255, 255, 0.025);

    font-family: var(--font-mono);
    font-size: 0.56rem;
    letter-spacing: 0.09em;

    text-align: left;
    text-transform: uppercase;
}

.admin-table td {
    padding: 14px;

    border-top: 1px solid var(--line);

    /*
     * Full --text, not a dimmer tier — this is the actual
     * data an admin is scanning, legibility matters more
     * here than it does for decorative/secondary labels.
     */
    color: var(--text);

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

.admin-table a:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.entry-excluded {
    opacity: 0.4;
}

.entry-excluded td:not(.exclude-column) {
    filter: grayscale(0.8);
}

.entry-excluded:hover {
    opacity: 0.55;
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

.exclude-column input:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.admin-state {
    display: grid;

    min-height: 220px;

    place-content: center;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.78rem;
}

.admin-error {
    margin: 0 0 14px;

    color: var(--coral);

    font-family: var(--font-mono);
    font-size: 0.7rem;
}


/* =========================
   MOBILE
========================= */

@media (max-width: 760px) {
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