import { getUnsyncedGames, markGameSynced } from "./gameSessions";
import type { GameResult } from "./gameDatabase";

const API_URL = import.meta.env.VITE_API_URL ?? "/api";

let syncing = false;

export async function syncGameResults() {
  if (syncing) {
    return;
  }

  if (!navigator.onLine) {
    return;
  }

  syncing = true;

  try {
    const results = await getUnsyncedGames();

    for (const result of results) {
      try {
        await uploadGameResult(result);

        await markGameSynced(result.id);
      } catch (error) {
        console.error("Failed to sync game result:", error);

        // Stop here.
        //
        // If the network/server is unavailable,
        // don't hammer the API with every result.
        break;
      }
    }
  } finally {
    syncing = false;
  }
}

async function uploadGameResult(result: GameResult) {
  const response = await fetch(`${API_URL}/games`, {
    method: "POST",

    headers: {
      "Content-Type": "application/json",
    },

    body: JSON.stringify({
      game_id: result.id,

      player_id: result.playerId,

      player_name: result.playerName,

      company_name: result.companyName,

      score: result.score,

      lightning_collected: result.lightning,

      duration: result.duration,
    }),
  });

  if (!response.ok) {
    throw new Error(`Game sync failed: ${response.status}`);
  }

  return response.json();
}
