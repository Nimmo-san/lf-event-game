<script setup lang="ts">
import { ref } from "vue";
import { queueLeaderboardSubmission } from "../storage/leaderboardDatabase";
import { syncLeaderboardSubmissions } from "../services/leaderboardSync";
import { getPlayerRank } from "../services/leaderboardApi";

const props = defineProps<{
    gameId: string;
    playerId: string;
    score: number;
}>();

const emit = defineEmits<{
    submitted: [rank: number];
    skipped: [];
    playAgain: [];
}>();

const email = ref("");
// const marketingConsent = ref(false);

const loading = ref(false);
const error = ref("");
const submitted = ref(false);
const syncStatus = ref("")
const rank = ref<number | null>(null);

async function submitEntry() {
    error.value = "";

    if (!email.value.trim()) {
        error.value = "Enter your email address.";
        return;
    }

    loading.value = true;

    try {
        /*
         * Save locally first.
         *
         * This is the important part of the
         * offline-first architecture.
         */
        await queueLeaderboardSubmission(
            props.gameId,
            props.playerId,
            email.value,
            // marketingConsent.value,
        );

        /*
         * Try to sync immediately.
         *
         * If we're offline, this simply fails
         * and the submission remains in IndexedDB.
         */
        const syncResult =
            await syncLeaderboardSubmissions();

        /*
         * The local save was successful regardless
         * of whether the network sync succeeded.
         */
        submitted.value = true;

        if (syncResult.synced > 0) {
            const currentRank =
                await getPlayerRank(
                    props.playerId,
                );

            rank.value =
                currentRank.rank;

            // submitted.value = true;

            syncStatus.value =
                "Your entry has been submitted.";
        } else {
            syncStatus.value =
                "Your entry is saved. Your position will be available once you're back online.";
        }
    } catch (err) {
        console.error(
            "Failed to save leaderboard entry:",
            err,
        );

        error.value =
            "We couldn't save your entry. Please try again.";
    } finally {
        loading.value = false;
    }
}

function skip() {
    emit("skipped");
}

function playAgain() {
    emit("playAgain");
}
</script>

<template>
    <section v-if="!submitted" class="leaderboard-entry">
        <p>
            {{ syncStatus }}
        </p>
        <p class="section-kicker">
            <i class="kicker-bolt">⚡</i>
            LIGHTNING FLIGHT
        </p>

        <h2>
            Join the leaderboard
        </h2>

        <p class="leaderboard-description">
            Enter your email to add your score
            to the leaderboard.
        </p>

        <div class="leaderboard-score">
            <span>Your score</span>

            <strong>
                {{ score }}
            </strong>
        </div>

        <form class="leaderboard-form" @submit.prevent="submitEntry">
            <label for="leaderboard-email">
                Email address
            </label>

            <input id="leaderboard-email" v-model="email" type="email" autocomplete="email" inputmode="email"
                placeholder="you@example.com" />

            <label class="marketing-consent">
                <!-- <input v-model="marketingConsent" type="checkbox" /> -->
                <span>
                    By entering the competition, you agree that Lightning Fibre may contact you by email to notify you
                    if you are a winner and to send you information about our business broadband services and offers.
                    You can unsubscribe at any time. View our <a
                        href="https://cdn.prod.website-files.com/644bdade08aad9ea8591b73a/65ccd66705a7ba08743a726a_Privacy%20Policy_LF%20HoldCo%202%20Ltd.pdf">Privacy
                        Policy</a>
                </span>
            </label>

            <p v-if="error" class="form-error">
                {{ error }}
            </p>

            <div class="leaderboard-actions">
                <button class="primary-button" type="submit" :disabled="loading">
                    <span>
                        <i class="btn-bolt">🏆</i>
                        {{
                            loading
                                ? "Submitting..."
                                : "Join leaderboard "
                        }}
                    </span>

                    <span v-if="!loading" class="primary-button-arrow">
                        →
                    </span>
                </button>

                <button class="secondary-button" type="button" @click="playAgain">
                    <span>
                        <i class="btn-bolt">↻</i>
                        Play again
                    </span>
                </button>
            </div>
        </form>
    </section>

    <section v-else class="leaderboard-success">
        <div class="success-icon">
            ✓
        </div>

        <p class="section-kicker">
            Score submitted
        </p>

        <h2>
            You're on the board!
        </h2>

        <p>
            Your score has been added to the
            Lightning Flight leaderboard.
        </p>

        <!-- TODO: rank cant be known offline, maybe add current rank on last update -->
        <div class="leaderboard-rank">
            <span>Your position</span>

            <strong v-if="rank !== null">
                #{{ rank }}
            </strong>
            <strong v-else>
                Pending
            </strong>
        </div>

        <button class="primary-button" type="button" @click="skip">
            <span>Continue </span>

            <span class="primary-button-arrow">
                →
            </span>
        </button>
    </section>
</template>

<style scoped>
.leaderboard-entry,
.leaderboard-success {
    width: 100%;
    display: grid;
    justify-items: center;
    text-align: center;
}


/* =========================
   KICKER + HEADING
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

.leaderboard-entry h2,
.leaderboard-success h2 {
    margin: 8px 0 4px;

    color: var(--text);

    font-family: var(--font-display);
    font-size: clamp(1.5rem, 6vw, 1.9rem);
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -0.01em;
}

.leaderboard-description,
.leaderboard-success>p {
    max-width: 320px;
    margin: 0;

    color: var(--text-dim);

    font-size: 0.8rem;
    line-height: 1.55;
}


/* =========================
   SCORE / RANK PANEL
========================= */

.leaderboard-score,
.leaderboard-rank {
    display: grid;
    justify-items: center;
    gap: 4px;

    width: 100%;
    margin: 18px 0 4px;
    padding: 16px;

    border: 1px solid var(--volt-dim);
    border-radius: 14px;

    background: rgba(var(--volt-rgb), 0.06);
}

.leaderboard-score span,
.leaderboard-rank span {
    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.58rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

.leaderboard-score strong,
.leaderboard-rank strong {
    color: var(--volt);

    font-family: var(--font-mono);
    font-size: 2.1rem;
    font-weight: 700;
}


/* =========================
   FORM
========================= */

.leaderboard-form {
    display: grid;
    gap: 8px;

    width: 100%;
    margin-top: 8px;
}

.leaderboard-form label:not(.marketing-consent) {
    margin-top: 6px;

    color: var(--text-dim);

    font-family: var(--font-mono);
    font-size: 0.6rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;

    text-align: left;
}

.leaderboard-form input[type="email"] {
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

.leaderboard-form input[type="email"]::placeholder {
    color: var(--text-faint);
}

.leaderboard-form input[type="email"]:focus {
    border-color: var(--volt);
}

.leaderboard-form input[type="email"]:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 4px;
}

.marketing-consent {
    display: flex;
    align-items: flex-start;
    gap: 9px;

    margin: 6px 0 2px;

    color: var(--text-faint);

    font-family: var(--font-mono);
    font-size: 0.66rem;
    line-height: 1.5;
    text-align: left;
}

.marketing-consent a {
    color: var(--cyan);
}

.marketing-consent input {
    margin-top: 3px;

    accent-color: var(--volt);
}


/* =========================
   ERROR
========================= */

.form-error {
    margin: -2px 0 0;

    color: var(--coral);

    font-family: var(--font-mono);
    font-size: 0.7rem;
    font-weight: 700;

    text-align: left;
}


/* =========================
   ACTIONS / BUTTONS
========================= */

.leaderboard-actions {
    display: grid;
    gap: 8px;

    margin-top: 10px;
}

.primary-button {
    display: flex;

    width: 100%;
    min-height: 54px;

    padding: 0 8px 0 20px;

    align-items: center;
    justify-content: space-between;

    border: 0;
    clip-path: polygon(0 0, 100% 0, 100% 70%, 96% 100%, 0 100%);

    color: var(--ink);
    background: linear-gradient(100deg, var(--volt), var(--volt-light));

    font-family: var(--font-display);
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.01em;
    text-transform: uppercase;

    cursor: pointer;

    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;

    transition: transform 120ms ease, filter 120ms ease, opacity 120ms ease;
}

.primary-button span {
    display: inline-flex;
    align-items: center;
    gap: 7px;
}

.btn-bolt {
    font-style: normal;
}

.primary-button:hover:not(:disabled) {
    filter: brightness(1.06);
}

.primary-button:active:not(:disabled) {
    transform: scale(0.98);
}

.primary-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
}

.primary-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 3px;
}

.primary-button-arrow {
    display: grid;

    width: 30px;
    height: 30px;

    place-items: center;

    border-radius: 8px;

    background: rgba(7, 7, 12, 0.14);

    font-size: 1rem;
}

.secondary-button {
    display: flex;

    width: 100%;
    min-height: 40px;

    padding: 8px 12px;

    align-items: center;
    justify-content: center;

    border: 0;
    border-radius: 10px;

    color: var(--text-faint);
    background: transparent;

    font-family: var(--font-mono);
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;

    cursor: pointer;

    -webkit-tap-highlight-color: transparent;
    touch-action: manipulation;

    transition: color 120ms ease, background 120ms ease;
}

.secondary-button span {
    display: inline-flex;
    align-items: center;
    gap: 6px;
}

.secondary-button:hover {
    color: var(--text-dim);
    background: rgba(255, 255, 255, 0.03);
}

.secondary-button:active {
    color: var(--text);
}

.secondary-button:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 2px;
}


/* =========================
   SUCCESS STATE
========================= */

.leaderboard-success .success-icon {
    display: grid;

    width: 64px;
    height: 64px;

    margin-bottom: 4px;

    place-items: center;

    border-radius: 18px;

    color: var(--ink);
    background: linear-gradient(145deg, var(--volt), var(--volt-light));

    font-size: 1.8rem;
    font-weight: 900;
}

.leaderboard-rank {
    width: 100%;
}

.leaderboard-success .primary-button {
    margin-top: 6px;
    justify-content: center;
}
</style>