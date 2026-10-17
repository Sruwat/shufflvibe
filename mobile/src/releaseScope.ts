/** First-release product contract. Deferred work must not leak into MVP navigation. */
export const RELEASE_SCOPE = {
  name: "mvp",
  venueCatalogueLocked: true,
  venueSource: "published_venue_api",
  openingHoursMode: "display_time_live",
  googleReviewsPersisted: false,
  goldCampaignEnabled: false,
  messagesShufflEnabled: false,
  groupInsightsEnabled: false,
} as const;

export function isProductionBuild(): boolean {
  return process.env.NODE_ENV === "production";
}

export function assertReleaseScope(): void {
  if (!isProductionBuild()) return;
  if (process.env.EXPO_PUBLIC_RELEASE_SCOPE?.trim() !== RELEASE_SCOPE.name) {
    throw new Error(
      `SHUFFL release scope is not configured for ${RELEASE_SCOPE.name}. Set EXPO_PUBLIC_RELEASE_SCOPE=mvp before shipping.`,
    );
  }
}

export function demoFallbackAllowed(): boolean {
  return !isProductionBuild();
}
