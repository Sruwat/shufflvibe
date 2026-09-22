import { factors, Factor } from './data';
export const ACTION_SCORE = { LOVE:88, UP:62, DOWN:38, HARD_PASS:12 } as const;
export type Action = keyof typeof ACTION_SCORE;
export function cardDeck(): { id:string; factor:Factor; side:'A'|'B' }[] {
 const out:{id:string; factor:Factor; side:'A'|'B'}[]=[]; factors.forEach(f=>{out.push({id:`V-${f}-A`,factor:f,side:'A'}); out.push({id:`V-${f}-B`,factor:f,side:'B'});});
 return out;
}
export function adaptiveDeck(max=14) { const result = factors.map(factor => ({ id: `V-${factor}-A`, factor, side: 'A' as const })); return result.slice(0, Math.max(0, max)); }
const VIBE_WEIGHT: Record<Factor, number> = { ENRG: 18, AFFIL: 16, CROWD: 14, TALK: 14, ROAM: 14, MOVE: 12, GAMES: 12 };
const NAME_WORDS: Record<Factor, [string, string, string, string]> = { ENRG: ['Low-Key','Slow-Burner','Peak','Climber'], AFFIL: ['Mingling','Mingler','Inner-Circle','Insider'], CROWD: ['Quiet','Quiet-One','Big-Room','Crowd-Chaser'], TALK: ['Loud','Noise-Seeker','Talking','Table-Talker'], ROAM: ['Settled','Settler','Nomad','Nomad'], MOVE: ['Seated','Sitter','Moving','Floor-Filler'], GAMES: ['No-Games','Lounger','Arcade','Score-Keeper'] };
const SINGLE_NAME: Record<Factor, [string, string]> = { ENRG: ['Slow Burner','Night Climber'], AFFIL: ['Room Worker','Inner Circle'], CROWD: ['Quiet One','Crowd Chaser'], TALK: ['Noise Seeker','Table Talker'], ROAM: ['Settler','Nomad'], MOVE: ['Sitter','Floor Filler'], GAMES: ['Lounger','Score Keeper'] };

export function vibeName(scores: Partial<Record<Factor, number>>, latencyFirmness: Partial<Record<Factor, number>> = {}, chosenTop?: Factor) {
 const distance = (factor: Factor) => Math.abs((scores[factor] ?? 50) - 50);
 const strongest = Math.max(...factors.map(distance));
 const tied = factors.filter((factor) => distance(factor) === strongest);
 const first = chosenTop && tied.includes(chosenTop) ? chosenTop : [...tied].sort((a, b) => (latencyFirmness[b] ?? 0) - (latencyFirmness[a] ?? 0))[0];
 const candidates = factors.filter((factor) => factor !== first && distance(factor) >= 25 && distance(factor) >= strongest - 15);
 const secondStrength = Math.max(0, ...candidates.map(distance));
 const secondTied = candidates.filter((factor) => distance(factor) === secondStrength);
 const rankedSecond = [...secondTied].sort((a, b) => (latencyFirmness[b] ?? 0) - (latencyFirmness[a] ?? 0));
 const second = rankedSecond.length > 1 && (latencyFirmness[rankedSecond[0]] ?? 0) - (latencyFirmness[rankedSecond[1]] ?? 0) < 0.15
   ? [...secondTied].sort((a, b) => VIBE_WEIGHT[b] - VIBE_WEIGHT[a])[0]
   : rankedSecond[0];
 const pole = (factor: Factor) => (scores[factor] ?? 50) >= 50 ? 2 : 0;
 if (!second) return SINGLE_NAME[first][pole(first) / 2];
 return `${NAME_WORDS[first][pole(first)]} ${NAME_WORDS[second][pole(second) + 1]}`;
}
export function createPlan(scores:Partial<Record<Factor,number>>) { const energy=scores.ENRG??62; return { style: energy>=70?'Could Go Late':'Settle Then Roam', stops: energy>=70?3:2, duration: energy>=70?'8:30 PM – 12:30 AM':'8:30 PM – 11:30 PM' }; }
