<script setup lang="ts">
import { onMounted, provide, ref } from "vue"

import {
    AdminAuthError,
    adminLogin,
    adminLogout,
    checkAdminSession,
} from "../services/adminApi"

import DashboardIcon from "../components/DashboardIcon.vue"
import DashboardExport from "../components/DashboardExport.vue"
import DashboardLogout from "../components/DashboardLogout.vue"

const authenticated = ref<boolean | null>(null)

const adminKey = ref("")
const loginError = ref("")
const loggingIn = ref(false)

const sidebarOpen = ref(
    !window.matchMedia("(max-width: 860px)").matches,
)

const isMobile = window.matchMedia("(max-width: 860px)").matches

function handleAdminError(err: unknown): boolean {
    if (err instanceof AdminAuthError) {
        authenticated.value = false
        return true
    }

    return false
}

provide("handleAdminError", handleAdminError)

function toggleSidebar() {
    sidebarOpen.value = !sidebarOpen.value
}

function closeSidebarOnMobileNav() {
    if (isMobile) {
        sidebarOpen.value = false
    }
}

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
    }
}

onMounted(checkSession)
</script>

<template>
    <main class="admin-page">

        <div v-if="authenticated === null" class="admin-checking" aria-live="polite">
            Checking session...
        </div>

        <section v-else-if="!authenticated" class="admin-login-card">
            <p class="section-kicker">
                <i class="kicker-bolt">⚡</i>
                LIGHTNING FLIGHT
            </p>

            <h1>Admin</h1>

            <p class="admin-intro">
                Sign in to view analytics and export
                leaderboard entry data.
            </p>

            <form class="admin-login-form" @submit.prevent="login">
                <label for="admin-key">Admin key</label>

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

        <div v-else class="admin-shell">

            <div v-if="sidebarOpen && isMobile" class="sidebar-backdrop" @click="sidebarOpen = false"></div>

            <button type="button" class="mobile-toggle" :aria-expanded="sidebarOpen" aria-label="Toggle navigation"
                @click="toggleSidebar">
                <span aria-hidden="true">☰</span>
                Menu
            </button>

            <nav class="admin-sidebar" :class="{
                'admin-sidebar--collapsed': !sidebarOpen && !isMobile,
                'admin-sidebar--open': sidebarOpen && isMobile,
            }" aria-label="Admin">

                <div class="sidebar-top">
                    <p v-if="sidebarOpen" class="section-kicker">
                        <i class="kicker-bolt">⚡</i>
                        LIGHTNING FLIGHT
                    </p>

                    <button type="button" class="sidebar-toggle" :aria-expanded="sidebarOpen"
                        aria-label="Toggle navigation" @click="toggleSidebar">
                        <span aria-hidden="true">☰</span>
                    </button>
                </div>

                <h1 v-if="sidebarOpen" class="sidebar-title">
                    Event Admin
                </h1>

                <div class="sidebar-links">
                    <RouterLink to="/admin/dashboard" class="nav-link" :title="!sidebarOpen ? 'Dashboard' : undefined"
                        @click="closeSidebarOnMobileNav">
                        <span aria-hidden="true">
                            <DashboardIcon/>
                        </span>
                        <span v-if="sidebarOpen" class="nav-label">Dashboard</span>
                    </RouterLink>

                    <RouterLink to="/admin/export" class="nav-link" :title="!sidebarOpen ? 'Export data' : undefined"
                        @click="closeSidebarOnMobileNav">
                        <span aria-hidden="true">
                            <DashboardExport/>
                        </span>
                        <span v-if="sidebarOpen" class="nav-label">Export data</span>
                    </RouterLink>
                </div>

                <button class="logout-button" type="button" :title="!sidebarOpen ? 'Logout' : undefined"
                    @click="logout">
                    <span aria-hidden="true">
                        <DashboardLogout/>
                    </span>
                    <span v-if="sidebarOpen" class="nav-label">Logout</span>
                </button>

            </nav>

            <div class="admin-content">
                <RouterView />
            </div>

        </div>

    </main>
</template>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

/*
 * Page is height-LOCKED to the viewport.
 */
.admin-page {
    width: 100%;
    height: 100dvh;

    overflow: hidden;

    color: var(--text);
    background: var(--ink);

    font-family: var(--font-body);
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

.admin-checking {
    display: grid;

    height: 100%;

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

.primary-button {
    min-height: 42px;

    padding: 0 16px;

    border: 0;
    border-radius: 11px;

    color: var(--ink);
    background: linear-gradient(100deg, var(--volt), var(--volt-light));

    font-family: var(--font-display);
    font-size: 0.76rem;
    font-weight: 700;

    cursor: pointer;
}

.primary-button:hover:not(:disabled) {
    filter: brightness(1.06);
}

.primary-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.primary-button:disabled {
    opacity: 0.45;
    cursor: not-allowed;
}


/* =========================
   SHELL
========================= */

.admin-shell {
    display: flex;

    height: 100%;
}


/* =========================
   SIDEBAR — always exactly
   one viewport tall
========================= */

.admin-sidebar {
    display: flex;

    flex: 0 0 240px;
    flex-direction: column;

    height: 100%;

    padding: 18px 14px;

    border-right: 1px solid var(--line);

    background: var(--surface);

    transition: flex-basis 160ms ease;
}

.admin-sidebar--collapsed {
    flex-basis: 68px;

    align-items: center;

    padding: 18px 10px;
}

.sidebar-top {
    display: flex;

    align-items: center;
    justify-content: space-between;

    width: 100%;

    margin-bottom: 14px;
}

.admin-sidebar--collapsed .sidebar-top {
    justify-content: center;
}

.sidebar-toggle {
    display: grid;

    flex-shrink: 0;

    width: 30px;
    height: 30px;

    place-items: center;

    border: 1px solid var(--line);
    border-radius: 8px;

    color: var(--text-dim);
    background: transparent;

    font-size: 0.9rem;

    cursor: pointer;
}

.sidebar-toggle:hover {
    color: var(--text);
    border-color: rgba(var(--volt-rgb), 0.4);
}

.sidebar-toggle:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}

.sidebar-title {
    margin: 0 0 20px;

    color: var(--text);

    font-family: var(--font-display);
    font-size: 1.2rem;
}

.sidebar-links {
    display: grid;
    gap: 4px;

    width: 100%;

    /*
     * Pushes the logout button to the bottom of the sidebar.
     */
    margin-bottom: auto;
}

.nav-link,
.logout-button {
    display: flex;
    align-items: center;
    gap: 10px;

    width: 100%;

    padding: 11px 12px;

    border: 0;
    border-radius: 10px;

    color: var(--text-dim);
    background: transparent;

    font-family: var(--font-display);
    font-size: 0.85rem;
    font-weight: 700;

    text-decoration: none;

    cursor: pointer;

    transition: background 120ms ease, color 120ms ease;
}

.admin-sidebar--collapsed .nav-link,
.admin-sidebar--collapsed .logout-button {
    justify-content: center;

    padding: 11px;
}

.nav-link:hover,
.logout-button:hover {
    color: var(--text);
    background: rgba(255, 255, 255, 0.04);
}

.nav-link:focus-visible,
.logout-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: -2px;
}

.nav-link.router-link-active {
    color: var(--ink);
    background: linear-gradient(100deg, var(--volt), var(--volt-light));
}

.logout-button {
    margin-top: 12px;

    color: var(--text-faint);
}

.logout-button:hover {
    color: var(--coral);
    background: rgba(var(--coral-rgb), 0.08);
}


/* =========================
   CONTENT — the only
   scrollable region
========================= */

.admin-content {
    flex: 1;
    min-width: 0;
    min-height: 0;

    height: 100%;

    padding: 28px;

    overflow-y: auto;
}


/* =========================
   MOBILE — overlay instead
   of a persistent rail
========================= */

.mobile-toggle {
    display: none;
}

@media (max-width: 860px) {

    .sidebar-top {
        display: none;
    }

    .mobile-toggle {
        display: flex;
        align-items: center;
        gap: 8px;

        position: fixed;
        top: 14px;
        left: 14px;
        z-index: 25;

        padding: 9px 14px;

        border: 1px solid var(--line);
        border-radius: 10px;

        color: var(--text);
        background: var(--surface);

        font-family: var(--font-display);
        font-size: 0.78rem;
        font-weight: 700;

        cursor: pointer;
    }

    .mobile-toggle:focus-visible {
        outline: 2px solid var(--cyan);
        outline-offset: 2px;
    }

    .sidebar-backdrop {
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

        flex-basis: min(78vw, 280px);

        transform: translateX(-100%);

        transition: transform 180ms ease;
    }

    .admin-sidebar--open {
        transform: translateX(0);
    }

    .admin-content {
        padding: 18px;
        padding-top: 64px;
    }
}
</style>