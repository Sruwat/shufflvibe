import { venues } from './data';
import { chemistryV2, fillVenues, selectVenueTypes } from './fullEngine';

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
  };
}

export function getService(): Service {
  return process.env.EXPO_PUBLIC_API_URL ? createApiService(process.env.EXPO_PUBLIC_API_URL) : DemoService;
}
