"""Server-side mirror of the scoring formula in src/game/Game.ts.

Duplicated here rather than shared (the frontend and backend are
separate languages/deploys) so routes/players.py can reject a score
that isn't achievable for the reported duration and lightning_collected
— without this, POST /api/games accepted any score up to the flat
100,000 ceiling regardless of how little gameplay it claimed.

If Game.ts's scoring constants ever change, update these to match, or
this check will start rejecting legitimate scores.
"""

# Mirrors Game.ts's SURVIVAL_RATE, LIGHTNING_BASE_SCORE, COMBO_STEP,
# COMBO_MAX_MULTIPLIER, and ROUND_DURATION exactly.
SURVIVAL_RATE = 12  # points per second alive
LIGHTNING_BASE_SCORE = 50  # points per bolt, before combo
COMBO_STEP = 0.25  # multiplier gained per consecutive bolt
COMBO_MAX_MULTIPLIER = 3  # multiplier ceiling

ROUND_DURATION = 120  # seconds — a round always ends by this point

# Rounding/floating-point slack between the client's running total and
# this exact recomputation. Not a security boundary — just noise, so
# it stays small.
SCORE_TOLERANCE = 5

# Buffer added to ROUND_DURATION for the max accepted `duration`, to
# absorb client-side timer/network jitter without opening the door to
# a duration far beyond what a real round can ever last.
DURATION_JITTER_ALLOWANCE = 10
MAX_DURATION_SECONDS = ROUND_DURATION + DURATION_JITTER_ALLOWANCE


def max_plausible_score(duration: float, lightning_collected: int) -> float:
    """The highest score `duration` seconds of survival plus
    `lightning_collected` bolts can produce.

    Mirrors Game.ts's scoring loop step for step: combo never resets
    mid-run (a collision ends the run outright), so the combo
    multiplier for the Nth bolt collected is always
    min(COMBO_MAX_MULTIPLIER, 1 + N * COMBO_STEP) — this is a loop
    rather than a closed-form sum so it stays a direct, checkable
    match to the client logic it's guarding.
    """
    survival_score = SURVIVAL_RATE * duration

    lightning_score = 0.0
    combo = 0

    for _ in range(lightning_collected):
        combo += 1
        multiplier = min(COMBO_MAX_MULTIPLIER, 1 + combo * COMBO_STEP)
        lightning_score += LIGHTNING_BASE_SCORE * multiplier

    return survival_score + lightning_score
