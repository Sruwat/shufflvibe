from app.full_engine import AssessmentSession, chemistry, chemistry_v2, fill_venues, firmness, rescale, select_venue_types

def test_soft_answer_inserts_partner_after_separation():
    session = AssessmentSession()
    session.answer('UP')
    assert session.queue[3].id == 'V-ENRG-B'

def test_two_timeouts_pause():
    session = AssessmentSession()
    session.defer('timeout')
    session.defer('timeout')
    assert session.paused is True
    assert session.away_prompt is True

def test_firmness_and_rescale_are_bounded():
    assert firmness({'ENRG': 88})['ENRG'] == 0.76
    assert all(0 <= value <= 100 for value in rescale({'ENRG': 88, 'ROAM': 12}).values())

def test_group_chemistry_has_plan_shape():
    result = chemistry([{'ENRG': 88, 'ROAM': 80}, {'ENRG': 62, 'ROAM': 70}])
    assert result['stops'] == 3
    assert result['formation'] == 'Best of Both'

def test_chemistry_v2_energy_is_asymmetric_and_talk_has_floor():
    result = chemistry_v2([{'ENRG': 88, 'TALK': 80}, {'ENRG': 12, 'TALK': 55}])
    assert result['vector']['ENRG'] == 58
    assert result['talk_floor'] == 40
    assert 'Buzz, Not Noise' in result['tags']

def test_roam_uses_firm_bend_weighting_and_duration_cap():
    flexible_low = chemistry_v2([{"ROAM": 92}, {"ROAM": 30}], duration_hours=6)
    assert flexible_low["roam"] == 92
    assert flexible_low["stops"] == 3

    fast_band_opposition = chemistry_v2([
        {"ROAM": 92},
        {"ROAM": 25, "latency_firmness": {"ROAM": 0.9}},
    ], duration_hours=6)
    assert fast_band_opposition["roam"] == 60
    assert fast_band_opposition["stops"] == 2
    assert fast_band_opposition["stop_durations"] == [0.55, 0.45]

    short_night = chemistry_v2([{"ROAM": 92}], duration_hours=3)
    assert short_night["stops"] == 1


def test_venue_types_filter_out_non_talkable_club_for_talker():
    types = select_venue_types([{'ENRG': 88, 'TALK': 88, 'ROAM': 80}, {'ENRG': 62, 'TALK': 75, 'ROAM': 70}])
    assert all(name != 'club' for name in types)

def test_preference_fill_prefers_food_for_food_whole_point():
    selected = fill_venues(['buzzy restaurant'], [{'preferences': {'FOOD': 88, 'SCEN': 38}}])
    assert selected[0]['name'] == 'Depot 48'
