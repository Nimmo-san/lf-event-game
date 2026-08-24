export interface PlayerSession {
  playerId: string;

  playerName: string;
  email: string;

  createdAt: number;
}

const STORAGE_KEY = "lightning-flight-player";

export function getPlayerSession(): PlayerSession | null {
  const value = localStorage.getItem(STORAGE_KEY);

  if (!value) {
    return null;
  }

  try {
    return JSON.parse(value) as PlayerSession;
  } catch {
    return null;
  }
}

export function createPlayerSession(
  playerName: string,
  email: string,
): PlayerSession {
  const session: PlayerSession = {
    playerId: crypto.randomUUID(),

    playerName: playerName.trim(),

    email: email.trim().toLowerCase(),

    createdAt: Date.now(),
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

  return session;
}

export function clearPlayerSession() {
  localStorage.removeItem(STORAGE_KEY);
}
