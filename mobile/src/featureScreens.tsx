import React, { useEffect, useState } from "react";
import {
  Alert,
  Image,
  Linking,
  PanResponder,
  Pressable,
  ScrollView,
  Share,
  StyleSheet,
  Switch,
  Text,
  TextInput,
  View,
} from "react-native";
import {
  SafeAreaView,
  useSafeAreaInsets,
} from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import { colors } from "./theme";
import { FeatureMode, useApp } from "./store";
import {
  factorCopy,
  factors,
  venues,
} from "./data";
import { venueArtwork } from "./assets";
import {
  getService,
  CapsuleRecord,
  ConversationRecord,
  VenueCard,
  VenueDetail,
  JoinerScores,
  JoinRequestRecord,
  PrivacySettings,
  PersonRecord,
  RoomRecord,
  GatheringRecord,
  GatheringProposal,
} from "./services";
import { latencyFirmness } from "./fullEngine";

const reportReasons = [
  "Harassment",
  "Spam or scam",
  "Inappropriate content",
  "Safety concern",
  "Something else",
];

function VenueDetailScreen() {
  const { selectedVenueName, lastVibeName, savedVenueNames, set } = useApp();
  const [showPairing, setShowPairing] = useState(false);
  const fallbackVenue = (venues.find((item) => item.name === selectedVenueName) ?? {
    name: selectedVenueName,
    type: "Venue",
    area: "Delhi NCR",
    tag: "A place to make the night yours",
    color: "#20DDA9",
    scores: {},
  }) as VenueCard;
  const [venue, setVenue] = useState(fallbackVenue);
  const [detail, setDetail] = useState<VenueDetail | null>(null);
  const [live, setLive] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [dataError, setDataError] = useState("");
  const [retryKey, setRetryKey] = useState(0);
  useEffect(() => {
    let alive = true;
    const service = getService();
    setLoading(true);
    service.getDiscovery().then(async (items) => {
      const match = items.find((item) => item.name === selectedVenueName) as VenueCard | undefined;
      if (!alive || !match) return;
      setVenue(match);
      if (match.id) {
        const result = await service.getVenue(match.id);
        if (!alive) return;
        setDetail(result);
        try {
          setLive(await service.getLiveVenue(match.id));
        } catch {
          setLive(null);
        }
      }
    }).catch((cause) => {
      if (alive) setDataError(cause instanceof Error ? cause.message : "Venue details could not be loaded.");
    }).finally(() => { if (alive) setLoading(false); });
    return () => { alive = false; };
  }, [selectedVenueName, retryKey]);
  const liveData = live ?? (venue.live as Record<string, unknown> | null | undefined) ?? null;
  const normalized = detail?.normalized ?? {};
  const identity = detail?.venue && typeof detail.venue === "object" ? detail.venue as Record<string, unknown> : {};
  const officialUrl = String(identity.official_url ?? identity.website_url ?? normalized.official_url ?? liveData?.website ?? "");
  const address = String(identity.address ?? normalized.address ?? liveData?.address ?? `${venue.area}, Delhi NCR`);
  const hours = liveData?.opening_hours ?? liveData?.hours ?? normalized.opening_hours ?? "Live hours unavailable";
  const rating = liveData?.rating ?? identity.rating ?? normalized.rating;
  const reviewCount = liveData?.review_count ?? identity.review_count ?? normalized.review_count;
  const menuUrl = String(identity.menu_url ?? normalized.menu_url ?? "");
  const tags = Array.isArray(identity.tags) ? identity.tags.map(String) : Array.isArray(normalized.tags) ? normalized.tags.map(String) : [];
  const photos = Array.isArray(identity.photos) ? identity.photos.map(String).filter((url) => /^https?:\/\//.test(url)) : [];
  const socialUrls = Array.isArray(identity.social_urls) ? identity.social_urls.map(String).filter((url) => /^https?:\/\//.test(url)) : [];
  const evidence = Array.isArray(normalized.evidence) ? normalized.evidence.map(String) : [];
  const strengths = Object.entries(venue.scores)
    .sort(([, a], [, b]) => b - a)
    .slice(0, 3);
  const [mapError, setMapError] = useState("");
  const openMaps = async () => {
    const query = encodeURIComponent(`${venue.name}, ${venue.area}, Delhi`);
    try {
      await Linking.openURL(
        venue.google_lookup_url || `https://www.google.com/maps/search/?api=1&query=${query}`,
      );
    } catch {
      setMapError("Maps couldn’t be opened on this device.");
    }
  };
  const shareVenue = () =>
    set({
      selectedVenueName: venue.name,
      pendingVenueShare: venue.name,
      screen: "feature",
      featureMode: "inbox",
    });
  const saved = savedVenueNames.includes(venue.name);
  const toggleSaved = () => set({
    savedVenueNames: saved
      ? savedVenueNames.filter((name) => name !== venue.name)
      : [...savedVenueNames, venue.name],
  });
  const preferenceLabels: Record<string, string> = {
    FOOD: "Food",
    LIVE: "Live music",
    POL: "Dress-up",
    SCEN: "The room",
    NOV: "Somewhere new",
    HERIT: "History",
  };
  const pairing = venue.name.includes("Sidecar")
    ? {
        dish: "Delhi-style small plates",
        drink: "Citrus highball / zero-proof spritz",
        why: "A bright, shareable pairing for a social room.",
        match: "Demo match · 86%",
      }
    : venue.name.includes("Piano Man")
      ? {
          dish: "Late-night comfort bites",
          drink: "Ginger-lime cooler / house cocktail",
          why: "Easy to enjoy between sets without missing the room.",
          match: "Demo match · 82%",
        }
      : venue.name.includes("Majnu")
        ? {
            dish: "Momos and market snacks",
            drink: "Nimbu soda / spiced cooler",
            why: "A casual street-food pairing for exploring new corners.",
            match: "Demo match · 80%",
          }
        : {
            dish: "Seasonal café plate",
            drink: "Mint-lime cooler / zero-proof spritz",
            why: "A light, easygoing pairing for a slower stop.",
            match: "Demo match · 78%",
          };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="VENUE DETAIL"
        onBack={() => set({ screen: "discover" })}
      />
      <ScrollView contentContainerStyle={[styles.content, venueStyles.content]}>
        <View style={[venueStyles.poster, { borderColor: venue.color + "88" }]}>
          <Text style={[styles.eyebrow, { color: venue.color }]}>
            SHUFFL · DELHI NCR
          </Text>
          <Ionicons name="sparkles" size={28} color={venue.color} />
          <Text style={venueStyles.posterName}>{venue.name.toUpperCase()}</Text>
          <Text style={venueStyles.posterArea}>
            {venue.area.toUpperCase()} · {venue.type.toUpperCase()}
          </Text>
          {venueArtwork[venue.name] ? (
            <Image source={venueArtwork[venue.name]} style={venueStyles.posterImage} accessibilityLabel={`${venue.name} venue artwork`} />
          ) : (
            <Text style={venueStyles.mediaFallback}>VENUE MEDIA NOT AVAILABLE</Text>
          )}
        </View>
        <View style={venueStyles.titleRow}>
          <View style={{ flex: 1 }}>
            <Text style={styles.title}>{venue.name}</Text>
            <Text style={styles.secondaryText}>
              {venue.area} · {venue.type}
            </Text>
          </View>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Share venue"
            onPress={shareVenue}
            style={venueStyles.shareButton}
          >
            <Ionicons name="share-outline" size={21} color={colors.text} />
          </Pressable>
        </View>
        <Text style={styles.body}>{venue.tag}. {loading ? "Loading verified venue details…" : "Details are sourced from the published venue record; Google live fields are fetched for display only."}</Text>
        {dataError ? <><Text accessibilityRole="alert" style={styles.notice}>{dataError}</Text><FeatureButton label="Retry venue details" onPress={() => setRetryKey((value) => value + 1)} secondary /></> : null}
        <View style={styles.roomCard}>
          <Text style={styles.routeText}>Official venue information</Text>
          <Text style={styles.secondaryText}>{address}</Text>
          {officialUrl ? <Pressable onPress={() => Linking.openURL(officialUrl).catch(() => setMapError("Official website could not be opened."))}><Text style={styles.notice}>Open official website</Text></Pressable> : <Text style={styles.secondaryText}>Official website not available</Text>}
          {menuUrl ? <Pressable onPress={() => Linking.openURL(menuUrl).catch(() => setMapError("Menu could not be opened."))}><Text style={styles.notice}>Open venue menu</Text></Pressable> : <Text style={styles.secondaryText}>Menu not available</Text>}
          {socialUrls.length ? <View>{socialUrls.slice(0, 4).map((url) => <Pressable key={url} onPress={() => Linking.openURL(url).catch(() => setMapError("Social profile could not be opened."))}><Text style={styles.notice}>Open social profile</Text></Pressable>)}</View> : <Text style={styles.secondaryText}>Social profiles not available</Text>}
        </View>
        <View style={styles.roomCard}>
          <Text style={styles.routeText}>Tags & evidence</Text>
          <Text style={styles.secondaryText}>{tags.length ? tags.join(" · ") : "Tags not available"}</Text>
          <Text style={styles.secondaryText}>{evidence.length ? `Evidence: ${evidence.join(" · ")}` : "Evidence details not available"}</Text>
        </View>
        <View style={styles.roomCard}>
          <Text style={styles.routeText}>Photos & media</Text>
          {photos.length ? <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={{ gap: 10 }}>{photos.slice(0, 6).map((photo) => <Image key={photo} source={{ uri: photo }} style={{ width: 132, height: 92, borderRadius: 14 }} accessibilityLabel={`${venue.name} venue photo`} />)}</ScrollView> : <Text style={styles.secondaryText}>No licensed venue photos available.</Text>}
        </View>
        <View style={styles.roomCard}>
          <Text style={styles.routeText}>Preference profile</Text>
          <Text style={styles.secondaryText}>
            SHUFFL scores are evidence-backed catalogue scores. Live Google
            rating/review totals are display-time enrichment and are not stored.
          </Text>
          {strengths.map(([factor, score]) => (
            <View key={factor} style={venueStyles.scoreRow}>
              <View style={{ flex: 1 }}>
                <Text style={venueStyles.scoreLabel}>
                  {preferenceLabels[factor] ?? factor}
                </Text>
                <View style={venueStyles.scoreTrack}>
                  <View
                    style={[
                      venueStyles.scoreFill,
                      { width: `${score}%`, backgroundColor: venue.color },
                    ]}
                  />
                </View>
              </View>
              <Text style={venueStyles.scoreValue}>{score}</Text>
            </View>
          ))}
        </View>
        <View style={styles.roomCard}>
          <Text style={styles.routeText}>Stories & notes</Text>
          <Text style={styles.secondaryText}>
            No moderated in-app stories or licensed venue media are available
            for this place yet.
          </Text>
        </View>
        <View style={styles.roomCard}>
          <Text style={styles.routeText}>Getting there</Text>
          <Text style={styles.secondaryText}>{address}</Text>
          <Text style={styles.secondaryText}>Hours: {typeof hours === "string" ? hours : "Live hours available in Google Maps"}</Text>
          <Text style={styles.secondaryText}>{liveData ? "Hours refreshed live from Google just now · not stored" : "Live hours unavailable · check Google Maps before leaving"}</Text>
          {rating !== undefined ? <Text style={styles.secondaryText}>Google rating: {String(rating)}{reviewCount !== undefined ? ` · ${String(reviewCount)} reviews` : ""}</Text> : <Text style={styles.secondaryText}>Google rating and reviews unavailable right now</Text>}
        </View>
        <View style={styles.roomCard}>
          <Text style={styles.routeText}>Why it matches tonight</Text>
          <Text style={styles.secondaryText}>{venue.tag}. Good fit for your {lastVibeName || "current"} energy.</Text>
          <Text style={styles.secondaryText}>{evidence.length ? `Pros · ${evidence.slice(0, 2).join(" · ")}` : "Pros · No verified pros recorded yet"}</Text>
          <Text style={styles.secondaryText}>{tags.length ? `Cons · Live conditions may vary · ${tags.slice(0, 1).join(" · ")}` : "Cons · No verified cons recorded yet"}</Text>
        </View>
        {false && <Pressable
          accessibilityRole="button"
          accessibilityLabel="Show recommended dish and drink"
          onPress={() => setShowPairing((value) => !value)}
          style={venueStyles.pairingTrigger}
        >
          <Text style={venueStyles.pairingEmoji}>🍸</Text>
          <View style={{ flex: 1 }}>
            <Text style={styles.routeText}>Dish & drink for your vibe</Text>
            <Text style={styles.secondaryText}>
              {lastVibeName || "Tonight"} · venue pairing
            </Text>
          </View>
          <Ionicons
            name={showPairing ? "chevron-up" : "chevron-down"}
            size={19}
            color={colors.pink}
          />
        </Pressable>}
        {false && showPairing && (
          <View style={styles.roomCard}>
            <Text style={styles.eyebrow}>
              {lastVibeName || "TONIGHT"} · AT {venue.name.toUpperCase()}
            </Text>
            <Text style={styles.routeText}>A pairing for this stop</Text>
            <View style={venueStyles.pairingRow}>
              <View style={venueStyles.pairingTile}>
                <Text style={venueStyles.pairingArt}>🍽️</Text>
                <Text style={venueStyles.pairingLabel}>DISH</Text>
                <Text style={venueStyles.pairingName}>{pairing.dish}</Text>
              </View>
              <View style={venueStyles.pairingTile}>
                <Text style={venueStyles.pairingArt}>🥂</Text>
                <Text style={venueStyles.pairingLabel}>DRINK</Text>
                <Text style={venueStyles.pairingName}>{pairing.drink}</Text>
              </View>
            </View>
            <Text style={styles.secondaryText}>{pairing.why}</Text>
            <Text style={venueStyles.pairingMatch}>{pairing.match}</Text>
            <Text style={styles.disclaimer}>
              Illustrative Delhi demo suggestions only. No venue menu, photos,
              availability or live match score is connected.
            </Text>
            <Pressable
              accessibilityRole="button"
              onPress={() =>
                Alert.alert(
                  "Demo only",
                  "Ordering and payment are not connected in this preview.",
                )
              }
              style={venueStyles.orderButton}
            >
              <Text style={venueStyles.goHereText}>Order now · preview</Text>
            </Pressable>
          </View>
        )}
        {mapError ? (
          <Text accessibilityRole="alert" style={styles.notice}>
            {mapError}
          </Text>
        ) : null}
        <FeatureButton
          label="Report venue information"
          onPress={() => set({ screen: "feature", featureMode: "report" })}
          secondary
        />
        <Pressable
          accessibilityRole="button"
          onPress={openMaps}
          style={venueStyles.goHere}
        >
          <Ionicons name="map" size={19} color={colors.bg} />
          <Text style={venueStyles.goHereText}>Go Here</Text>
        </Pressable>
        <Pressable accessibilityRole="button" accessibilityState={{ selected: saved }} onPress={toggleSaved} style={venueStyles.mapsButton}>
          <Ionicons name={saved ? "bookmark" : "bookmark-outline"} size={19} color={colors.text} />
          <Text style={venueStyles.mapsButtonText}>{saved ? "Saved" : "Save venue"}</Text>
        </Pressable>
        <Pressable accessibilityRole="button" onPress={() => set({ screen: "shuffl" })} style={venueStyles.mapsButton}>
          <Ionicons name="people-outline" size={19} color={colors.text} />
          <Text style={venueStyles.mapsButtonText}>Find rooms</Text>
        </Pressable>
        <Pressable accessibilityRole="button" onPress={() => set({ screen: "feature", featureMode: "customOuting", selectedVenueName: venue.name })} style={venueStyles.mapsButton}><Ionicons name="add-circle-outline" size={19} color={colors.text}/><Text style={venueStyles.mapsButtonText}>Build my night around this</Text></Pressable>
      </ScrollView>
    </SafeAreaView>
  );
}

function MusicScreen() {
  const { activeMusic, lastVibeName, set } = useApp();
  const [query, setQuery] = useState("");
  const songs = [
    ["Midnight City", "M83 · neon, open-road energy"],
    ["Sunset Lover", "Petit Biscuit · warm-up and roam"],
    ["Electric Feel", "MGMT · bright, social pulse"],
    ["A Sky Full of Stars", "Coldplay · peak-room lift"],
  ] as const;
  const visible = songs.filter(([title, artist]) =>
    `${title} ${artist}`.toLowerCase().includes(query.trim().toLowerCase()),
  );
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader label="ADD MUSIC" onBack={() => set({ screen: "discover" })} />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>TUNES FOR YOUR SHAPE</Text>
        <Text style={styles.title}>Set the room’s soundtrack.</Text>
        <Text style={styles.body}>These tunes are catered to your {lastVibeName || "vibe"} today. Your room starts muted; tap a song to set the current track.</Text>
        <View style={inboxStyles.inboxSearch}>
          <Ionicons name="search" size={18} color={colors.muted} />
          <TextInput accessibilityLabel="Search music" value={query} onChangeText={setQuery} placeholder="Search songs or artists" placeholderTextColor={colors.muted} style={inboxStyles.inboxSearchText} />
        </View>
        {visible.map(([title, artist]) => {
          const selected = activeMusic === title;
          return <Pressable key={title} accessibilityRole="radio" accessibilityState={{ selected }} onPress={() => set({ activeMusic: title })} style={[styles.route, selected && { borderColor: colors.pink, backgroundColor: colors.pink + "18" }]}>
            <View style={[styles.heroIcon, { marginRight: 12 }]}><Ionicons name={selected ? "disc" : "musical-notes-outline"} size={22} color={colors.pink} /></View>
            <View style={{ flex: 1 }}><Text style={styles.routeText}>{title}</Text><Text style={styles.secondaryText}>{artist}</Text></View>
            {selected ? <Ionicons name="checkmark-circle" size={23} color={colors.pink} /> : <Ionicons name="chevron-forward" size={19} color={colors.muted} />}
          </Pressable>;
        })}
        {activeMusic ? <View style={styles.roomCard}><Text style={styles.eyebrow}>NOW IN THE ROOM</Text><Text style={styles.routeText}>{activeMusic}</Text><Text style={styles.secondaryText}>Spinning record preview · speaker starts muted</Text></View> : null}
        <FeatureButton label="Back to the room" onPress={() => set({ screen: "discover" })} secondary />
      </ScrollView>
    </SafeAreaView>
  );
}

function FeedbackScreen() {
  const { plan, set } = useApp();
  const stops = plan.stops.length ? plan.stops : ["Tonight’s stop"];
  const [index, setIndex] = useState(0);
  const [rating, setRating] = useState(0);
  const [note, setNote] = useState("");
  const submit = () => {
    if (!rating) return;
    if (index < stops.length - 1) {
      setIndex((value) => value + 1);
      setRating(0);
      setNote("");
      return;
    }
    Alert.alert("Feedback saved", "Thanks — your notes will help tune future nights.");
    set({ screen: "feature", featureMode: "activePlan" });
  };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader label="STOP FEEDBACK" onBack={() => set({ screen: "feature", featureMode: "activePlan" })} />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>STOP {index + 1} OF {stops.length}</Text>
        <Text style={styles.title}>How did {stops[index]} feel?</Text>
        <Text style={styles.body}>Rate the room, the conversation, and whether it delivered what the plan promised.</Text>
        <View style={feedbackStyles.stars}>
          {[1, 2, 3, 4, 5].map((value) => <Pressable key={value} accessibilityRole="radio" accessibilityLabel={`${value} stars`} accessibilityState={{ selected: rating === value }} onPress={() => setRating(value)}><Ionicons name={value <= rating ? "star" : "star-outline"} size={43} color={colors.pink} /></Pressable>)}
        </View>
        <TextInput accessibilityLabel="Optional stop feedback" value={note} onChangeText={setNote} placeholder="Anything you want to remember? (optional)" placeholderTextColor={colors.muted} style={[styles.input, { minHeight: 120, textAlignVertical: "top" }]} multiline maxLength={240} />
        <FeatureButton label={index < stops.length - 1 ? "Next stop" : "Save feedback"} onPress={submit} />
        <FeatureButton label="Skip feedback" onPress={() => set({ screen: "feature", featureMode: "activePlan" })} secondary />
      </ScrollView>
    </SafeAreaView>
  );
}
const venueStyles = StyleSheet.create({
  content: { paddingBottom: 190 },
  posterImage: { width: "100%", height: 120, borderRadius: 16, marginVertical: 10 },
  poster: {
    minHeight: 230,
    borderWidth: 1,
    borderRadius: 24,
    backgroundColor: colors.surface,
    padding: 22,
    justifyContent: "space-between",
    marginBottom: 24,
    overflow: "hidden",
  },
  posterName: {
    color: colors.text,
    fontSize: 31,
    lineHeight: 36,
    fontWeight: "900",
    letterSpacing: 1,
  },
  posterArea: {
    color: colors.muted,
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 1.4,
  },
  mediaFallback: {
    color: colors.mutedDeep,
    fontSize: 9,
    fontWeight: "800",
    letterSpacing: 1.2,
    marginTop: 20,
  },
  titleRow: { flexDirection: "row", alignItems: "center", gap: 12 },
  shareButton: {
    width: 48,
    height: 48,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.raised,
    borderWidth: 1,
    borderColor: colors.line,
  },
  scoreRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginTop: 16,
  },
  scoreLabel: {
    color: colors.textSecondary,
    fontSize: 12,
    fontWeight: "700",
    marginBottom: 7,
  },
  scoreTrack: {
    height: 5,
    borderRadius: 3,
    backgroundColor: colors.raised,
    overflow: "hidden",
  },
  scoreFill: { height: 5, borderRadius: 3 },
  scoreValue: { color: colors.text, fontSize: 13, fontWeight: "800" },
  pairingTrigger: {
    minHeight: 76,
    padding: 16,
    borderRadius: 18,
    borderWidth: 1,
    borderColor: colors.pinkBorder,
    backgroundColor: colors.surface,
    flexDirection: "row",
    alignItems: "center",
    gap: 13,
    marginBottom: 14,
  },
  pairingEmoji: { fontSize: 25 },
  pairingRow: { flexDirection: "row", gap: 10, marginVertical: 14 },
  pairingTile: {
    flex: 1,
    minHeight: 145,
    padding: 12,
    borderRadius: 16,
    backgroundColor: colors.raised,
    borderWidth: 1,
    borderColor: colors.line,
    justifyContent: "center",
  },
  pairingArt: { fontSize: 34, marginBottom: 10 },
  pairingLabel: {
    color: colors.pink,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1.5,
    marginBottom: 6,
  },
  pairingName: {
    color: colors.text,
    fontSize: 14,
    lineHeight: 20,
    fontWeight: "800",
  },
  pairingMatch: {
    color: colors.green,
    fontSize: 13,
    fontWeight: "800",
    marginTop: 10,
  },
  orderButton: {
    minHeight: 48,
    borderRadius: 14,
    backgroundColor: colors.pink,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 14,
  },
  goHere: {
    minHeight: 56,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 9,
    borderRadius: 18,
    backgroundColor: colors.pink,
    marginTop: 12,
    marginBottom: 24,
    elevation: 6,
  },
  goHereText: {
    color: colors.bg,
    fontSize: 15,
    fontWeight: "900",
    letterSpacing: 0.3,
  },
  mapsButton: { minHeight: 52, borderRadius: 18, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.surface, flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8, marginTop: 10, marginBottom: 24 },
  mapsButtonText: { color: colors.text, fontSize: 14, fontWeight: "800" },
});

function ReportSafetyScreen() {
  const { selectedVenueName, set } = useApp();
  const service = React.useMemo(() => getService(), []);
  const [targetId, setTargetId] = useState(selectedVenueName || "demo-user-2");
  const [reason, setReason] = useState(reportReasons[0]);
  const [details, setDetails] = useState("");
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("");
  const [blocked, setBlocked] = useState(false);
  useEffect(() => {
    let mounted = true;
    service
      .getBlockedUsers()
      .then((items) => {
        if (mounted) setBlocked(items.includes(targetId.trim()));
      })
      .catch(() => undefined);
    return () => {
      mounted = false;
    };
  }, [service, targetId]);
  const submit = async () => {
    if (!targetId.trim()) {
      setMessage("Enter the profile ID you want to report.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const result = await service.submitReport(
        targetId.trim(),
        `${reason}${details.trim() ? `: ${details.trim()}` : ""}`,
      );
      setMessage(`Report received · ${result.id}`);
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Could not submit report. Try again.",
      );
    } finally {
      setBusy(false);
    }
  };
  const toggleBlock = async () => {
    if (!targetId.trim()) {
      setMessage("Enter the profile ID you want to block.");
      return;
    }
    setBusy(true);
    setMessage("");
    try {
      const result = blocked
        ? await service.unblockUser(targetId.trim())
        : await service.blockUser(targetId.trim());
      setBlocked(result.blocked);
      setMessage(
        result.blocked
          ? "Profile blocked in this SHUFFL account."
          : "Profile unblocked.",
      );
    } catch (error) {
      setMessage(
        error instanceof Error
          ? error.message
          : "Could not update block state.",
      );
    } finally {
      setBusy(false);
    }
  };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="SAFETY"
        onBack={() => set({ screen: "feature", featureMode: "visitor" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>REPORT & BLOCK</Text>
        <Text style={styles.title}>Your safety comes first</Text>
        <Text style={styles.body}>
          Reports are recorded for review. For a venue, report incorrect hours,
          identity, media, or safety information. For a person, use their
          profile ID and block them if needed.
        </Text>
        <Text style={styles.fieldLabel}>{selectedVenueName ? "VENUE OR PROFILE ID" : "PROFILE ID"}</Text>
        <TextInput
          accessibilityLabel="Profile ID to report or block"
          autoCapitalize="none"
          value={targetId}
          onChangeText={setTargetId}
          style={styles.input}
          placeholder="Venue or profile ID"
          placeholderTextColor={colors.muted}
        />
        <Text style={styles.fieldLabel}>WHY ARE YOU REPORTING?</Text>
        {reportReasons.map((item) => (
          <Pressable
            key={item}
            accessibilityRole="radio"
            accessibilityState={{ selected: reason === item }}
            onPress={() => setReason(item)}
            style={[styles.reason, reason === item && styles.reasonSelected]}
          >
            <Text style={styles.routeText}>{item}</Text>
            <Ionicons
              name={reason === item ? "radio-button-on" : "radio-button-off"}
              size={20}
              color={reason === item ? colors.mint : colors.muted}
            />
          </Pressable>
        ))}
        <TextInput
          accessibilityLabel="Optional report details"
          value={details}
          onChangeText={setDetails}
          style={[styles.input, styles.multiline]}
          placeholder="Optional details (do not include exact location)"
          placeholderTextColor={colors.muted}
          multiline
          maxLength={1600}
          textAlignVertical="top"
        />
        <FeatureButton
          label={busy ? "Submitting…" : "Submit report"}
          onPress={submit}
        />
        <FeatureButton
          label={
            busy
              ? "Please wait…"
              : blocked
                ? "Unblock this profile"
                : "Block this profile"
          }
          onPress={toggleBlock}
          secondary
        />
        {message ? (
          <Text accessibilityRole="alert" style={styles.notice}>
            {message}
          </Text>
        ) : null}
        <Text style={styles.disclaimer}>
          Only include information needed to understand the safety concern. This
          demo does not notify or contact an external moderation team.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}

const content: Record<
  FeatureMode,
  {
    eyebrow: string;
    title: string;
    body: string;
    action: string;
    next?: FeatureMode;
    icon: keyof typeof Ionicons.glyphMap;
  }
> = {
  venue: {
    eyebrow: "VENUE DETAIL",
    title: "Sidecar, GK-2",
    body: "Buzzy, easy to settle into · Greater Kailash II. Venue media, review notes, pinboard, and preference fit are kept together here.",
    action: "Add to plan",
    next: "activePlan",
    icon: "location-outline",
  },
  customOuting: {
    eyebrow: "CUSTOM OUTING",
    title: "Shape your night",
    body: "Choose a duration, name the plan, and refresh the suggested stops.",
    action: "Review plan",
    next: "activePlan",
    icon: "sparkles-outline",
  },
  gathering: {
    eyebrow: "ADD FRIENDS",
    title: "Give the night a name",
    body: "Bring the right people into the same shape before choosing a room.",
    action: "Start gathering",
    icon: "people-outline",
  },
  activePlan: {
    eyebrow: "PERSONAL PLAN",
    title: "Settle Then Roam",
    body: "Friday · 8:30 PM – 12:30 AM. Three stops, travel time, approximate arrival windows, and the reason each stop made the cut.",
    action: "Lock plan",
    next: "arrival",
    icon: "map-outline",
  },
  arrival: {
    eyebrow: "ACTIVE PLAN",
    title: "You have arrived",
    body: "Location sharing is off by default. Arrival is a private state for your plan, not an exact location signal to other people.",
    action: "End plan",
    next: "feedback",
    icon: "flag-outline",
  },
  feedback: {
    eyebrow: "STOP FEEDBACK",
    title: "How did this stop feel?",
    body: "Rate the room, the conversation, and whether it delivered what the plan promised. Feedback improves venue confidence.",
    action: "Save feedback",
    next: "activePlan",
    icon: "star-outline",
  },
  music: {
    eyebrow: "ADD MUSIC",
    title: "Set the room’s soundtrack.",
    body: "Choose a tune catered to your vibe today. Rooms start muted and remember your selection.",
    action: "Choose a track",
    icon: "musical-notes-outline",
  },
  hostRoom: {
    eyebrow: "HOST A ROOM",
    title: "Give the night a reason",
    body: "Add co-hosts, choose a room plan, set visibility, and publish. Exact locations stay hidden until the plan consent state allows them.",
    action: "Add co-hosts",
    next: "joinRequests",
    icon: "people-outline",
  },
  joinRequests: {
    eyebrow: "JOIN REQUESTS",
    title: "People who want in",
    body: "Review requests, see compatibility bands, and accept people without exposing anyone’s exact location.",
    action: "Open capsule",
    next: "capsule",
    icon: "person-add-outline",
  },
  capsule: {
    eyebrow: "CAPSULE",
    title: "A smaller circle inside the room",
    body: "Members approve before joining. The capsule can be invite-only, friends-only, or opened to the room.",
    action: "Approve member",
    next: "chat",
    icon: "lock-open-outline",
  },
  notifications: {
    eyebrow: "NOTIFICATIONS",
    title: "Stay in the loop",
    body: "Room requests, plan changes, approvals, and support updates live here. No silent social state changes.",
    action: "Open inbox",
    next: "inbox",
    icon: "notifications-outline",
  },
  inbox: {
    eyebrow: "INBOX",
    title: "Your conversations",
    body: "Direct messages and group conversations stay separate from the plan. Unread state is explicit.",
    action: "Open group chat",
    next: "chat",
    icon: "mail-outline",
  },
  chat: {
    eyebrow: "GROUP CHAT",
    title: "Friday room",
      body: "Talk through arrival, plan edits, and the next stop. Messages stay scoped to the room and are synced when the API is connected.",
    action: "View active plan",
    next: "activePlan",
    icon: "chatbubbles-outline",
  },
  visitor: {
    eyebrow: "VISITOR PROFILE",
    title: "Someone from the room",
    body: "See shared vibe context, mutual rooms, and safety controls. No exact location or unrestricted private content is shown.",
    action: "Report or block",
    next: "report",
    icon: "person-outline",
  },
  editProfile: {
    eyebrow: "EDIT PROFILE",
    title: "Keep it current",
    body: "Update your name, bio, pronouns, photo, preferences, and privacy choices. Vibe history remains immutable per session.",
    action: "Save profile",
    next: "history",
    icon: "create-outline",
  },
  history: {
    eyebrow: "VIBE HISTORY",
    title: "Your nights have a shape",
    body: "Review frozen daily names, preference badges, and past plans without rewriting history when the population centre changes.",
    action: "Open past plans",
    next: "activePlan",
    icon: "time-outline",
  },
  privacy: {
    eyebrow: "PRIVACY & SAFETY",
    title: "You choose what is shared",
    body: "Location is off by default. Presence is approximate. Per-plan consent, report, block, and data contribution controls are visible.",
    action: "Open settings",
    next: "settings",
    icon: "shield-checkmark-outline",
  },
  settings: {
    eyebrow: "SETTINGS",
    title: "Make SHUFFL yours",
    body: "Demo mode, notifications, privacy, support, account, and accessibility preferences are all reachable from one place.",
    action: "Privacy & safety",
    next: "privacy",
    icon: "settings-outline",
  },
  report: {
    eyebrow: "SAFETY",
    title: "Report or block",
    body: "Choose a reason, block immediately if needed, and send a report for review. The user is not notified of the report details.",
    action: "Send report",
    next: "settings",
    icon: "flag-outline",
  },
  joinRoom: {
    eyebrow: "FIND A ROOM",
    title: "Join a night with a reason",
    body: "Browse hosted rooms and ask to join. Hosts review requests before anyone is added.",
    action: "Browse hosted rooms",
    icon: "people-outline",
  },
  support: {
    eyebrow: "SUPPORT",
    title: "Need a hand?",
    body: "Account help, safety questions, and plan issues are routed to a clear support state instead of dead-ending.",
    action: "Back to settings",
    next: "settings",
    icon: "help-circle-outline",
  },
};

function FeatureButton({
  label,
  onPress,
  secondary = false,
}: {
  label: string;
  onPress: () => void;
  secondary?: boolean;
}) {
  return (
    <Pressable
      onPress={onPress}
      style={secondary ? styles.secondary : styles.primary}
    >
      <Text style={secondary ? styles.secondaryText : styles.primaryText}>
        {label}
      </Text>
    </Pressable>
  );
}
function FeatureHeader({
  label,
  onBack,
}: {
  label: string;
  onBack: () => void;
}) {
  const back = () => {
    const set = useApp.getState().set;
    if (label === "HOST A ROOM") set({ screen: "feature", featureMode: "gathering" });
    else if (label === "PRIVACY & SAFETY")
      set({ screen: "feature", featureMode: "settings" });
    else if (label === "ACTIVE PLAN") set({ screen: "shuffl" });
    else onBack();
  };
  return (
    <View style={styles.header}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Go back"
        onPress={back}
        style={styles.back}
      >
        <Ionicons name="arrow-back" size={22} color={colors.text} />
      </Pressable>
      <Text style={styles.headerLabel}>{label}</Text>
      <Ionicons name="sparkles-outline" size={22} color={colors.mint} />
    </View>
  );
}
function CustomOutingScreen() {
  const { plan, scores, preferences: preferenceState, room, skeleton, set } = useApp();
  const [step, setStep] = useState(0);
  const [distance, setDistance] = useState("Up to 8 km");
  const [budget, setBudget] = useState("Flexible");
  const [title, setTitle] = useState(plan.title);
  const [duration, setDuration] = useState(plan.durationHours || 4);
  const [shapeEnergy, setShapeEnergy] = useState([0.42, 0.7, 0.5, 0.28]);
  const [shapeCrowd, setShapeCrowd] = useState([0.45, 0.7, 0.55, 0.35]);
  const [stopOptions, setStopOptions] = useState<VenueCard[][]>([]);
  const [selectedStops, setSelectedStops] = useState<(VenueCard | null)[]>([]);
  const [optionsLoaded, setOptionsLoaded] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const service = React.useMemo(() => getService(), []);
  const presets = [
    { title: "The Pregame Clubbing Night", energy: [0.35, 0.7, 0.95, 0.75], crowd: [0.3, 0.55, 0.85, 0.75] },
    { title: "The Pub Crawl", energy: [0.3, 0.52, 0.68, 0.48], crowd: [0.35, 0.45, 0.6, 0.5] },
    { title: "The Brunch and Cocktail Day Out", energy: [0.55, 0.4, 0.5, 0.7], crowd: [0.35, 0.3, 0.42, 0.55] },
  ];
  const updateShapeFromGesture = (gesture: { moveX: number; moveY: number }, width = 320) => {
    const index = Math.max(0, Math.min(3, Math.round((gesture.moveX / width) * 3)));
    const energy = Math.max(0.12, Math.min(0.95, 1 - gesture.moveY / 210));
    setShapeEnergy((current) => current.map((value, item) => item === index ? energy : value));
  };
  const shapeResponder = React.useMemo(() => PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onMoveShouldSetPanResponder: () => true,
    onPanResponderMove: (_, gesture) => updateShapeFromGesture({ moveX: gesture.moveX - 24, moveY: gesture.moveY - 12 }),
    onPanResponderRelease: () => undefined,
  }), []);
  const stopCount = Math.max(1, Math.min(3, skeleton.stops || 1));
  const loadStopOptions = async () => {
    if (busy || plan.locked) return;
    setBusy(true);
    setError("");
    try {
      await service.saveSkeleton({
        scores: Object.fromEntries(factors.map((factor) => [factor, scores[factor] ?? 50])),
        stops: stopCount,
        energy: Math.round((shapeEnergy.reduce((sum, value) => sum + value, 0) / shapeEnergy.length) * 100),
        crowd: Math.round((shapeCrowd.reduce((sum, value) => sum + value, 0) / shapeCrowd.length) * 100),
        tags: skeleton.tags,
        stop_durations: skeleton.stopDurations,
        source: "mvp_picker",
      });
      const target = {
        energy: skeleton.energy ?? scores.ENRG ?? 50,
        crowd: skeleton.crowd ?? scores.CROWD ?? 50,
        conversation: scores.TALK ?? 50,
        food: preferenceState.readings.FOOD?.score ?? 50,
        scene: preferenceState.readings.SCEN?.score ?? 50,
        live_music: preferenceState.readings.LIVE?.score ?? 50,
      };
      const options = await Promise.all(Array.from({ length: stopCount }, () => service.getStopOptions(target, { city: "New Delhi", limit: 10, includeLive: true })));
      setStopOptions(options);
      setSelectedStops((current) => Array.from({ length: stopCount }, (_, index) => current[index] ?? null));
      setOptionsLoaded(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not load venue options.");
    } finally {
      setBusy(false);
    }
  };
  const buildSelectedPlan = async () => {
    if (busy || plan.locked) return;
    if (selectedStops.some((venue) => !venue)) {
      setError("Choose one venue for every stop before building the night.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const selected = selectedStops.filter((venue): venue is VenueCard => Boolean(venue));
      const selectedPayload = selected.map((venue, index) => ({ venue_id: venue.id, name: venue.name, area: venue.area, stop_index: index }));
      const generated = plan.id
        ? await service.updatePlanStops(plan.id, selectedPayload)
        : await service.createSelectedPlan({
          title: title.trim() || "Tonight, out together",
          duration_hours: duration,
          scores: Object.fromEntries(factors.map((factor) => [factor, scores[factor] ?? 50])),
          stops: selectedPayload,
          chemistry: { tags: skeleton.tags, stop_count: stopCount, stop_durations: skeleton.stopDurations },
        });
      set({ plan: { ...plan, id: generated.id, exists: true, locked: false, style: generated.style, title: title.trim() || generated.style, durationHours: duration, stops: generated.stops, chemistry: generated.chemistry } });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not save this stop list.");
    } finally {
      setBusy(false);
    }
  };
  const lock = async () => {
    if (!plan.id || busy) return;
    setBusy(true);
    try {
      await service.lockPlan(plan.id);
      set({ plan: { ...plan, title: title.trim() || plan.style, durationHours: duration, locked: true }, screen: "feature", featureMode: "activePlan" });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not lock this plan.");
    } finally {
      setBusy(false);
    }
  };
  const nextStep = () => {
    if (step < 3) setStep((current) => current + 1);
    else if (!optionsLoaded) void loadStopOptions();
    else void buildSelectedPlan();
  };
  const topFactor = factors.reduce((best, factor) => (scores[factor] ?? 50) > (scores[best] ?? 50) ? factor : best, factors[0]);
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader label="CUSTOM OUTING" onBack={() => set({ screen: "shuffl" })} />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>CUSTOM OUTING · {step + 1} OF 4</Text>
        <Text style={styles.title}>{plan.exists ? "Your night, shaped." : "Shape your night."}</Text>
        <Text style={styles.body}>One choice at a time. The plan stays yours until you lock it.</Text>
        <View style={customStyles.stepTrack}>
          {["Distance", "Time", "Budget", "Shape"].map((label, index) => (
            <Pressable key={label} onPress={() => index <= step && setStep(index)} style={[customStyles.step, { borderColor: index === step ? colors.pink : colors.line }]}>
              <Text style={[customStyles.stepText, index === step && { color: colors.text }]}>{index + 1}</Text>
              <Text style={customStyles.stepLabel}>{label}</Text>
            </Pressable>
          ))}
        </View>
        {step === 0 && <>
          <Text style={styles.fieldLabel}>HOW FAR DO YOU WANT TO GO?</Text>
          <Text style={styles.body}>Keep it close, or let the night move across Delhi NCR.</Text>
          <View style={customStyles.purposeRow}>{["Near me", "Up to 8 km", "Anywhere in NCR"].map((value) => <Pressable key={value} onPress={() => setDistance(value)} style={[customStyles.purposeOption, distance === value && customStyles.durationSelected]}><Text style={[customStyles.durationText, distance === value && customStyles.durationTextSelected]}>{value}</Text></Pressable>)}</View>
          <Text style={styles.fieldLabel}>NAME YOUR OUTING</Text>
          <TextInput accessibilityLabel="Outing plan name" value={title} onChangeText={setTitle} style={styles.input} placeholder="Tonight, out together" placeholderTextColor={colors.muted} maxLength={48} />
        </>}
        {step === 1 && <>
          <Text style={styles.fieldLabel}>HOW LONG ARE YOU OUT?</Text>
          <Text style={styles.body}>The route will pace itself around this window.</Text>
          <View style={customStyles.durationRow}>{[2, 4, 6].map((hours) => <Pressable key={hours} accessibilityRole="radio" accessibilityState={{ selected: duration === hours }} onPress={() => setDuration(hours)} style={[customStyles.durationOption, duration === hours && customStyles.durationSelected]}><Text style={[customStyles.durationText, duration === hours && customStyles.durationTextSelected]}>{hours} hours</Text></Pressable>)}</View>
        </>}
        {step === 2 && <>
          <Text style={styles.fieldLabel}>WHAT FEELS RIGHT?</Text>
          <Text style={styles.body}>This steers the places we consider, not who gets to join.</Text>
          <View style={customStyles.purposeRow}>{["Easy", "Flexible", "Open"].map((value) => <Pressable key={value} onPress={() => setBudget(value)} style={[customStyles.purposeOption, budget === value && customStyles.durationSelected]}><Text style={[customStyles.durationText, budget === value && customStyles.durationTextSelected]}>{value}</Text></Pressable>)}</View>
        </>}
        {step === 3 && <>
          <Text style={styles.fieldLabel}>DRAW THE SHAPE OF YOUR NIGHT</Text>
          <Text style={styles.body}>Drag across the line for energy. Press a stop to change how much crowd feels right.</Text>
          <View {...shapeResponder.panHandlers} style={customStyles.skeleton}>
            <View style={customStyles.skeletonAxis}><Text style={customStyles.axisLabel}>MORE ENERGY</Text><Text style={customStyles.axisLabel}>QUIETER</Text></View>
            <View style={customStyles.skeletonLine} />
            {shapeEnergy.map((energy, index) => <Pressable key={index} accessibilityRole="adjustable" accessibilityLabel={`Stop ${index + 1} crowd level`} onPress={() => setShapeCrowd((current) => current.map((value, item) => item === index ? value >= 0.85 ? 0.25 : value + 0.2 : value))} style={[customStyles.shapeStop, { left: `${10 + index * 27}%`, bottom: `${energy * 72 + 10}%` }]}><View style={[customStyles.shapeCircle, { width: 22 + shapeCrowd[index] * 30, height: 22 + shapeCrowd[index] * 30 }]}><Text style={customStyles.shapeCircleText}>{index + 1}</Text></View></Pressable>)}
            <View style={customStyles.stopAxis}>{["Arrive", "Open up", "Peak", "Wind down"].map((label) => <Text key={label} style={customStyles.axisLabel}>{label}</Text>)}</View>
          </View>
          <Text style={styles.secondaryText}>Tap each stop to grow or soften its crowd level.</Text>
          <Text style={styles.fieldLabel}>OR SELECT FROM PRESETS</Text>
          {presets.map((preset) => <Pressable key={preset.title} onPress={() => { setTitle(preset.title); setShapeEnergy(preset.energy); setShapeCrowd(preset.crowd); }} style={customStyles.preset}><Text style={styles.routeText}>{preset.title}</Text><Text style={styles.secondaryText}>Use this shape as a starting point</Text></Pressable>)}
          {optionsLoaded && stopOptions.map((options, stopIndex) => <View key={`stop-options-${stopIndex}`} style={customStyles.optionsBlock}>
            <View style={customStyles.optionsHeader}><Text style={styles.fieldLabel}>STOP {stopIndex + 1}</Text><Text style={styles.secondaryText}>{selectedStops[stopIndex] ? "Selected" : "Choose one"}</Text></View>
            {options.length ? options.map((venue) => {
              const selected = selectedStops[stopIndex]?.id === venue.id || selectedStops[stopIndex]?.name === venue.name;
              const liveLabel = venue.live ? "Hours checked live" : "Hours available at display time";
              return <Pressable key={`${stopIndex}-${venue.id ?? venue.name}`} accessibilityRole="radio" accessibilityState={{ selected }} onPress={() => setSelectedStops((current) => current.map((item, index) => index === stopIndex ? venue : item))} style={[customStyles.optionCard, selected && customStyles.optionCardSelected]}>
                <View style={customStyles.optionCopy}><Text style={customStyles.optionName}>{venue.name}</Text><Text style={styles.secondaryText}>{venue.type} · {venue.area}</Text><Text style={customStyles.optionMeta}>{venue.tag} · {liveLabel}</Text></View><Ionicons name={selected ? "checkmark-circle" : "radio-button-off"} size={22} color={selected ? colors.pink : colors.muted} />
              </Pressable>;
            }) : <Text style={styles.secondaryText}>No published venues matched this stop. Try refreshing the options.</Text>}
          </View>)}
        </>}
        {plan.exists && step === 3 && <View style={customStyles.planMeta}><View><Text style={styles.eyebrow}>TONIGHT’S SHAPE</Text><Text style={styles.routeText}>{plan.style}</Text></View><Text style={styles.secondaryText}>{duration}h · {plan.stops.length} stops</Text></View>}
        {plan.exists && step === 3 && plan.stops.map((stop, index) => { const venue = venues.find((item) => item.name === stop || stop.startsWith(item.name)); return <View key={`${index}-${stop}`} style={customStyles.stopCard}><View style={customStyles.stopTop}><Text style={styles.eyebrow}>{index === 0 ? "START OFF WITH" : index === plan.stops.length - 1 ? "WIND DOWN AT" : "THEN, HEAD TO"}</Text><Text style={customStyles.stopNumber}>0{index + 1}</Text></View><Text style={customStyles.stopName}>{venue?.name ?? stop}</Text><Text style={styles.secondaryText}>{venue ? `${venue.type} · ${venue.area}` : "Delhi NCR"}</Text><Text style={styles.body}>{venue?.tag ?? "A Delhi stop selected for this lineup."}</Text><View style={customStyles.reason}><Ionicons name="sparkles" size={16} color={colors.pink} /><Text style={customStyles.reasonText}>Your night leans toward {factorCopy[topFactor].title.toLowerCase()}.</Text></View></View>; })}
        {error ? <Text accessibilityRole="alert" style={styles.notice}>{error}</Text> : null}
        <FeatureButton label={busy ? (optionsLoaded ? "Saving…" : "Finding venues…") : step === 3 ? (!optionsLoaded ? "Find venues" : plan.exists ? "Save new choices" : "Build my lineup") : "Next"} onPress={nextStep} />
        {step === 3 && plan.exists && <FeatureButton label={busy ? "Please wait…" : plan.locked ? "Open active plan" : "Lock this plan"} onPress={() => plan.locked ? set({ screen: "feature", featureMode: "activePlan" }) : void lock()} />}
      </ScrollView>
    </SafeAreaView>
  );
}

function GatheringScreen() {
  const { set, scores } = useApp();
  const [name, setName] = useState("Tonight together");
  const [people, setPeople] = useState<PersonRecord[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [gathering, setGathering] = useState<GatheringRecord | null>(null);
  const [proposals, setProposals] = useState<GatheringProposal[]>([]);
  const [stage, setStage] = useState<"invite" | "draw" | "proposal">("invite");
  const [skeleton, setSkeleton] = useState<Record<string, unknown> | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    getService().listPeople().then((items) => { if (active) setPeople(items); }).catch(() => undefined);
    return () => { active = false; };
  }, []);
  const create = async () => {
    if (!name.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const gathering = await getService().createGathering(name.trim(), selected);
      setGathering(gathering);
      setStage("draw");
      set({ room: { ...useApp.getState().room, name: gathering.name, members: gathering.members.map((member) => member.user_id), cohosts: selected } });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not start the gathering.");
    } finally { setBusy(false); }
  };
  const draw = async () => {
    if (!gathering || busy) return;
    setBusy(true); setError("");
    try {
      const payload = { scores: Object.fromEntries(Object.entries(scores).map(([key, value]) => [key, Number(value ?? 50)])), stops: 2, energy: Number(scores.ENRG ?? 50), crowd: Number(scores.CROWD ?? 50), tags: ["good food", "somewhere to roam"], stop_durations: [90, 120], source: "mobile" };
      await getService().saveGatheringSkeleton(gathering.id, payload);
      const merged = await getService().mergeGatheringSkeleton(gathering.id);
      const result = await getService().listGatheringProposals(gathering.id);
      setSkeleton((merged.merged ?? {}) as Record<string, unknown>);
      setProposals(result);
      setStage("proposal");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Every active member must draw before the night can be merged.");
    } finally { setBusy(false); }
  };
  const decide = async (proposal: GatheringProposal, status: "accepted" | "declined") => {
    if (!gathering || busy) return;
    setBusy(true); setError("");
    try {
      const result = await getService().decideGatheringProposal(gathering.id, proposal.id, status);
      setProposals((items) => items.map((item) => item.id === result.id ? result : item));
      if (status === "accepted") set({ screen: "shuffl" });
    } catch (cause) { setError(cause instanceof Error ? cause.message : "Could not update this proposal."); }
    finally { setBusy(false); }
  };
  return (
    <FeatureShell>
      <SafeAreaView style={styles.safe}>
        <FeatureHeader label="ADD FRIENDS" onBack={() => set({ screen: "shuffl" })} />
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.eyebrow}>ONE NIGHT · TOGETHER</Text>
          <Text style={styles.title}>{stage === "invite" ? "Give the night a name." : stage === "draw" ? "Draw your shape." : "Choose the room proposal."}</Text>
          <Text style={styles.body}>{stage === "invite" ? "Add the people who want your kind of night today. Everyone draws their own shape before the room comes together." : stage === "draw" ? "Your wheel is active. Submit your shape, then SHUFFL will merge the room when every active member has drawn." : "The merged shape is ready. Accept it to continue into ranked rooms, or decline and draw again."}</Text>
          {stage === "invite" ? <>
            <TextInput accessibilityLabel="Gathering name" value={name} onChangeText={setName} style={styles.input} placeholder="Tonight together" placeholderTextColor={colors.muted} />
            <Text style={styles.fieldLabel}>YOUR PEOPLE</Text>
            {people.length ? people.map((person) => {
              const isSelected = selected.includes(person.id);
              return <Pressable key={person.id} accessibilityRole="checkbox" accessibilityState={{ checked: isSelected }} onPress={() => setSelected((current) => isSelected ? current.filter((id) => id !== person.id) : [...current, person.id])} style={[styles.route, isSelected && { borderColor: colors.pink, backgroundColor: colors.pink + "12" }]}><View style={{ flex: 1 }}><Text style={styles.routeText}>{person.name}</Text><Text style={styles.secondaryText}>{person.city ?? "Delhi NCR"}</Text></View><Ionicons name={isSelected ? "checkmark-circle" : "add-circle-outline"} size={23} color={isSelected ? colors.pink : colors.muted} /></Pressable>;
            }) : <Text style={styles.secondaryText}>No discoverable friends yet. You can start your own night and add people later.</Text>}
            <FeatureButton label={busy ? "Starting…" : "Start gathering"} onPress={() => void create()} />
          </> : null}
          {stage === "draw" ? <>
            <View style={styles.roomCard}><Text style={styles.routeText}>{gathering?.name}</Text><Text style={styles.secondaryText}>{gathering?.members.length ?? 1} members · wheel held by you</Text><Text style={styles.body}>Invited members must accept and draw before the merge can complete.</Text></View>
            <FeatureButton label={busy ? "Merging…" : "Submit my shape"} onPress={() => void draw()} />
          </> : null}
          {stage === "proposal" ? <>
            <View style={styles.roomCard}><Text style={styles.routeText}>Merged room shape</Text><Text style={styles.secondaryText}>{skeleton ? `${String(skeleton.stops ?? 2)} stops · ${Array.isArray(skeleton.tags) ? (skeleton.tags as string[]).join(" · ") : "matched to the room"}` : "Ready for review"}</Text></View>
            {proposals.map((proposal) => <View key={proposal.id} style={styles.roomCard}><Text style={styles.routeText}>{proposal.kind.toUpperCase()} PROPOSAL</Text><Text style={styles.secondaryText}>{proposal.status === "pending" ? "Waiting for your decision" : `Proposal ${proposal.status}`}</Text>{proposal.status === "pending" ? <View style={styles.inlineActions}><FeatureButton label="Accept room" onPress={() => void decide(proposal, "accepted")} /><FeatureButton label="Decline" secondary onPress={() => void decide(proposal, "declined")} /></View> : null}</View>)}
          </> : null}
          {error ? <Text accessibilityRole="alert" style={styles.notice}>{error}</Text> : null}
        </ScrollView>
      </SafeAreaView>
    </FeatureShell>
  );
}
const customStyles = StyleSheet.create({
  stepTrack: { flexDirection: "row", gap: 6, marginBottom: 18 },
  step: {
    flex: 1,
    minHeight: 48,
    borderWidth: 1,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surface,
  },
  stepText: { color: colors.pink, fontWeight: "900" },
  stepLabel: { color: colors.muted, fontSize: 10, marginTop: 2 },
  durationRow: {
    flexDirection: "row",
    gap: 9,
    marginBottom: 22,
    flexWrap: "wrap",
  },
  durationOption: {
    minHeight: 44,
    paddingHorizontal: 16,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
  },
  purposeRow: { gap: 8, marginBottom: 22 },
  purposeOption: {
    minHeight: 44,
    paddingHorizontal: 16,
    borderRadius: 14,
    justifyContent: "center",
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
  },
  durationSelected: { backgroundColor: "#351323", borderColor: colors.pink },
  durationText: { color: colors.muted, fontWeight: "700" },
  durationTextSelected: { color: colors.text },
  disabled: { opacity: 0.55 },
  skeleton: {
    height: 300,
    marginTop: 8,
    marginBottom: 12,
    paddingLeft: 38,
    paddingRight: 12,
    paddingTop: 22,
    borderRadius: 20,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    position: "relative",
  },
  skeletonAxis: {
    position: "absolute",
    left: 10,
    top: 24,
    bottom: 52,
    justifyContent: "space-between",
  },
  skeletonLine: {
    position: "absolute",
    left: 40,
    right: 14,
    top: 165,
    height: 1,
    backgroundColor: colors.line,
  },
  axisLabel: { color: colors.muted, fontSize: 9, letterSpacing: 0.8, textTransform: "uppercase" },
  shapeStop: { position: "absolute", alignItems: "center", justifyContent: "center" },
  shapeCircle: { borderRadius: 60, backgroundColor: colors.pink, borderWidth: 3, borderColor: colors.amber, alignItems: "center", justifyContent: "center" },
  shapeCircleText: { color: colors.bg, fontWeight: "900", fontSize: 12 },
  stopAxis: { position: "absolute", left: 42, right: 8, bottom: 14, flexDirection: "row", justifyContent: "space-between" },
  preset: { padding: 14, borderRadius: 16, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.line, marginBottom: 9 },
  optionsBlock: { marginTop: 16, gap: 8 },
  optionsHeader: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 2 },
  optionCard: { flexDirection: "row", alignItems: "center", gap: 12, padding: 14, borderRadius: 16, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.line },
  optionCardSelected: { borderColor: colors.pink, backgroundColor: "#351323" },
  optionCopy: { flex: 1 },
  optionName: { color: colors.text, fontSize: 16, fontWeight: "900" },
  optionMeta: { color: colors.muted, fontSize: 11, marginTop: 5 },
  planMeta: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 12,
    padding: 14,
    backgroundColor: colors.raised,
    borderRadius: 16,
  },
  stopCard: {
    padding: 17,
    marginBottom: 12,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 20,
  },
  stopTop: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  stopNumber: {
    color: colors.pink,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 1.5,
  },
  stopName: {
    color: colors.text,
    fontSize: 23,
    fontWeight: "800",
    marginBottom: 7,
  },
  reason: {
    flexDirection: "row",
    alignItems: "center",
    gap: 8,
    padding: 11,
    borderRadius: 12,
    backgroundColor: "#25121C",
  },
  reasonText: { color: colors.text, fontSize: 13, flexShrink: 1 },
  mediaNote: {
    color: colors.muted,
    fontSize: 11,
    lineHeight: 16,
    marginTop: 12,
  },
});
function HostRoomScreen() {
  const { room, plan, set } = useApp();
  const [venueQuery, setVenueQuery] = useState("");
  const [venueFeed, setVenueFeed] = useState<VenueCard[]>([]);
  const [venueLoading, setVenueLoading] = useState(false);
  const [venueError, setVenueError] = useState("");
  const [hostIntent, setHostIntent] = useState<"choose" | "cohosts">("choose");
  const [cohostQuery, setCohostQuery] = useState("");
  const [people, setPeople] = useState<PersonRecord[]>([]);
  const [peopleLoading, setPeopleLoading] = useState(false);
  const [selectedCohosts, setSelectedCohosts] = useState<string[]>(room.cohosts);
  const [confirm, setConfirm] = useState<"create" | "host" | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    if (hostIntent !== "choose") return undefined;
    let active = true;
    setVenueLoading(true);
    setVenueError("");
    getService().getDiscovery().then((items) => {
      if (active) setVenueFeed(items);
    }).catch((cause) => {
      if (active) setVenueError(cause instanceof Error ? cause.message : "Could not load published venues.");
    }).finally(() => {
      if (active) setVenueLoading(false);
    });
    return () => { active = false; };
  }, [hostIntent]);
  useEffect(() => {
    if (hostIntent !== "cohosts") return undefined;
    let active = true;
    setPeopleLoading(true);
    getService().listPeople(cohostQuery).then((items) => {
      if (active) setPeople(items);
    }).catch((cause) => {
      if (active) setError(cause instanceof Error ? cause.message : "Could not load discoverable friends.");
    }).finally(() => {
      if (active) setPeopleLoading(false);
    });
    return () => { active = false; };
  }, [cohostQuery, hostIntent]);
  // WebSocket clients receive pushes; this lightweight polling path keeps the
  // room state correct after reconnects or on networks that block WebSockets.
  useEffect(() => {
    if (!room.id || !plan.id || getService().mode !== "api") return undefined;
    let active = true;
    const sync = async () => {
      try {
        const current = await getService().getPlan(plan.id!);
        if (!active) return;
        set({ plan: { ...plan, id: current.id, stops: current.stops, locked: Boolean(current.locked) } });
      } catch {
        // The next interval retries; the current UI remains usable offline.
      }
    };
    const timer = setInterval(sync, 15000);
    sync();
    return () => { active = false; clearInterval(timer); };
  }, [room.id, plan.id]);
  const addCohost = () =>
    set({ room: { ...room, cohosts: ["Bela"], members: ["Aarav", "Bela"] } });
  const createPlan = async () => {
    if (!room.cohosts.length && confirm !== "create")
      return setConfirm("create");
    setConfirm(null);
    set({ screen: "feature", featureMode: "customOuting" });
  };
  const host = async () => {
    if (!plan.exists || !plan.id || busy) return;
    if (!room.cohosts.length && confirm !== "host") return setConfirm("host");
    setBusy(true);
    setError("");
    try {
      const service = getService();
      const currentRoom = room.id ? room : await service.createRoom(room.name, room.members);
      await service.hostRoom(currentRoom.id!, plan.id);
      set({ room: { ...room, id: currentRoom.id!, public: true }, plan: { ...plan, locked: true } });
      setConfirm(null);
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Could not host this room. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  };
  const shareInvite = async () => {
    if (!room.id) return;
    try {
      const invite = await getService().createRoomInvite(room.id);
      await Share.share({ message: `Join my SHUFFL room: ${invite.invite_url}` });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not create invite link.");
    }
  };
  const confirmAction = () => (confirm === "host" ? host() : createPlan());
  const suggestedVenues = venueFeed.filter((venue) => venue.selectable !== false).filter((venue) => {
    const query = venueQuery.trim().toLowerCase();
    return !query || `${venue.name} ${venue.area} ${venue.type}`.toLowerCase().includes(query);
  }).slice(0, 5);
  if (!room.id && !plan.exists && !room.public && !room.cohosts.length && hostIntent === "choose") {
    return (
      <SafeAreaView style={styles.safe}>
        <FeatureHeader label="ADD FRIENDS" onBack={() => set({ screen: "shuffl" })} />
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.eyebrow}>MAKE THE FIRST MOVE</Text>
          <Text style={styles.title}>What would you like to host?</Text>
          <Text style={styles.body}>Start with a place, or shape a night with your people. The plan comes before the room.</Text>
          <View style={inboxStyles.inboxSearch}>
            <Ionicons name="search" size={18} color={colors.muted} />
            <TextInput accessibilityLabel="Search venues to host" value={venueQuery} onChangeText={setVenueQuery} placeholder="Search venues or areas" placeholderTextColor={colors.muted} style={inboxStyles.inboxSearchText} />
          </View>
          <FeatureButton label="Make a custom plan" onPress={() => set({ screen: "feature", featureMode: "customOuting" })} />
          <FeatureButton label="Make a custom plan with friends" secondary onPress={() => setHostIntent("cohosts")} />
          <Text style={styles.eyebrow}>SUGGESTED FOR YOUR VIBE</Text>
          {venueLoading ? <Text style={styles.secondaryText}>Loading published venues…</Text> : null}
          {venueError ? <Text accessibilityRole="alert" style={styles.notice}>{venueError}</Text> : null}
          {!venueLoading && !venueError && !suggestedVenues.length ? <Text style={styles.secondaryText}>No published venues match this search.</Text> : null}
          {suggestedVenues.map((venue) => <Pressable key={venue.name} onPress={() => set({ selectedVenueName: venue.name, screen: "feature", featureMode: "venue" })} style={styles.route}><View style={{ width: 52, height: 52, borderRadius: 14, overflow: "hidden", backgroundColor: venue.color + "28", alignItems: "center", justifyContent: "center", marginRight: 12 }}>{venueArtwork[venue.name] ? <Image source={venueArtwork[venue.name]} style={{ width: "100%", height: "100%" }} /> : <Ionicons name="location-outline" size={24} color={venue.color} />}</View><View style={{ flex: 1 }}><Text style={styles.routeText}>{venue.name}</Text><Text style={styles.secondaryText}>{venue.type} · {venue.area}</Text><Text style={styles.notice}>{venue.tag}</Text></View><Ionicons name="chevron-forward" size={19} color={colors.muted} /></Pressable>)}
        </ScrollView>
      </SafeAreaView>
    );
  }
  if (!room.id && !plan.exists && !room.public && !room.cohosts.length && hostIntent === "cohosts") {
    return (
      <SafeAreaView style={styles.safe}>
        <FeatureHeader label="ADD CO-HOSTS" onBack={() => setHostIntent("choose")} />
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.eyebrow}>A NIGHT WITH YOUR PEOPLE</Text>
          <Text style={styles.title}>Add co-hosts</Text>
          <Text style={styles.body}>Everyone draws their own night shape before the plan becomes public.</Text>
          <View style={inboxStyles.inboxSearch}><Ionicons name="search" size={18} color={colors.muted} /><TextInput accessibilityLabel="Search co-hosts" value={cohostQuery} onChangeText={setCohostQuery} placeholder="Search usernames" placeholderTextColor={colors.muted} style={inboxStyles.inboxSearchText} /></View>
          {peopleLoading ? <Text style={styles.secondaryText}>Loading discoverable friends…</Text> : null}
          {!peopleLoading && !people.length ? <Text style={styles.secondaryText}>No discoverable friends match that search.</Text> : null}
          {people.map((person) => { const selected = selectedCohosts.includes(person.id); return <Pressable key={person.id} accessibilityRole="checkbox" accessibilityState={{ checked: selected }} onPress={() => setSelectedCohosts((current) => selected ? current.filter((item) => item !== person.id) : [...current, person.id])} style={styles.route}><View style={capsuleStyles.friendAvatar}><Text style={capsuleStyles.friendInitial}>{person.name.charAt(0)}</Text></View><View style={{ flex: 1 }}><Text style={styles.routeText}>{person.name}</Text><Text style={styles.secondaryText}>{person.city || "Delhi NCR"} · discoverable member</Text></View><Ionicons name={selected ? "checkmark-circle" : "ellipse-outline"} size={24} color={selected ? colors.pink : colors.muted} /></Pressable>; })}
          <FeatureButton label={selectedCohosts.length ? `Continue with ${selectedCohosts.length} co-host${selectedCohosts.length > 1 ? "s" : ""}` : "Choose at least one co-host"} onPress={() => { if (!selectedCohosts.length) return; set({ room: { ...room, cohosts: selectedCohosts, members: ["Aarav", ...selectedCohosts] }, screen: "feature", featureMode: "customOuting" }); }} />
        </ScrollView>
      </SafeAreaView>
    );
  }
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="HOST A ROOM"
        onBack={() => set({ screen: "control" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>ROOM SETUP</Text>
        <Text style={styles.title}>{room.name}</Text>
        <Text style={styles.body}>
          {room.public
            ? "Room is public. The plan and chemistry are now frozen for everyone who joins."
            : "Build the room privately, make the plan, then host it when the room is ready."}
        </Text>
        <FeatureButton
          label={useApp.getState().activeMusic ? `Music · ${useApp.getState().activeMusic}` : "Add music for the room"}
          onPress={() => set({ screen: "feature", featureMode: "music" })}
          secondary
        />
        <View style={styles.routeList}>
          {room.members.map((member) => (
            <View key={member} style={styles.route}>
              <Text style={styles.routeText}>{member} · today’s vibe</Text>
              <Text style={styles.secondaryText}>
                {member === "Aarav" ? "HOST" : "CO-HOST"}
              </Text>
            </View>
          ))}
        </View>
        {!room.public && !plan.exists && !room.cohosts.length && (
          <FeatureButton label="Add a co-host" onPress={addCohost} />
        )}{" "}
        {!room.public && !plan.exists && (
          <FeatureButton
            label={busy ? "Building plan…" : "Create plan"}
            onPress={createPlan}
            secondary={!!room.cohosts.length}
          />
        )}{" "}
        {error ? (
          <Text accessibilityRole="alert" style={styles.secondaryText}>
            {error}
          </Text>
        ) : null}
        {confirm && (
          <View style={styles.route}>
            <Text style={styles.body}>
              {confirm === "host"
                ? "You will not be able to add co-hosts after hosting this room. Continue?"
                : "This plan is just for you because you have not added co-hosts. Continue?"}
            </Text>
            <FeatureButton
              label={busy ? "Please wait…" : "Continue"}
              onPress={confirmAction}
            />
            <FeatureButton
              label="Cancel"
              onPress={() => setConfirm(null)}
              secondary
            />
          </View>
        )}{" "}
        {plan.exists && (
          <View style={styles.routeList}>
            <Text style={styles.eyebrow}>
              {plan.style} · {plan.locked ? "LOCKED" : "PRIVATE DRAFT"}
            </Text>
            {plan.stops.map((stop, index) => (
              <View key={`${index}-${stop}`} style={styles.route}>
                <Text style={styles.routeText}>
                  {index + 1}. {stop}
                </Text>
              </View>
            ))}
          </View>
        )}{" "}
        {plan.exists && !room.public && (
          <FeatureButton
            label={busy ? "Hosting…" : "Host room"}
            onPress={host}
          />
        )}{" "}
        {room.public && (
          <FeatureButton
            label="Share room invite"
            onPress={() => void shareInvite()}
            secondary
          />
        )}{" "}
        {room.public && (
          <FeatureButton
            label="Open join requests"
            onPress={() =>
              set({ screen: "feature", featureMode: "joinRequests" })
            }
            secondary
          />
        )}{" "}
        {plan.exists && (
          <FeatureButton
            label="View plan"
            onPress={() =>
              set({ screen: "feature", featureMode: "activePlan" })
            }
            secondary
          />
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
function ArrivalScreen() {
  const { plan, set } = useApp();
  const [consented, setConsented] = useState(false);
  const [allowed, setAllowed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    if (!plan.id || !plan.exists)
      return () => {
        active = false;
      };
    setLoading(true);
    Promise.all([
      getService().getPrivacy(),
      getService().getPlanLocationConsent(plan.id),
    ])
      .then(([privacy, consent]) => {
        if (active) {
          setAllowed(privacy.location_sharing);
          setConsented(consent.approved);
        }
      })
      .catch((cause) => {
        if (active)
          setError(
            cause instanceof Error
              ? cause.message
              : "Could not load arrival consent.",
          );
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, [plan.id, plan.exists]);
  const toggleConsent = async () => {
    if (!plan.id || busy) return;
    setBusy(true);
    setError("");
    try {
      const result = await getService().savePlanLocationConsent(
        plan.id,
        !consented,
      );
      setConsented(result.approved);
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Could not update consent.",
      );
    } finally {
      setBusy(false);
    }
  };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="ARRIVAL & CONSENT"
        onBack={() => set({ screen: "feature", featureMode: "activePlan" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>PLAN CHECK-IN</Text>
        <Text style={styles.title}>You have arrived</Text>
        <Text style={styles.body}>
          The demo does not read GPS or expose exact coordinates. You can
          separately opt in to approximate presence for this plan.
        </Text>
        {!plan.exists || !plan.id ? (
          <Text style={styles.secondaryText}>
            Create a plan before setting arrival consent.
          </Text>
        ) : (
          <View style={styles.route}>
            <View style={{ flex: 1, paddingRight: 12 }}>
              <Text style={styles.routeText}>
                Approximate presence for this plan
              </Text>
              <Text style={styles.secondaryText}>
                {loading
                  ? "Checking saved consent…"
                  : allowed
                    ? consented
                      ? "Shared as approximate presence"
                      : "Not shared"
                    : "Turn on per-plan permission in Privacy & Safety first"}
              </Text>
            </View>
            <Switch
              value={consented}
              disabled={loading || busy || !allowed}
              onValueChange={toggleConsent}
              trackColor={{ false: "#35413F", true: "#32D6B0" }}
              thumbColor={consented ? "#07100E" : "#E8EFEC"}
              accessibilityLabel="Approximate presence for this plan"
            />
          </View>
        )}
        {error ? (
          <Text accessibilityRole="alert" style={styles.secondaryText}>
            {error}
          </Text>
        ) : null}
        {!allowed && plan.id ? (
          <FeatureButton
            label="Open Privacy & Safety"
            onPress={() => set({ screen: "feature", featureMode: "privacy" })}
            secondary
          />
        ) : null}
        <FeatureButton
          label="End plan"
          onPress={() => set({ screen: "feature", featureMode: "feedback" })}
        />
      </ScrollView>
    </SafeAreaView>
  );
}

function PrivacySafetyScreen() {
  const { set } = useApp();
  const [settings, setSettings] = useState<PrivacySettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    getService()
      .getPrivacy()
      .then((result) => {
        if (active) setSettings(result);
      })
      .catch((cause) => {
        if (active)
          setError(
            cause instanceof Error
              ? cause.message
              : "Could not load privacy settings.",
          );
      })
      .finally(() => {
        if (active) setLoading(false);
      });
    return () => {
      active = false;
    };
  }, []);
  const update = (patch: Partial<PrivacySettings>) => {
    if (!settings) return;
    setSettings({ ...settings, ...patch });
    setMessage("");
  };
  const cycleVisibility = (key: string) => {
    if (!settings) return;
    const current = settings.visibility[key] ?? "friends";
    const next =
      current === "everyone"
        ? "friends"
        : current === "friends"
          ? "nobody"
          : "everyone";
    update({ visibility: { ...settings.visibility, [key]: next } });
  };
  const save = async () => {
    if (!settings || saving) return;
    setSaving(true);
    setError("");
    setMessage("");
    try {
      setSettings(await getService().savePrivacy(settings));
      setMessage("Your privacy settings are saved.");
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Could not save privacy settings.",
      );
    } finally {
      setSaving(false);
    }
  };
  const deleteAccount = () => Alert.alert("Delete SHUFFL account?", "Your profile, vibe history, plans, and privacy state will be reset. The locked venue catalogue will not be changed.", [
    { text: "Cancel", style: "cancel" },
    { text: "Delete account", style: "destructive", onPress: () => { void getService().deleteAccount().then(() => { set({ userName: "", userPronouns: "", userBio: "", screen: "welcome", onboardingComplete: false }); }).catch((cause) => setError(cause instanceof Error ? cause.message : "Account could not be deleted.")); } },
  ]);
  const row = (
    title: string,
    detail: string,
    value: boolean,
    onChange: (value: boolean) => void,
  ) => (
    <View key={title} style={styles.route}>
      <View style={{ flex: 1, paddingRight: 16 }}>
        <Text style={styles.routeText}>{title}</Text>
        <Text style={styles.secondaryText}>{detail}</Text>
      </View>
      <Switch
        value={value}
        onValueChange={onChange}
        trackColor={{ false: "#35413F", true: "#32D6B0" }}
        thumbColor={value ? "#07100E" : "#E8EFEC"}
        accessibilityLabel={title}
      />
    </View>
  );
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="PRIVACY & SAFETY"
        onBack={() => set({ screen: "control" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>YOUR CONTROLS</Text>
        <Text style={styles.title}>You choose what is shared</Text>
        <Text style={styles.body}>
          Exact location is not shown to other members. Presence is approximate,
          and plan-level sharing still requires consent.
        </Text>
        {loading ? (
          <Text style={styles.secondaryText}>Loading your saved choices…</Text>
        ) : !settings ? (
          <Text accessibilityRole="alert" style={styles.secondaryText}>
            {error || "Privacy settings are unavailable."}
          </Text>
        ) : (
          <>
            {row(
              "Allow per-plan location sharing",
              "Off by default. This does not enable sharing for a plan without your consent.",
              settings.location_sharing,
              (value) => update({ location_sharing: value }),
            )}
            {row(
              "Approximate group presence",
              "Share a broad arrival/presence state, never an exact position.",
              settings.approximate_presence,
              (value) => update({ approximate_presence: value }),
            )}
            {row(
              "Discoverability",
              "Allow your profile to appear in eligible room and discovery surfaces.",
              settings.discoverability,
              (value) => update({ discoverability: value }),
            )}
            <Text style={styles.eyebrow}>WHO CAN SEE WHAT</Text>
            {(["profile", "vibe", "plans"] as const).map((key) => (
              <Pressable
                key={key}
                accessibilityRole="button"
                accessibilityLabel={`Change ${key} visibility`}
                onPress={() => cycleVisibility(key)}
                style={styles.route}
              >
                <View>
                  <Text style={styles.routeText}>
                    {key === "profile"
                      ? "Profile"
                      : key === "vibe"
                        ? "Vibe context"
                        : "Plans"}
                  </Text>
                  <Text style={styles.secondaryText}>Tap to change access</Text>
                </View>
                <Text style={styles.secondaryText}>
                  {settings.visibility[key] ?? "friends"} ›
                </Text>
              </Pressable>
            ))}
            {error ? (
              <Text accessibilityRole="alert" style={styles.secondaryText}>
                {error}
              </Text>
            ) : null}
            {message ? (
              <Text accessibilityRole="alert" style={styles.secondaryText}>
                {message}
              </Text>
            ) : null}
            <FeatureButton
              label={saving ? "Saving…" : "Save privacy choices"}
              onPress={save}
            />
          </>
        )}
        <FeatureButton
          label="Report or block someone"
          onPress={() => set({ screen: "feature", featureMode: "report" })}
          secondary
        />
        <FeatureButton label="Delete account" onPress={deleteAccount} secondary />
      </ScrollView>
    </SafeAreaView>
  );
}

function ActivePlanScreen() {
  const { room, plan, set } = useApp();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const lock = async () => {
    if (!plan.id || busy || plan.locked || room.public) return;
    setBusy(true);
    setError("");
    try {
      await getService().lockPlan(plan.id);
      set({ plan: { ...plan, locked: true } });
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Could not lock this plan. Please try again.",
      );
    } finally {
      setBusy(false);
    }
  };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="ACTIVE PLAN"
        onBack={() => set({ screen: "control" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>
          {room.public
            ? "HOSTED PLAN"
            : plan.exists
              ? "PRIVATE PLAN"
              : "PLAN BUILDER"}
        </Text>
        <Text style={styles.title}>
          {plan.exists
            ? plan.title || plan.style
            : "Your night, shaped around you"}
        </Text>
        <Text style={styles.body}>
          {room.public
            ? "This plan is frozen for the hosted room."
            : plan.locked
              ? "This plan is locked. Its chemistry and stops will not change."
              : plan.exists
                ? "Review the selected stops. Change any venue before you lock the night."
                : "No plan has been created yet. Draw your night and choose one published venue for every stop."}
        </Text>
        {plan.exists ? (
          plan.stops.map((stop, index) => {
            const venue = venues.find(
              (item) => stop === item.name || stop.startsWith(item.name),
            );
            return (
              <View key={`${index}-${stop}`} style={activePlanStyles.stopCard}>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel={`Open venue ${venue?.name ?? stop}`}
                  onPress={() =>
                    set({
                      screen: "feature",
                      featureMode: "venue",
                      selectedVenueName: venue?.name ?? stop,
                    })
                  }
                >
                  <View style={activePlanStyles.stopHead}>
                    <View style={activePlanStyles.stopIndex}>
                      <Text style={activePlanStyles.stopIndexText}>
                        {String(index + 1).padStart(2, "0")}
                      </Text>
                    </View>
                    <View style={{ flex: 1 }}>
                      <Text style={styles.routeText}>
                        {venue?.name ?? stop}
                      </Text>
                      <Text style={styles.secondaryText}>
                        {venue
                          ? `${venue.type} · ${venue.area}`
                          : index === 0
                            ? "START HERE · DELHI NCR"
                            : "NEXT STOP · DELHI NCR"}
                      </Text>
                    </View>
                    <Ionicons
                      name="chevron-forward"
                      size={19}
                      color={colors.muted}
                    />
                  </View>
                  {venue && (
                    <Text style={activePlanStyles.stopDescription}>
                      {venue.tag}
                    </Text>
                  )}
                  <Text style={activePlanStyles.stopAction}>
                    {index === 0 ? "START THE NIGHT" : "VIEW STOP DETAILS"}
                  </Text>
                </Pressable>
                <Pressable
                  accessibilityRole="button"
                  accessibilityLabel={`Dish and drink suggestions for ${venue?.name ?? stop}`}
                  onPress={() =>
                    set({
                      screen: "feature",
                      featureMode: "venue",
                      selectedVenueName: venue?.name ?? stop,
                    })
                  }
                  style={activePlanStyles.pairingLink}
                >
                  <Text style={activePlanStyles.pairingText}>
                    🍸 Dish & drink pairing
                  </Text>
                  <Ionicons
                    name="arrow-forward"
                    size={16}
                    color={colors.pink}
                  />
                </Pressable>
              </View>
            );
          })
        ) : (
          <View style={styles.route}>
            <Text style={styles.secondaryText}>
              Your plan will appear here after generation.
            </Text>
          </View>
        )}
        {error ? (
          <Text accessibilityRole="alert" style={styles.secondaryText}>
            {error}
          </Text>
        ) : null}
        {!plan.exists && (
          <FeatureButton
            label="Draw my night and choose venues"
            onPress={() => set({ screen: "feature", featureMode: "customOuting" })}
          />
        )}
        {plan.exists && !plan.locked && !room.public && (
          <FeatureButton
            label={busy ? "Locking…" : "Lock this plan"}
            onPress={lock}
          />
        )}
        {plan.exists && !plan.locked && !room.public && (
          <FeatureButton
            label="Change selected venues"
            onPress={() => set({ screen: "feature", featureMode: "customOuting" })}
            secondary
          />
        )}
        {!plan.exists && (
          <FeatureButton
            label="Set up a hosted room"
            onPress={() => set({ screen: "feature", featureMode: "hostRoom" })}
            secondary
          />
        )}
        {plan.exists && (
          <FeatureButton
            label="Check-in & location consent"
            onPress={() => set({ screen: "feature", featureMode: "arrival" })}
            secondary
          />
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
const activePlanStyles = StyleSheet.create({
  stopCard: {
    padding: 15,
    marginBottom: 10,
    borderRadius: 18,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
  },
  stopHead: { flexDirection: "row", alignItems: "center", gap: 12 },
  stopIndex: {
    width: 36,
    height: 36,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#351323",
  },
  stopIndexText: { color: colors.pink, fontWeight: "900", letterSpacing: 1 },
  stopDescription: {
    color: colors.muted,
    fontSize: 13,
    lineHeight: 19,
    marginTop: 12,
  },
  stopAction: {
    color: colors.pink,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1.2,
    marginTop: 13,
  },
  pairingLink: {
    marginTop: 12,
    minHeight: 38,
    borderTopWidth: 1,
    borderTopColor: colors.line,
    paddingTop: 10,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  pairingText: { color: colors.text, fontSize: 13, fontWeight: "700" },
});
function JoinRoomScreen() {
  const { set, scores, assessment } = useApp();
  const service = React.useMemo(() => getService(), []);
  const [rooms, setRooms] = useState<RoomRecord[]>([]);
  const [requests, setRequests] = useState<Record<string, JoinRequestRecord>>(
    {},
  );
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const joinerScores = React.useMemo(() => {
    const vector = Object.fromEntries(
      factors.map((factor) => [factor, scores[factor] ?? 50]),
    ) as JoinerScores;
    vector.latency_firmness = latencyFirmness(assessment);
    return vector;
  }, [scores, assessment]);
  useEffect(() => {
    let active = true;
    service
      .listHostedRooms()
      .then(async (items) => {
        if (!active) return;
        const [fits, existing] = await Promise.all([
          Promise.all(
            items.map(
              async (room) =>
                [
                  room.id,
                  await service.getRoomEligibility(room.id, joinerScores),
                ] as const,
            ),
          ),
          Promise.all(
            items.map(
              async (room) =>
                [
                  room.id,
                  (await service.getJoinRequests(room.id, "all")).find(
                    (item) => item.member_id === "demo-visitor",
                  ),
                ] as const,
            ),
          ),
        ]);
        if (!active) return;
        const fitByRoom = Object.fromEntries(fits);
        setRooms(
          items.map((room) => ({
            ...room,
            join_eligibility: fitByRoom[room.id],
          })),
        );
        setRequests(
          Object.fromEntries(
            existing
              .filter((entry): entry is readonly [string, JoinRequestRecord] =>
                Boolean(entry[1]),
              )
              .map(([roomId, item]) => [roomId, item]),
          ),
        );
      })
      .catch((cause) => {
        if (active)
          setError(
            cause instanceof Error
              ? cause.message
              : "Could not load hosted rooms.",
          );
      });
    return () => {
      active = false;
    };
  }, [service, joinerScores]);
  const requestJoin = async (room: RoomRecord) => {
    setBusy(true);
    setError("");
    try {
      const result = await service.requestToJoin(
        room.id,
        "demo-visitor",
        "I would like to join this room.",
        joinerScores,
      );
      setRequests((current) => ({ ...current, [room.id]: result }));
    } catch (cause) {
      setError(
        cause instanceof Error ? cause.message : "Could not request to join.",
      );
    } finally {
      setBusy(false);
    }
  };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="FIND A ROOM"
        onBack={() => set({ screen: "rooms" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>HOSTED NIGHTS</Text>
        <Text style={styles.title}>Find your people</Text>
        <Text style={styles.body}>
          Your vibe fit is shown as a helpful signal. It never blocks a join
          request; the host decides who joins.
        </Text>
        {rooms.map((room) => {
          const existing = requests[room.id];
          const fit = room.join_eligibility;
          return (
            <View key={room.id} style={styles.roomCard}>
              <Text style={styles.routeText}>{room.title}</Text>
              <Text style={styles.secondaryText}>
                {room.members?.length ?? 0} members · {room.status}
              </Text>
              {room.stop_types?.length ? (
                <Text style={styles.secondaryText}>
                  {room.stop_count} stop{room.stop_count === 1 ? "" : "s"} ·{" "}
                  {room.stop_types.join(" → ")}
                </Text>
              ) : null}
              {room.selected_stops?.length ? (
                <View style={styles.routeList}>
                  <Text style={styles.eyebrow}>HOST'S STOP LIST · READ ONLY</Text>
                  {room.selected_stops.map((stop, index) => (
                    <Text key={`${room.id}-${index}-${stop.name}`} style={styles.secondaryText}>
                      {index + 1}. {stop.name}{stop.area ? ` · ${stop.area}` : ""}
                    </Text>
                  ))}
                </View>
              ) : null}
              {fit?.eligible ? (
                <Text style={styles.notice}>
                  Vibe fit · every stop and the night’s ROAM count are inside
                  your bend
                </Text>
              ) : (
                <Text style={styles.secondaryText}>
                  Outside your current vibe bend · request is still allowed
                  {fit?.reasons?.length
                    ? ": " + fit.reasons.join(" · ")
                    : " · eligibility unavailable"}
                </Text>
              )}
              {existing ? (
                <Text style={styles.notice}>
                  {existing.status === "pending"
                    ? "Request sent · waiting for host"
                    : "Request " + existing.status}
                </Text>
              ) : (
                <FeatureButton
                  label={busy ? "Sending…" : "Request to join"}
                  onPress={() => requestJoin(room)}
                />
              )}
            </View>
          );
        })}
        {!rooms.length && !error && (
          <View style={styles.route}>
            <Text style={styles.body}>
              No hosted rooms are available right now.
            </Text>
          </View>
        )}
        {error ? (
          <Text accessibilityRole="alert" style={styles.notice}>
            {error}
          </Text>
        ) : null}
        <FeatureButton
          label="Add friends to your night"
          onPress={() => set({ screen: "feature", featureMode: "gathering" })}
          secondary
        />
      </ScrollView>
    </SafeAreaView>
  );
}
function JoinRequestsScreen() {
  const { room, set } = useApp();
  const service = React.useMemo(() => getService(), []);
  const [requests, setRequests] = useState<JoinRequestRecord[]>([]);
  const [busyId, setBusyId] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const reload = React.useCallback(async () => {
    if (!room.id) {
      setRequests([]);
      return;
    }
    try {
      setRequests(await service.getJoinRequests(room.id));
      setError("");
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Could not load join requests.",
      );
    }
  }, [room.id, service]);
  useEffect(() => {
    void reload();
  }, [reload]);
  const decide = async (
    request: JoinRequestRecord,
    status: "accepted" | "declined",
  ) => {
    if (!room.id || busyId) return;
    setBusyId(request.id);
    setError("");
    setNotice("");
    try {
      const result = await service.decideJoinRequest(
        room.id,
        request.id,
        status,
      );
      setRequests((items) => items.filter((item) => item.id !== request.id));
      if (status === "accepted")
        set({
          room: {
            ...room,
            members: [...new Set([...room.members, request.member_id])],
            accepted: [...new Set([...room.accepted, request.member_id])],
          },
        });
      setNotice(
        status === "accepted"
          ? request.member_id + " joined. Hosted plan remains frozen."
          : "Request declined.",
      );
      if (!result.plan_frozen) setNotice("Request updated.");
    } catch (cause) {
      setError(
        cause instanceof Error
          ? cause.message
          : "Could not resolve this request.",
      );
    } finally {
      setBusyId("");
    }
  };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="JOIN REQUESTS"
        onBack={() => set({ screen: "feature", featureMode: "hostRoom" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>
          {room.public ? "ROOM IS HOSTED" : "ROOM NOT HOSTED"}
        </Text>
        <Text style={styles.title}>People who want in</Text>
        <Text style={styles.body}>
          Review each request explicitly. Accepting adds the requester’s member
          ID and keeps the hosted plan unchanged. Fit is a label for context,
          never an automatic admission gate.
        </Text>
        {error ? (
          <Text accessibilityRole="alert" style={styles.notice}>
            {error}
          </Text>
        ) : null}
        {notice ? (
          <Text accessibilityRole="alert" style={styles.notice}>
            {notice}
          </Text>
        ) : null}
        {requests.map((request) => (
          <View key={request.id} style={styles.requestCard}>
            <Text style={styles.routeText}>{request.member_id}</Text>
            <Text style={styles.secondaryText}>
              {request.note || "No note provided"}
            </Text>
            <Text style={styles.disclaimer}>
              {request.fit
                ? "Vibe fit looks aligned with this room."
                : `Vibe mismatch noted${request.fit_reasons?.length ? ` · ${request.fit_reasons.join(" · ")}` : ""}. Host decision required.`}
            </Text>
            <View style={styles.requestActions}>
              <Pressable
                accessibilityRole="button"
                accessibilityLabel={"Accept request from " + request.member_id}
                disabled={!!busyId}
                onPress={() => decide(request, "accepted")}
              >
                <Ionicons
                  name="checkmark-circle"
                  size={30}
                  color={colors.mint}
                />
              </Pressable>
              <Pressable
                accessibilityRole="button"
                accessibilityLabel={"Decline request from " + request.member_id}
                disabled={!!busyId}
                onPress={() => decide(request, "declined")}
              >
                <Ionicons name="close-circle" size={30} color={colors.danger} />
              </Pressable>
            </View>
          </View>
        ))}
        {!requests.length && !error && (
          <View style={styles.route}>
            <Text style={styles.body}>No pending join requests.</Text>
          </View>
        )}
        <FeatureButton
          label="Refresh requests"
          onPress={() => void reload()}
          secondary
        />
        <FeatureButton
          label="Return to your gathering"
          onPress={() => set({ screen: "feature", featureMode: "gathering" })}
          secondary
        />
      </ScrollView>
    </SafeAreaView>
  );
}
function CapsuleScreen() {
  const { capsule, room, set } = useApp();
  const [query, setQuery] = useState("");
  const [people, setPeople] = useState<PersonRecord[]>([]);
  const [peopleLoading, setPeopleLoading] = useState(false);
  const [selected, setSelected] = useState<string[]>(capsule.members);
  const [invitesSent, setInvitesSent] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => {
    let active = true;
    setPeopleLoading(true);
    getService().listPeople(query).then((items) => {
      if (active) setPeople(items);
    }).catch((cause) => {
      if (active) setError(cause instanceof Error ? cause.message : "Could not load discoverable friends.");
    }).finally(() => {
      if (active) setPeopleLoading(false);
    });
    return () => { active = false; };
  }, [query]);
  const ready =
    capsule.members.length > 0 &&
    capsule.members.every((member) => capsule.approvals[member] === true);
  const toggleFriend = (id: string) =>
    setSelected((current) =>
      current.includes(id)
        ? current.filter((item) => item !== id)
        : [...current, id],
    );
  const sendInvites = async () => {
    if (!selected.length) return;
    setBusy(true);
    setError("");
    try {
      const record = room.id
        ? await getService().createCapsule(room.id, selected)
        : { id: undefined, room_id: undefined, members: selected, approvals: Object.fromEntries(selected.map((member) => [member, false])), status: "awaiting_approval" as const };
      const roomId = (record as CapsuleRecord & { room_id?: string }).room_id;
      set({ capsule: { id: record.id, roomId, status: record.status, members: record.members, approvals: record.approvals } });
      setInvitesSent(true);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not send capsule invites.");
    } finally {
      setBusy(false);
    }
  };
  const approveMember = async (member: string) => {
    if (capsule.approvals[member] || busy) return;
    setBusy(true);
    setError("");
    try {
      const record = capsule.id
        ? await getService().approveCapsule(capsule.id, member, true)
        : { ...capsule, approvals: { ...capsule.approvals, [member]: true }, status: "approved" as const };
      const roomId = (record as CapsuleRecord & { room_id?: string }).room_id;
      set({ capsule: { id: record.id, roomId, status: record.status, members: record.members, approvals: record.approvals } });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not save approval.");
    } finally {
      setBusy(false);
    }
  };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="CAPSULE"
        onBack={() => set({ screen: "feature", featureMode: "inbox" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>SHUFFL CAPSULE</Text>
        <Text style={styles.title}>Bring your circle along.</Text>
        <Text style={styles.body}>
          Choose friends for your capsule. Everyone needs to approve a room
          before the group request can move forward.
        </Text>
        <View style={inboxStyles.inboxSearch}>
          <Ionicons name="search" size={18} color={colors.muted} />
          <TextInput
            accessibilityLabel="Search friends for capsule"
            value={query}
            onChangeText={setQuery}
            placeholder="Search your friends"
            placeholderTextColor={colors.muted}
            style={inboxStyles.inboxSearchText}
          />
        </View>
        <Text style={styles.eyebrow}>YOUR SHUFFL FRIENDS</Text>
        {peopleLoading ? <Text style={styles.secondaryText}>Loading discoverable friends…</Text> : null}
        {people.map((person) => {
          const checked = selected.includes(person.id);
          return (
            <Pressable
              key={person.id}
              accessibilityRole="checkbox"
              accessibilityState={{ checked }}
              onPress={() => toggleFriend(person.id)}
              style={styles.route}
            >
              <View style={capsuleStyles.friendAvatar}>
                <Text style={capsuleStyles.friendInitial}>
                  {person.name.charAt(0)}
                </Text>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={styles.routeText}>{person.name}</Text>
                <Text style={styles.secondaryText}>
                  {person.city || "Delhi NCR"} · discoverable member
                </Text>
              </View>
              <Ionicons
                name={checked ? "checkmark-circle" : "ellipse-outline"}
                size={24}
                color={checked ? colors.pink : colors.muted}
              />
            </Pressable>
          );
        })}
        {!peopleLoading && !people.length && (
          <Text style={styles.secondaryText}>No discoverable friends match that name.</Text>
        )}
        <FeatureButton label={busy ? "Saving…" : "Send capsule invites"} onPress={() => void sendInvites()} />
        {error ? <Text accessibilityRole="alert" style={styles.notice}>{error}</Text> : null}
        {invitesSent && (
          <View style={capsuleStyles.notice}>
            <Ionicons
              name="information-circle-outline"
              size={18}
              color={colors.cyan}
            />
            <Text style={capsuleStyles.noticeText}>
              {room.id ? "Invites are saved to this room. Each member must approve before continuing." : "Preview mode: connect the API to send real capsule notifications."}
            </Text>
          </View>
        )}
        {invitesSent &&
          capsule.members.map((member) => (
            <View key={member} style={styles.route}>
              <View style={{ flex: 1 }}>
                <Text style={styles.routeText}>{member}</Text>
                <Text style={styles.secondaryText}>
                  {capsule.approvals[member]
                    ? "APPROVED"
                    : "WAITING FOR APPROVAL"}
                </Text>
              </View>
              <Pressable
                accessibilityRole="button"
                accessibilityLabel={`Approve capsule for ${member}`}
                disabled={!!capsule.approvals[member] || busy}
                onPress={() => void approveMember(member)}
              >
                <Ionicons
                  name={
                    capsule.approvals[member]
                      ? "checkmark-circle"
                      : "checkmark-circle-outline"
                  }
                  size={28}
                  color={
                    capsule.approvals[member] ? colors.green : colors.muted
                  }
                />
              </Pressable>
            </View>
          ))}
        {invitesSent && (
          <Pressable
            accessibilityRole="button"
            accessibilityState={{ disabled: !ready }}
            disabled={!ready}
            onPress={() => set({ screen: "feature", featureMode: "joinRoom" })}
            style={[styles.primary, !ready && capsuleStyles.disabled]}
          >
            <Text style={styles.primaryText}>
              {ready
                ? "Browse rooms for everyone"
                : "Waiting for everyone to approve"}
            </Text>
          </Pressable>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
const capsuleStyles = StyleSheet.create({
  friendAvatar: {
    width: 40,
    height: 40,
    borderRadius: 20,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.raised,
    marginRight: 11,
  },
  friendInitial: { color: colors.pink, fontSize: 16, fontWeight: "800" },
  notice: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 8,
    padding: 12,
    marginTop: 14,
    borderRadius: 12,
    backgroundColor: colors.raised,
  },
  noticeText: { flex: 1, color: colors.muted, fontSize: 12, lineHeight: 17 },
  disabled: { opacity: 0.48 },
});
const inboxStyles = StyleSheet.create({
  inboxTitleRow: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  newMessage: {
    width: 44,
    height: 44,
    borderRadius: 22,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.raised,
    borderWidth: 1,
    borderColor: colors.line,
  },
  storyRail: { gap: 16, paddingVertical: 14 },
  storyItem: { width: 60, alignItems: "center", gap: 7 },
  storyRing: {
    width: 58,
    height: 58,
    borderRadius: 29,
    borderWidth: 2,
    padding: 3,
  },
  storyAvatar: {
    flex: 1,
    borderRadius: 26,
    alignItems: "center",
    justifyContent: "center",
  },
  storyInitial: { color: colors.text, fontSize: 20, fontWeight: "800" },
  storyName: { color: colors.muted, fontSize: 11 },
  inboxSearch: {
    height: 48,
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 14,
    borderRadius: 16,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    marginVertical: 12,
  },
  inboxSearchText: { flex: 1, color: colors.text, padding: 0 },
  inboxTabs: {
    flexDirection: "row",
    gap: 20,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
    marginTop: 6,
    marginBottom: 4,
  },
  inboxTab: {
    paddingVertical: 12,
    borderBottomWidth: 2,
    borderBottomColor: "transparent",
  },
  inboxTabActive: { borderBottomColor: colors.pink },
  inboxTabText: { color: colors.text, fontWeight: "700" },
  inviteCard: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    padding: 14,
    backgroundColor: colors.surface,
    borderRadius: 16,
    marginTop: 14,
    borderWidth: 1,
    borderColor: colors.line,
  },
  inviteIcon: {
    width: 42,
    height: 42,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#351323",
  },
  conversationRow: {
    minHeight: 76,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  conversationAvatar: {
    width: 48,
    height: 48,
    borderRadius: 24,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.raised,
  },
  conversationTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginBottom: 5,
  },
  conversationBottom: { flexDirection: "row", alignItems: "center", gap: 8 },
  unreadDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: colors.pink,
  },
  demoNotice: {
    color: colors.muted,
    fontSize: 11,
    lineHeight: 16,
    marginTop: 22,
  },
});
function InboxScreen() {
  const { set, pendingVenueShare } = useApp();
  const [query, setQuery] = useState("");
  const [tab, setTab] = useState<"messages" | "invites">("messages");
  const service = React.useMemo(() => getService(), []);
  const [conversationRecords, setConversationRecords] = useState<ConversationRecord[]>([]);
  const [notifications, setNotifications] = useState<import("./services").NotificationRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [retryKey, setRetryKey] = useState(0);
  const stories = [
    ["You", "#FF2E7A"],
    ["Bela", "#874D8C"],
    ["Chirag", "#365873"],
    ["Maya", "#9A5C47"],
    ["Dev", "#566A44"],
  ];
  useEffect(() => {
    let active = true;
    Promise.all([service.listConversations(), service.listNotifications()])
      .then(([items, notices]) => { if (active) { setConversationRecords(items); setNotifications(notices); } })
      .catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : "Could not load your inbox."); })
      .finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [service, retryKey]);
  const conversations = conversationRecords.map((conversation) => {
    const last = conversation.messages[conversation.messages.length - 1];
    return { id: conversation.id, name: conversation.title, preview: last?.body ?? "No messages yet", time: last?.created_at ? new Date(last.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) : "New", unread: conversation.unread > 0, icon: conversation.kind === "direct" ? "person-outline" as const : "people-outline" as const };
  });
  const visible = conversations.filter(
    (item) =>
      item.name.toLowerCase().includes(query.toLowerCase()) ||
      item.preview.toLowerCase().includes(query.toLowerCase()),
  );
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label="MESSAGES"
        onBack={() => set({ screen: "discover" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={inboxStyles.inboxTitleRow}>
          <View>
            <Text style={styles.eyebrow}>YOUR PEOPLE</Text>
            <Text style={styles.title}>Messages</Text>
          </View>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Open your SHUFFL capsule"
            onPress={() => set({ screen: "feature", featureMode: "capsule" })}
            style={inboxStyles.newMessage}
          >
            <Ionicons name="people-outline" size={22} color={colors.text} />
          </Pressable>
        </View>
        <ScrollView
          horizontal
          showsHorizontalScrollIndicator={false}
          contentContainerStyle={inboxStyles.storyRail}
        >
          {stories.map(([name, color]) => (
            <Pressable
              key={name}
              onPress={() =>
                name === "You"
                  ? set({ screen: "profileHome" })
                  : set({ screen: "feature", featureMode: "visitor" })
              }
              style={inboxStyles.storyItem}
            >
              <View style={[inboxStyles.storyRing, { borderColor: color }]}>
                <View
                  style={[inboxStyles.storyAvatar, { backgroundColor: color }]}
                >
                  <Text style={inboxStyles.storyInitial}>
                    {name === "You" ? "＋" : name[0]}
                  </Text>
                </View>
              </View>
              <Text numberOfLines={1} style={inboxStyles.storyName}>
                {name}
              </Text>
            </Pressable>
          ))}
        </ScrollView>
        <View style={inboxStyles.inboxSearch}>
          <Ionicons name="search" size={18} color={colors.muted} />
          <TextInput
            accessibilityLabel="Search messages"
            placeholder="Search messages"
            placeholderTextColor={colors.muted}
            value={query}
            onChangeText={setQuery}
            style={inboxStyles.inboxSearchText}
          />
        </View>
        <View style={inboxStyles.inboxTabs}>
          <Pressable
            onPress={() => setTab("messages")}
            style={[
              inboxStyles.inboxTab,
              tab === "messages" && inboxStyles.inboxTabActive,
            ]}
          >
            <Text style={inboxStyles.inboxTabText}>Messages</Text>
          </Pressable>
          <Pressable
            onPress={() => setTab("invites")}
            style={[
              inboxStyles.inboxTab,
              tab === "invites" && inboxStyles.inboxTabActive,
            ]}
          >
            <Text style={inboxStyles.inboxTabText}>
              Invites <Text style={{ color: colors.pink }}>1</Text>
            </Text>
          </Pressable>
        </View>
        {pendingVenueShare ? (
          <View style={inboxStyles.inviteCard}>
            <View style={inboxStyles.inviteIcon}>
              <Ionicons name="location" size={20} color={colors.pink} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.routeText}>Share {pendingVenueShare}</Text>
              <Text style={styles.secondaryText}>
                Choose a conversation to preview the share.
              </Text>
            </View>
          </View>
        ) : null}
        {tab === "invites" ? (
          notifications.map((item) => <Pressable key={item.id} onPress={() => { void service.markNotificationRead(item.id); setNotifications((items) => items.map((current) => current.id === item.id ? { ...current, read: true } : current)); set({ screen: "feature", featureMode: item.kind.includes("room") ? "joinRoom" : "notifications" }); }} style={inboxStyles.inviteCard}>
            <View style={inboxStyles.inviteIcon}><Ionicons name="notifications-outline" size={20} color={colors.pink} /></View>
            <View style={{ flex: 1 }}><Text style={styles.routeText}>{item.title}</Text><Text style={styles.secondaryText}>{item.body || "Open to review this update."}</Text><Text style={styles.notice}>{item.read ? "Read" : "Unread"}</Text></View>
            <Ionicons name="chevron-forward" size={18} color={colors.muted} />
          </Pressable>)
        ) : (
          visible.map((item) => (
            <Pressable
              key={item.name}
              onPress={() =>
              set({
                  activeConversation: item.id,
                  screen: "feature",
                  featureMode: "chat",
                })
              }
              style={inboxStyles.conversationRow}
            >
              <View style={inboxStyles.conversationAvatar}>
                <Ionicons name={item.icon} size={21} color={colors.text} />
              </View>
              <View style={{ flex: 1 }}>
                <View style={inboxStyles.conversationTop}>
                  <Text style={styles.routeText}>{item.name}</Text>
                  <Text style={styles.secondaryText}>{item.time}</Text>
                </View>
                <View style={inboxStyles.conversationBottom}>
                  <Text numberOfLines={1} style={styles.secondaryText}>
                    {item.preview}
                  </Text>
                  {item.unread && <View style={inboxStyles.unreadDot} />}
                </View>
              </View>
            </Pressable>
          ))
        )}
        {loading && <Text style={styles.secondaryText}>Loading conversations…</Text>}
        {error ? <><Text accessibilityRole="alert" style={styles.notice}>{error}</Text><FeatureButton label="Retry inbox" onPress={() => { setError(""); setLoading(true); setRetryKey((value) => value + 1); }} secondary /></> : null}
        {tab === "invites" && notifications.filter((item) => !item.read).length === 0 && <Text style={styles.secondaryText}>No unread invites or alerts.</Text>}
        {tab === "messages" && !loading && !visible.length && (
          <Text style={styles.secondaryText}>
            No conversations match that search.
          </Text>
        )}
        <Text style={inboxStyles.demoNotice}>Unread state and messages are synced to your SHUFFL account when the API is connected.</Text>
      </ScrollView>
    </SafeAreaView>
  );
}
function ChatScreen() {
  const { set, activeConversation, pendingVenueShare } = useApp();
  const service = React.useMemo(() => getService(), []);
  const [conversation, setConversation] = useState<ConversationRecord | null>(null);
  const [draft, setDraft] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [sharedVenue, setSharedVenue] = useState("");
  useEffect(() => {
    let active = true;
    service.listConversations().then((items) => {
      const found = items.find((item) => item.id === activeConversation) ?? items.find((item) => item.title === activeConversation) ?? items[0] ?? null;
      if (active) setConversation(found);
      if (found) void service.markConversationRead(found.id);
    }).catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : "Could not load this conversation."); });
    return () => { active = false; };
  }, [activeConversation, service]);
  const sendVenue = () => {
    setSharedVenue(pendingVenueShare);
    set({ pendingVenueShare: "" });
  };
  const sendMessage = async () => {
    if (!conversation || !draft.trim() || busy) return;
    setBusy(true);
    setError("");
    try {
      const message = await service.sendChatMessage(conversation.id, draft.trim());
      setConversation((current) => current ? { ...current, messages: [...current.messages, message] } : current);
      setDraft("");
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not send message.");
    } finally { setBusy(false); }
  };
  return (
    <SafeAreaView style={styles.safe}>
      <FeatureHeader
        label={activeConversation.toUpperCase()}
        onBack={() => set({ screen: "feature", featureMode: "inbox" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.eyebrow}>{conversation?.kind === "group" ? "GROUP CHAT" : "DIRECT MESSAGE"}</Text>
        <Text style={styles.title}>{conversation?.title ?? activeConversation}</Text>
        {conversation?.messages.map((message) => <View key={message.id} style={styles.roomCard}><Text style={styles.eyebrow}>{message.sender_id ?? "SHUFFL MEMBER"}</Text><Text style={styles.routeText}>{message.body}</Text><Text style={styles.secondaryText}>{message.created_at ? new Date(message.created_at).toLocaleTimeString([], { hour: "numeric", minute: "2-digit" }) : ""}</Text></View>)}
        {error ? <Text accessibilityRole="alert" style={styles.notice}>{error}</Text> : null}
        {pendingVenueShare ? (
          <View style={styles.roomCard}>
            <Text style={styles.eyebrow}>VENUE CARD · PREVIEW</Text>
            <Text style={styles.routeText}>{pendingVenueShare}</Text>
            <Text style={styles.secondaryText}>
              Share this place in the conversation.
            </Text>
            <FeatureButton
              label="Send venue card in demo chat"
              onPress={sendVenue}
            />
          </View>
        ) : null}
        {sharedVenue && (
          <View style={styles.roomCard}>
            <Text style={styles.eyebrow}>YOU · LOCAL PREVIEW</Text>
            <Text style={styles.routeText}>{sharedVenue}</Text>
            <Text style={styles.secondaryText}>
              Venue card ready to share in this conversation.
            </Text>
          </View>
        )}
        <View style={{ flexDirection: "row", alignItems: "center", gap: 8 }}><TextInput accessibilityLabel="Message" value={draft} onChangeText={setDraft} placeholder="Write a message" placeholderTextColor={colors.muted} style={[styles.input, { flex: 1, marginBottom: 0 }]} /><FeatureButton label={busy ? "…" : "Send"} onPress={() => void sendMessage()} /></View>
        <FeatureButton
          label="View active plan"
          onPress={() => set({ screen: "feature", featureMode: "activePlan" })}
          secondary
        />
        <Text style={styles.disclaimer}>Messages are scoped to this conversation and saved when the API is connected.</Text>
      </ScrollView>
    </SafeAreaView>
  );
}

function FeatureShell({ children }: { children: React.ReactNode }) {
  const { screen, featureMode, set } = useApp();
  const insets = useSafeAreaInsets();
  const activeChat =
    screen === "feature" &&
    ["inbox", "chat", "notifications"].includes(featureMode);
  return (
    <View style={navigationStyles.shell}>
      {children}
      <View
        style={[
          navigationStyles.bar,
          { height: 78 + insets.bottom, paddingBottom: insets.bottom },
        ]}
      >
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Home"
          onPress={() => set({ screen: "discover" })}
          style={navigationStyles.item}
        >
          <Ionicons name="home-outline" size={23} color={colors.muted} />
          <Text style={navigationStyles.label}>Home</Text>
        </Pressable>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Play"
          onPress={() => set({ screen: "shuffl" })}
          style={navigationStyles.play}
        >
          <Ionicons name="play" size={22} color={colors.bg} />
        </Pressable>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Chat"
          onPress={() => set({ screen: "feature", featureMode: "inbox" })}
          style={navigationStyles.item}
        >
          <Ionicons
            name="chatbubbles-outline"
            size={23}
            color={activeChat ? colors.pink : colors.muted}
          />
          <Text
            style={[
              navigationStyles.label,
              activeChat && { color: colors.pink },
            ]}
          >
            Chat
          </Text>
        </Pressable>
      </View>
    </View>
  );
}

function NotificationsScreen() {
  const { set } = useApp();
  const service = React.useMemo(() => getService(), []);
  const [items, setItems] = useState<import("./services").NotificationRecord[]>([]);
  const [error, setError] = useState("");
  const [retryKey, setRetryKey] = useState(0);
  useEffect(() => { service.listNotifications().then(setItems).catch((cause) => setError(cause instanceof Error ? cause.message : "Could not load notifications.")); }, [service, retryKey]);
  const nextFor = (kind: string) => kind.includes("room") || kind.includes("capsule") || kind.includes("gathering") ? { screen: "feature" as const, featureMode: "gathering" as const } : kind.includes("message") ? { screen: "feature" as const, featureMode: "inbox" as const } : { screen: "feature" as const, featureMode: "activePlan" as const };
  return <FeatureShell><SafeAreaView style={styles.safe}><FeatureHeader label="NOTIFICATIONS" onBack={() => set({ screen: "discover" })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>YOUR NIGHT, IN THE LOOP</Text><Text style={styles.title}>Notifications</Text><Text style={styles.body}>Join requests, room invitations, capsule approvals and plan updates stay visible here.</Text>{error ? <><Text accessibilityRole="alert" style={styles.notice}>{error}</Text><FeatureButton label="Retry notifications" onPress={() => { setError(""); setRetryKey((value) => value + 1); }} secondary /></> : null}{items.map(item => <Pressable key={item.id} accessibilityRole="button" onPress={() => { void service.markNotificationRead(item.id); setItems((current) => current.map((entry) => entry.id === item.id ? { ...entry, read: true } : entry)); set(nextFor(item.kind)); }} style={styles.route}><View style={styles.heroIcon}><Ionicons name={item.read ? "notifications-outline" : "notifications"} size={22} color={item.read ? colors.muted : colors.pink}/></View><View style={{flex:1}}><Text style={styles.routeText}>{item.title}</Text><Text style={styles.secondaryText}>{item.body || "No additional detail."}</Text><Text style={styles.notice}>{item.read ? "Read" : "Unread · tap to open"}</Text></View><Ionicons name="chevron-forward" size={19} color={colors.muted}/></Pressable>)}{!items.length && !error ? <Text style={styles.secondaryText}>No notifications yet.</Text> : null}</ScrollView></SafeAreaView></FeatureShell>;
}

function SupportScreen() {
  const { set } = useApp();
  const [error, setError] = useState("");
  const contact = async () => {
    setError("");
    try {
      await Linking.openURL("mailto:support@shuffl.app?subject=SHUFFL%20MVP%20support");
    } catch {
      setError("Email could not be opened on this device. Please contact the SHUFFL support team.");
    }
  };
  return (
    <FeatureShell>
      <SafeAreaView style={styles.safe}>
        <FeatureHeader label="SUPPORT" onBack={() => set({ screen: "control" })} />
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.eyebrow}>HELP DESK</Text>
          <Text style={styles.title}>We can help you untangle the night.</Text>
          <Text style={styles.body}>Use support for account, venue information, room, safety, or plan issues. Include the screen and venue/room name so the team can act quickly.</Text>
          {[
            ["Venue information", "Report wrong hours, address, photos, website, or tags from the venue page."],
            ["Room or capsule", "Tell us the room title and what happened to the request or approval."],
            ["Safety concern", "Use Report & Block immediately; support can follow up on the review."],
          ].map(([title, body]) => <View key={title} style={styles.route}><View style={{ flex: 1 }}><Text style={styles.routeText}>{title}</Text><Text style={styles.secondaryText}>{body}</Text></View></View>)}
          {error ? <Text accessibilityRole="alert" style={styles.notice}>{error}</Text> : null}
          <FeatureButton label="Email SHUFFL support" onPress={() => void contact()} />
          <FeatureButton label="Open Privacy & Safety" onPress={() => set({ screen: "feature", featureMode: "privacy" })} secondary />
          <FeatureButton label="Report or block" onPress={() => set({ screen: "feature", featureMode: "report" })} secondary />
        </ScrollView>
      </SafeAreaView>
    </FeatureShell>
  );
}

export function FeatureScreen({ mode }: { mode: FeatureMode }) {
  const { set } = useApp();
  if (mode === "gathering") return <GatheringScreen />;
  if (mode === "inbox")
    return (
      <FeatureShell>
        <InboxScreen />
      </FeatureShell>
    );
  if (mode === "notifications") return <NotificationsScreen />;
  if (mode === "support") return <SupportScreen />;
  if (mode === "music") return <MusicScreen />;
  if (mode === "feedback") return <FeedbackScreen />;
  if (mode === "customOuting")
    return (
      <FeatureShell>
        <CustomOutingScreen />
      </FeatureShell>
    );
  if (mode === "venue")
    return (
      <FeatureShell>
        <VenueDetailScreen />
      </FeatureShell>
    );
  if (mode === "privacy")
    return (
      <FeatureShell>
        <PrivacySafetyScreen />
      </FeatureShell>
    );
  if (mode === "arrival")
    return (
      <FeatureShell>
        <ArrivalScreen />
      </FeatureShell>
    );
  if (mode === "hostRoom" || mode === "joinRequests" || mode === "joinRoom" || mode === "capsule")
    return <GatheringScreen />;
  if (mode === "activePlan")
    return (
      <FeatureShell>
        <ActivePlanScreen />
      </FeatureShell>
    );
  if (mode === "chat")
    return (
      <FeatureShell>
        <ChatScreen />
      </FeatureShell>
    );
  if (mode === "report")
    return (
      <FeatureShell>
        <ReportSafetyScreen />
      </FeatureShell>
    );
  const item = content[mode];
  const go = () =>
    item.next
      ? set({ screen: "feature", featureMode: item.next })
      : set({ screen: "profileHome" });
  return (
    <FeatureShell>
      <SafeAreaView style={styles.safe}>
        <View style={styles.header}>
          <Pressable
            onPress={() => set({ screen: "discover" })}
            style={styles.back}
          >
            <Ionicons name="arrow-back" size={22} color={colors.text} />
          </Pressable>
          <Text style={styles.headerLabel}>{item.eyebrow}</Text>
          <Ionicons name={item.icon} size={22} color={colors.mint} />
        </View>
        <ScrollView contentContainerStyle={styles.content}>
          <View style={styles.heroIcon}>
            <Ionicons name={item.icon} size={34} color={colors.mint} />
          </View>
          <Text style={styles.eyebrow}>{item.eyebrow}</Text>
          <Text style={styles.title}>{item.title}</Text>
          <Text style={styles.body}>{item.body}</Text>
          <Pressable onPress={go} style={styles.primary}>
            <Text style={styles.primaryText}>{item.action}</Text>
          </Pressable>
          {mode === "settings" && (
            <View style={styles.routeList}>
              {(Object.keys(content) as FeatureMode[]).filter((route) => !["hostRoom", "joinRequests", "joinRoom", "capsule"].includes(route)).map((route) => (
                <Pressable
                  key={route}
                  onPress={() => set({ screen: "feature", featureMode: route })}
                  style={styles.route}
                >
                  <Text style={styles.routeText}>{content[route].eyebrow}</Text>
                  <Ionicons
                    name="chevron-forward"
                    size={18}
                    color={colors.muted}
                  />
                </Pressable>
              ))}
            </View>
          )}
          <Pressable
            onPress={() => set({ screen: "feature", featureMode: "settings" })}
            style={styles.secondary}
          >
            <Text style={styles.secondaryText}>Open feature hub</Text>
          </Pressable>
        </ScrollView>
      </SafeAreaView>
    </FeatureShell>
  );
}

const feedbackStyles = StyleSheet.create({
  stars: { flexDirection: "row", justifyContent: "space-between", paddingVertical: 26, paddingHorizontal: 8 },
});

const navigationStyles = StyleSheet.create({
  shell: { flex: 1, backgroundColor: colors.bg },
  bar: {
    flexShrink: 0,
    height: 78,
    backgroundColor: "#171714",
    borderTopWidth: 1,
    borderTopColor: colors.line,
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    paddingHorizontal: 28,
  },
  item: {
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    minWidth: 64,
    minHeight: 64,
    paddingVertical: 4,
  },
  label: { color: colors.muted, fontSize: 11, fontWeight: "700" },
  play: {
    width: 58,
    height: 58,
    borderRadius: 29,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.pink,
    marginTop: -21,
    elevation: 8,
  },
});
const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  header: {
    height: 76,
    paddingHorizontal: 20,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  back: {
    width: 44,
    height: 44,
    alignItems: "center",
    justifyContent: "center",
  },
  headerLabel: { color: colors.muted, fontSize: 12, letterSpacing: 1.3 },
  content: { padding: 20, paddingBottom: 112 },
  heroIcon: {
    width: 76,
    height: 76,
    borderRadius: 20,
    backgroundColor: colors.raised,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 24,
  },
  eyebrow: {
    color: colors.mint,
    fontSize: 11,
    letterSpacing: 1.7,
    fontWeight: "800",
    marginBottom: 12,
  },
  title: {
    color: colors.text,
    fontSize: 34,
    lineHeight: 41,
    fontWeight: "700",
    letterSpacing: -0.8,
    marginBottom: 14,
  },
  body: { color: colors.muted, fontSize: 16, lineHeight: 25, marginBottom: 24 },
  primary: {
    minHeight: 56,
    borderRadius: 12,
    backgroundColor: colors.mint,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 8,
  },
  primaryText: { color: colors.bg, fontWeight: "800", fontSize: 15 },
  roomCard: {
    padding: 18,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 20,
    backgroundColor: colors.surface,
    marginBottom: 14,
  },
  requestCard: {
    padding: 16,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 18,
    marginBottom: 12,
  },
  requestActions: {
    flexDirection: "row",
    justifyContent: "flex-end",
    gap: 20,
    marginTop: 8,
  },
  inlineActions: { gap: 10, marginTop: 14 },
  routeList: { marginTop: 18, borderTopWidth: 1, borderTopColor: colors.line },
  route: {
    minHeight: 50,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  fieldLabel: {
    color: colors.mint,
    fontSize: 11,
    letterSpacing: 1.4,
    fontWeight: "800",
    marginTop: 18,
    marginBottom: 8,
  },
  input: {
    minHeight: 50,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.raised,
    paddingHorizontal: 14,
    color: colors.text,
    fontSize: 15,
    marginBottom: 8,
  },
  multiline: { minHeight: 104, paddingTop: 12 },
  reason: {
    minHeight: 48,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 12,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 12,
    marginBottom: 8,
  },
  reasonSelected: { borderColor: colors.mint, backgroundColor: "#292C20" },
  notice: { color: colors.mint, fontSize: 14, lineHeight: 20, marginTop: 16 },
  disclaimer: {
    color: colors.muted,
    fontSize: 12,
    lineHeight: 18,
    marginTop: 16,
  },
  routeText: {
    color: colors.text,
    fontSize: 13,
    fontWeight: "700",
    letterSpacing: 0.5,
  },
  secondary: {
    minHeight: 54,
    borderRadius: 16,
    backgroundColor: colors.raised,
    borderWidth: 1,
    borderColor: colors.line,
    alignItems: "center",
    justifyContent: "center",
    marginTop: 12,
  },
  secondaryText: { color: colors.text, fontWeight: "700", fontSize: 15 },
});
