import { openDB } from "idb";

export interface GameResult {
  id: string;

  playerId: string;
  playerName: string;
  companyName: string;

  score: number;
  lightning: number;
  duration: number;

  createdAt: number;
  synced: boolean;
}

export interface LeaderboardSubmission {
  id: string;

  gameId: string;
  playerId: string;

  email: string;
  marketingConsent: boolean;

  createdAt: number;
  synced: boolean;
}

const LOCAL_DB_NAME = "lightning-quest";

const LOCAL_DB_VERSION = 4;

export const db = openDB(LOCAL_DB_NAME, LOCAL_DB_VERSION, {
  upgrade(database) {
    if (!database.objectStoreNames.contains("games")) {
      const store = database.createObjectStore("games", {
        keyPath: "id",
      });

      store.createIndex("synced", "synced");

      store.createIndex("createdAt", "createdAt");
    }

    if (!database.objectStoreNames.contains("leaderboardSubmissions")) {
      const store = database.createObjectStore("leaderboardSubmissions", {
        keyPath: "id",
      });

      store.createIndex("gameId", "gameId", {
        unique: true,
      });

      // store.createIndex("synced", "synced");

      store.createIndex("createdAt", "createdAt");
    }
  },
});
