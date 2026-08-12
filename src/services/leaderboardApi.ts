const API_URL = import.meta.env.VITE_API_URL ?? "/api";

export interface PlayerRank {
  player_id: string;
  rank: number;
  score: number;
}

export async function getPlayerRank(playerId: string): Promise<PlayerRank> {
  const response = await fetch(`${API_URL}/leaderboard/rank/${playerId}`);

  if (!response.ok) {
    throw new Error("Unable to retrieve leaderboard rank.");
  }

  return response.json();
}
