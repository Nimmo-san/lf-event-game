<script setup lang="ts">
import { onMounted, provide, ref } from "vue"

import {
    AdminAuthError,
    checkAdminSession,
    adminLogin,
    adminLogout
} from "../services/adminApi"

// null = "still checking", so the login form doesn't flash
// on screen for a moment while the session check is in flight.
const authenticated = ref<boolean | null>(null)

const adminKey = ref("")
const loginError = ref("")
const loggingIn = ref(false)

const sidebarOpen = ref(false)

/*
 * Provided to child route views (AdminDashboard, AdminExport)
 * so a 401 from *either* tab's own API calls consistently
 * bounces back to the login screen, without each tab needing
 * its own copy of "if 401, set authenticated = false".
 */
function handleAdminError(err: unknown): boolean {
    if (err instanceof AdminAuthError) {
        authenticated.value = false
        return true
    }

    return false
}

provide("handleAdminError", handleAdminError)

async function checkSession() {
    authenticated.value = await checkAdminSession()
}

async function login() {
    loginError.value = ""

    if (!adminKey.value.trim()) {
        loginError.value = "Enter the admin key."
        return
    }

    loggingIn.value = true

    try {
        await adminLogin(adminKey.value)

        adminKey.value = ""
        authenticated.value = true
    } catch {
        loginError.value = "Invalid admin key."
    } finally {
        loggingIn.value = false
    }
}

async function logout() {
    try {
        await adminLogout()
    } finally {
        authenticated.value = false
        sidebarOpen.value = false
    }
}

onMounted(checkSession)
</script>

<template>
    <main class="admin-page">

        <!-- STILL CHECKING SESSION -->

        <div v-if="authenticated === null" class="admin-checking" aria-live="polite">
            Checking session...
        </div>


        <!-- LOGIN -->

        <section v-else-if="!authenticated" class="admin-login-card">
            <p class="section-kicker">
                <i class="kicker-bolt">⚡</i>
                LIGHTNING FLIGHT
            </p>

            <h1>
                Admin
            </h1>

            <p class="admin-intro">
                Sign in to view analytics and export
                leaderboard entry data.
            </p>

            <form class="admin-login-form" @submit.prevent="login">
                <label for="admin-key">
                    Admin key
                </label>

                <input id="admin-key" v-model="adminKey" type="password" autocomplete="current-password"
                    placeholder="Enter admin key" />

                <p v-if="loginError" class="form-error" role="alert">
                    {{ loginError }}
                </p>

                <button class="primary-button" type="submit" :disabled="loggingIn">
                    {{ loggingIn ? "Signing in..." : "Sign in" }}
                </button>
            </form>
        </section>


        <!-- AUTHENTICATED SHELL -->

        <div v-else class="admin-shell">

            <button type="button" class="sidebar-toggle" :aria-expanded="sidebarOpen" aria-controls="admin-sidebar"
                @click="sidebarOpen = !sidebarOpen">
                <span aria-hidden="true">☰</span>
                Menu
            </button>

            <div v-if="sidebarOpen" class="sidebar-backdrop" @click="sidebarOpen = false"></div>

            <nav id="admin-sidebar" class="admin-sidebar" :class="{ 'admin-sidebar--open': sidebarOpen }"
                aria-label="Admin">

                <p class="section-kicker">
                    <i class="kicker-bolt">⚡</i>
                    LIGHTNING FLIGHT
                </p>

                <h1 class="sidebar-title">
                    Event Admin
                </h1>

                <div class="sidebar-links">
                    <router-link to="/admin/dashboard" class="nav-link" @click="sidebarOpen = false">
                        <span aria-hidden="true">📊</span>
                        Dashboard
                    </router-link>

                    <router-link to="/admin/export" class="nav-link" @click="sidebarOpen = false">
                        <span aria-hidden="true">📤</span>
                        Export data
                    </router-link>
                </div>

                <button class="logout-button" type="button" @click="logout">
                    Logout
                </button>

            </nav>

            <div class="admin-content">
                <router-view />
            </div>

        </div>

    </main>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

.admin-page {
    width: 100%;
    min-height: 100dvh;

    color: var(--text);

    background: var(--ink);

    font-family: var(--font-body);
}


/* =========================
   SHARED KICKER
========================= */

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


/* =========================
   CHECKING / LOGIN
========================= */

.admin-checking {
    display: grid;

    min-height: 100dvh;

    place-content: center;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.8rem;
}

.admin-login-card {
    width: min(100%, 430px);

    margin: 8vh auto 0;
    padding: 28px;

    border: 1px solid var(--line);
    border-radius: 20px;

    background: linear-gradient(165deg, var(--surface), var(--surface-2));
}

.admin-login-card h1 {
    margin: 8px 0 10px;

    font-family: var(--font-display);
    font-size: 2.3rem;
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

.admin-login-form label {
    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.admin-login-form input {
    width: 100%;

    padding: 13px 14px;

    border: 1px solid var(--line);
    border-radius: 12px;

    outline: none;

    color: var(--text);
    background: rgba(255, 255, 255, 0.035);

    font: inherit;
}

.admin-login-form input:focus {
    border-color: rgba(var(--volt-rgb), 0.55);
}

.admin-login-form input:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.form-error {
    color: var(--coral);

    font-family: var(--font-mono);
    font-size: 0.7rem;
}


/* =========================
   BUTTONS (shared)
========================= */

.primary-button,
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
    background: linear-gradient(100deg, var(--volt), var(--volt-light));
}

.primary-button:hover:not(:disabled) {
    filter: brightness(1.06);
}

.logout-button {
    border: 1px solid var(--line);

    color: var(--text-dim);
    background: rgba(255, 255, 255, 0.03);
}

.logout-button:hover {
    color: var(--text);
    border-color: rgba(var(--coral-rgb), 0.4);
}

button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}

.primary-button:focus-visible,
.logout-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}


/* =========================
   SHELL / SIDEBAR
========================= */

.admin-shell {
    display: flex;

    min-height: 100dvh;
}

.sidebar-toggle {
    display: none;
}

.sidebar-backdrop {
    display: none;
}

.admin-sidebar {
    display: flex;

    flex: 0 0 240px;
    flex-direction: column;

    padding: 24px 18px;

    border-right: 1px solid var(--line);

    background: var(--surface);
}

.sidebar-title {
    margin: 8px 0 24px;

    font-family: var(--font-display);
    font-size: 1.3rem;
}

.sidebar-links {
    display: grid;
    gap: 4px;

    margin-bottom: auto;
}

.nav-link {
    display: flex;
    align-items: center;
    gap: 10px;

    padding: 11px 12px;

    border-radius: 10px;

    color: var(--text-dim);

    font-family: var(--font-display);
    font-size: 0.85rem;
    font-weight: 700;

    text-decoration: none;

    transition: background 120ms ease, color 120ms ease;
}

.nav-link:hover {
    color: var(--text);
    background: rgba(255, 255, 255, 0.04);
}

.nav-link:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: -2px;
}

/*
 * Vue Router applies this class (and aria-current="page")
 * to the matching link automatically — no manual active-
 * state computation needed.
 */
.nav-link.router-link-active {
    color: var(--ink);
    background: linear-gradient(100deg, var(--volt), var(--volt-light));
}

.admin-content {
    flex: 1;
    min-width: 0;

    padding: 28px;

    overflow-y: auto;
}


/* =========================
   MOBILE — collapsible sidebar
========================= */

@media (max-width: 860px) {

    .admin-shell {
        display: block;
    }

    .sidebar-toggle {
        display: flex;
        align-items: center;
        gap: 8px;

        width: 100%;

        padding: 14px 16px;

        border: 0;
        border-bottom: 1px solid var(--line);

        color: var(--text);
        background: var(--surface);

        font-family: var(--font-display);
        font-size: 0.85rem;
        font-weight: 700;

        cursor: pointer;
    }

    .sidebar-toggle:focus-visible {
        outline: 2px solid var(--cyan);
        outline-offset: -2px;
    }

    .sidebar-backdrop {
        display: block;

        position: fixed;
        inset: 0;
        z-index: 15;

        background: rgba(7, 7, 12, 0.6);
    }

    .admin-sidebar {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        z-index: 20;

        flex: 0 0 auto;
        width: min(78vw, 280px);

        transform: translateX(-100%);

        transition: transform 180ms ease;
    }

    .admin-sidebar--open {
        transform: translateX(0);
    }

    .admin-content {
        padding: 18px;
    }
}
</style>