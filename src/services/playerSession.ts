export interface PlayerSession {
  playerId: string;

  playerName: string;
  email: string;

  companyName: string;

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

    /*
     * Kept temporarily because the existing
     * backend GameResult requires company_name.
     *
     * Wont be rendered publicly.
     */
    companyName: "Not provided",

    createdAt: Date.now(),
  };

  localStorage.setItem(STORAGE_KEY, JSON.stringify(session));

  return session;
}

export function clearPlayerSession() {
  localStorage.removeItem(STORAGE_KEY);
}
