import { venues } from './data';

export type ServiceMode = 'demo' | 'api';
export type PlanInput = { scores: Record<string, number>; members?: string[] };
export type Service = {
  mode: ServiceMode;
  getDiscovery: () => Promise<typeof venues>;
  generatePlan: (input: PlanInput) => Promise<Record<string, unknown>>;
  createRoom: (title: string) => Promise<Record<string, unknown>>;
};

export const DemoService: Service = {
  mode: 'demo',
  getDiscovery: async () => venues,
  generatePlan: async (input) => ({ style: (input.scores.ENRG ?? 50) >= 70 ? 'Could Go Late' : 'Settle Then Roam', stops: (input.scores.ROAM ?? 50) >= 65 ? 3 : 2, venues }),
  createRoom: async (title) => ({ id: `demo-room-${Date.now()}`, title, status: 'draft' }),
};

export function createApiService(baseUrl: string): Service {
  const request = async (path: string, init?: RequestInit) => { const response = await fetch(`${baseUrl}${path}`, { headers: { 'Content-Type': 'application/json' }, ...init }); if (!response.ok) throw new Error(`SHUFFL API ${response.status}`); return response.json(); };
  return {
    mode: 'api',
    getDiscovery: async () => (await request('/v1/discovery')).items,
    generatePlan: async (input) => request('/v1/plans/generate', { method: 'POST', body: JSON.stringify(input) }),
    createRoom: async (title) => request('/v1/rooms', { method: 'POST', body: JSON.stringify({ title }) }),
  };
}

export function getService(): Service { return process.env.EXPO_PUBLIC_API_URL ? createApiService(process.env.EXPO_PUBLIC_API_URL) : DemoService; }
