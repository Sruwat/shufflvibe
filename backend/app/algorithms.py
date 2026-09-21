FACTORS = ('ENRG','AFFIL','CROWD','TALK','ROAM','MOVE','GAMES')
ACTION_SCORE = {'LOVE': 88, 'UP': 62, 'DOWN': 38, 'HARD_PASS': 12}

def vibe_name(scores: dict[str, float]) -> str:
    first = max(FACTORS, key=lambda f: abs(scores.get(f, 50)-50))
    distance = abs(scores.get(first, 50)-50)
    candidates = [f for f in FACTORS if f != first and abs(scores.get(f, 50)-50) >= 25 and abs(scores.get(f, 50)-50) >= distance-15]
    second = max(candidates, key=lambda f: abs(scores.get(f, 50)-50), default=None)
    first_words = {'ENRG':('Slow Burner','Night Climber'),'AFFIL':('Room Worker','Inner Circle'),'CROWD':('Quiet One','Crowd Chaser'),'TALK':('Noise Seeker','Table Talker'),'ROAM':('Settler','Nomad'),'MOVE':('Sitter','Floor Filler'),'GAMES':('Lounger','Score Keeper')}
    second_words = {'ENRG':('Slow-Burner','Climber'),'AFFIL':('Mingler','Insider'),'CROWD':('Quiet-One','Crowd-Chaser'),'TALK':('Noise-Seeker','Table-Talker'),'ROAM':('Settler','Nomad'),'MOVE':('Sitter','Floor-Filler'),'GAMES':('Lounger','Score-Keeper')}
    pole = lambda f: 1 if scores.get(f,50) >= 50 else 0
    return first_words[first][pole(first)] if not second else f"{('Low-Key' if first=='ENRG' and not pole(first) else first_words[first][pole(first)].split()[0])} {second_words[second][pole(second)]}"
