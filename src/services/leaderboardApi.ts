const API_URL = import.meta.env.VITE_API_URL ?? "/api";

export interface LeaderboardRow {
  rank: number;
  player_id: string;
  player_name: string;
  score: number;
  lightning_collected: number;
}

export interface PlayerRank {
  player_id: string;
  rank: number;
  score: number;
}

export async function getLeaderboard(): Promise<LeaderboardRow[]> {
  const response = await fetch(`${API_URL}/leaderboard`);

  if (!response.ok) {
    throw new Error("Unable to retrieve leaderboard.");
  }

  return response.json();
}

export async function getPlayerRank(playerId: string): Promise<PlayerRank> {
  const response = await fetch(`${API_URL}/leaderboard/rank/${playerId}`);

  // change Promise value to <PlayerRank | null>
  // // Player does not currently have a leaderboard entry.
  // if (response.status === 404){
  //   return null;
  // }

  if (!response.ok) {
    throw new Error("Unable to retrieve leaderboard rank.");
  }

  return response.json();
}
