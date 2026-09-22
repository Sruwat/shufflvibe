import { venues } from './data';
import { chemistryV2, fillVenues, selectVenueTypes } from './fullEngine';

export type PrivacySettings = { location_sharing: boolean; approximate_presence: boolean; discoverability: boolean; visibility: Record<string, 'everyone' | 'friends' | 'nobody'> };
export type PlanLocationConsent = { approved: boolean };
const defaultPrivacy: PrivacySettings = { location_sharing: false, approximate_presence: true, discoverability: true, visibility: { profile: 'friends', vibe: 'friends', plans: 'friends' } };
let demoPrivacy: PrivacySettings = { ...defaultPrivacy, visibility: { ...defaultPrivacy.visibility } };
const demoPlanConsents: Record<string, boolean> = {};

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
export type RoomRecord = { id: string; title: string; status: string };
export type Service = {
  mode: ServiceMode;
  getDiscovery: () => Promise<typeof venues>;
  generatePlan: (input: PlanInput) => Promise<GeneratedPlan>;
  createRoom: (title: string, members?: string[]) => Promise<RoomRecord>;
  hostRoom: (roomId: string, planId: string) => Promise<RoomRecord>;
  lockPlan: (planId: string) => Promise<void>;
  getPrivacy: () => Promise<PrivacySettings>;
  savePrivacy: (settings: PrivacySettings) => Promise<PrivacySettings>;
  getPlanLocationConsent: (planId: string) => Promise<PlanLocationConsent>;
  savePlanLocationConsent: (planId: string, approved: boolean) => Promise<PlanLocationConsent>;
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
  createRoom: async (title) => ({ id: `demo-room-${Date.now()}`, title, status: 'draft' }),
  hostRoom: async (roomId) => ({ id: roomId, title: 'Demo room', status: 'hosted' }),
  lockPlan: async () => undefined,
  getPrivacy: async () => ({ ...demoPrivacy, visibility: { ...demoPrivacy.visibility } }),
  savePrivacy: async (settings) => { demoPrivacy = { ...settings, visibility: { ...settings.visibility } }; if (!settings.location_sharing) Object.keys(demoPlanConsents).forEach((key) => { demoPlanConsents[key] = false; }); return { ...demoPrivacy, visibility: { ...demoPrivacy.visibility } }; },
  getPlanLocationConsent: async (planId) => ({ approved: demoPrivacy.location_sharing && Boolean(demoPlanConsents[planId]) }),
  savePlanLocationConsent: async (planId, approved) => { if (approved && !demoPrivacy.location_sharing) throw new Error("Enable per-plan location sharing in privacy settings first"); demoPlanConsents[planId] = approved; return { approved }; },
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
  };
}

export function getService(): Service {
  return process.env.EXPO_PUBLIC_API_URL ? createApiService(process.env.EXPO_PUBLIC_API_URL) : DemoService;
}
