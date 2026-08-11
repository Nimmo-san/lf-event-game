import { db } from "./gameDatabase";

export interface LeaderboardSubmission {
  id: string;

  gameId: string;
  playerId: string;

  email: string;
  // marketingConsent: boolean;

  createdAt: number;

  synced: boolean;
}

export async function saveLeaderboardSubmission(
  submission: LeaderboardSubmission,
): Promise<void> {
  const database = await db;

  await database.put("leaderboardSubmissions", submission);
}

export async function queueLeaderboardSubmission(
  gameId: string,
  playerId: string,
  email: string,
  // marketingConsent: boolean,
): Promise<LeaderboardSubmission> {
  const database = await db;

  const existing = await database.getFromIndex(
    "leaderboardSubmissions",
    "gameId",
    gameId,
  );

  if (existing) {
    return existing;
  }

  const submission: LeaderboardSubmission = {
    id: crypto.randomUUID(),

    gameId,
    playerId,

    email: email.trim(),
    // marketingConsent,

    createdAt: Date.now(),

    synced: false,
  };

  await saveLeaderboardSubmission(submission);

  return submission;
}

export async function getLeaderboardSubmission(
  id: string,
): Promise<LeaderboardSubmission | undefined> {
  const database = await db;

  return database.get("leaderboardSubmissions", id);
}

export async function getUnsyncedLeaderboardSubmissions(): Promise<
  LeaderboardSubmission[]
> {
  const database = await db;

  const submissions = await database.getAll("leaderboardSubmissions");

  return submissions.filter((submission) => submission.synced === false);
}

export async function markLeaderboardSubmissionSynced(
  id: string,
): Promise<void> {
  const database = await db;

  const submission = await database.get("leaderboardSubmissions", id);

  if (!submission) {
    return;
  }

  submission.synced = true;

  await database.put("leaderboardSubmissions", submission);
}

export async function deleteLeaderboardSubmission(id: string): Promise<void> {
  const database = await db;

  await database.delete("leaderboardSubmissions", id);
}

export async function getLeaderboardSubmissionByGameId(
  gameId: string,
): Promise<LeaderboardSubmission | undefined> {
  const database = await db;

  return database.getFromIndex("leaderboardSubmissions", "gameId", gameId);
}
