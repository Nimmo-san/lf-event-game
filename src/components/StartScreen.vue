<script setup lang="ts">
import { ref } from "vue"
import { useRouter } from "vue-router"

import {
    createPlayerSession,
} from "../services/playerSession"

import {
    ROUND_DURATION,
} from "../game/Game"


const router =
    useRouter()

const playerName =
    ref("")

const companyName =
    ref("")

const error =
    ref("")

const EMAIL_REGEX =
    /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const DOMAIN_REGEX =
  /^(?:[a-z0-9-]+\.)+[a-z]{2,}(?:\/.*)?$/i;

function startGame() {
    error.value = ""

    if (!playerName.value.trim()) {
        error.value =
            "Enter your name."

        return
    }

    const companyError = validateCompanyName(companyName.value)

    if (companyError) {
        error.value =
            companyError;

        return;
    }

    createPlayerSession(
        playerName.value,
        companyName.value,
    )

    router.push({
        name: "game",
    })
}

function validateCompanyName(
    value: string,
): string | null {
    const company =
        value.trim();

    if (!company) {
        return "Enter your company name.";
    }

    if (EMAIL_REGEX.test(company)) {
        return "Enter your company name, not your email address.";
    }

    if (DOMAIN_REGEX.test(company)) {
        return "Enter your company name, not a website.";
    }

    return null;
}
</script>

<template>
    <section class="start-screen">

        <div class="bg-grid" aria-hidden="true"></div>

        <div class="bg-streaks" aria-hidden="true">
            <span class="streak streak-1"></span>
            <span class="streak streak-2"></span>
            <span class="streak streak-3"></span>
        </div>

        <div class="start-card">

            <div class="brand-strip">

                <span class="brand-mark">
                    <i class="brand-bolt">⚡</i>
                    LIGHTNING FIBRE
                </span>

                <span class="live-tag">
                    <i class="live-dot"></i>
                    LIVE AT THIS EVENT
                </span>

            </div>

            <header class="hero">

                <h1 class="hero-title">
                    LIGHTNING
                    <br />
                    FLIGHT<span class="cursor">_</span>
                </h1>

                <p class="hero-tagline">
                    Dodge. Collect. Win.
                </p>

                <p class="hero-desc">
                    Navigate the skies, dodging space rocks
                    and collecting lightning bolts, to
                    supercharge your score.
                </p>

                <p>
                    GOOD LUCK!
                </p>

            </header>

            <div class="bolt-divider" aria-hidden="true">
                <svg viewBox="0 0 400 36" preserveAspectRatio="none" xmlns="http://www.w3.org/2000/svg">
                    <path class="bolt-path" pathLength="1"
                        d="M0,18 L150,18 L172,4 L190,30 L212,10 L232,26 L256,18 L400,18" />
                </svg>
            </div>

            <div class="hud-strip">

                <div class="hud-item">
                    <strong>
                        {{ ROUND_DURATION }}s
                    </strong>

                    <span>
                        Flight
                    </span>
                </div>

                <div class="hud-item">
                    <strong class="hud-icon">
                        <img src="/sprites/glowbolt.svg" alt="Lightning" />
                    </strong>

                    <span>
                        Collect
                    </span>
                </div>

                <div class="hud-item">
                    <strong class="hud-icon">
                        <img src="/sprites/obstacle.png" alt="Obstacle" />
                    </strong>

                    <span>
                        Dodge
                    </span>
                </div>

                <div class="hud-item">
                    <strong>
                        🏆
                    </strong>

                    <span>
                        Win
                    </span>
                </div>

            </div>

            <form class="start-form" @submit.prevent="startGame">

                <div class="form-heading">

                    <strong>
                        Ready to fly?
                    </strong>

                    <span>
                        Let us know your details for the leaderboard.
                    </span>

                </div>

                <div class="form-field">

                    <label for="player-name">
                        Your name
                    </label>

                    <input id="player-name" v-model="playerName" type="text" autocomplete="name" minlength="2" maxlength="100"
                        placeholder="e.g. Emma Pearce" />

                </div>

                <div class="form-field">

                    <label for="company-name">
                        Company
                    </label>

                    <input id="company-name" v-model="companyName" type="text" autocomplete="organization" minlength="2"
                        maxlength="150" placeholder="e.g. Lightning Fibre" />

                </div>

                <p v-if="error" class="form-error">
                    {{ error }}
                </p>

                <button class="start-button" type="submit">
                    <span>
                        <i class="btn-bolt">⚡</i>
                        Play now
                    </span>

                    <span class="start-button-arrow">
                        →
                    </span>
                </button>

            </form>

            <footer class="start-footer">

                <span>
                    {{ ROUND_DURATION }} seconds
                </span>

                <i></i>

                <span>
                    No app required
                </span>

                <i></i>

                <span>
                    Works offline
                </span>

            </footer>

        </div>

    </section>
</template>

<style lang="css" scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;700&family=Inter:wght@400;600;700&family=JetBrains+Mono:wght@500;700&display=swap');

.start-screen {
    position: relative;

    min-height: 100dvh;
    width: 100%;

    display: grid;
    place-items: center;

    padding: 24px 16px;

    overflow: hidden;

    color: var(--text);

    background: var(--ink);

    font-family: var(--font-body);
}


/* =========================
   AMBIENT BACKGROUND
========================= */

.bg-grid {
    position: absolute;
    inset: 0;

    pointer-events: none;

    background-image:
        linear-gradient(rgba(255, 255, 255, 0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(255, 255, 255, 0.035) 1px, transparent 1px);

    background-size: 42px 42px;

    mask-image: radial-gradient(circle at 50% 20%, #000 0%, transparent 72%);
}


.bg-streaks {
    position: absolute;
    inset: 0;

    overflow: hidden;

    pointer-events: none;
}


.streak {
    position: absolute;

    width: 160%;
    height: 1px;

    left: -30%;

    background: linear-gradient(90deg, transparent, var(--cyan), transparent);

    opacity: 0;

    transform: rotate(-18deg);

    animation: streak-move 7s ease-in-out infinite;
}


.streak-1 {
    top: 18%;
    animation-delay: 0s;
}


.streak-2 {
    top: 52%;
    background: linear-gradient(90deg, transparent, var(--volt), transparent);
    animation-delay: 2.3s;
}


.streak-3 {
    top: 78%;
    animation-delay: 4.6s;
}


@keyframes streak-move {
    0% {
        opacity: 0;
        transform: translateX(-6%) rotate(-18deg);
    }

    12% {
        opacity: 0.35;
    }

    50% {
        opacity: 0.12;
    }

    88% {
        opacity: 0.3;
    }

    100% {
        opacity: 0;
        transform: translateX(6%) rotate(-18deg);
    }
}


/* =========================
   MAIN CARD
========================= */

.start-card {
    position: relative;
    z-index: 1;

    width: min(100%, 460px);

    padding: 30px 26px 24px;

    border: 1px solid var(--line);

    border-radius: 20px;

    background: linear-gradient(165deg, var(--surface), var(--surface) 55%, var(--surface-2));

    box-shadow:
        0 40px 100px rgba(0, 0, 0, 0.55),
        0 0 0 1px rgba(255, 255, 255, 0.02) inset;
}


/* =========================
   BRAND STRIP
========================= */

.brand-strip {
    display: flex;

    align-items: center;
    justify-content: space-between;
    gap: 10px;

    margin-bottom: 22px;

    padding-bottom: 14px;

    border-bottom: 1px solid var(--line);
}


.brand-mark {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.62rem;
    font-weight: 700;
    letter-spacing: 0.14em;
}


.brand-bolt {
    font-style: normal;
    color: var(--volt);
}


.live-tag {
    display: inline-flex;
    align-items: center;
    gap: 6px;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.56rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    white-space: nowrap;
}


.live-dot {
    width: 6px;
    height: 6px;

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


/* =========================
   HERO
========================= */

.hero {
    text-align: left;
}


.hero-title {
    margin: 0;

    color: var(--text);

    font-family: var(--font-display);
    font-size: clamp(2.5rem, 10vw, 3.4rem);
    font-weight: 700;
    line-height: 0.94;
    letter-spacing: -0.02em;
    text-transform: uppercase;
}


.cursor {
    display: inline-block;

    color: var(--volt);

    animation: blink 1.1s step-end infinite;
}


@keyframes blink {

    0%,
    49% {
        opacity: 1;
    }

    50%,
    100% {
        opacity: 0;
    }
}


.hero-tagline {
    margin: 14px 0 6px;

    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 0.82rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}


.hero-desc {
    max-width: 360px;
    margin: 0;

    color: var(--text-dim);

    font-size: 0.85rem;
    line-height: 1.55;
}


/* =========================
   BOLT DIVIDER (signature)
========================= */

.bolt-divider {
    margin: 22px 0;
}


.bolt-divider svg {
    width: 100%;
    height: 22px;

    overflow: visible;
}


.bolt-path {
    fill: none;

    stroke: var(--volt);
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;

    filter: drop-shadow(0 0 6px var(--volt-dim));

    stroke-dasharray: 1;
    stroke-dashoffset: 1;

    animation:
        bolt-draw 0.7s cubic-bezier(0.2, 0.8, 0.2, 1) 0.15s forwards,
        bolt-flicker 3.4s ease-in-out 1s infinite;
}


@keyframes bolt-draw {
    to {
        stroke-dashoffset: 0;
    }
}


@keyframes bolt-flicker {

    0%,
    92%,
    100% {
        opacity: 1;
    }

    94% {
        opacity: 0.35;
    }

    96% {
        opacity: 1;
    }

    97% {
        opacity: 0.5;
    }
}


/* =========================
   HUD STRIP
========================= */

.hud-strip {
    display: grid;

    grid-template-columns: repeat(4, 1fr);

    margin-bottom: 24px;

    border: 1px solid var(--line);
    border-radius: 12px;

    background: rgba(255, 255, 255, 0.02);
}


.hud-item {
    display: grid;
    justify-items: center;
    gap: 5px;

    padding: 11px 4px;

    text-align: center;
}


.hud-item+.hud-item {
    border-left: 1px solid var(--line);
}


.hud-item strong {
    color: var(--text);

    font-family: var(--font-mono);
    font-size: 0.92rem;
    font-weight: 700;
}

.hud-item strong.hud-icon {
    display: flex;
    align-items: center;
    justify-content: center;
}


.hud-item strong.hud-icon img {
    height: 1.15em;
    width: auto;

    object-fit: contain;

    filter: drop-shadow(0 0 4px var(--volt-dim));
}

.hud-item span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.52rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}


/* =========================
   FORM
========================= */

.start-form {
    display: grid;
    gap: 16px;
}


.form-heading {
    display: grid;
    gap: 3px;
}


.form-heading strong {
    font-family: var(--font-display);
    font-size: 1.05rem;
    font-weight: 700;
}


.form-heading span {
    color: var(--text-faint);

    font-size: 0.75rem;
}


.form-field {
    display: grid;
    gap: 8px;
}


.form-field label {
    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
}


.form-field input {
    width: 100%;

    padding: 12px 2px;

    border: none;
    border-bottom: 1.5px solid var(--line);

    outline: none;

    color: var(--text);
    background: transparent;

    font: inherit;
    font-family: var(--font-mono);
    font-size: 0.9rem;

    caret-color: var(--volt);

    transition: border-color 160ms ease;
}


.form-field input::placeholder {
    color: var(--text-faint);
}


.form-field input:focus {
    border-color: var(--volt);
}


.form-field input:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 4px;
}


/* =========================
   ERROR
========================= */

.form-error {
    margin: -6px 0 0;

    color: var(--coral);

    font-family: var(--font-mono);
    font-size: 0.72rem;
    font-weight: 700;
}


/* =========================
   PLAY BUTTON
========================= */

.start-button {
    display: flex;

    width: 100%;
    min-height: 58px;

    margin-top: 2px;
    padding: 0 8px 0 20px;

    align-items: center;
    justify-content: space-between;

    border: 0;
    clip-path: polygon(0 0, 100% 0, 100% 70%, 96% 100%, 0 100%);

    color: var(--ink);
    background: linear-gradient(100deg, var(--volt), var(--volt-light));

    font: inherit;
    font-family: var(--font-display);
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    text-transform: uppercase;

    cursor: pointer;

    transition: transform 150ms ease, filter 150ms ease;
}


.start-button span {
    display: inline-flex;
    align-items: center;
    gap: 7px;
}


.btn-bolt {
    font-style: normal;
}


.start-button:hover {
    filter: brightness(1.06);
    transform: translateY(-1px);
}


.start-button:active {
    transform: translateY(1px);
}


.start-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 3px;
}


.start-button-arrow {
    display: grid;

    width: 34px;
    height: 34px;

    place-items: center;

    border-radius: 9px;

    background: rgba(7, 7, 12, 0.14);

    font-size: 1.05rem;
}


/* =========================
   FOOTER
========================= */

.start-footer {
    display: flex;

    margin-top: 20px;

    align-items: center;
    justify-content: center;
    gap: 8px;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.56rem;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-align: center;
}


.start-footer i {
    width: 3px;
    height: 3px;
    flex: 0 0 3px;

    border-radius: 50%;

    background: var(--text-faint);
}


/* =========================
   REDUCED MOTION
========================= */

@media (prefers-reduced-motion: reduce) {

    .streak,
    .cursor,
    .live-dot,
    .bolt-path {
        animation: none !important;
    }

    .bolt-path {
        stroke-dashoffset: 0;
        opacity: 1;
    }
}


/* =========================
   MOBILE
========================= */

@media (max-width: 480px) {

    .start-screen {
        display: block;

        padding: 14px;

        overflow-y: auto;
    }


    .start-card {
        width: 100%;
        margin: 0 auto;

        padding: 22px 18px 19px;

        border-radius: 16px;
    }


    .hero-title {
        font-size: clamp(2.2rem, 12vw, 2.8rem);
    }


    .hero-desc {
        font-size: 0.78rem;
    }


    .hud-strip {
        margin-bottom: 20px;
    }


    .hud-item {
        padding: 9px 2px;
    }


    .hud-item strong {
        font-size: 0.8rem;
    }


    .hud-item span {
        font-size: 0.46rem;
    }


    .start-button {
        min-height: 54px;
    }
}


/* =========================
   SHORT MOBILE HEIGHT
========================= */

@media (max-height: 700px) and (min-width: 481px) {

    .start-screen {
        place-items: start center;

        padding-top: 14px;
        padding-bottom: 14px;

        overflow-y: auto;
    }


    .start-card {
        padding: 20px 24px 17px;
    }


    .brand-strip {
        margin-bottom: 16px;
        padding-bottom: 10px;
    }


    .hero-title {
        font-size: 2.4rem;
    }


    .bolt-divider {
        margin: 16px 0;
    }


    .hud-strip {
        margin-bottom: 18px;
    }
}


/* =========================
   LANDSCAPE PHONE
========================= */

@media (max-height: 500px) and (orientation: landscape) {

    .start-screen {
        display: block;

        padding: 12px;
    }


    .start-card {
        max-width: 700px;
        margin: 0 auto;

        padding: 16px 22px;
    }


    .brand-strip {
        margin-bottom: 12px;
        padding-bottom: 8px;
    }


    .hero-title {
        font-size: 1.9rem;
    }


    .hero-desc {
        display: none;
    }


    .bolt-divider {
        margin: 12px 0;
    }


    .hud-strip {
        margin-bottom: 14px;
    }


    .start-footer {
        margin-top: 10px;
    }
}
</style>