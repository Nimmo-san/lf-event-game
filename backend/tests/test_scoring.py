from app.scoring import max_plausible_score


def test_max_plausible_score_survival_only():
    assert max_plausible_score(duration=10, lightning_collected=0) == 120


def test_max_plausible_score_zero_duration_zero_lightning():
    assert max_plausible_score(duration=0, lightning_collected=0) == 0


def test_max_plausible_score_combo_multiplier_ramps_up():
    # Bolts 1-8 ramp the multiplier from 1.25x to the 3x cap
    # (1 + 8 * 0.25 == 3); bolt 9 stays capped at 3x rather than
    # climbing further.
    assert max_plausible_score(duration=0, lightning_collected=8) == 850
    assert max_plausible_score(duration=0, lightning_collected=9) == 1000


def test_max_plausible_score_combines_survival_and_lightning():
    # 12 * 45.5 (survival) + 1450 (12 bolts, see the combo-ramp test
    # above for how that 1450 is made up).
    assert max_plausible_score(duration=45.5, lightning_collected=12) == 1996
