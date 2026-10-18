import { create } from "zustand";
import { Action } from "./algorithms";
import { Factor } from "./data";
import {
  AssessmentState,
  createAssessment,
  createPreferences,
  PreferenceState,
} from "./fullEngine";
import * as SecureStore from "expo-secure-store";
import { splitSecureStoreValue } from "./secureStoreChunks";
import { Platform } from "react-native";
export type FeatureMode =
  | "venue"
  | "customOuting"
  | "activePlan"
  | "arrival"
  | "feedback"
  | "hostRoom"
  | "joinRequests"
  | "capsule"
  | "notifications"
  | "inbox"
  | "chat"
  | "visitor"
  | "editProfile"
  | "history"
  | "privacy"
  | "settings"
  | "report"
  | "support"
  | "joinRoom"
  | "music";
export type DemoRoomState = {
  id?: string;
  name: string;
  public: boolean;
  cohosts: string[];
  members: string[];
  requests: string[];
  accepted: string[];
};
export type DemoPlanState = {
  id?: string;
  exists: boolean;
  locked: boolean;
  style: string;
  title: string;
  durationHours: number;
  stops: string[];
  chemistry?: Record<string, unknown>;
};
export type DemoCapsuleState = {
  id?: string;
  roomId?: string;
  status?: "awaiting_approval" | "approved";
  members: string[];
  approvals: Record<string, boolean>;
};
export type SkeletonState = {
  stops: number;
  energy: number;
  crowd: number;
  tags: string[];
  stopDurations: number[];
  updatedAt: string;
};
type Screen =
  | "welcome"
  | "intro"
  | "login"
  | "profile"
  | "preferenceIntro"
  | "preferences"
  | "instructions"
  | "dailyCheckin"
  | "assessment"
  | "reveal"
  | "discover"
  | "playMenu"
  | "shuffl"
  | "search"
  | "plans"
  | "rooms"
  | "profileHome"
  | "control"
  | "feature";
type State = {
  screen: Screen;
  hydrated: boolean;
  onboardingComplete: boolean;
  lastVibeDate: string;
  lastVibeName: string;
  reuseLastVibe: boolean;
  featureMode: FeatureMode;
  assessmentIndex: number;
  scores: Partial<Record<Factor, number>>;
  actions: Record<string, Action>;
  assessment: AssessmentState;
  preferences: PreferenceState;
  room: DemoRoomState;
  plan: DemoPlanState;
  capsule: DemoCapsuleState;
  skeleton: SkeletonState;
  locked: boolean;
  postVibeProfile: boolean;
  userName: string;
  userPronouns: string;
  userBio: string;
  avatarUri: string;
  activeConversation: string;
  selectedVenueName: string;
  savedVenueNames: string[];
  pendingVenueShare: string;
  activeMusic: string;
  set: (p: Partial<State>) => void;
  reset: () => void;
};
const initialRoom = (): DemoRoomState => ({
  name: "Aarav’s Friday Room",
  public: false,
  cohosts: [],
  members: ["Aarav"],
  requests: [],
  accepted: [],
});
const initialPlan = (): DemoPlanState => ({
  exists: false,
  locked: false,
  style: "Settle Then Roam",
  title: "Tonight, out together",
  durationHours: 4,
  stops: [],
});
const initialCapsule = (): DemoCapsuleState => ({
  members: ["Bela", "Chirag"],
  approvals: { Bela: false, Chirag: false },
});
const initialSkeleton = (): SkeletonState => ({
  stops: 1,
  energy: 50,
  crowd: 50,
  tags: [],
  stopDurations: [1],
  updatedAt: "",
});
const STORAGE_KEY = "shuffl.frontend-demo.v1";
const STORAGE_MANIFEST_KEY = `${STORAGE_KEY}.manifest`;
const STORAGE_PART_PREFIX = `${STORAGE_KEY}.part`;
type SavedState = Pick<
  State,
  | "onboardingComplete"
  | "lastVibeDate"
  | "lastVibeName"
  | "scores"
  | "preferences"
  | "userName"
  | "userPronouns"
  | "userBio"
  | "avatarUri"
  | "plan"
  | "room"
  | "capsule"
  | "skeleton"
  | "activeMusic"
  | "savedVenueNames"
>;
const today = () => {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
};
let saveTimer: ReturnType<typeof setTimeout> | undefined;
let saveChain = Promise.resolve();
let storageRevision = 0;

// Expo SecureStore is native-only. The web preview needs a real persistence
// adapter as well, otherwise every reload logs a restore failure and starts a
// fresh session. Keep the same keys and chunking semantics on web via the
// browser's local storage; native builds continue using SecureStore.
async function storageGet(key: string) {
  if (Platform.OS === "web") return globalThis.localStorage?.getItem(key) ?? null;
  return SecureStore.getItemAsync(key);
}

async function storageSet(key: string, value: string) {
  if (Platform.OS === "web") {
    globalThis.localStorage?.setItem(key, value);
    return;
  }
  await SecureStore.setItemAsync(key, value);
}

async function storageDelete(key: string) {
  if (Platform.OS === "web") {
    globalThis.localStorage?.removeItem(key);
    return;
  }
  await SecureStore.deleteItemAsync(key);
}

function parseManifest(value: string | null) {
  if (!value) return undefined;
  const separator = value.lastIndexOf(":");
  if (separator < 1) return undefined;
  const generation = value.slice(0, separator);
  const count = Number(value.slice(separator + 1));
  return generation && Number.isInteger(count) && count > 0
    ? { generation, count }
    : undefined;
}

async function readSavedState() {
  const manifest = parseManifest(
    await storageGet(STORAGE_MANIFEST_KEY),
  );
  if (!manifest) return storageGet(STORAGE_KEY);
  const parts: string[] = [];
  for (let index = 0; index < manifest.count; index++) {
    const part = await storageGet(
      `${STORAGE_PART_PREFIX}.${manifest.generation}.${index}`,
    );
    if (part === null)
      throw new Error("Saved SHUFFL demo state is incomplete.");
    parts.push(part);
  }
  return parts.join("");
}

async function saveState(snapshot: SavedState) {
  const serialized = JSON.stringify(snapshot);
  const chunks = splitSecureStoreValue(serialized);
  const previous = parseManifest(
    await storageGet(STORAGE_MANIFEST_KEY),
  );
  const generation = `${Date.now().toString(36)}-${(++storageRevision).toString(36)}`;
  for (let index = 0; index < chunks.length; index++) {
    await storageSet(
      `${STORAGE_PART_PREFIX}.${generation}.${index}`,
      chunks[index],
    );
  }
  await storageSet(
    STORAGE_MANIFEST_KEY,
    `${generation}:${chunks.length}`,
  );
  await storageDelete(STORAGE_KEY);
  if (previous) {
    for (let index = 0; index < previous.count; index++) {
      await storageDelete(
        `${STORAGE_PART_PREFIX}.${previous.generation}.${index}`,
      );
    }
  }
}

async function clearSavedState() {
  const manifest = parseManifest(
    await storageGet(STORAGE_MANIFEST_KEY),
  );
  await storageDelete(STORAGE_KEY);
  await storageDelete(STORAGE_MANIFEST_KEY);
  if (manifest) {
    for (let index = 0; index < manifest.count; index++) {
      await storageDelete(
        `${STORAGE_PART_PREFIX}.${manifest.generation}.${index}`,
      );
    }
  }
}
export const useApp = create<State>((set) => ({
  screen: "welcome",
  hydrated: false,
  onboardingComplete: false,
  lastVibeDate: "",
  lastVibeName: "",
  reuseLastVibe: false,
  featureMode: "settings",
  assessmentIndex: 0,
  scores: {},
  actions: {},
  assessment: createAssessment(),
  preferences: createPreferences(),
  room: initialRoom(),
  plan: initialPlan(),
  capsule: initialCapsule(),
  skeleton: initialSkeleton(),
  locked: true,
  postVibeProfile: false,
  userName: "",
  userPronouns: "",
  userBio: "",
  avatarUri: "",
  activeConversation: "Friday Room",
  selectedVenueName: "",
  savedVenueNames: [],
  pendingVenueShare: "",
  activeMusic: "",
  set: (p) => set(p),
  reset: () => {
    if (saveTimer) clearTimeout(saveTimer);
    saveChain = saveChain
      .then(clearSavedState)
      .catch((error) =>
        console.warn("SHUFFL demo state could not be cleared.", error),
      );
    set({
      screen: "welcome",
      hydrated: true,
      onboardingComplete: false,
      lastVibeDate: "",
      lastVibeName: "",
      reuseLastVibe: false,
      featureMode: "settings",
      assessmentIndex: 0,
      scores: {},
      actions: {},
      assessment: createAssessment(),
      preferences: createPreferences(),
      room: initialRoom(),
      plan: initialPlan(),
      capsule: initialCapsule(),
      skeleton: initialSkeleton(),
      locked: true,
      postVibeProfile: false,
      userName: "",
      userPronouns: "",
      userBio: "",
      avatarUri: "",
      activeConversation: "Friday Room",
      selectedVenueName: "",
      savedVenueNames: [],
      pendingVenueShare: "",
      activeMusic: "",
    });
  },
}));

export async function hydrateDemoState() {
  try {
    const raw = await readSavedState();
    if (raw) {
      const saved = JSON.parse(raw) as Partial<SavedState>;
      if (saved.onboardingComplete) {
        const completedToday = saved.lastVibeDate === today();
        useApp
          .getState()
          .set({
            ...saved,
            savedVenueNames: saved.savedVenueNames ?? [],
            skeleton: saved.skeleton ?? initialSkeleton(),
            screen: "discover",
            locked: !completedToday,
            hydrated: true,
          });
        return;
      }
    }
  } catch (error) {
    console.warn(
      "SHUFFL demo state could not be restored; starting a fresh local session.",
      error,
    );
  }
  useApp.getState().set({ hydrated: true });
}

useApp.subscribe((state) => {
  if (!state.hydrated || !state.onboardingComplete) return;
  if (saveTimer) clearTimeout(saveTimer);
  const snapshot: SavedState = {
    onboardingComplete: state.onboardingComplete,
    lastVibeDate: state.lastVibeDate,
    lastVibeName: state.lastVibeName,
    scores: state.scores,
    preferences: state.preferences,
    userName: state.userName,
    userPronouns: state.userPronouns,
    userBio: state.userBio,
    avatarUri: state.avatarUri,
    plan: state.plan,
    room: state.room,
    capsule: state.capsule,
    skeleton: state.skeleton,
    activeMusic: state.activeMusic,
    savedVenueNames: state.savedVenueNames,
  };
  saveTimer = setTimeout(() => {
    saveChain = saveChain
      .then(() => saveState(snapshot))
      .catch((error) =>
        console.warn("SHUFFL demo state could not be saved.", error),
      );
  }, 350);
});
