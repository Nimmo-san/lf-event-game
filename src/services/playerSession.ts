export interface PlayerSession {
  playerId: string;
  playerName: string;
  companyName: string;
  // email: string;
}

const STORAGE_KEY = "lightning-quest-player-session";

export function getPlayerSession(): PlayerSession | null {
  const stored = localStorage.getItem(STORAGE_KEY);

  if (!stored) {
    return null;
  }

  try {
    return JSON.parse(stored) as PlayerSession;
  } catch {
    localStorage.removeItem(STORAGE_KEY);

    return null;
  }
}

export function createPlayerSession(
  playerName: string,
  companyName: string,
  // email: string,
): PlayerSession {
  const session: PlayerSession = {
    playerId: crypto.randomUUID(),

    playerName: playerName.trim(),

    companyName: companyName.trim(),

    // not required for the start of the game
    // email: email.trim().toLowerCase(),
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

  return session;
}

export function clearPlayerSession() {
  localStorage.removeItem(STORAGE_KEY);
}
