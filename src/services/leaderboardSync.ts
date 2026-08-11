import {
  getUnsyncedLeaderboardSubmissions,
  markLeaderboardSubmissionSynced,
} from "../storage/leaderboardDatabase";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

let syncing = false;

export interface LeaderboardSyncResult {
  synced: number;
  failed: number;
}

export async function syncLeaderboardSubmissions(): Promise<LeaderboardSyncResult> {
  if (syncing) {
    return {
      synced: 0,
      failed: 0,
    };
  }

  syncing = true;

  let synced = 0;
  let failed = 0;

  try {
    const submissions = await getUnsyncedLeaderboardSubmissions();

    for (const submission of submissions) {
      try {
        const response = await fetch(`${API_URL}/leaderboard/entries`, {
          method: "POST",

          headers: {
            "Content-Type": "application/json",
          },

          body: JSON.stringify({
            game_id: submission.gameId,

            player_id: submission.playerId,

            email: submission.email,

            // marketing_consent: submission.marketingConsent,
          }),
        });

        /*
         * 409 means the server already has
         * this game submission.
         *
         * Therefore it is safe to mark
         * the local copy as synced.
         */
        if (response.ok || response.status === 409) {
          await markLeaderboardSubmissionSynced(submission.id);

          synced += 1;

          continue;
        }
        // else {
        //   console.error("Leaderboard sync failed", {
        //     status: response.status,
        //     body: response,
        //     submission,
        //   });
        // }

        /*
         * 4xx/5xx errors are not considered
         * successfully synced.
         *
         * Keep the submission in IndexedDB
         * so we can retry later.
         */
        failed += 1;
      } catch (error) {
        /*
         * Network failure / offline.
         *
         * Leave the submission untouched.
         */
        // console.error("Leaderboard network error:", error);
        failed += 1;
      }
    }
  } finally {
    // console.log("leaderboard sync attempt finished");
    syncing = false;
  }

  return {
    synced,
    failed,
  };
}

export function startLeaderboardSync(): () => void {
  const sync = () => {
    void syncLeaderboardSubmissions();
  };

  /*
   * Try immediately when the application starts.
   */
  sync();

  /*
   * Try whenever the browser detects
   * that the connection has returned.
   */
  window.addEventListener("online", sync);

  /*
   * Also periodically retry while the app
   * remains open.
   */
  const interval = window.setInterval(sync, 30_000);

  /*
   * Return cleanup function.
   */
  return () => {
    window.removeEventListener("online", sync);

    window.clearInterval(interval);
  };
}
