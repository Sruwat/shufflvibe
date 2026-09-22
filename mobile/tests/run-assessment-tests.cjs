const assert = require('node:assert/strict');
const fs = require('node:fs');
const ts = require('typescript');
require.extensions['.ts'] = (module, filename) => {
  const source = fs.readFileSync(filename, 'utf8');
  const output = ts.transpileModule(source, { compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020, esModuleInterop: true } }).outputText;
  module._compile(output, filename);
};
const { createAssessment, currentCard, beginExposure, deferCard, resolveAway, resumeAssessment, isRequiredAnswerExposure, backCard, answerCard, latencyFirmness, chemistryV2, selectVenueTypes, joinerShapeFit } = require('../src/fullEngine.ts');
const { vibeName } = require('../src/algorithms.ts');
const { DemoService } = require('../src/services.ts');

function testAwayPromptDiscardsTimeoutsAndResumesInPlace() {
  let state = createAssessment();
  state = beginExposure(state, 0);
  state = deferCard(state, 'timeout', 12000);
  state = beginExposure(state, 13000);
  state = deferCard(state, 'timeout', 25000);
  assert.equal(state.awayPrompt, true);
  assert.equal(state.paused, true);
  const resumed = resolveAway(state, 'present');
  assert.equal(resumed.paused, false);
  assert.equal(resumed.awayPrompt, false);
  assert.equal(resumed.exposures.length, 0);
  assert.equal(currentCard(resumed).factor, 'CROWD');
}
function testAwayChoiceResetsToFirstTimedOutCard() {
  let state = createAssessment();
  const first = currentCard(state);
  state = { ...state, exposures: [{ card: { ...first }, index: 0, startedAt: 1, endedAt: 2, endedBy: 'back', nextCount: 0 }] };
  state = beginExposure(state, 0);
  state = deferCard(state, 'timeout', 12000);
  state = beginExposure(state, 13000);
  state = deferCard(state, 'timeout', 25000);
  const returned = resolveAway(state, 'away');
  assert.equal(currentCard(returned).id, first.id);
  assert.equal(returned.exposures.length, 1);
  assert.equal(returned.exposures[0].endedBy, 'back');
  assert.equal(returned.history.length, 0);
  assert.equal(returned.paused, false);
}
function testUnansweredPauseRequiresExplicitResume() {
  let state = createAssessment();
  state = beginExposure(state, 0);
  state = deferCard(state, 'timeout', 12000);
  state = beginExposure(state, 13000);
  state = deferCard(state, 'timeout', 25000);
  const paused = resolveAway(state, 'unanswered');
  assert.equal(paused.paused, true);
  assert.equal(paused.awayPrompt, false);
  assert.equal(currentCard(paused).id, 'V-ENRG-A');
  const resumed = resumeAssessment(paused);
  assert.equal(resumed.paused, false);
  assert.equal(resumeAssessment(resumed), resumed);
}
function testThirdExposureCannotBeDeferred() {
  let state = createAssessment();
  const card = currentCard(state);
  state = { ...state, exposures: [0, 1].map((n) => ({ card, index: n, startedAt: n * 1000, endedAt: n * 1000 + 800, endedBy: 'next', nextCount: n + 1 })) };
  assert.equal(isRequiredAnswerExposure(state), true);
  state = beginExposure(state, 3000);
  assert.equal(isRequiredAnswerExposure(state), true);
  assert.equal(deferCard(state, 'next', 4000), state);
}
function testBackAfterAnsweredCardReturnsToTheCurrentCard() {
  let state = createAssessment();
  state = beginExposure(state, 100);
  state = answerCard(state, 'UP', 200);
  state = beginExposure(state, 300);
  state = backCard(state, 400);
  assert.equal(currentCard(state).id, 'V-ENRG-A');
  state = beginExposure(state, 500);
  state = answerCard(state, 'LOVE', 600);
  assert.equal(currentCard(state).factor, 'AFFIL');
}
function testBackRecordsExposureAndReturnsToPreviousCard() {
  let state = createAssessment();
  state = beginExposure(state, 100);
  state = deferCard(state, 'next', 500);
  const current = currentCard(state);
  state = beginExposure(state, 600);
  const returned = backCard(state, 900);
  assert.equal(currentCard(returned).id, 'V-ENRG-A');
  const backExposure = returned.exposures.find((exposure) => exposure.card.id === current.id);
  assert.equal(backExposure.endedBy, 'back');
  assert.equal(backExposure.latency, 300);
}
function testOneTimeoutDoesNotOpenAwayPrompt() {
  let state = createAssessment();
  state = beginExposure(state, 0);
  state = deferCard(state, 'timeout', 12000);
  assert.equal(state.awayPrompt, false);
  assert.equal(state.paused, false);
  assert.equal(currentCard(state).factor, 'AFFIL');
}
function testDeferredPartnerIsPulledForwardOnCollision() {
  let state = createAssessment();
  const first = currentCard(state);
  const partner = { id: 'V-ENRG-B', factor: first.factor, side: 'B' };
  state = { ...state, queue: [...state.queue, partner] };
  state = beginExposure(state, 100);
  state = deferCard(state, 'next', 200);
  assert.equal(currentCard(state).id, partner.id);
  assert.notEqual(state.queue[state.queue.length - 1].id, partner.id);
}
function testVenueTypesUseMaximinTopFactorSatisfaction() {
  const types = selectVenueTypes([{ GAMES: 88 }, { GAMES: 12 }], 6);
  assert.equal(types[0], 'pub');
  assert.equal(types.includes('games bar'), false);
}

function testRoamBendConsensusAndDurationCap() {
  const flexibleLow = chemistryV2([{ ROAM: 92 }, { ROAM: 30 }], 6);
  assert.equal(flexibleLow.roam, 92);
  assert.equal(flexibleLow.stopCount, 3);
  const fastBandOpposition = chemistryV2([{ ROAM: 92 }, { ROAM: 25, latency_firmness: { ROAM: 0.9 } }], 6);
  assert.equal(fastBandOpposition.roamSplit, true);
  assert.equal(fastBandOpposition.stopCount, 2);
  assert.deepEqual(fastBandOpposition.stopDurations, [0.55, 0.45]);
  const shortNight = chemistryV2([{ ROAM: 92 }], 3);
  assert.equal(shortNight.stopCount, 1);
}

function testLatencyFirmnessUsesPostWarmupAnsweredCards() {
  const factorIds = ['ENRG', 'AFFIL', 'CROWD', 'TALK', 'ROAM', 'MOVE', 'GAMES'];
  const state = createAssessment();
  state.answers = Object.fromEntries(factorIds.map((factor) => [`V-${factor}-A`, 'LOVE']));
  state.exposures = factorIds.map((factor, index) => ({ card: { id: `V-${factor}-A`, factor, side: 'A' }, index: index + 3, startedAt: 0, endedAt: 100, endedBy: 'swiped', nextCount: 0, latency: (index + 1) * 100 }));
  const firmness = latencyFirmness(state);
  assert.equal(firmness.ENRG, 1);
  assert.equal(firmness.GAMES, 0);
}

function testVibeNameV4UsesTheChosenTopAndFactorWeightForSecondTie() {
  const scores = { ENRG: 88, AFFIL: 12, CROWD: 88, TALK: 62, ROAM: 50, MOVE: 50, GAMES: 50 };
  assert.equal(vibeName(scores, {}, 'CROWD').startsWith('Big-Room'), true);
  assert.equal(vibeName({ ENRG: 88, AFFIL: 88, CROWD: 12, TALK: 50, ROAM: 50, MOVE: 50, GAMES: 50 }), 'Peak Insider');
  assert.equal(vibeName({ ENRG: 88, AFFIL: 50, CROWD: 50, TALK: 50, ROAM: 50, MOVE: 50, GAMES: 50 }), 'Night Climber');
}


function testJoinerShapeFitUsesFrozenTypesAndRoamBend() {
  const member = { ENRG: 12, AFFIL: 88, CROWD: 12, TALK: 70, ROAM: 12, MOVE: 12, GAMES: 12 };
  assert.deepEqual(joinerShapeFit(member, ['table for the night'], 1), { eligible: true, reasons: [] });
  const mismatch = joinerShapeFit({ ...member, AFFIL: 12 }, ['table for the night'], 3);
  assert.equal(mismatch.eligible, false);
  assert.ok(mismatch.reasons.some(reason => reason.includes('AFFIL')));
  assert.ok(mismatch.reasons.some(reason => reason.includes('ROAM')));
}

async function testDemoRoomJoinRequestEndToEnd() {
  const room = (await DemoService.listHostedRooms()).find(item => item.id === 'room-demo');
  assert.ok(room);
  const created = await DemoService.requestToJoin(room.id, 'mobile-test-joiner', 'Joining for dinner', { ENRG: 12, AFFIL: 88, CROWD: 12, TALK: 70, ROAM: 12, MOVE: 12, GAMES: 12 });
  const rejectedFit = await DemoService.getRoomEligibility(room.id, { ENRG: 95, AFFIL: 5, CROWD: 5, TALK: 5, ROAM: 95, MOVE: 95, GAMES: 95 });
  assert.equal(rejectedFit.eligible, false);
  assert.equal(created.status, 'pending');
  assert.equal((await DemoService.requestToJoin(room.id, 'mobile-test-joiner', '', { ENRG: 12, AFFIL: 88, CROWD: 12, TALK: 70, ROAM: 12, MOVE: 12, GAMES: 12 })).id, created.id);
  assert.equal((await DemoService.getJoinRequests(room.id)).length, 1);
  const decision = await DemoService.decideJoinRequest(room.id, created.id, 'accepted');
  assert.equal(decision.plan_frozen, true);
  assert.deepEqual(decision.room.members, ['demo-user', 'mobile-test-joiner']);
  assert.equal((await DemoService.getJoinRequests(room.id)).length, 0);
}

for (const test of [testOneTimeoutDoesNotOpenAwayPrompt, testDeferredPartnerIsPulledForwardOnCollision, testAwayPromptDiscardsTimeoutsAndResumesInPlace, testAwayChoiceResetsToFirstTimedOutCard, testUnansweredPauseRequiresExplicitResume, testThirdExposureCannotBeDeferred, testBackRecordsExposureAndReturnsToPreviousCard, testBackAfterAnsweredCardReturnsToTheCurrentCard, testVibeNameV4UsesTheChosenTopAndFactorWeightForSecondTie, testLatencyFirmnessUsesPostWarmupAnsweredCards, testRoamBendConsensusAndDurationCap, testVenueTypesUseMaximinTopFactorSatisfaction, testJoinerShapeFitUsesFrozenTypesAndRoamBend]) test();
testDemoRoomJoinRequestEndToEnd().then(() => console.log('14 mobile assessment, naming, plan-chemistry, and room-flow tests passed')).catch(error => { console.error(error); process.exitCode = 1; });
