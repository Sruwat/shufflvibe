import { Factor, factors, preferences } from './data';
import { ACTION_SCORE, Action } from './algorithms';

export type Card = { id: string; factor: Factor; side: 'A' | 'B' };
export type ExposureEnd = 'swiped' | 'next' | 'timeout' | 'back';
export type Exposure = { card: Card; index: number; startedAt: number; endedAt?: number; endedBy?: ExposureEnd; nextCount: number; latency?: number };
export type Preference = typeof preferences[number];
export type PreferenceReading = { score: number; importance: number; sense?: 'classy' | 'current' | 'both' };
export type AssessmentState = { queue: Card[]; cursor: number; exposures: Exposure[]; answers: Record<string, Action>; scores: Partial<Record<Factor, number>>; forcedChoice?: [Factor, Factor]; paused: boolean; awayPrompt: boolean; completed: boolean };

export const VIBE_CARDS: Card[] = factors.flatMap((factor) => [
  { id: `V-${factor}-A`, factor, side: 'A' as const },
  { id: `V-${factor}-B`, factor, side: 'B' as const },
]);

export const SWIPE_SCORE = ACTION_SCORE;

export function createAssessment(): AssessmentState {
  // One opening exposure per factor. Partners are inserted only after a soft answer.
  return { queue: factors.map((factor) => VIBE_CARDS.find((card) => card.factor === factor && card.side === 'A')!), cursor: 0, exposures: [], answers: {}, scores: {}, paused: false, awayPrompt: false, completed: false };
}

function partner(card: Card): Card { return VIBE_CARDS.find((candidate) => candidate.factor === card.factor && candidate.side !== card.side)!; }

export function currentCard(state: AssessmentState): Card | undefined { return state.queue[state.cursor]; }

export function beginExposure(state: AssessmentState, now = Date.now()): AssessmentState {
  const card = currentCard(state);
  if (!card || state.paused || state.completed) return state;
  const already = state.exposures.find((exposure) => exposure.card.id === card.id && !exposure.endedAt);
  if (already) return state;
  return { ...state, exposures: [...state.exposures, { card, index: state.exposures.length, startedAt: now, nextCount: 0 }] };
}

export function deferCard(state: AssessmentState, kind: 'next' | 'timeout', now = Date.now()): AssessmentState {
  const card = currentCard(state);
  if (!card || state.completed) return state;
  const exposures = state.exposures.map((exposure) => exposure.card.id === card.id && !exposure.endedAt ? { ...exposure, endedAt: now, endedBy: kind, latency: Math.max(0, now - exposure.startedAt), nextCount: exposure.nextCount + 1 } : exposure);
  const index = Math.min(state.queue.length, state.cursor + 4);
  const queue = [...state.queue];
  const moved = queue.splice(state.cursor, 1)[0];
  queue.splice(Math.min(index, queue.length), 0, moved);
  const timedOut = kind === 'timeout';
  const timeouts = exposures.filter((exposure) => exposure.endedBy === 'timeout').length;
  return { ...state, queue, exposures, cursor: Math.min(state.cursor, queue.length - 1), paused: timeouts >= 2, awayPrompt: timeouts >= 2, completed: false };
}

export function answerCard(state: AssessmentState, action: Action, now = Date.now()): AssessmentState {
  const card = currentCard(state);
  if (!card || state.paused || state.completed) return state;
  const exposures = state.exposures.map((exposure) => exposure.card.id === card.id && !exposure.endedAt ? { ...exposure, endedAt: now, endedBy: 'swiped' as const, latency: Math.max(0, now - exposure.startedAt) } : exposure);
  const answers = { ...state.answers, [card.id]: action };
  const previous = state.answers[VIBE_CARDS.find((candidate) => candidate.factor === card.factor && candidate.side !== card.side)?.id ?? ''];
  const isSoft = action === 'UP' || action === 'DOWN';
  let queue = state.queue;
  if (isSoft && !previous && !queue.some((candidate, index) => index > state.cursor && candidate.factor === card.factor)) {
    const p = partner(card);
    queue = [...queue];
    queue.splice(Math.min(queue.length, state.cursor + 3), 0, p);
  }
  const scores = { ...state.scores, [card.factor]: scorePair(queue, exposures, answers, card.factor) };
  const nextCursor = state.cursor + 1;
  const completed = nextCursor >= queue.length || Object.keys(scores).length === factors.length && Object.keys(answers).length >= 7;
  const forcedChoice = completed ? unresolvedTie(scores) : undefined;
  return { ...state, queue, cursor: Math.min(nextCursor, queue.length), exposures, answers, scores, completed: completed && !forcedChoice, forcedChoice };
}

function scorePair(queue: Card[], exposures: Exposure[], answers: Record<string, Action>, factor: Factor): number {
  const cards = queue.filter((card) => card.factor === factor);
  const answered = cards.map((card) => answers[card.id]).filter(Boolean);
  if (!answered.length) return 50;
  if (answered.length === 1) return SWIPE_SCORE[answered[0]];
  return Math.round(answered.reduce((sum, action) => sum + SWIPE_SCORE[action], 0) / answered.length);
}

function unresolvedTie(scores: Partial<Record<Factor, number>>): [Factor, Factor] | undefined {
  const ranked = factors.map((factor) => [factor, Math.abs((scores[factor] ?? 50) - 50)] as const).sort((a, b) => b[1] - a[1]);
  return ranked[0] && ranked[1] && ranked[0][1] === ranked[1][1] ? [ranked[0][0], ranked[1][0]] : undefined;
}

export function answerForcedChoice(state: AssessmentState, selected: Factor): AssessmentState {
  if (!state.forcedChoice?.includes(selected)) return state;
  return { ...state, forcedChoice: undefined, completed: true };
}

export function resolveAway(state: AssessmentState, away: boolean): AssessmentState {
  if (!state.awayPrompt) return state;
  return { ...state, awayPrompt: false, paused: away };
}

export function firmness(scores: Partial<Record<Factor, number>>): Partial<Record<Factor, number>> {
  return Object.fromEntries(factors.map((factor) => [factor, Math.abs((scores[factor] ?? 50) - 50) / 50])) as Partial<Record<Factor, number>>;
}

export function refused(scores: Partial<Record<Factor, number>>, answers: Record<string, Action>): Factor[] {
  return factors.filter((factor) => (scores[factor] ?? 50) <= 25 && Object.entries(answers).some(([id, action]) => id.includes(`V-${factor}-`) && action === 'HARD_PASS'));
}

export function rescale(scores: Record<string, number>, populationCentre = 70.5, populationSpread = 26.5, stretchWeight = 0.33): Record<string, number> {
  const values = Object.values(scores);
  const mean = values.reduce((sum, value) => sum + value, 0) / Math.max(1, values.length);
  const spread = Math.max(15, Math.sqrt(values.reduce((sum, value) => sum + (value - mean) ** 2, 0) / Math.max(1, values.length)));
  const stretch = 1 + stretchWeight * (populationSpread / spread - 1);
  return Object.fromEntries(Object.entries(scores).map(([factor, score]) => [factor, Math.max(0, Math.min(100, populationCentre + (score - mean) * stretch))]));
}

export function preferenceReading(score: number, sense?: PreferenceReading['sense']): PreferenceReading { return { score, importance: score / 100, sense }; }

export type Chemistry = { vector: Partial<Record<Factor, number>>; tags: string[]; formation: string; stopCount: number; stopDurations: number[] };

export const VENUE_TYPES: Record<string, Partial<Record<Factor, number>>> = {
  'table for the night': { ENRG: 25, AFFIL: 85, CROWD: 35, TALK: 90, MOVE: 10, GAMES: 15 },
  'quiet bar': { ENRG: 35, AFFIL: 75, CROWD: 40, TALK: 85, MOVE: 15, GAMES: 20 },
  'buzzy restaurant': { ENRG: 55, AFFIL: 70, CROWD: 70, TALK: 65, MOVE: 15, GAMES: 10 },
  pub: { ENRG: 60, AFFIL: 60, CROWD: 70, TALK: 55, MOVE: 25, GAMES: 45 },
  'games bar': { ENRG: 65, AFFIL: 65, CROWD: 65, TALK: 45, MOVE: 40, GAMES: 90 },
  'games pub': { ENRG: 55, AFFIL: 70, CROWD: 60, TALK: 60, MOVE: 20, GAMES: 65 },
  'live room': { ENRG: 65, AFFIL: 50, CROWD: 70, TALK: 25, MOVE: 45, GAMES: 10 },
  'lounge / rooftop': { ENRG: 50, AFFIL: 45, CROWD: 60, TALK: 60, MOVE: 20, GAMES: 10 },
  club: { ENRG: 90, AFFIL: 30, CROWD: 90, TALK: 10, MOVE: 90, GAMES: 5 },
  'street / market': { ENRG: 60, AFFIL: 55, CROWD: 85, TALK: 60, MOVE: 60, GAMES: 10 },
  'open ground': { ENRG: 50, AFFIL: 70, CROWD: 40, TALK: 75, MOVE: 70, GAMES: 40 },
};

export function chemistry(members: Array<Partial<Record<Factor, number>>>, durationHours = 4): Chemistry {
  const vector = Object.fromEntries(factors.map((factor) => [factor, Math.round(members.reduce((sum, member) => sum + (member[factor] ?? 50), 0) / Math.max(1, members.length))])) as Partial<Record<Factor, number>>;
  const energy = vector.ENRG ?? 50; const roam = vector.ROAM ?? 50;
  const tags: string[] = [];
  if (energy >= 80) tags.push('Running Hot'); else if (energy <= 30) tags.push('Slow Burn'); else if (energy >= 55 && energy < 80) tags.push('Could Go Late');
  if ((vector.AFFIL ?? 50) >= 75 && members.length > 1) tags.push('Our Table');
  if ((vector.AFFIL ?? 50) <= 30 && members.length > 1) tags.push('Meet the Room');
  const stopCount = roam < 35 ? 1 : roam < 65 ? 2 : Math.min(3, Math.max(2, Math.floor(durationHours)));
  const first = tags.includes('Settle Then Roam') ? 0.55 : 1 / stopCount;
  const stopDurations = stopCount === 1 ? [1] : [first, ...Array.from({ length: stopCount - 1 }, () => (1 - first) / (stopCount - 1))];
  return { vector, tags: tags.slice(0, 1), formation: members.length > 1 ? 'Best of Both' : 'In Sync', stopCount, stopDurations };
}

export function chemistryV2(members: Array<Partial<Record<Factor, number>>>, durationHours = 4, strangers = false) {
  const safeMembers = members.length ? members : [Object.fromEntries(factors.map((factor) => [factor, 50])) as Partial<Record<Factor, number>>];
  const vector = Object.fromEntries(factors.map((factor) => [factor, Math.round(safeMembers.reduce((sum, member) => sum + (member[factor] ?? 50), 0) / safeMembers.length)])) as Partial<Record<Factor, number>>;
  const strength = (score: number) => score >= 80 || score <= 20 ? 1 : score >= 70 || score <= 30 ? 0.5 : 0;
  const highs = safeMembers.map((member) => member.ENRG ?? 50).filter((score) => score >= 70 && strength(score));
  const lows = safeMembers.map((member) => member.ENRG ?? 50).filter((score) => score <= 30 && strength(score));
  const tags: string[] = [];
  if (highs.length && highs.reduce((sum, score) => sum + strength(score), 0) > lows.reduce((sum, score) => sum + strength(score), 0)) vector.ENRG = Math.max(...highs);
  else if (highs.length && lows.length) { const pull = lows.length <= 2 ? 0.6 : lows.length === 3 ? 0.5 : 0.4; vector.ENRG = Math.round(lows.reduce((sum, score) => sum + score, 0) / lows.length + pull * (Math.max(...highs) - Math.min(...lows))); tags.push('Slow Burn'); }
  const talker = safeMembers.some((member) => (member.TALK ?? 50) >= 70 && strength(member.TALK ?? 50));
  if (talker) tags.push('Buzz, Not Noise');
  const affilHigh = safeMembers.some((member) => (member.AFFIL ?? 50) >= 70); const affilLow = safeMembers.some((member) => (member.AFFIL ?? 50) <= 30);
  if (affilHigh && affilLow) tags.push('Table and Floor'); else if (strangers || safeMembers.every((member) => (member.AFFIL ?? 50) <= 30)) tags.push('Meet the Room');
  const roam = vector.ROAM ?? 50; const stopCount = roam < 35 ? 1 : roam < 65 ? 2 : 3;
  return { vector, tags: tags.slice(0, 2), formation: safeMembers.length > 1 ? 'Best of Both' : 'In Sync', stopCount, talkFloor: talker ? 40 : 0, stopDurations: stopCount === 1 ? [1] : Array.from({ length: stopCount }, () => 1 / stopCount) };
}

export function selectVenueTypes(members: Array<Partial<Record<Factor, number>>>, durationHours = 4, strangers = false) {
  const room = chemistryV2(members, durationHours, strangers); const target = room.vector;
  const ranked = Object.entries(VENUE_TYPES).filter(([, scores]) => !room.talkFloor || (scores.TALK ?? 0) >= room.talkFloor).map(([name, scores]) => {
    let distance = factors.reduce((sum, factor) => sum + Math.abs((scores[factor] ?? 50) - (target[factor] ?? 50)), 0);
    if (strangers && ['games pub', 'pub', 'street / market', 'open ground'].includes(name)) distance -= 12;
    return [name, distance] as const;
  }).sort((a, b) => a[1] - b[1]);
  return ranked.slice(0, room.stopCount).map(([name]) => name);
}

export function generatePlan(members: Array<Partial<Record<Factor, number>>>, venues: Array<{ name: string; type: string; scores: Partial<Record<Factor, number>> }>) {
  const room = chemistry(members); const used = new Set<string>();
  return Array.from({ length: room.stopCount }, (_, index) => {
    const venue = venues.filter((candidate) => !used.has(candidate.name)).sort((a, b) => closeness(room.vector, a.scores) - closeness(room.vector, b.scores))[0] ?? venues[0];
    if (venue) used.add(venue.name);
    return { index: index + 1, venue, durationShare: room.stopDurations[index] ?? 0, type: venue?.type ?? 'open night' };
  });
}

function closeness(target: Partial<Record<Factor, number>>, candidate: Partial<Record<Factor, number>>) { return factors.reduce((sum, factor) => sum + Math.abs((target[factor] ?? 50) - (candidate[factor] ?? 50)), 0); }
