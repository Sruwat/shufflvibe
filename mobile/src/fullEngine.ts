import { Factor, factors, preferences } from './data';
import { ACTION_SCORE, Action } from './algorithms';

export type Card = { id: string; factor: Factor; side: 'A' | 'B' };
export type ExposureEnd = 'swiped' | 'next' | 'timeout' | 'back';
export type Exposure = { card: Card; index: number; startedAt: number; endedAt?: number; endedBy?: ExposureEnd; nextCount: number; latency?: number };
export type Preference = typeof preferences[number];
export type PreferenceReading = { score: number; importance: number; sense?: 'classy' | 'current' | 'both' };
export type PreferenceAction = 'WHOLE_POINT' | 'NICE_TO_HAVE' | 'DONT_MIND' | 'DONT_CARE';
export type PreferenceCard = { id: string; factor: Preference; title: string; subtitle: string };
export type PreferenceState = { queue: PreferenceCard[]; cursor: number; answers: Record<string, PreferenceAction>; readings: Partial<Record<Preference, PreferenceReading>>; sense?: 'classy' | 'current' | 'both'; stage: 'deck' | 'sense' | 'done' };
export type AssessmentState = { queue: Card[]; cursor: number; history: string[]; exposures: Exposure[]; answers: Record<string, Action>; scores: Partial<Record<Factor, number>>; forcedChoice?: [Factor, Factor]; chosenTop?: Factor; paused: boolean; awayPrompt: boolean; awayStartCardId?: string; completed: boolean };

export const VIBE_CARDS: Card[] = factors.flatMap((factor) => [
  { id: `V-${factor}-A`, factor, side: 'A' as const },
  { id: `V-${factor}-B`, factor, side: 'B' as const },
]);

export const SWIPE_SCORE = ACTION_SCORE;
export const PREFERENCE_SCORE: Record<PreferenceAction, number> = { WHOLE_POINT: 88, NICE_TO_HAVE: 62, DONT_MIND: 38, DONT_CARE: 12 };
export const PREFERENCE_CARDS: PreferenceCard[] = [
  { id: 'P-FOOD', factor: 'FOOD', title: 'Something worth eating', subtitle: 'The plate, the kitchen, the thing you would tell someone about tomorrow.' },
  { id: 'P-LIVE', factor: 'LIVE', title: 'A live act in the room', subtitle: 'A band, a set, or a voice that gives the night its centre.' },
  { id: 'P-POL', factor: 'POL', title: 'A dressed-up room', subtitle: 'A place where the way you show up feels part of the night.' },
  { id: 'P-SCEN', factor: 'SCEN', title: 'A beautiful room', subtitle: 'The light, the table, the walls, and the details you notice.' },
  { id: 'P-NOV', factor: 'NOV', title: 'An unmarked door', subtitle: 'Somewhere new, with a corner you have not found before.' },
  { id: 'P-HERIT', factor: 'HERIT', title: 'An old building', subtitle: 'A place with a past, materials, and a story in the walls.' },
];
export function createPreferences(): PreferenceState { return { queue: PREFERENCE_CARDS, cursor: 0, answers: {}, readings: {}, stage: 'deck' }; }
export function currentPreference(state: PreferenceState): PreferenceCard | undefined { return state.stage === 'deck' ? state.queue[state.cursor] : undefined; }
export function answerPreference(state: PreferenceState, action: PreferenceAction): PreferenceState { const card = currentPreference(state); if (!card) return state; const readings = { ...state.readings, [card.factor]: preferenceReading(PREFERENCE_SCORE[action], card.factor === 'POL' ? state.sense : undefined) }; const answers = { ...state.answers, [card.id]: action }; const cursor = state.cursor + 1; return { ...state, answers, readings, cursor, stage: card.factor === 'POL' ? 'sense' : cursor >= state.queue.length ? 'done' : 'deck' }; }
export function deferPreference(state: PreferenceState): PreferenceState { const card = currentPreference(state); if (!card) return state; const queue = [...state.queue]; queue.splice(state.cursor, 1); queue.push(card); return { ...state, queue, cursor: Math.min(state.cursor, queue.length - 1) }; }
export function backPreference(state: PreferenceState): PreferenceState { return state.stage === 'deck' && state.cursor > 0 ? { ...state, cursor: state.cursor - 1 } : state; }
export function choosePreferenceSense(state: PreferenceState, sense: 'classy' | 'current' | 'both'): PreferenceState { const reading = state.readings.POL; const readings = reading ? { ...state.readings, POL: { ...reading, sense } } : state.readings; return { ...state, readings, sense, stage: state.cursor >= state.queue.length ? 'done' : 'deck' }; }

export function createAssessment(): AssessmentState {
  // One opening exposure per factor. Partners are inserted only after a soft answer.
  return { queue: factors.map((factor) => VIBE_CARDS.find((card) => card.factor === factor && card.side === 'A')!), cursor: 0, history: [], exposures: [], answers: {}, scores: {}, paused: false, awayPrompt: false, completed: false };
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
  if (!card || state.completed || state.paused || isRequiredAnswerExposure(state)) return state;
  const exposures = state.exposures.map((exposure) => exposure.card.id === card.id && !exposure.endedAt ? { ...exposure, endedAt: now, endedBy: kind, latency: Math.max(0, now - exposure.startedAt), nextCount: exposure.nextCount + 1 } : exposure);
  const queue = [...state.queue];
  const moved = queue.splice(state.cursor, 1)[0];
  queue.push(moved);
  const partnerIndex = queue.findIndex((candidate) => candidate.factor === card.factor && candidate.id !== card.id);
  if (partnerIndex === queue.length - 2) {
    const [pairedCard] = queue.splice(partnerIndex, 1);
    queue.splice(state.cursor, 0, pairedCard);
  }
  const last = exposures.at(-1);
  const previous = exposures.at(-2);
  const consecutiveTimeout = kind === 'timeout' && last?.endedBy === 'timeout' && previous?.endedBy === 'timeout';
  let firstTimedOut: string | undefined;
  if (consecutiveTimeout) {
    for (let index = exposures.length - 1; index >= 0 && exposures[index].endedBy === 'timeout'; index -= 1) {
      firstTimedOut = exposures[index].card.id;
    }
  }
  const shouldPrompt = consecutiveTimeout && !state.awayPrompt;
  return { ...state, queue, history: [...state.history, card.id], exposures, cursor: Math.min(state.cursor, queue.length - 1),
    paused: shouldPrompt || state.paused, awayPrompt: shouldPrompt || state.awayPrompt,
    awayStartCardId: shouldPrompt ? firstTimedOut : state.awayStartCardId, completed: false };
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
  return { ...state, queue, cursor: Math.min(nextCursor, queue.length), history: [...state.history, card.id], exposures, answers, scores, completed: completed && !forcedChoice, forcedChoice };
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
  return { ...state, chosenTop: selected, forcedChoice: undefined, completed: true };
}

export type AwayResolution = 'present' | 'away' | 'unanswered';

export function resolveAway(state: AssessmentState, resolution: AwayResolution): AssessmentState {
  if (!state.awayPrompt) return state;
  const timeoutIndexes = new Set<number>();
  for (let index = state.exposures.length - 1; index >= 0 && state.exposures[index].endedBy === 'timeout'; index -= 1) {
    timeoutIndexes.add(index);
  }
  const exposures = state.exposures.filter((_, index) => !timeoutIndexes.has(index));
  const cursor = Math.max(0, state.queue.findIndex((card) => card.id === state.awayStartCardId));
  if (resolution === 'present') return { ...state, exposures, awayPrompt: false, paused: false, awayStartCardId: undefined };
  const history = state.history.slice(0, Math.max(0, state.history.length - timeoutIndexes.size));
  return { ...state, exposures, history, cursor, awayPrompt: false, paused: resolution === 'unanswered', awayStartCardId: undefined };
}

export function resumeAssessment(state: AssessmentState): AssessmentState {
  return state.paused && !state.awayPrompt ? { ...state, paused: false } : state;
}

export function isRequiredAnswerExposure(state: AssessmentState): boolean {
  const card = currentCard(state);
  if (!card || state.answers[card.id]) return false;
  const seen = state.exposures.filter((exposure) => exposure.card.id === card.id);
  const hasOpenExposure = seen.some((exposure) => !exposure.endedAt);
  return seen.length >= 3 || (seen.length === 2 && !hasOpenExposure);
}

export function backCard(state: AssessmentState, now = Date.now()): AssessmentState {
  if (!state.history.length || state.paused || state.completed) return state;
  const card = currentCard(state);
  const exposures = card ? state.exposures.map((exposure) => exposure.card.id === card.id && !exposure.endedAt
    ? { ...exposure, endedAt: now, endedBy: 'back' as const, latency: Math.max(0, now - exposure.startedAt) }
    : exposure) : state.exposures;
  const queue = [...state.queue];
  const previousId = state.history[state.history.length - 1];
  const previousIndex = queue.findIndex((candidate) => candidate.id === previousId);
  if (previousIndex < 0) return state;
  const history = state.history.slice(0, -1);
  if (previousIndex < state.cursor) {
    return { ...state, cursor: previousIndex, history, exposures };
  }
  const [previous] = queue.splice(previousIndex, 1);
  const cursor = Math.min(state.cursor, queue.length);
  queue.splice(cursor, 0, previous);
  return { ...state, queue, cursor, history, exposures };
}

export function latencyFirmness(state: AssessmentState): Partial<Record<Factor, number>> {
  const answered = Object.keys(state.answers).flatMap((id) => {
    const exposures = state.exposures.filter((exposure) => exposure.card.id === id);
    if (!exposures.length || Math.min(...exposures.map((exposure) => exposure.index)) < 3) return [];
    const latency = exposures.reduce((sum, exposure) => sum + (exposure.latency ?? 0), 0);
    return latency > 0 ? [{ factor: exposures[0].card.factor, latency: Math.log(latency) }] : [];
  });
  if (answered.length < 5) return {};
  const sorted = [...answered].sort((a, b) => a.latency - b.latency);
  const ranked = new Map<typeof answered[number], number>();
  sorted.forEach((answer, index) => ranked.set(answer, 1 - index / (sorted.length - 1)));
  return Object.fromEntries(factors.flatMap((factor) => {
    const values = answered.filter((answer) => answer.factor === factor).map((answer) => ranked.get(answer) ?? 0);
    return values.length ? [[factor, values.reduce((sum, value) => sum + value, 0) / values.length]] : [];
  })) as Partial<Record<Factor, number>>;
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

export const PREFERENCE_WEIGHTS = { FOOD: 20, LIVE: 18, POL: 18, SCEN: 16, NOV: 14, HERIT: 14 } as const;

type PreferenceMember = Partial<Record<keyof typeof PREFERENCE_WEIGHTS, number>> & { preferences?: Partial<Record<keyof typeof PREFERENCE_WEIGHTS, number>>; pol_sense?: string; visited_venues?: string[] };
type PreferenceVenue = { name: string; type: string; scores?: Partial<Record<keyof typeof PREFERENCE_WEIGHTS, number>>; pol_sense?: string };

function senseOk(venue: PreferenceVenue, member: PreferenceMember) {
  const sense = member.pol_sense ?? 'both'; const venueSense = venue.pol_sense ?? 'both';
  return sense === 'both' || venueSense === 'both' || sense === venueSense;
}

export function preferenceFit(venue: PreferenceVenue, members: PreferenceMember[], visited = new Set<string>(), had: Set<string>[] = members.map(() => new Set<string>())) {
  const people = members.length ? members : [{}];
  const served = had.length ? had : people.map(() => new Set<string>());
  return people.reduce((total, member, index) => total + Object.entries(PREFERENCE_WEIGHTS).reduce((sum, [factor]) => {
    if (factor === 'POL' && !senseOk(venue, member)) return sum;
    const prefs = member.preferences ?? member;
    const preference = prefs[factor as keyof typeof PREFERENCE_WEIGHTS] ?? 50;
    const memberVisited = visited.has(venue.name) || (member.visited_venues ?? []).includes(venue.name);
    const delivery = factor === 'NOV' ? (memberVisited ? 20 : 100) : venue.scores?.[factor as keyof typeof PREFERENCE_WEIGHTS] ?? 50;
    const urgency = preference >= 75 && !served[index]?.has(factor) ? 2 : 1;
    return sum + (preference / 100) * urgency * Math.min(delivery, preference);
  }, 0), 0);
}

export function fillVenues(types: string[], members: PreferenceMember[], pool: PreferenceVenue[], visited = new Set<string>()) {
  const people = members.length ? members : [{}];
  const seen = new Set(visited); const had = people.map(() => new Set<string>()); const used = new Set<string>();
  const selected: PreferenceVenue[] = [];
  types.forEach((type) => {
    const choices = pool.filter((venue) => !used.has(venue.name) && venue.type === type);
    if (!choices.length) return;
    const choice = choices.reduce((best, candidate) => preferenceFit(candidate, people, seen, had) > preferenceFit(best, people, seen, had) ? candidate : best);
    selected.push(choice); used.add(choice.name);
    people.forEach((member, index) => Object.keys(PREFERENCE_WEIGHTS).forEach((factor) => {
      if (factor === 'POL' && !senseOk(choice, member)) return;
      const prefs = member.preferences ?? member; const preference = prefs[factor as keyof typeof PREFERENCE_WEIGHTS] ?? 50;
      const memberVisited = seen.has(choice.name) || (member.visited_venues ?? []).includes(choice.name);
      const delivery = factor === 'NOV' ? (memberVisited ? 20 : 100) : choice.scores?.[factor as keyof typeof PREFERENCE_WEIGHTS] ?? 50;
      if (preference >= 75 && delivery >= 55) had[index].add(factor);
    }));
    seen.add(choice.name);
  });
  return selected;
}

export function chemistry(members: Partial<Record<Factor, number>>[], durationHours = 4): Chemistry {
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

type ChemistryMember = Partial<Record<Factor, number>> & { latency_firmness?: Partial<Record<Factor, number>>; preferences?: Partial<Record<keyof typeof PREFERENCE_WEIGHTS, number>>; pol_sense?: string };

function planBend(member: ChemistryMember, factor: Factor): { firm: boolean; bend: number } {
  const score = member[factor] ?? 50;
  const latency = member.latency_firmness?.[factor] ?? 0;
  const extreme = score <= 20 || score >= 80;
  const band = (score > 20 && score < 30) || (score > 70 && score < 80);
  const firm = extreme || (band && latency >= 0.6);
  return { firm, bend: extreme ? 25 : band && firm ? 28 : Math.abs(score - 50) + 5 };
}

export function joinerShapeFit(member: ChemistryMember, venueTypes: string[], stopCount: number) {
  const reasons: string[] = [];
  venueTypes.forEach((venueType, stopIndex) => {
    const template = VENUE_TYPES[venueType];
    if (!template) { reasons.push(`Stop ${stopIndex + 1}: unknown venue type`); return; }
    stopAxes.forEach((factor) => {
      const score = member[factor] ?? 50; const bend = planBend(member, factor).bend; const value = template[factor] ?? 50;
      const fits = score >= 50 ? value >= score - bend : value <= score + bend;
      if (!fits) reasons.push(`Stop ${stopIndex + 1}: ${factor} is outside your bend`);
    });
  });
  const roam = member.ROAM ?? 50; const roamValue = ({ 1: 20, 2: 50, 3: 80 } as Record<number, number>)[stopCount];
  if (roamValue === undefined) reasons.push('The frozen plan has an unsupported stop count');
  else { const bend = planBend(member, 'ROAM').bend; const fits = roam >= 50 ? roamValue >= roam - bend : roamValue <= roam + bend; if (!fits) reasons.push(`The plan's stop count is outside your ROAM bend`); }
  return { eligible: reasons.length === 0, reasons };
}

function roamConsensus(members: ChemistryMember[]) {
  const firm = members.flatMap((member) => {
    const { firm: isFirm, bend } = planBend(member, 'ROAM');
    return isFirm ? [{ score: member.ROAM ?? 50, bend }] : [];
  });
  const poles = new Set(firm.map(({ score }) => score >= 50 ? 'high' : 'low'));
  if (firm.length) {
    const weights = firm.map(({ bend }) => 1 / bend);
    return { value: firm.reduce((sum, item, index) => sum + item.score * weights[index], 0) / weights.reduce((sum, weight) => sum + weight, 0), split: poles.size > 1 };
  }
  const wants = members.flatMap((member) => {
    const score = member.ROAM ?? 50;
    return Math.abs(score - 50) >= 25 ? [{ score, weight: Math.abs(score - 50) / 50 }] : [];
  });
  const weight = wants.reduce((sum, item) => sum + item.weight, 0);
  return { value: weight ? wants.reduce((sum, item) => sum + item.score * item.weight, 0) / weight : 50, split: false };
}

function planStopCount(roam: number, durationHours: number) {
  const roamStops = roam < 35 ? 1 : roam < 65 ? 2 : 3;
  return Math.min(roamStops, Math.max(1, Math.min(3, Math.floor(durationHours / 1.75))));
}

export function chemistryV2(members: ChemistryMember[], durationHours = 4, strangers = false) {
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
  const roam = roamConsensus(safeMembers); const stopCount = planStopCount(roam.value, durationHours);
  const stopDurations = roam.split && stopCount > 1 ? [0.55, ...Array.from({ length: stopCount - 1 }, () => 0.45 / (stopCount - 1))] : Array.from({ length: stopCount }, () => 1 / stopCount);
  return { vector, tags: tags.slice(0, 2), formation: safeMembers.length > 1 ? 'Best of Both' : 'In Sync', stopCount, roam: Math.round(roam.value), roamSplit: roam.split, talkFloor: talker ? 40 : 0, stopDurations };
}

const stopAxes: Factor[] = ['ENRG', 'AFFIL', 'CROWD', 'TALK', 'MOVE', 'GAMES'];
const wantFloor = 25;
const subMin = 18;
const degree = 0.5;

function effectiveTop(member: ChemistryMember, members: ChemistryMember[]): Factor | undefined {
  const ranked = [...stopAxes].sort((a, b) => Math.abs((member[b] ?? 50) - 50) - Math.abs((member[a] ?? 50) - 50) || (member.latency_firmness?.[b] ?? 0) - (member.latency_firmness?.[a] ?? 0) || stopAxes.indexOf(a) - stopAxes.indexOf(b));
  const wants = ranked.filter((factor) => Math.abs((member[factor] ?? 50) - 50) >= wantFloor);
  const top = wants[0];
  if (!top) return undefined;
  const score = member[top] ?? 50;
  const opposed = members.some((other) => other !== member && planBend(other, top).firm && (((other[top] ?? 50) >= 50) !== (score >= 50)));
  const second = ranked.find((factor) => factor !== top && Math.abs((member[factor] ?? 50) - 50) >= subMin);
  return opposed && second ? second : top;
}

function topSatisfaction(template: Partial<Record<Factor, number>>, member: ChemistryMember, factor?: Factor): number {
  if (!factor) return 1;
  const score = member[factor] ?? 50;
  const bend = planBend(member, factor).bend;
  const value = template[factor] ?? 50;
  const delivered = score >= 50 ? value >= score - bend : value <= score + bend;
  if (delivered) return 1;
  return Math.abs(value - 50) <= 5 || ((value >= 50) === (score >= 50)) ? degree : 0;
}

export function selectVenueTypes(members: ChemistryMember[], durationHours = 4, strangers = false) {
  const safeMembers: ChemistryMember[] = members.length ? members : [Object.fromEntries(factors.map((factor) => [factor, 50])) as ChemistryMember];
  const room = chemistryV2(safeMembers, durationHours, strangers);
  const tops = safeMembers.map((member) => effectiveTop(member, safeMembers));
  const used = new Set<string>();
  const selected: string[] = [];
  let previousEnergy = -1;
  for (let stopIndex = 0; stopIndex < room.stopCount; stopIndex += 1) {
    const candidates = Object.entries(VENUE_TYPES).flatMap(([name, template]) => {
      if ((name === 'open ground' && stopIndex > 0) || (room.talkFloor && (template.TALK ?? 0) < room.talkFloor)) return [];
      const satisfaction = safeMembers.flatMap((member, index) => tops[index] ? [topSatisfaction(template, member, tops[index])] : []);
      const minimum = satisfaction.length ? Math.min(...satisfaction) : 1;
      const total = satisfaction.reduce((sum, value) => sum + value, 0);
      const arc = stopIndex === 0 ? -(template.ENRG ?? 50) : Number((template.ENRG ?? 50) >= previousEnergy - 10);
      const bridge = Number((satisfaction.includes(degree) || (strangers && stopIndex === 0)) && (template.GAMES ?? 0) >= 60);
      const tableFloor = Number(room.tags.includes('Table and Floor') && (template.AFFIL ?? 0) >= 55 && (template.CROWD ?? 0) >= 60);
      const commonGround = Number(room.tags.includes('Common Ground') && (template.GAMES ?? 0) >= 55 && (template.GAMES ?? 0) <= 70);
      const signalDistance = safeMembers.reduce((totalDistance, member) => totalDistance + stopAxes.reduce((sum, factor) => {
        const deviation = Math.abs((member[factor] ?? 50) - 50) / 50;
        return sum + Math.abs((template[factor] ?? 50) - (member[factor] ?? 50)) * (planBend(member, factor).firm ? 1 : 0.25) * deviation;
      }, 0), 0);
      const shapeDistance = stopAxes.reduce((sum, factor) => sum + Math.abs((template[factor] ?? 50) - (room.vector[factor] ?? 50)), 0);
      return [{ key: [minimum, total, Number(!used.has(name)), tableFloor, bridge, commonGround, arc, -signalDistance, -shapeDistance], name, energy: template.ENRG ?? 50 }];
    });
    candidates.sort((a, b) => {
      for (let index = 0; index < a.key.length; index += 1) if (a.key[index] !== b.key[index]) return b.key[index] - a.key[index];
      return a.name.localeCompare(b.name);
    });
    const winner = candidates[0];
    if (!winner) break;
    selected.push(winner.name);
    used.add(winner.name);
    previousEnergy = winner.energy;
  }
  return selected.length ? selected : ['pub'];
}

export function generatePlan(members: Partial<Record<Factor, number>>[], venues: { name: string; type: string; scores: Partial<Record<Factor, number>> }[]) {
  const room = chemistry(members); const used = new Set<string>();
  return Array.from({ length: room.stopCount }, (_, index) => {
    const venue = venues.filter((candidate) => !used.has(candidate.name)).sort((a, b) => closeness(room.vector, a.scores) - closeness(room.vector, b.scores))[0] ?? venues[0];
    if (venue) used.add(venue.name);
    return { index: index + 1, venue, durationShare: room.stopDurations[index] ?? 0, type: venue?.type ?? 'open night' };
  });
}

function closeness(target: Partial<Record<Factor, number>>, candidate: Partial<Record<Factor, number>>) { return factors.reduce((sum, factor) => sum + Math.abs((target[factor] ?? 50) - (candidate[factor] ?? 50)), 0); }
