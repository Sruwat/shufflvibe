import { venues } from './data';
import { chemistryV2, fillVenues, selectVenueTypes } from './fullEngine';

export type PrivacySettings = { location_sharing: boolean; approximate_presence: boolean; discoverability: boolean; visibility: Record<string, 'everyone' | 'friends' | 'nobody'> };
export type PlanLocationConsent = { approved: boolean };
export type SafetyAction = { blocked: boolean };
export type SafetyReport = { id: string; status: string };
const defaultPrivacy: PrivacySettings = { location_sharing: false, approximate_presence: true, discoverability: true, visibility: { profile: 'friends', vibe: 'friends', plans: 'friends' } };
let demoPrivacy: PrivacySettings = { ...defaultPrivacy, visibility: { ...defaultPrivacy.visibility } };
const demoPlanConsents: Record<string, boolean> = {};
const demoBlockedUsers = new Set<string>();
const demoRooms: Record<string, RoomRecord & { visibility: string; join_requests: JoinRequestRecord[] }> = { 'room-demo': { id: 'room-demo', title: 'Friday night, open to the city', status: 'hosted', visibility: 'public', members: ['demo-user'], join_requests: [] } };
let demoReportSequence = 0;

export type ServiceMode = 'demo' | 'api';
export type PlanInput = {
  scores: Record<string, number>;
  preferences?: Record<string, number>;
  pol_sense?: 'classy' | 'current' | 'both';
  members?: string[];
  duration_hours?: number;
  strangers?: boolean;
};
export type GeneratedPlan = { id: string; style: string; stops: string[]; chemistry?: Record<string, unknown> };
export type RoomRecord = { id: string; title: string; status: string; members?: string[] };
export type JoinRequestRecord = { id: string; room_id: string; member_id: string; status: 'pending' | 'accepted' | 'declined'; note: string; created_at?: string };
export type Service = {
  mode: ServiceMode;
  getDiscovery: () => Promise<typeof venues>;
  generatePlan: (input: PlanInput) => Promise<GeneratedPlan>;
  createRoom: (title: string, members?: string[]) => Promise<RoomRecord>;
  hostRoom: (roomId: string, planId: string) => Promise<RoomRecord>;
  listHostedRooms: () => Promise<RoomRecord[]>;
  requestToJoin: (roomId: string, memberId: string, note?: string) => Promise<JoinRequestRecord>;
  getJoinRequests: (roomId: string, status?: 'pending' | 'accepted' | 'declined' | 'all') => Promise<JoinRequestRecord[]>;
  decideJoinRequest: (roomId: string, requestId: string, status: 'accepted' | 'declined') => Promise<{ request: JoinRequestRecord; room: RoomRecord; plan_frozen: boolean }>;
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
  getDiscovery: async () => venues,
  generatePlan: async (input) => {
    const memberScores = [input.scores];
    const chemistry = chemistryV2(memberScores, input.duration_hours ?? 4, input.strangers ?? false);
    const types = selectVenueTypes(memberScores, input.duration_hours ?? 4, input.strangers ?? false);
    const selected = fillVenues(types, [input.preferences ?? {}], venues);
    return {
      id: `demo-plan-${Date.now()}`,
      style: chemistry.tags[0] ?? 'Settle Then Roam',
      stops: selected.map((venue) => venue.name),
      chemistry,
    };
  },
  createRoom: async (title, members = []) => { const id = `demo-room-${Date.now()}`; demoRooms[id] = { id, title, status: 'draft', visibility: 'private', members: [...members], join_requests: [] }; return demoRooms[id]; },
  hostRoom: async (roomId) => { const room = demoRooms[roomId]; if (!room) throw new Error('Room not found'); room.status = 'hosted'; room.visibility = 'public'; return room; },
  listHostedRooms: async () => Object.values(demoRooms).filter(room => room.status === 'hosted').map(({ join_requests: _requests, ...room }) => room),
  requestToJoin: async (roomId, memberId, note = '') => { const room = demoRooms[roomId]; if (!room || room.status !== 'hosted') throw new Error('Room is not accepting requests'); if (room.members?.includes(memberId)) throw new Error('You are already a room member'); const old = room.join_requests.find(item => item.member_id === memberId && item.status === 'pending'); if (old) return old; const request: JoinRequestRecord = { id: `demo-join-${Date.now()}`, room_id: roomId, member_id: memberId, status: 'pending', note }; room.join_requests.push(request); return request; },
  getJoinRequests: async (roomId, status = 'pending') => { const room = demoRooms[roomId]; if (!room) throw new Error('Room not found'); return room.join_requests.filter(item => status === 'all' || item.status === status); },
  decideJoinRequest: async (roomId, requestId, status) => { const room = demoRooms[roomId]; const request = room?.join_requests.find(item => item.id === requestId); if (!room || !request) throw new Error('Join request not found'); if (request.status !== 'pending') throw new Error('Join request already resolved'); request.status = status; if (status === 'accepted' && !room.members?.includes(request.member_id)) room.members = [...(room.members ?? []), request.member_id]; const { join_requests: _requests, ...roomRecord } = room; return { request, room: roomRecord, plan_frozen: true }; },
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
  const request = async (path: string, init?: RequestInit) => {
    const response = await fetch(`${baseUrl}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...init,
    });
    if (!response.ok) throw new Error(`SHUFFL API ${response.status}`);
    return response.json() as Promise<Record<string, unknown>>;
  };
  return {
    mode: 'api',
    getDiscovery: async () => (await request('/v1/discovery')).items as typeof venues,
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
    requestToJoin: async (roomId, memberId, note = '') => await request('/v1/rooms/join-requests', { method: 'POST', body: JSON.stringify({ room_id: roomId, member_id: memberId, note }) }) as JoinRequestRecord,
    getJoinRequests: async (roomId, status = 'pending') => (await request(`/v1/rooms/${encodeURIComponent(roomId)}/join-requests?status=${status}`)).items as JoinRequestRecord[],
    decideJoinRequest: async (roomId, requestId, status) => await request(`/v1/rooms/${encodeURIComponent(roomId)}/join-requests/${encodeURIComponent(requestId)}/decision`, { method: 'POST', body: JSON.stringify({ status }) }) as { request: JoinRequestRecord; room: RoomRecord; plan_frozen: boolean },
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
  return process.env.EXPO_PUBLIC_API_URL ? createApiService(process.env.EXPO_PUBLIC_API_URL) : DemoService;
}
