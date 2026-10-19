import { Factor, venues } from './data';
import { chemistryV2, fillVenues, joinerShapeFit, selectVenueTypes } from './fullEngine';
import { RELEASE_SCOPE } from './releaseScope';

export type PrivacySettings = { location_sharing: boolean; approximate_presence: boolean; discoverability: boolean; visibility: Record<string, 'everyone' | 'friends' | 'nobody'> };
export type PlanLocationConsent = { approved: boolean };
export type SafetyAction = { blocked: boolean };
export type SafetyReport = { id: string; status: string };
export type AuthUser = { id: string; email: string; name: string; created_at?: string };
export type AuthSession = { access_token: string; token_type: 'bearer'; user: AuthUser };
const defaultPrivacy: PrivacySettings = { location_sharing: false, approximate_presence: true, discoverability: true, visibility: { profile: 'friends', vibe: 'friends', plans: 'friends' } };
let demoPrivacy: PrivacySettings = { ...defaultPrivacy, visibility: { ...defaultPrivacy.visibility } };
const demoPlanConsents: Record<string, boolean> = {};
const demoBlockedUsers = new Set<string>();
const demoPlans: Record<string, { types: string[]; count: number }> = { 'plan-demo': { types: ['table for the night'], count: 1 } };
const demoRooms: Record<string, RoomRecord & { visibility: string; join_requests: JoinRequestRecord[]; plan_id?: string }> = { 'room-demo': { id: 'room-demo', title: 'Friday night, open to the city', status: 'hosted', visibility: 'public', members: ['demo-user'], plan_id: 'plan-demo', join_requests: [] } };
let demoReportSequence = 0;

export type ServiceMode = 'demo' | 'api';
export type PlanInput = {
  scores: Record<string, number>;
  preferences?: Record<string, number>;
  selectedVenueName?: string;
  pol_sense?: 'classy' | 'current' | 'both';
  members?: string[];
  duration_hours?: number;
  strangers?: boolean;
};
export type GeneratedPlan = { id: string; style: string; stops: string[]; chemistry?: Record<string, unknown> };
export type JoinerScores = Partial<Record<Factor, number>> & { latency_firmness?: Partial<Record<Factor, number>> };
export type RoomFit = { eligible: boolean; reasons: string[] };
export type RoomStop = { venue_id?: string; name: string; area?: string; stop_index?: number };
export type RoomRecord = { id: string; title: string; status: string; members?: string[]; plan_id?: string; stop_types?: string[]; stop_count?: number; selected_stops?: RoomStop[]; join_eligibility?: RoomFit };
export type JoinRequestRecord = { id: string; room_id: string; member_id: string; status: 'pending' | 'accepted' | 'declined'; note: string; fit?: boolean; fit_reasons?: string[]; created_at?: string };
export type CapsuleRecord = { id: string; room_id: string; members: string[]; approvals: Record<string, boolean>; status: 'awaiting_approval' | 'approved'; created_at?: string };
export type ChatMessage = { id: string; conversation_id: string; body: string; sender_id?: string; status?: string; read?: boolean; created_at?: string };
export type ConversationRecord = { id: string; kind: 'group' | 'direct'; title: string; unread: number; messages: ChatMessage[] };
export type NotificationRecord = { id: string; kind: string; title: string; body?: string; read: boolean; room_id?: string; gathering_id?: string; created_at?: string };
export type WheelRequest = { id: string; gathering_id: string; requester_id: string; status: 'pending' | 'accepted' | 'declined'; created_at?: string };
export type ProfileRecord = { name: string; city: string; pronouns?: string; bio?: string; preferences: Record<string, number>; updated_at?: string };
export type PersonRecord = { id: string; name: string; city?: string; bio?: string };
export type FriendRecord = PersonRecord & { status: 'pending' | 'accepted' | 'declined'; request_id?: string };
export type GatheringRecord = { id: string; name: string; status: string; wheel_owner_id: string; conversation_id?: string; members: Array<{ user_id: string; role: string; invite_status: string; skeleton?: Record<string, unknown> }> };
export type GatheringProposal = { id: string; gathering_id?: string; kind: 'room' | 'venue' | 'plan'; payload: Record<string, unknown>; status: 'pending' | 'accepted' | 'declined' | 'ignored'; created_at?: string };
export type VenueCard = (typeof venues)[number] & { id?: string; google_place_id?: string; google_lookup_url?: string; official_url?: string; hours_mode?: string; match_distance?: number; live?: Record<string, unknown> | null; address?: string; website_url?: string; menu_url?: string; social_urls?: string[]; tags?: string[]; rating?: number; review_count?: number; photos?: string[]; selectable?: boolean; admission_badge?: string; eligibility_status?: string };
export type VenueDetail = { venue: VenueCard | Record<string, unknown>; normalized: Record<string, unknown>; google_place_id?: string; google_lookup_url?: string; live_fields: { source: string; persisted: boolean } };
export type SkeletonPayload = { scores: Record<string, number>; stops: number; energy: number; crowd: number; tags: string[]; stop_durations: number[]; source?: string };
export type SkeletonRecord = SkeletonPayload & { id: string; created_at: string };
export type AssessmentCompletion = { scores: Record<string, number>; vibe_name: string; chosen_top?: string; latency_firmness?: Record<string, number>; actions?: Record<string, string> };
export type SelectedPlanStop = { venue_id?: string; name: string; area?: string; stop_index: number };
export type Service = {
  mode: ServiceMode;
  register: (email: string, password: string, name?: string) => Promise<AuthSession>;
  login: (email: string, password: string) => Promise<AuthSession>;
  loginWithGoogle: (idToken: string) => Promise<AuthSession>;
  getAuthUser: () => Promise<AuthUser>;
  logout: () => Promise<void>;
  getDiscovery: () => Promise<typeof venues>;
  getVenue: (venueId: string) => Promise<VenueDetail>;
  getLiveVenue: (venueId: string) => Promise<Record<string, unknown>>;
  getStopOptions: (target: Record<string, number>, options?: { city?: string; area?: string; limit?: number; includeLive?: boolean }) => Promise<VenueCard[]>;
  completeAssessment: (payload: AssessmentCompletion) => Promise<void>;
  saveSkeleton: (payload: SkeletonPayload) => Promise<SkeletonRecord>;
  getLatestSkeleton: () => Promise<SkeletonRecord | null>;
  createSelectedPlan: (input: { title: string; duration_hours: number; scores: Record<string, number>; stops: SelectedPlanStop[]; chemistry?: Record<string, unknown> }) => Promise<GeneratedPlan>;
  updatePlanStops: (planId: string, stops: SelectedPlanStop[]) => Promise<GeneratedPlan>;
  getPlan: (planId: string) => Promise<GeneratedPlan & { locked?: boolean; selected_stops?: SelectedPlanStop[] }>;
  generatePlan: (input: PlanInput) => Promise<GeneratedPlan>;
  createRoom: (title: string, members?: string[]) => Promise<RoomRecord>;
  hostRoom: (roomId: string, planId: string) => Promise<RoomRecord>;
  listHostedRooms: () => Promise<RoomRecord[]>;
  getRoomEligibility: (roomId: string, scores: JoinerScores) => Promise<RoomFit>;
  requestToJoin: (roomId: string, memberId: string, note?: string, scores?: JoinerScores) => Promise<JoinRequestRecord>;
  getJoinRequests: (roomId: string, status?: 'pending' | 'accepted' | 'declined' | 'all') => Promise<JoinRequestRecord[]>;
  decideJoinRequest: (roomId: string, requestId: string, status: 'accepted' | 'declined') => Promise<{ request: JoinRequestRecord; room: RoomRecord; plan_frozen: boolean }>;
  createCapsule: (roomId: string, memberIds: string[]) => Promise<CapsuleRecord>;
  getCapsule: (capsuleId: string) => Promise<CapsuleRecord>;
  approveCapsule: (capsuleId: string, memberId: string, approved: boolean) => Promise<CapsuleRecord>;
  createRoomInvite: (roomId: string) => Promise<{ room_id: string; invite_token: string; invite_url: string }>;
  joinRoomByInvite: (inviteToken: string) => Promise<RoomRecord>;
  listConversations: () => Promise<ConversationRecord[]>;
  sendChatMessage: (conversationId: string, body: string) => Promise<ChatMessage>;
  markConversationRead: (conversationId: string) => Promise<void>;
  listNotifications: (unreadOnly?: boolean) => Promise<NotificationRecord[]>;
  markNotificationRead: (notificationId: string) => Promise<NotificationRecord>;
  getProfile: () => Promise<ProfileRecord>;
  listPeople: (query?: string) => Promise<PersonRecord[]>;
  listFriends: () => Promise<FriendRecord[]>;
  createFriendRequest: (userId: string) => Promise<FriendRecord>;
  createGathering: (name: string, memberIds?: string[]) => Promise<GatheringRecord>;
  getGathering: (gatheringId: string) => Promise<GatheringRecord>;
  addGatheringMember: (gatheringId: string, userId: string) => Promise<void>;
  decideGatheringInvite: (gatheringId: string, userId: string, status: 'accepted' | 'declined') => Promise<Record<string, unknown>>;
  requestWheel: (gatheringId: string) => Promise<Record<string, unknown>>;
  listWheelRequests: (gatheringId: string) => Promise<WheelRequest[]>;
  decideWheel: (gatheringId: string, status: 'accepted' | 'declined') => Promise<Record<string, unknown>>;
  saveGatheringSkeleton: (gatheringId: string, payload: SkeletonPayload) => Promise<Record<string, unknown>>;
  getGatheringSkeleton: (gatheringId: string) => Promise<Record<string, unknown>>;
  mergeGatheringSkeleton: (gatheringId: string) => Promise<Record<string, unknown>>;
  listGatheringProposals: (gatheringId: string) => Promise<GatheringProposal[]>;
  createGatheringProposal: (gatheringId: string, kind: GatheringProposal['kind'], payload: Record<string, unknown>) => Promise<GatheringProposal>;
  decideGatheringProposal: (gatheringId: string, proposalId: string, status: 'accepted' | 'declined' | 'ignored') => Promise<GatheringProposal>;
  saveProfile: (profile: ProfileRecord) => Promise<ProfileRecord>;
  deleteAccount: () => Promise<{ deleted: boolean; message: string }>;
  lockPlan: (planId: string) => Promise<void>;
  getPrivacy: () => Promise<PrivacySettings>;
  savePrivacy: (settings: PrivacySettings) => Promise<PrivacySettings>;
  getPlanLocationConsent: (planId: string) => Promise<PlanLocationConsent>;
  savePlanLocationConsent: (planId: string, approved: boolean) => Promise<PlanLocationConsent>;
  submitReport: (targetId: string, reason: string) => Promise<SafetyReport>;
  blockUser: (targetId: string) => Promise<SafetyAction>;
  unblockUser: (targetId: string) => Promise<SafetyAction>;
  getBlockedUsers: () => Promise<string[]>;
};

export const DemoService: Service = {
  mode: 'demo',
  register: async (email, _password, name = '') => ({ access_token: 'demo-token', token_type: 'bearer', user: { id: 'demo-user', email, name } }),
  login: async (email, _password) => ({ access_token: 'demo-token', token_type: 'bearer', user: { id: 'demo-user', email, name: 'Aarav Mehta' } }),
  loginWithGoogle: async () => ({ access_token: 'demo-token', token_type: 'bearer', user: { id: 'demo-user', email: 'demo@shuffl.local', name: 'Aarav Mehta' } }),
  getAuthUser: async () => ({ id: 'demo-user', email: 'demo@shuffl.local', name: 'Aarav Mehta' }),
  logout: async () => undefined,
  getDiscovery: async () => venues,
  getVenue: async (venueId) => ({ venue: venues.find((venue) => venue.name === venueId) ?? venues[0], normalized: {}, live_fields: { source: 'demo', persisted: false } }),
  getLiveVenue: async () => ({}),
  getStopOptions: async (target) => venues.map((venue) => ({ ...venue, match_distance: Object.keys(target).length ? 50 : undefined })),
  completeAssessment: async () => undefined,
  saveSkeleton: async (payload) => ({ id: `demo-skeleton-${Date.now()}`, created_at: new Date().toISOString(), ...payload }),
  getLatestSkeleton: async () => null,
  createSelectedPlan: async (input) => ({ id: `demo-plan-${Date.now()}`, style: input.title || 'Your night', stops: input.stops.map((stop) => `${stop.name} · ${stop.area ?? 'Delhi NCR'}`), chemistry: input.chemistry }),
  updatePlanStops: async (planId, stops) => ({ id: planId, style: 'Your night', stops: stops.map((stop) => `${stop.name} · ${stop.area ?? 'Delhi NCR'}`) }),
  getPlan: async (planId) => ({ id: planId, style: 'Your night', stops: [] }),
  generatePlan: async (input) => {
    const memberScores = [input.scores];
    const chemistry = chemistryV2(memberScores, input.duration_hours ?? 4, input.strangers ?? false);
    const types = selectVenueTypes(memberScores, input.duration_hours ?? 4, input.strangers ?? false);
    const selected = fillVenues(types, [input.preferences ?? {}], venues);
    const fixed = input.selectedVenueName ? venues.find((venue) => venue.name === input.selectedVenueName) : undefined;
    const ordered = fixed ? [fixed, ...selected.filter((venue) => venue.name !== fixed.name)] : selected;
    const id = `demo-plan-${Date.now()}`;
    demoPlans[id] = { types, count: selected.length };
    return { id, style: chemistry.tags[0] ?? 'Settle Then Roam', stops: ordered.slice(0, Math.max(1, chemistry.stopCount)).map((venue) => venue.name), chemistry };
  },
  createRoom: async (title, members = []) => { const id = `demo-room-${Date.now()}`; demoRooms[id] = { id, title, status: 'draft', visibility: 'private', members: [...members], join_requests: [] }; return demoRooms[id]; },
  hostRoom: async (roomId, planId) => { const room = demoRooms[roomId]; if (!room) throw new Error('Room not found'); if (!demoPlans[planId]) throw new Error('Plan shape not found'); room.plan_id = planId; room.status = 'hosted'; room.visibility = 'public'; return room; },
  listHostedRooms: async () => Object.values(demoRooms).filter(room => room.status === 'hosted').map(({ join_requests: _requests, ...room }) => { const plan = demoPlans[room.plan_id ?? '']; return { ...room, ...(plan ? { stop_types: plan.types, stop_count: plan.count } : {}) }; }),
  getRoomEligibility: async (roomId, scores) => { const room = demoRooms[roomId]; if (!room || room.status !== 'hosted') throw new Error('Room is not accepting requests'); const plan = demoPlans[room.plan_id ?? '']; if (!plan) throw new Error('This room has no available frozen plan'); return joinerShapeFit(scores, plan.types, plan.count); },
  requestToJoin: async (roomId, memberId, note = '', scores = {}) => { const room = demoRooms[roomId]; if (!room || room.status !== 'hosted') throw new Error('Room is not accepting requests'); if (room.members?.includes(memberId)) throw new Error('You are already a room member'); const plan = demoPlans[room.plan_id ?? '']; if (!plan) throw new Error('This room has no available frozen plan'); const fit = joinerShapeFit(scores, plan.types, plan.count); const old = room.join_requests.find(item => item.member_id === memberId && item.status === 'pending'); if (old) return old; const request: JoinRequestRecord = { id: 'demo-join-' + Date.now(), room_id: roomId, member_id: memberId, status: 'pending', note, fit: fit.eligible, fit_reasons: fit.reasons }; room.join_requests.push(request); return request; },
  getJoinRequests: async (roomId, status = 'pending') => { const room = demoRooms[roomId]; if (!room) throw new Error('Room not found'); return room.join_requests.filter(item => status === 'all' || item.status === status); },
  decideJoinRequest: async (roomId, requestId, status) => { const room = demoRooms[roomId]; const request = room?.join_requests.find(item => item.id === requestId); if (!room || !request) throw new Error('Join request not found'); if (request.status !== 'pending') throw new Error('Join request already resolved'); request.status = status; if (status === 'accepted' && !room.members?.includes(request.member_id)) room.members = [...(room.members ?? []), request.member_id]; const { join_requests: _requests, ...roomRecord } = room; return { request, room: roomRecord, plan_frozen: true }; },
  createCapsule: async (roomId, memberIds) => ({ id: `demo-capsule-${Date.now()}`, room_id: roomId, members: [...new Set(memberIds)], approvals: Object.fromEntries(memberIds.map((member) => [member, false])), status: 'awaiting_approval' }),
  getCapsule: async () => { throw new Error('Capsule lookup is available after connecting the API'); },
  approveCapsule: async (capsuleId, memberId, approved) => ({ id: capsuleId, room_id: 'demo-room', members: [memberId], approvals: { [memberId]: approved }, status: approved ? 'approved' : 'awaiting_approval' }),
  createRoomInvite: async (roomId) => ({ room_id: roomId, invite_token: 'demo-token', invite_url: `shuffl://join/${roomId}?token=demo-token` }),
  joinRoomByInvite: async (inviteToken) => { if (inviteToken !== 'demo-token') throw new Error('Invite is invalid or expired'); return demoRooms['room-demo']; },
  listConversations: async () => [{ id: 'conversation-demo', kind: 'group', title: 'Friday Room', unread: 1, messages: [{ id: 'demo-message-1', conversation_id: 'conversation-demo', sender_id: 'Bela Shah', body: 'The plan is in. I’m in for the first stop.', read: false, status: 'sent' }] }],
  sendChatMessage: async (conversationId, body) => ({ id: `demo-message-${Date.now()}`, conversation_id: conversationId, sender_id: 'You', body, status: 'sent', read: true, created_at: new Date().toISOString() }),
  markConversationRead: async () => undefined,
  listNotifications: async () => [{ id: 'demo-notification-1', kind: 'room_request', title: 'A room is forming', body: 'Friday night, open to the city has join requests open.', read: false }],
  markNotificationRead: async (notificationId) => ({ id: notificationId, kind: 'room_request', title: 'Notification', read: true }),
  getProfile: async () => ({ name: 'Aarav Mehta', city: 'New Delhi', preferences: { FOOD: 88, SCEN: 88, NOV: 62 } }),
  listPeople: async (query = '') => [{ id: 'demo-user-2', name: 'Bela Shah', city: 'New Delhi', bio: '' }, { id: 'demo-user-3', name: 'Chirag Mehta', city: 'New Delhi', bio: '' }, { id: 'demo-user-4', name: 'Maya Kapoor', city: 'New Delhi', bio: '' }, { id: 'demo-user-5', name: 'Dev Malhotra', city: 'New Delhi', bio: '' }].filter((person) => person.name.toLowerCase().includes(query.trim().toLowerCase())),
  listFriends: async () => [],
  createFriendRequest: async (userId) => ({ id: `friend-${userId}`, user_id: userId, name: userId, status: 'pending' }),
  createGathering: async (name, memberIds = []) => ({ id: `gathering-${Date.now()}`, name, status: 'gathering', wheel_owner_id: 'demo-user', members: [{ user_id: 'demo-user', role: 'owner', invite_status: 'accepted' }, ...memberIds.map((user_id) => ({ user_id, role: 'member', invite_status: 'pending' }))] }),
  getGathering: async (gatheringId) => ({ id: gatheringId, name: 'Tonight together', status: 'gathering', wheel_owner_id: 'demo-user', members: [{ user_id: 'demo-user', role: 'owner', invite_status: 'accepted' }] }),
  addGatheringMember: async () => undefined,
  decideGatheringInvite: async (gatheringId, userId, status) => ({ gathering_id: gatheringId, user_id: userId, invite_status: status }),
  requestWheel: async (gatheringId) => ({ id: `wheel-${Date.now()}`, gathering_id: gatheringId, status: 'pending' }),
  listWheelRequests: async () => [],
  decideWheel: async (gatheringId, status) => ({ gathering_id: gatheringId, status }),
  saveGatheringSkeleton: async (gatheringId, payload) => ({ gathering_id: gatheringId, skeleton: payload }),
  getGatheringSkeleton: async () => ({ members: [], complete: false }),
  mergeGatheringSkeleton: async (gatheringId) => ({ gathering_id: gatheringId, merged: {} }),
  listGatheringProposals: async () => [],
  createGatheringProposal: async (gatheringId, kind, payload) => ({ id: `proposal-${Date.now()}`, gathering_id: gatheringId, kind, payload, status: 'pending' }),
  decideGatheringProposal: async (gatheringId, proposalId, status) => ({ id: proposalId, gathering_id: gatheringId, kind: 'room', payload: {}, status }),
  saveProfile: async (profile) => profile,
  deleteAccount: async () => ({ deleted: true, message: 'Local account data reset.' }),
  lockPlan: async () => undefined,
  getPrivacy: async () => ({ ...demoPrivacy, visibility: { ...demoPrivacy.visibility } }),
  savePrivacy: async (settings) => { demoPrivacy = { ...settings, visibility: { ...settings.visibility } }; if (!settings.location_sharing) Object.keys(demoPlanConsents).forEach((key) => { demoPlanConsents[key] = false; }); return { ...demoPrivacy, visibility: { ...demoPrivacy.visibility } }; },
  getPlanLocationConsent: async (planId) => ({ approved: demoPrivacy.location_sharing && Boolean(demoPlanConsents[planId]) }),
  savePlanLocationConsent: async (planId, approved) => { if (approved && !demoPrivacy.location_sharing) throw new Error("Enable per-plan location sharing in privacy settings first"); demoPlanConsents[planId] = approved; return { approved }; },
  submitReport: async (_targetId, _reason) => ({ id: `demo-report-${++demoReportSequence}`, status: 'received' }),
  blockUser: async (targetId) => { demoBlockedUsers.add(targetId); return { blocked: true }; },
  unblockUser: async (targetId) => { demoBlockedUsers.delete(targetId); return { blocked: false }; },
  getBlockedUsers: async () => [...demoBlockedUsers].sort(),
};

export function createApiService(baseUrl: string): Service {
  const sessionStorageKey = `shuffl.api-session:${baseUrl}`;
  const authStorageKey = `shuffl.auth-token:${baseUrl}`;
  let sessionId: string | undefined = (() => {
    try {
      return typeof localStorage === "undefined" ? undefined : localStorage.getItem(sessionStorageKey) ?? undefined;
    } catch {
      return undefined;
    }
  })();
  let authToken: string | undefined = (() => {
    try {
      return typeof localStorage === "undefined" ? undefined : localStorage.getItem(authStorageKey) ?? undefined;
    } catch {
      return undefined;
    }
  })();
  let sessionPromise: Promise<void> | undefined;
  const ensureSession = async () => {
    if (sessionId) return;
    if (!sessionPromise) {
      sessionPromise = fetch(`${baseUrl}/v1/sessions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "ngrok-skip-browser-warning": "true",
        },
        body: JSON.stringify({ client_id: `mobile-${Date.now().toString(36)}` }),
      }).then(async (response) => {
        if (!response.ok) throw new Error(`SHUFFL session ${response.status}`);
        const payload = (await response.json()) as { id?: string };
        if (!payload.id) throw new Error("SHUFFL session response was invalid.");
        sessionId = payload.id;
        try {
          if (typeof localStorage !== "undefined") localStorage.setItem(sessionStorageKey, payload.id);
        } catch {
          // Native builds keep the session in memory until secure auth storage is added.
        }
      }).finally(() => {
        sessionPromise = undefined;
      });
    }
    await sessionPromise;
  };
  const request = async (path: string, init?: RequestInit) => {
    const method = (init?.method ?? 'GET').toUpperCase();
    let lastError: unknown;
    if (path !== "/v1/sessions") await ensureSession();
    for (let attempt = 0; attempt < (method === 'GET' ? 2 : 1); attempt += 1) {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 10000);
      try {
        const headers = new Headers(init?.headers);
        headers.set('Content-Type', 'application/json');
        headers.set('ngrok-skip-browser-warning', 'true');
        if (sessionId) headers.set('X-Session-Id', sessionId);
        if (authToken) headers.set('Authorization', `Bearer ${authToken}`);
        const response = await fetch(`${baseUrl}${path}`, {
          headers,
          ...init,
          signal: controller.signal,
        });
        if (!response.ok) {
          if (method === 'GET' && response.status >= 500 && attempt === 0) continue;
          throw new Error(response.status >= 500 ? 'SHUFFL server is temporarily unavailable.' : `SHUFFL API ${response.status}`);
        }
        return response.json() as Promise<Record<string, unknown>>;
      } catch (cause) {
        lastError = cause;
        if (method !== 'GET' || attempt > 0) break;
      } finally {
        clearTimeout(timeout);
      }
    }
    if (lastError instanceof Error && lastError.name === 'AbortError') throw new Error('SHUFFL request timed out. Check your connection and retry.');
    throw new Error('SHUFFL is offline or unreachable. Check your connection and retry.');
  };
  const toVenue = (value: unknown): VenueCard => {
    const item = (value ?? {}) as Record<string, unknown>;
    const rawScores = (item.scores ?? {}) as Record<string, number>;
    const readScore = (upper: string, lower: string) => rawScores[upper] ?? rawScores[lower] ?? 50;
    const tags = Array.isArray(item.tags) ? item.tags.map(String) : [];
    return {
      id: item.id ? String(item.id) : undefined,
      google_place_id: item.google_place_id ? String(item.google_place_id) : undefined,
      google_lookup_url: item.google_lookup_url ? String(item.google_lookup_url) : undefined,
      official_url: item.official_url ? String(item.official_url) : undefined,
      address: item.address ? String(item.address) : undefined,
      website_url: item.website_url ? String(item.website_url) : undefined,
      menu_url: item.menu_url ? String(item.menu_url) : undefined,
      social_urls: Array.isArray(item.social_urls) ? item.social_urls.map(String) : [],
      tags,
      rating: typeof item.rating === 'number' ? item.rating : undefined,
      review_count: typeof item.review_count === 'number' ? item.review_count : undefined,
      photos: Array.isArray(item.photos) ? item.photos.map(String) : [],
      selectable: item.selectable !== false,
      admission_badge: item.admission_badge ? String(item.admission_badge) : undefined,
      eligibility_status: item.eligibility_status ? String(item.eligibility_status) : undefined,
      hours_mode: item.hours_mode ? String(item.hours_mode) : undefined,
      match_distance: typeof item.match_distance === 'number' ? item.match_distance : undefined,
      live: (item.live as Record<string, unknown> | null | undefined) ?? null,
      name: String(item.name ?? item.display_name ?? 'SHUFFL venue'),
      type: String(item.type ?? 'venue'),
      area: String(item.area ?? item.city ?? 'Delhi NCR'),
      tag: String(item.manual_vibe ?? tags[0] ?? 'A place to make the night yours'),
      color: String(item.color ?? '#24E0FF'),
      scores: { FOOD: readScore('FOOD', 'food'), LIVE: readScore('LIVE', 'live_music'), POL: readScore('POL', 'politics'), SCEN: readScore('SCEN', 'scene'), NOV: readScore('NOV', 'novelty'), HERIT: readScore('HERIT', 'heritage'), GAMES: readScore('GAMES', 'games') },
    };
  };
  return {
    mode: 'api',
    register: async (email, password, name = '') => {
      const result = await request('/v1/auth/register', { method: 'POST', body: JSON.stringify({ email, password, name }) });
      authToken = String(result.access_token);
      try { localStorage.setItem(authStorageKey, authToken); } catch { /* native storage can be added later */ }
      return result as unknown as AuthSession;
    },
    login: async (email, password) => {
      const result = await request('/v1/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) });
      authToken = String(result.access_token);
      try { localStorage.setItem(authStorageKey, authToken); } catch { /* native storage can be added later */ }
      return result as unknown as AuthSession;
    },
    loginWithGoogle: async (idToken) => {
      const result = await request('/v1/auth/google', { method: 'POST', body: JSON.stringify({ id_token: idToken }) });
      authToken = String(result.access_token);
      try { localStorage.setItem(authStorageKey, authToken); } catch { /* native secure storage can replace this later */ }
      return result as unknown as AuthSession;
    },
    getAuthUser: async () => await request('/v1/auth/me') as unknown as AuthUser,
    logout: async () => {
      try { await request('/v1/auth/logout', { method: 'POST' }); } finally {
        authToken = undefined;
        try { localStorage.removeItem(authStorageKey); } catch { /* native storage can be added later */ }
      }
    },
    getDiscovery: async () => {
      const result = await request('/v1/discovery');
      return Array.isArray(result.items) ? result.items.map(toVenue) : [];
    },
    getVenue: async (venueId) => await request(`/v1/venues/${encodeURIComponent(venueId)}`) as unknown as VenueDetail,
    getLiveVenue: async (venueId) => {
      const result = await request(`/v1/venues/${encodeURIComponent(venueId)}/live`);
      return (result.google_live as Record<string, unknown> | undefined) ?? {};
    },
    getStopOptions: async (target, options = {}) => {
      const params = new URLSearchParams(Object.entries({ ...target, city: options.city ?? '', area: options.area ?? '', limit: String(options.limit ?? 10), include_live: String(options.includeLive ?? true) }).filter(([, value]) => value !== undefined && value !== ''));
      const result = await request(`/v1/venues/stop-options?${params.toString()}`);
      return Array.isArray(result.items) ? result.items.map(toVenue) : [];
    },
    completeAssessment: async (payload) => {
      await request('/v1/assessment/complete', { method: 'POST', body: JSON.stringify(payload) });
    },
    saveSkeleton: async (payload) => await request('/v1/skeletons', { method: 'POST', body: JSON.stringify(payload) }) as unknown as SkeletonRecord,
    getLatestSkeleton: async () => {
      const result = await request('/v1/skeletons/latest');
      return (result.skeleton as SkeletonRecord | null) ?? null;
    },
    createSelectedPlan: async (input) => {
      const result = await request('/v1/plans', { method: 'POST', body: JSON.stringify(input) });
      return {
        id: String(result.id),
        style: String(result.style ?? input.title),
        stops: Array.isArray(result.stops) ? result.stops.map(String) : [],
        chemistry: result.chemistry as Record<string, unknown> | undefined,
      };
    },
    updatePlanStops: async (planId, stops) => {
      const result = await request(`/v1/plans/${encodeURIComponent(planId)}/stops`, { method: 'PATCH', body: JSON.stringify({ stops }) });
      return { id: String(result.id), style: String(result.style ?? 'Your night'), stops: Array.isArray(result.stops) ? result.stops.map(String) : [], chemistry: result.chemistry as Record<string, unknown> | undefined, locked: Boolean(result.locked), selected_stops: result.selected_stops as SelectedPlanStop[] | undefined };
    },
    getPlan: async (planId) => await request(`/v1/plans/${encodeURIComponent(planId)}`) as GeneratedPlan & { locked?: boolean; selected_stops?: SelectedPlanStop[] },
    generatePlan: async (input) => {
      const result = await request('/v1/plans/generate', {
        method: 'POST',
        body: JSON.stringify(input),
      });
      const stops = Array.isArray(result.venues)
        ? result.venues.map((venue) => {
            const item = venue as Record<string, unknown>;
            return `${String(item.name ?? 'Venue')} · ${String(item.area ?? 'New Delhi')}`;
          })
        : [];
      return {
        id: String(result.id),
        style: String(result.style ?? 'Settle Then Roam'),
        stops,
        chemistry: result.chemistry as Record<string, unknown> | undefined,
      };
    },
    createRoom: async (title, members = []) => {
      const result = await request('/v1/rooms', {
        method: 'POST',
        body: JSON.stringify({ title, member_ids: members, visibility: 'private' }),
      });
      return { id: String(result.id), title: String(result.title), status: String(result.status) };
    },
    hostRoom: async (roomId, planId) => {
      const path = `/v1/rooms/${encodeURIComponent(roomId)}/host?plan_id=${encodeURIComponent(planId)}`;
      const result = await request(path, { method: 'POST' });
      return { id: String(result.id), title: String(result.title), status: String(result.status) };
    },
    listHostedRooms: async () => (await request('/v1/rooms?status=hosted')).items as RoomRecord[],
    getRoomEligibility: async (roomId, scores) => await request('/v1/rooms/join-eligibility', { method: 'POST', body: JSON.stringify({ room_id: roomId, scores }) }) as RoomFit,
    requestToJoin: async (roomId, memberId, note = '', scores = {}) => await request('/v1/rooms/join-requests', { method: 'POST', body: JSON.stringify({ room_id: roomId, member_id: memberId, note, scores }) }) as JoinRequestRecord,
    getJoinRequests: async (roomId, status = 'pending') => (await request(`/v1/rooms/${encodeURIComponent(roomId)}/join-requests?status=${status}`)).items as JoinRequestRecord[],
    decideJoinRequest: async (roomId, requestId, status) => await request(`/v1/rooms/${encodeURIComponent(roomId)}/join-requests/${encodeURIComponent(requestId)}/decision`, { method: 'POST', body: JSON.stringify({ status }) }) as { request: JoinRequestRecord; room: RoomRecord; plan_frozen: boolean },
    createCapsule: async (roomId, memberIds) => await request('/v1/capsules', { method: 'POST', body: JSON.stringify({ room_id: roomId, member_ids: memberIds }) }) as unknown as CapsuleRecord,
    getCapsule: async (capsuleId) => await request(`/v1/capsules/${encodeURIComponent(capsuleId)}`) as unknown as CapsuleRecord,
    approveCapsule: async (capsuleId, memberId, approved) => await request(`/v1/capsules/${encodeURIComponent(capsuleId)}/approvals`, { method: 'POST', body: JSON.stringify({ member_id: memberId, approved }) }) as unknown as CapsuleRecord,
    createRoomInvite: async (roomId) => await request(`/v1/rooms/${encodeURIComponent(roomId)}/invite`, { method: 'POST' }) as { room_id: string; invite_token: string; invite_url: string },
    joinRoomByInvite: async (inviteToken) => await request('/v1/rooms/join-by-invite', { method: 'POST', body: JSON.stringify({ invite_token: inviteToken }) }) as unknown as RoomRecord,
    listConversations: async () => (await request('/v1/conversations')).items as ConversationRecord[],
    sendChatMessage: async (conversationId, body) => await request('/v1/conversations/messages', { method: 'POST', body: JSON.stringify({ conversation_id: conversationId, body }) }) as unknown as ChatMessage,
    markConversationRead: async (conversationId) => { await request(`/v1/conversations/${encodeURIComponent(conversationId)}/read`, { method: 'POST' }); },
    listNotifications: async (unreadOnly = false) => (await request(`/v1/notifications?unread_only=${String(unreadOnly)}`)).items as NotificationRecord[],
    markNotificationRead: async (notificationId) => await request(`/v1/notifications/${encodeURIComponent(notificationId)}/read`, { method: 'POST' }) as unknown as NotificationRecord,
    getProfile: async () => await request('/v1/profiles/me') as unknown as ProfileRecord,
    listPeople: async (query = '') => {
      const result = await request(`/v1/people?${new URLSearchParams({ q: query, limit: '24' }).toString()}`);
      return Array.isArray(result.items) ? result.items as PersonRecord[] : [];
    },
    listFriends: async () => (await request('/v1/friends')).items as FriendRecord[],
    createFriendRequest: async (userId) => await request('/v1/friends/requests', { method: 'POST', body: JSON.stringify({ user_id: userId }) }) as unknown as FriendRecord,
    createGathering: async (name, memberIds = []) => await request('/v1/gatherings', { method: 'POST', body: JSON.stringify({ name, member_ids: memberIds }) }) as unknown as GatheringRecord,
    getGathering: async (gatheringId) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}`) as unknown as GatheringRecord,
    addGatheringMember: async (gatheringId, userId) => { await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/members`, { method: 'POST', body: JSON.stringify({ user_id: userId }) }); },
    decideGatheringInvite: async (gatheringId, userId, status) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/invites/${encodeURIComponent(userId)}/decision`, { method: 'POST', body: JSON.stringify({ status }) }),
    requestWheel: async (gatheringId) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/wheel/request`, { method: 'POST' }),
    listWheelRequests: async (gatheringId) => (await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/wheel/requests`)).items as WheelRequest[],
    decideWheel: async (gatheringId, status) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/wheel/decision`, { method: 'POST', body: JSON.stringify({ status }) }),
    saveGatheringSkeleton: async (gatheringId, payload) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/skeletons`, { method: 'POST', body: JSON.stringify(payload) }),
    getGatheringSkeleton: async (gatheringId) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/skeleton`),
    mergeGatheringSkeleton: async (gatheringId) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/skeleton/merge`, { method: 'POST' }),
    listGatheringProposals: async (gatheringId) => (await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/proposals`)).items as GatheringProposal[],
    createGatheringProposal: async (gatheringId, kind, payload) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/proposals`, { method: 'POST', body: JSON.stringify({ kind, payload }) }) as GatheringProposal,
    decideGatheringProposal: async (gatheringId, proposalId, status) => await request(`/v1/gatherings/${encodeURIComponent(gatheringId)}/proposals/${encodeURIComponent(proposalId)}/decision`, { method: 'POST', body: JSON.stringify({ status }) }) as GatheringProposal,
    saveProfile: async (profile) => await request('/v1/profiles/me', { method: 'PATCH', body: JSON.stringify(profile) }) as unknown as ProfileRecord,
    deleteAccount: async () => await request('/v1/account', { method: 'DELETE' }) as { deleted: boolean; message: string },
    lockPlan: async (planId) => {
      await request(`/v1/plans/${encodeURIComponent(planId)}/lock`, { method: 'POST' });
    },
    getPrivacy: async () => {
      const result = await request('/v1/privacy');
      return { ...defaultPrivacy, ...result, visibility: { ...defaultPrivacy.visibility, ...(result.visibility as Record<string, PrivacySettings['visibility'][string]> | undefined) } } as PrivacySettings;
    },
    savePrivacy: async (settings) => {
      const result = await request('/v1/privacy', { method: 'POST', body: JSON.stringify(settings) });
      return { ...defaultPrivacy, ...(result.settings as Partial<PrivacySettings>), visibility: { ...defaultPrivacy.visibility, ...((result.settings as PrivacySettings | undefined)?.visibility ?? {}) } };
    },
    getPlanLocationConsent: async (planId) => await request(
      "/v1/plans/" + encodeURIComponent(planId) + "/location-consent",
    ) as PlanLocationConsent,
    savePlanLocationConsent: async (planId, approved) => await request(
      "/v1/plans/" + encodeURIComponent(planId) + "/location-consent",
      { method: "POST", body: JSON.stringify({ approved }) },
    ) as PlanLocationConsent,
    submitReport: async (targetId, reason) => await request('/v1/reports', { method: 'POST', body: JSON.stringify({ target_id: targetId, reason }) }) as SafetyReport,
    blockUser: async (targetId) => await request('/v1/blocks', { method: 'POST', body: JSON.stringify({ target_id: targetId }) }) as SafetyAction,
    unblockUser: async (targetId) => await request('/v1/blocks/' + encodeURIComponent(targetId), { method: 'DELETE' }) as SafetyAction,
    getBlockedUsers: async () => (await request('/v1/blocks')).items as string[],
  };
}

export function getService(): Service {
  const apiUrl = process.env.EXPO_PUBLIC_API_URL?.trim();
  if (apiUrl) return createApiService(apiUrl);
  if (process.env.EXPO_PUBLIC_DEMO_MODE?.trim() === '1') return DemoService;
  throw new Error('SHUFFL API is not configured. Set EXPO_PUBLIC_API_URL or explicitly enable EXPO_PUBLIC_DEMO_MODE=1 for fixture mode.');
}

export { RELEASE_SCOPE };
