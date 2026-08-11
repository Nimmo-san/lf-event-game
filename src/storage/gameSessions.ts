import { db, type GameResult } from "./gameDatabase";

export async function saveGameResult(result: GameResult) {
  const database = await db;

  await database.put("games", result);
}

export async function getGameResult(id: string) {
  const database = await db;

  return database.get("games", id);
}

export async function getUnsyncedGames() {
  const database = await db;

  const games = await database.getAll("games");

  return games.filter((game) => !game.synced);
}

export async function markGameSynced(id: string) {
  const database = await db;

  const game = await database.get("games", id);

  if (!game) {
    return;
  }

  game.synced = true;

  await database.put("games", game);
}
