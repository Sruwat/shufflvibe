import React, {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  Animated,
  Easing,
  Image,
  ImageBackground,
  PanResponder,
  Pressable,
  ScrollView as NativeScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { SafeAreaProvider, SafeAreaView } from "react-native-safe-area-context";
import { Ionicons } from "@expo/vector-icons";
import * as WebBrowser from "expo-web-browser";
import * as Google from "expo-auth-session/providers/google";
import { ResponseType } from "expo-auth-session";
import { colors, radius } from "../src/theme";

import { factorCopy, factors, venues } from "../src/data";
import { Action, vibeName } from "../src/algorithms";
import {
  answerCard,
  answerForcedChoice,
  beginExposure,
  currentCard,
  createAssessment,
  createPreferences,
  deferCard,
  deferPreference,
  PreferenceAction,
  answerPreference,
  backPreference,
  choosePreferenceSense,
  currentPreference,
  resolveAway,
  resumeAssessment,
  isRequiredAnswerExposure,
  backCard,
  latencyFirmness,
  chemistryV2,
} from "../src/fullEngine";
import { hydrateDemoState, useApp } from "../src/store";
import { FeatureScreen } from "../src/featureScreens";
import { getService, RoomRecord } from "../src/services";
import { assertReleaseScope } from "../src/releaseScope";

WebBrowser.maybeCompleteAuthSession();
import {
  dressSenseArtwork,
  homeCityArtwork,
  preferenceArtwork,
  profileBadges,
  profileHeaderArtwork,
  revealArtwork,
  shfflOpeningAnimation,
  shfflWordmark,
  venueArtwork,
  vibeCardArtwork,
  welcomeHeroArtwork,
} from "../src/assets";

type CheckinStyles = { checkinChoice: object };

const ScrollView = (props: React.ComponentProps<typeof NativeScrollView>) => (
  <NativeScrollView
    {...props}
    style={props.horizontal ? props.style : [{ flex: 1 }, props.style]}
  />
);

function Button({
  children,
  onPress,
  kind = "primary",
  disabled = false,
}: {
  children: React.ReactNode;
  onPress: () => void;
  kind?: "primary" | "secondary" | "ghost";
  disabled?: boolean;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      disabled={disabled}
      style={[
        styles.button,
        kind === "secondary" && styles.secondary,
        kind === "ghost" && styles.ghost,
        disabled && { opacity: 0.45 },
      ]}
    >
      <Text
        style={[
          styles.buttonText,
          kind !== "primary" && { color: colors.text },
        ]}
      >
        {children}
      </Text>
    </Pressable>
  );
}
function localDateKey() {
  const date = new Date();
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
}
function commitAssessment(next: ReturnType<typeof createAssessment>) {
  const completed = !currentCard(next);
  const state = useApp.getState();
  const resultName = vibeName(
    next.scores,
    latencyFirmness(next),
    next.chosenTop,
  );
  const shape = chemistryV2([next.scores]);
  const skeleton = {
    stops: shape.stopCount,
    energy: Math.round(next.scores.ENRG ?? 50),
    crowd: Math.round(next.scores.CROWD ?? 50),
    tags: shape.tags,
    stopDurations: shape.stopDurations,
    updatedAt: localDateKey(),
  };
  state.set({
    assessment: next,
    scores: next.scores,
    actions: next.answers,
    assessmentIndex: next.cursor,
    skeleton,
    reuseLastVibe: false,
    ...(completed
      ? {
          screen: "reveal" as const,
          locked: false,
          lastVibeDate: localDateKey(),
          lastVibeName: resultName,
        }
      : {}),
  });
  if (completed) {
    const service = getService();
    void Promise.all([
      service.completeAssessment({
        scores: Object.fromEntries(Object.entries(next.scores).map(([key, value]) => [key, value ?? 50])),
        vibe_name: resultName,
        chosen_top: next.chosenTop,
        latency_firmness: latencyFirmness(next) as Record<string, number>,
        actions: next.answers,
      }),
      service.saveSkeleton({
        scores: Object.fromEntries(Object.entries(next.scores).map(([key, value]) => [key, value ?? 50])),
        stops: skeleton.stops,
        energy: skeleton.energy,
        crowd: skeleton.crowd,
        tags: skeleton.tags,
        stop_durations: skeleton.stopDurations,
      }),
    ]).catch((error) => console.warn("Could not sync assessment shape.", error));
  }
}
function Brand() {
  return (
    <Image source={shfflWordmark} style={styles.brandWordmark} resizeMode="contain" accessibilityLabel="SHFFL" />
  );
}
function OpeningAnimation() {
  return (
    <SafeAreaView style={styles.openingScreen}>
      <Image source={shfflOpeningAnimation} style={styles.openingAnimation} resizeMode="contain" accessibilityLabel="SHFFL opening animation" />
    </SafeAreaView>
  );
}
function resolveRevealArtwork(name: string) {
  if (revealArtwork[name]) return revealArtwork[name];
  const words = name
    .toLowerCase()
    .split(/[^a-z]+/)
    .filter(Boolean);
  const key = Object.keys(revealArtwork).sort((a, b) => {
    const score = (value: string) =>
      value
        .toLowerCase()
        .split(/[^a-z]+/)
        .filter(Boolean)
        .filter((word) => words.includes(word)).length;
    return score(b) - score(a);
  })[0];
  return revealArtwork[key];
}
function resolveVibeArtwork(
  scores: Partial<Record<(typeof factors)[number], number>>,
) {
  const factor = factors.reduce(
    (best, current) =>
      (scores[current] ?? 50) > (scores[best] ?? 50) ? current : best,
    factors[0],
  );
  const map: Record<(typeof factors)[number], keyof typeof vibeCardArtwork> = {
    ENRG: "V-ENRG-A",
    AFFIL: "V-AFFIL-A",
    CROWD: "V-CROWD-A",
    TALK: "V-TALK-A",
    ROAM: "V-ROAM-A",
    MOVE: "V-MOVE-A",
    GAMES: "V-GAMES-A",
  };
  return vibeCardArtwork[map[factor]];
}
function VibeCardArtwork({
  source,
  label,
}: {
  source: import("react-native").ImageSourcePropType;
  label: string;
}) {
  const [loaded, setLoaded] = useState(false);
  const [failed, setFailed] = useState(false);
  return (
    <View style={artworkStyles.swipeGesture}>
      <Image
        source={source}
        style={artworkStyles.cardArtwork}
        accessibilityLabel={label}
        onLoad={() => setLoaded(true)}
        onError={() => {
          setFailed(true);
          setLoaded(true);
        }}
      />
      {!loaded && (
        <View pointerEvents="none" style={artworkStyles.cardArtworkLoading}>
          <View style={artworkStyles.loaderRing} />
          <Text style={artworkStyles.cardArtworkLoadingText}>
            Loading tonight’s scene…
          </Text>
        </View>
      )}
      {failed && (
        <View pointerEvents="none" style={artworkStyles.cardArtworkFallback}>
          <Text style={styles.kicker}>TONIGHT’S SCENE</Text>
          <Text style={styles.cardTitle}>{label}</Text>
        </View>
      )}
    </View>
  );
}
async function selectAvatar(
  onSelected: (uri: string) => void,
  onError: (message: string) => void,
) {
  try {
    const ImagePicker =
      require("expo-image-picker") as typeof import("expo-image-picker");
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      onError("Allow photo access to add an avatar.");
      return;
    }
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ["images"],
      allowsEditing: true,
      aspect: [1, 1],
      quality: 0.85,
    });
    if (!result.canceled && result.assets[0]?.uri)
      onSelected(result.assets[0].uri);
  } catch {
    onError("Avatar picker is not available in this installed build yet.");
  }
}
function Header({ label, onBack }: { label: string; onBack?: () => void }) {
  return (
    <View style={styles.header}>
      {onBack ? (
        <Pressable onPress={onBack} style={styles.iconButton}>
          <Ionicons name="arrow-back" size={22} color={colors.text} />
        </Pressable>
      ) : (
        <Brand />
      )}
      <Text style={styles.headerLabel}>{label}</Text>
      <Pressable
        onPress={() =>
          useApp.getState().set({ screen: "feature", featureMode: "settings" })
        }
        style={styles.iconButton}
      >
        <Ionicons name="options-outline" size={22} color={colors.muted} />
      </Pressable>
    </View>
  );
}
function Nav() {
  const { screen, featureMode, set } = useApp();
  const activeChat =
    screen === "feature" &&
    ["inbox", "chat", "notifications"].includes(featureMode);
  return (
    <View style={styles.nav}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Home"
        hitSlop={4}
        onPress={() => set({ screen: "discover" })}
        style={styles.navItem}
      >
        <Ionicons
          name="home-outline"
          size={23}
          color={screen === "discover" ? colors.pink : colors.muted}
        />
        <Text
          style={[
            styles.navText,
            screen === "discover" && { color: colors.pink },
          ]}
        >
          Home
        </Text>
      </Pressable>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Choose what to do on SHUFFL"
        onPress={() => set({ screen: "playMenu" })}
        style={styles.navPlayItem}
      >
        <View style={artworkStyles.playNav}>
          <Ionicons name="play" size={22} color={colors.bg} />
        </View>
        <Text style={styles.navPlayLabel}>PLAY</Text>
      </Pressable>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Chat"
        hitSlop={4}
        onPress={() => set({ screen: "feature", featureMode: "inbox" })}
        style={styles.navItem}
      >
        <Ionicons
          name="chatbubbles-outline"
          size={23}
          color={activeChat ? colors.pink : colors.muted}
        />
        <Text style={[styles.navText, activeChat && { color: colors.pink }]}>
          Chat
        </Text>
      </Pressable>
    </View>
  );
}
function PlayMenu() {
  const { set, locked } = useApp();
  const gated = (
    screen: "shuffl" | "feature",
    featureMode?: "hostRoom" | "joinRoom",
  ) =>
    set(
      locked
        ? { screen: "dailyCheckin" }
        : screen === "feature"
          ? { screen, featureMode: featureMode! }
          : { screen },
    );
  return (
    <SafeAreaView style={styles.safe}>
      <Header label="Your night" onBack={() => set({ screen: "discover" })} />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>MAKE IT A SHUFFL</Text>
        <Text style={styles.h1}>How are you going out?</Text>
        <Text style={styles.body}>
          Choose a way to find your people or build a plan around tonight’s
          vibe.
        </Text>
        <Pressable
          accessibilityRole="button"
          onPress={() => set({ screen: "dailyCheckin" })}
          style={[artworkStyles.playChoice, { borderColor: colors.pink }]}
        >
          <View style={artworkStyles.playChoiceIcon}>
            <Ionicons name="sparkles" size={24} color={colors.pink} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>
              {locked ? "Set today’s vibe" : "Today’s vibe is ready"}
            </Text>
            <Text style={styles.small}>
              {locked
                ? "Play today or reuse your most recent result."
                : "Review your result or change tonight’s answers."}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={colors.muted} />
        </Pressable>
        <Pressable
          accessibilityRole="button"
          onPress={() => gated("feature", "hostRoom")}
          style={artworkStyles.playChoice}
        >
          <View style={artworkStyles.playChoiceIcon}>
            <Ionicons name="people-outline" size={24} color={colors.pink} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>Host</Text>
            <Text style={styles.small}>
              {locked
                ? "Set today’s vibe before opening a room."
                : "Bring your people together and open a room."}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={colors.muted} />
        </Pressable>
        <Pressable
          accessibilityRole="button"
          onPress={() => gated("feature", "joinRoom")}
          style={artworkStyles.playChoice}
        >
          <View style={artworkStyles.playChoiceIcon}>
            <Ionicons name="compass-outline" size={24} color={colors.pink} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>Join</Text>
            <Text style={styles.small}>
              {locked
                ? "Set today’s vibe to find a matching room."
                : "Find a hosted night that fits your vibe."}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={colors.muted} />
        </Pressable>
        <Pressable
          accessibilityRole="button"
          onPress={() => gated("shuffl")}
          style={artworkStyles.playChoice}
        >
          <View style={artworkStyles.playChoiceIcon}>
            <Ionicons name="map-outline" size={24} color={colors.pink} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>SHUFFL</Text>
            <Text style={styles.small}>
              {locked
                ? "Set today’s vibe to build your Delhi lineup."
                : "Get a personal Delhi lineup for tonight."}
            </Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={colors.muted} />
        </Pressable>
      </ScrollView>
      <Nav />
    </SafeAreaView>
  );
}
function DailyCheckin() {
  const { set, lastVibeName, locked } = useApp();
  const panX = useRef(new Animated.Value(0)).current;
  const reuse = () =>
    set({
      screen: "reveal",
      lastVibeDate: localDateKey(),
      locked: false,
      reuseLastVibe: true,
    });
  const play = () =>
    set({
      screen: "assessment",
      assessmentIndex: 0,
      scores: {},
      actions: {},
      assessment: createAssessment(),
      locked: true,
      reuseLastVibe: false,
    });
  const responder = useMemo(
    () =>
      PanResponder.create({
        onStartShouldSetPanResponder: () => Boolean(lastVibeName),
        onMoveShouldSetPanResponder: (_, gesture) =>
          Boolean(lastVibeName) && Math.abs(gesture.dx) > 8,
        onPanResponderMove: (_, gesture) => panX.setValue(gesture.dx),
        onPanResponderRelease: (_, gesture) => {
          if (gesture.dx > 90) {
            Animated.timing(panX, {
              toValue: 520,
              duration: 180,
              useNativeDriver: true,
            }).start(reuse);
          } else if (gesture.dx < -90) {
            Animated.timing(panX, {
              toValue: -520,
              duration: 180,
              useNativeDriver: true,
            }).start(play);
          } else {
            Animated.spring(panX, {
              toValue: 0,
              useNativeDriver: true,
            }).start();
          }
        },
      }),
    [lastVibeName],
  );
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Your daily vibe"
        onBack={() => set({ screen: "playMenu" })}
      />
      <View style={[styles.content, { flex: 1, justifyContent: "center" }]}>
        <View style={styles.pill}>
          <View style={styles.liveDot} />
          <Text style={styles.pillText}>A NEW NIGHT, YOUR CALL</Text>
        </View>
        <Text style={styles.h1}>
          {lastVibeName
            ? "Do you feel the same right now?"
            : "What feels right today?"}
        </Text>
        <Text style={styles.body}>
          Your answer stays private. Swipe right to reuse your last vibe, or
          left to play a fresh set of cards.
        </Text>
        {lastVibeName && (
          <>
            <Animated.View
              {...responder.panHandlers}
              accessibilityRole="adjustable"
              accessibilityLabel="Swipe right to reuse your last vibe or left to play again"
              style={[styles.surface, { transform: [{ translateX: panX }] }]}
            >
              <Text style={styles.kicker}>YOUR MOST RECENT VIBE</Text>
              <Text style={styles.h2}>{lastVibeName}</Text>
              <Text style={styles.body}>Swipe right if yes. Swipe left if no.</Text>
              <View style={styles.swipeLegend}>
                <Text style={[styles.small, { color: colors.pink }]}>← PLAY AGAIN</Text>
                <Text style={[styles.small, { color: colors.green }]}>REUSE →</Text>
              </View>
            </Animated.View>
            <View style={styles.swipeLegend}>
              <Button kind="secondary" onPress={play}>Play again</Button>
              <Button onPress={reuse}>Reuse vibe</Button>
            </View>
          </>
        )}
        {!lastVibeName && (
          <Button onPress={play}>Play tonight’s swipe game</Button>
        )}
        {lastVibeName && locked && (
          <Text style={[styles.small, { marginTop: 14 }]}>
            Choose one to unlock tonight’s feed.
          </Text>
        )}
      </View>
    </SafeAreaView>
  );
}
function Welcome() {
  const { set } = useApp();
  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.welcomeScreen}>
        <View style={styles.welcomeTop}>
          <Brand />
          <Text style={styles.welcomeStamp}>SHAPE YOUR NIGHT</Text>
        </View>
        <View style={styles.welcomeHeroWrap}>
          <Image
            source={welcomeHeroArtwork}
            style={artworkStyles.welcomeHero}
            accessibilityLabel="Abstract glowing night shape artwork"
          />
          <View pointerEvents="none" style={artworkStyles.welcomeHeroShade} />
          <View pointerEvents="none" style={artworkStyles.welcomeHeroCopy}>
            <Text style={styles.coreText}>your night{"\n"}has a shape</Text>
          </View>
        </View>
        <View style={styles.welcomeCopy}>
          <Text style={styles.kicker}>MAKE PLANS THAT FEEL LIKE YOU</Text>
          <Text style={styles.h1}>Find the room{"\n"}you want to be in.</Text>
          <Text style={styles.body}>
            A daily vibe, a better room, and people who are up for the same kind
            of night.
          </Text>
          <Button onPress={() => set({ screen: "profile" })}>
            Enter SHUFFL
          </Button>
          <Button kind="ghost" onPress={() => set({ screen: "login" })}>
            Sign in
          </Button>
        </View>
      </View>
    </SafeAreaView>
  );
}
function Intro() {
  const { set } = useApp();
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="A little context"
        onBack={() => set({ screen: "welcome" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>BEFORE THE NIGHT</Text>
        <Text style={styles.h2}>First, tell us what matters in a place.</Text>
        <Text style={styles.body}>
          We use this once to make the feed feel like yours. There are no wrong
          answers and you can change these later.
        </Text>
        {["Your preferences", "Your daily vibe", "Your people"].map((x, i) => (
          <View style={styles.feature} key={x}>
            <View style={styles.featureNo}>
              <Text style={styles.featureNoText}>0{i + 1}</Text>
            </View>
            <View>
              <Text style={styles.cardTitle}>{x}</Text>
              <Text style={styles.small}>
                {
                  [
                    "Food, music, polish and the details you notice.",
                    "A quick adaptive swipe game shaped around your night.",
                    "Rooms are approximate and always consent-first.",
                  ][i]
                }
              </Text>
            </View>
          </View>
        ))}
        <Button onPress={() => set({ screen: "login" })}>Continue</Button>
      </ScrollView>
    </SafeAreaView>
  );
}
function Login() {
  const { set } = useApp();
  const [step, setStep] = useState<"identifier" | "password">("identifier");
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const googleClientId = process.env.EXPO_PUBLIC_GOOGLE_WEB_CLIENT_ID?.trim();
  const [googleRequest, googleResponse, promptGoogle] = Google.useAuthRequest({
    webClientId: googleClientId,
    iosClientId: process.env.EXPO_PUBLIC_GOOGLE_IOS_CLIENT_ID?.trim(),
    androidClientId: process.env.EXPO_PUBLIC_GOOGLE_ANDROID_CLIENT_ID?.trim(),
    responseType: ResponseType.IdToken,
    scopes: ["openid", "profile", "email"],
  });
  useEffect(() => {
    const idToken = googleResponse?.type === "success"
      ? googleResponse.params?.id_token
      : undefined;
    if (!idToken || busy) return;
    let active = true;
    setBusy(true);
    setError("");
    getService().loginWithGoogle(idToken)
      .then((session) => { if (active) set({ screen: "profile", userName: session.user.name || "" }); })
      .catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : "Could not sign in with Google."); })
      .finally(() => { if (active) setBusy(false); });
    return () => { active = false; };
  }, [googleResponse]);
  const continueToPassword = () => {
    if (!identifier.trim()) {
      setError("Enter your phone number or email.");
      return;
    }
    setError("");
    setStep("password");
  };
  const verify = async (createAccount = false) => {
    if (password.length < 8) {
      setError("Use a password with at least 8 characters.");
      return;
    }
    setBusy(true);
    setError("");
    try {
      const service = getService();
      const session = createAccount
        ? await service.register(identifier.trim(), password)
        : await service.login(identifier.trim(), password);
      set({ screen: "profile", userName: session.user.name || "" });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : "Could not sign you in.");
    } finally {
      setBusy(false);
    }
  };
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Sign in"
        onBack={() =>
          step === "password" ? setStep("identifier") : set({ screen: "welcome" })
        }
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>
          {step === "password" ? "SECURE SIGN IN" : "WELCOME BACK"}
        </Text>
        <Text style={styles.h2}>
          {step === "password"
            ? "Use your account password."
            : "Find your way back in."}
        </Text>
        <Text style={styles.body}>
          {step === "password"
            ? `Account: ${identifier}`
            : "Use your phone number or email to sign in to SHUFFL."}
        </Text>
        {step === "identifier" ? (
          <>
            <TextInput
              accessibilityLabel="Phone number or email"
              value={identifier}
              onChangeText={setIdentifier}
              placeholder="Phone number or email"
              placeholderTextColor={colors.muted}
              autoCapitalize="none"
              keyboardType="email-address"
              style={artworkStyles.profileInput}
            />
            <Button onPress={continueToPassword}>Continue</Button>
            <Button
              kind="secondary"
              disabled={!googleRequest || busy}
              onPress={() => {
                if (!googleClientId) {
                  setError("Google login is not configured for this build.");
                  return;
                }
                promptGoogle();
              }}
            >
              Continue with Google
            </Button>
          </>
        ) : (
          <>
            <TextInput
              accessibilityLabel="Account password"
              value={password}
              onChangeText={setPassword}
              placeholder="Enter your password"
              placeholderTextColor={colors.muted}
              secureTextEntry
              style={artworkStyles.profileInput}
            />
            <Button onPress={() => void verify()}>{busy ? "Signing in…" : "Sign in"}</Button>
            <Button kind="secondary" onPress={() => void verify(true)}>{busy ? "Please wait…" : "Create account"}</Button>
            <Button kind="ghost" onPress={() => setStep("identifier")}>Change email</Button>
          </>
        )}
        {error ? (
          <Text
            accessibilityRole="alert"
            style={[styles.small, { color: colors.danger, marginTop: 8 }]}
          >
            {error}
          </Text>
        ) : null}
        <Text style={styles.privacy}>
          Your exact location is never shown to another person.
        </Text>
      </ScrollView>
    </SafeAreaView>
  );
}
function ProfileWizard() {
  const { set, userName, userPronouns, userBio, avatarUri } = useApp();
  const [step, setStep] = useState<0 | 1 | 2>(0);
  const [error, setError] = useState("");
  const next = () => {
    if (step === 0 && !userName.trim()) {
      setError("Please enter your name.");
      return;
    }
    setError("");
    if (step < 2) setStep((step + 1) as 1 | 2);
    else set({ screen: "preferenceIntro" });
  };
  const pickAvatar = async () => {
    await selectAvatar((uri) => {
      set({ avatarUri: uri });
      setError("");
    }, setError);
  };
  const initials = (userName || "You")
    .trim()
    .split(/\s+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Set up your profile"
        onBack={() => set({ screen: "welcome" })}
      />
      <View style={styles.stepTrack}>
        <View
          style={[styles.stepFill, { width: `${((step + 1) / 3) * 100}%` }]}
        />
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={artworkStyles.wizardIntro}>
          <Text style={styles.kicker}>WELCOME TO SHUFFL</Text>
          <Text style={styles.h2}>Build a profile that feels like you.</Text>
          <Text style={styles.body}>
            A few quick details help the right rooms recognise you. You can edit
            everything later.
          </Text>
        </View>
        {step === 0 && (
          <>
            <View style={artworkStyles.wizardAvatarRow}>
              <Pressable
                accessibilityRole="button"
                accessibilityLabel="Add profile avatar"
                onPress={pickAvatar}
                style={artworkStyles.wizardAvatar}
              >
                {avatarUri ? (
                  <Image
                    source={{ uri: avatarUri }}
                    style={artworkStyles.wizardAvatarImage}
                  />
                ) : (
                  <>
                    <Text style={artworkStyles.profileAvatarInitials}>
                      {initials}
                    </Text>
                    <View style={artworkStyles.wizardAvatarAdd}>
                      <Ionicons name="camera" size={15} color={colors.bg} />
                    </View>
                  </>
                )}
              </Pressable>
              <View style={{ flex: 1 }}>
                <Text style={styles.cardTitle}>Add your avatar</Text>
                <Text style={styles.small}>
                  Optional, but it makes your profile feel human.
                </Text>
              </View>
            </View>
            <Text style={styles.kicker}>01 · YOUR NAME</Text>
            <Text style={styles.h2}>What should we call you?</Text>
            <Text style={styles.body}>
              Use the name you want people to see in a room.
            </Text>
            <TextInput
              accessibilityLabel="Your name"
              value={userName}
              onChangeText={(value) => set({ userName: value })}
              placeholder="Your first name"
              placeholderTextColor={colors.muted}
              autoFocus
              style={artworkStyles.profileInput}
            />
          </>
        )}
        {step === 1 && (
          <>
            <Text style={styles.h2}>What do you identify as?</Text>
            <Text style={styles.body}>Choose one, or skip this step.</Text>
            <View style={artworkStyles.pronouns}>
              {[
                "He / him",
                "She / her",
                "They / them",
                "Prefer not to say",
              ].map((value) => (
                <Pressable
                  key={value}
                  onPress={() => set({ userPronouns: value })}
                  style={[
                    artworkStyles.pronounChoice,
                    userPronouns === value && artworkStyles.pronounSelected,
                  ]}
                >
                  <Text
                    style={[
                      styles.small,
                      userPronouns === value && { color: colors.text },
                    ]}
                  >
                    {value}
                  </Text>
                </Pressable>
              ))}
            </View>
          </>
        )}
        {step === 2 && (
          <>
            <Text style={styles.h2}>A little more about you</Text>
            <Text style={styles.body}>
              This helps your profile feel like yours. You can skip it.
            </Text>
            <View style={styles.surface}>
              <Text style={styles.cardTitle}>Delhi NCR</Text>
              <Text style={styles.small}>
                Your city is kept private at neighbourhood level.
              </Text>
            </View>
            <TextInput
              accessibilityLabel="Profile bio"
              value={userBio}
              onChangeText={(value) => set({ userBio: value })}
              placeholder="A line about you (optional)"
              placeholderTextColor={colors.muted}
              style={artworkStyles.profileInput}
            />
          </>
        )}
        <Button onPress={next}>
          {step === 2 ? "Continue to preferences" : "Continue"}
        </Button>
        {step > 0 && (
          <Button kind="secondary" onPress={() => setStep((step - 1) as 0 | 1)}>
            Back
          </Button>
        )}
        {error ? (
          <Text
            accessibilityRole="alert"
            style={[styles.small, { color: colors.danger, marginTop: 8 }]}
          >
            {error}
          </Text>
        ) : null}
      </ScrollView>
    </SafeAreaView>
  );
}
function Profile() {
  const {
    set,
    preferences,
    userName,
    userPronouns,
    userBio,
    avatarUri,
    postVibeProfile,
  } = useApp();
  const [nameError, setNameError] = useState("");
  if (!postVibeProfile) return <ProfileWizard />;
  const chosen = Object.entries(preferences.readings)
    .filter(([, reading]) => (reading?.score ?? 0) >= 88)
    .flatMap(([factor]) =>
      factor === "FOOD"
        ? ["Foodie"]
        : factor === "LIVE"
          ? ["Gig-Goer"]
          : factor === "POL"
            ? preferences.sense === "classy"
              ? ["Dressed For It"]
              : preferences.sense === "current"
                ? ["Hype"]
                : []
            : factor === "SCEN"
              ? ["Good Eye"]
              : factor === "NOV"
                ? ["First Timer"]
                : factor === "HERIT"
                  ? ["Old Soul"]
                  : [],
    );
  const preferenceLabels: Record<string, string> = {
    WHOLE_POINT: "The whole point",
    NICE_TO_HAVE: "Nice to have",
    DONT_MIND: "Don’t mind",
    DONT_CARE: "Don’t care",
  };
  const preferenceRows = [
    ["FOOD", "Food"],
    ["LIVE", "Live act"],
    ["POL", "Dressed-up"],
    ["SCEN", "The look"],
    ["NOV", "Somewhere new"],
    ["HERIT", "Somewhere old"],
  ];
  const finish = async () => {
    const current = useApp.getState();
    try {
      await getService().saveProfile({ name: current.userName.trim(), city: "New Delhi", pronouns: current.userPronouns, bio: current.userBio, preferences: Object.fromEntries(Object.entries(current.preferences.readings).map(([key, value]) => [key, value?.score ?? 0])) });
    } catch (cause) {
      setNameError(cause instanceof Error ? cause.message : "Profile could not be saved. Try again.");
      return;
    }
    set({
      screen: "discover",
      locked: false,
      postVibeProfile: false,
      onboardingComplete: true,
      lastVibeDate: localDateKey(),
      lastVibeName: current.reuseLastVibe
        ? current.lastVibeName
        : vibeName(
            current.scores,
            latencyFirmness(current.assessment),
            current.assessment.chosenTop,
          ),
    });
  };
  const pickAvatar = async () => {
    await selectAvatar((uri) => {
      set({ avatarUri: uri });
      setNameError("");
    }, setNameError);
  };
  const initials = (userName || "You")
    .trim()
    .split(/\s+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Your profile"
        onBack={() => set({ screen: postVibeProfile ? "reveal" : "login" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={artworkStyles.profileHero}>
          <Image
            source={profileHeaderArtwork}
            style={artworkStyles.profileHeroImage}
          />
          <View style={artworkStyles.profileHeroOverlay} />
          <View style={artworkStyles.profileHeroTop}>
            <Text style={artworkStyles.profileHeroEyebrow}>
              PROFILE DETAILS
            </Text>
            <View style={artworkStyles.profileHeroStatus}>
              <View style={styles.liveDot} />
              <Text style={artworkStyles.profileHeroStatusText}>
                PRIVATE BY DEFAULT
              </Text>
            </View>
          </View>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Add or change profile avatar"
            onPress={pickAvatar}
            style={artworkStyles.profileAvatarButton}
          >
            {avatarUri ? (
              <Image
                source={{ uri: avatarUri }}
                style={artworkStyles.profileAvatarImage}
              />
            ) : (
              <View style={artworkStyles.profileAvatarFallback}>
                <Text style={artworkStyles.profileAvatarInitials}>
                  {initials}
                </Text>
              </View>
            )}
            <View style={artworkStyles.profileAvatarAdd}>
              <Ionicons name="camera" size={16} color={colors.bg} />
            </View>
          </Pressable>
          <View style={artworkStyles.profileHeroIdentity}>
            <Text style={artworkStyles.profileHeroName}>
              {userName || "Your name"}
            </Text>
            <Text style={artworkStyles.profileHeroMeta}>
              Delhi NCR
              {userPronouns ? ` · ${userPronouns}` : " · pronouns are optional"}
            </Text>
          </View>
        </View>
        <View style={artworkStyles.profileIntroRow}>
          <View>
            <Text style={styles.kicker}>YOUR PROFILE</Text>
            <Text style={styles.h2}>A little more you.</Text>
          </View>
          <Text style={artworkStyles.profileCompletion}>03{`\n`}FIELDS</Text>
        </View>
        <View style={artworkStyles.profileSection}>
          <View style={artworkStyles.profileSectionHeading}>
            <Text style={styles.cardTitle}>Identity</Text>
            <Ionicons name="sparkles-outline" size={19} color={colors.pink} />
          </View>
          <TextInput
            accessibilityLabel="Your name"
            value={userName}
            onChangeText={(userName) => set({ userName })}
            placeholder="Your first name"
            placeholderTextColor={colors.muted}
            style={artworkStyles.profileInput}
            maxLength={40}
          />
          <Text style={styles.small}>This is how you’ll appear in rooms.</Text>
          <View style={artworkStyles.pronouns}>
            {["He / him", "She / her", "They / them", "Prefer not to say"].map(
              (value) => (
                <Pressable
                  key={value}
                  onPress={() => set({ userPronouns: value })}
                  style={[
                    artworkStyles.pronounChoice,
                    userPronouns === value && artworkStyles.pronounSelected,
                  ]}
                >
                  <Text
                    style={[
                      styles.small,
                      userPronouns === value && { color: colors.text },
                    ]}
                  >
                    {value}
                  </Text>
                </Pressable>
              ),
            )}
          </View>
        </View>
        <View style={artworkStyles.profileSection}>
          <View style={artworkStyles.profileSectionHeading}>
            <Text style={styles.cardTitle}>Your intro</Text>
            <Text style={artworkStyles.optional}>OPTIONAL</Text>
          </View>
          <TextInput
            accessibilityLabel="Profile bio"
            value={userBio}
            onChangeText={(userBio) => set({ userBio })}
            placeholder="One line that feels like you"
            placeholderTextColor={colors.muted}
            style={artworkStyles.profileInput}
            maxLength={120}
          />
          <Text style={styles.small}>{userBio.length}/120 characters</Text>
        </View>
        <View style={artworkStyles.profileSection}>
          <View style={artworkStyles.profileSectionHeading}>
            <Text style={styles.cardTitle}>Your signals</Text>
            <Text style={artworkStyles.optional}>FROM YOUR VIBE</Text>
          </View>
          {chosen.length > 0 ? (
            <View style={artworkStyles.badges}>
              {chosen.map(
                (tag) =>
                  profileBadges[tag] && (
                    <View key={tag} style={artworkStyles.badgeWrap}>
                      <Image
                        source={profileBadges[tag]}
                        style={artworkStyles.badgeImage}
                        accessibilityLabel={tag}
                      />
                      <Text style={artworkStyles.badgeLabel}>{tag}</Text>
                    </View>
                  ),
              )}
            </View>
          ) : (
            <Text style={styles.small}>
              Play your preference game to unlock personal signals.
            </Text>
          )}
        </View>
        {(preferences.stage === "done" || postVibeProfile) && (
          <View style={styles.surface}>
            <Text style={styles.cardTitle}>What I care about in a place</Text>
            {preferenceRows.map(([factor, label]) => {
              const answer = preferences.answers[`P-${factor}`];
              return (
                <View key={factor} style={styles.menu}>
                  <Text style={styles.small}>{label}</Text>
                  <Text style={styles.small}>
                    {answer ? preferenceLabels[answer] : "Not set"}
                  </Text>
                </View>
              );
            })}
            {preferences.sense && (
              <Text style={styles.small}>
                Dressed-up, to me · {preferences.sense}
              </Text>
            )}
            {preferences.stage === "done" && (
              <Button
                kind="secondary"
                onPress={() =>
                  set({
                    screen: "preferences",
                    preferences: createPreferences(),
                  })
                }
              >
                Redo my preferences
              </Button>
            )}
          </View>
        )}
        {postVibeProfile ? (
          <>
            <Button onPress={finish}>Save profile</Button>
            <Button kind="ghost" onPress={finish}>
              Skip for now
            </Button>
          </>
        ) : (
          <>
            <Button
              onPress={() => {
                if (!userName.trim()) {
                  setNameError("Please enter your name.");
                  return;
                }
                setNameError("");
                set({
                  screen:
                    preferences.stage === "done"
                      ? "instructions"
                      : "preferenceIntro",
                });
              }}
            >
              {preferences.stage === "done" ? "Set today’s vibe" : "Continue"}
            </Button>
            {nameError ? (
              <Text
                accessibilityRole="alert"
                style={[styles.small, { color: colors.danger, marginTop: 8 }]}
              >
                {nameError}
              </Text>
            ) : null}
          </>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
function PreferenceIntro() {
  const { set } = useApp();
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Your preferences"
        onBack={() => set({ screen: "profile" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>BEFORE THE NIGHT</Text>
        <Text style={styles.h2}>
          First, the things you care about in a place.
        </Text>
        <Text style={styles.body}>
          Swipe on the following things on the basis of how important they are
          to you in a place.
        </Text>
        <Button onPress={() => set({ screen: "preferences" })}>Let’s go</Button>
      </ScrollView>
    </SafeAreaView>
  );
}
function PreferenceSwipeCard({
  card,
  preferences,
  set,
}: {
  card: any;
  preferences: any;
  set: any;
}) {
  const panX = useRef(new Animated.Value(0)).current;
  const panY = useRef(new Animated.Value(0)).current;
  const [swipeFeedback, setSwipeFeedback] = useState("");
  const [artworkFailed, setArtworkFailed] = useState(false);
  const choose = (action: PreferenceAction) =>
    set({ preferences: answerPreference(preferences, action) });
  const chooseRef = useRef(choose);
  chooseRef.current = choose;
  const responder = useMemo(
    () =>
      PanResponder.create({
        onStartShouldSetPanResponder: () => true,
        onMoveShouldSetPanResponder: (_, g) =>
          Math.abs(g.dx) + Math.abs(g.dy) > 6,
        onPanResponderMove: (_, g) => {
          panX.setValue(g.dx);
          panY.setValue(g.dy);
        },
        onPanResponderRelease: (_, g) => {
          const distance = Math.max(Math.abs(g.dx), Math.abs(g.dy));
          if (distance < 90) {
            Animated.parallel([
              Animated.spring(panX, { toValue: 0, useNativeDriver: true }),
              Animated.spring(panY, { toValue: 0, useNativeDriver: true }),
            ]).start();
            setSwipeFeedback("");
            return;
          }
          const horizontal = Math.abs(g.dx) >= Math.abs(g.dy);
          const action: PreferenceAction = horizontal
            ? g.dx >= 0
              ? "NICE_TO_HAVE"
              : "DONT_MIND"
            : g.dy < 0
              ? "WHOLE_POINT"
              : "DONT_CARE";
          const label =
            action === "NICE_TO_HAVE"
              ? "NICE TO HAVE"
              : action === "DONT_MIND"
                ? "DON’T MIND"
                : action === "WHOLE_POINT"
                  ? "THE WHOLE POINT"
                  : "DON’T CARE";
          const dirX = horizontal ? (g.dx >= 0 ? 1 : -1) : 0;
          const dirY = horizontal ? 0 : g.dy < 0 ? -1 : 1;
          setSwipeFeedback(label);
          Animated.parallel([
            Animated.timing(panX, {
              toValue: dirX * 520,
              duration: 220,
              useNativeDriver: true,
            }),
            Animated.timing(panY, {
              toValue: dirY * 520,
              duration: 220,
              useNativeDriver: true,
            }),
          ]).start(() => {
            chooseRef.current(action);
            panX.setValue(0);
            panY.setValue(0);
            setSwipeFeedback("");
          });
        },
      }),
    [],
  );
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Your preferences"
        onBack={() => set({ screen: "profile" })}
      />
      <View style={styles.progress}>
        <View style={styles.progressTrack}>
          <View
            style={[
              styles.progressFill,
              {
                width: `${Math.max(8, (preferences.cursor / preferences.queue.length) * 100)}%`,
              },
            ]}
          />
        </View>
      </View>
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>THE THINGS YOU CARE ABOUT</Text>
        <Text style={styles.h2}>How much does this matter in a place?</Text>
        <Animated.View
          {...responder.panHandlers}
          style={[
            artworkStyles.preferenceSwipeCard,
            {
              transform: [{ translateX: panX }, { translateY: panY }],
              opacity: panX.interpolate({
                inputRange: [-520, 0, 520],
                outputRange: [0.5, 1, 0.5],
              }),
            },
          ]}
        >
          {artworkFailed ? (
            <View style={artworkStyles.preferenceImageFallback}>
              <Ionicons name="images-outline" size={42} color={colors.amber} />
              <Text style={artworkStyles.preferenceImageFallbackTitle}>{card.title}</Text>
              <Text style={artworkStyles.preferenceImageFallbackCopy}>Swipe to place this signal on your night.</Text>
            </View>
          ) : (
            <Image
              source={preferenceArtwork[card.id]}
              style={artworkStyles.preferenceImage}
              resizeMode="cover"
              onError={() => setArtworkFailed(true)}
              accessibilityLabel={card.title}
            />
          )}
          {swipeFeedback ? (
            <View
              pointerEvents="none"
              style={artworkStyles.preferenceSwipeFeedback}
            >
              <Text style={artworkStyles.preferenceSwipeFeedbackText}>
                {swipeFeedback}
              </Text>
            </View>
          ) : null}
        </Animated.View>
        <Text style={styles.cardTitle}>{card.title}</Text>
        <Text style={styles.body}>{card.subtitle}</Text>
        <Text style={styles.swipeHint}>Swipe left, right, up or down</Text>
        <View style={styles.swipes}>
          {(
            [
              ["WHOLE_POINT", "THE WHOLE POINT", "arrow-up", colors.amber],
              ["NICE_TO_HAVE", "NICE TO HAVE", "arrow-forward", colors.green],
              ["DONT_MIND", "DON’T MIND", "arrow-back", colors.muted],
              ["DONT_CARE", "DON’T CARE", "arrow-down", colors.danger],
            ] as const
          ).map(([action, label, icon, color]) => (
            <Pressable
              key={action}
              onPress={() => choose(action)}
              style={styles.swipe}
            >
              <View style={[styles.swipeIcon, { borderColor: color }]}>
                <Ionicons name={icon as any} size={20} color={color} />
              </View>
              <Text style={styles.swipeLabel}>{label}</Text>
            </Pressable>
          ))}
        </View>
        <View style={styles.swipeLegend}>
          <Button
            kind="secondary"
            onPress={() => set({ preferences: backPreference(preferences) })}
          >
            Back
          </Button>
          <Button
            kind="secondary"
            onPress={() => set({ preferences: deferPreference(preferences) })}
          >
            Next
          </Button>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
function Preferences() {
  const { set, preferences } = useApp();
  const card = currentPreference(preferences);
  const [selectedSense, setSelectedSense] = useState<
    "classy" | "current" | "both" | ""
  >(preferences.sense ?? "");
  if (preferences.stage === "sense")
    return (
      <SafeAreaView style={styles.safe}>
        <Header
          label="Your preferences"
          onBack={() => set({ screen: "profile" })}
        />
        <ScrollView contentContainerStyle={styles.content}>
          <Text style={styles.kicker}>ONE DETAIL</Text>
          <Text style={styles.h2}>Which of these is dressed-up, to you?</Text>
          <Text style={styles.body}>
            There is no right answer. Choose the room that feels like dressed-up
            to you.
          </Text>
          {[
            ["classy", "Suits and dresses"],
            ["current", "Streetwear and polish"],
          ].map(([sense, label]) => (
            <Pressable
              key={sense}
              style={[
                artworkStyles.senseOption,
                selectedSense === sense && artworkStyles.senseSelected,
              ]}
              onPress={() => setSelectedSense(sense as "classy" | "current")}
            >
              <Image
                source={
                  dressSenseArtwork[sense as keyof typeof dressSenseArtwork]
                }
                style={artworkStyles.senseImage}
              />
              <Text style={[styles.cardTitle, artworkStyles.senseLabel]}>
                {label}
              </Text>
              {selectedSense === sense ? (
                <Ionicons
                  name="checkmark-circle"
                  size={24}
                  color={colors.pink}
                  style={artworkStyles.senseCheck}
                />
              ) : null}
            </Pressable>
          ))}
          <Pressable
            style={[
              artworkStyles.senseBoth,
              selectedSense === "both" && artworkStyles.senseSelected,
            ]}
            onPress={() => setSelectedSense("both")}
          >
            <Text style={styles.cardTitle}>Both</Text>
            {selectedSense === "both" ? (
              <Ionicons name="checkmark-circle" size={24} color={colors.pink} />
            ) : null}
          </Pressable>
          <Button
            onPress={() =>
              selectedSense
                ? set({
                    preferences: choosePreferenceSense(
                      preferences,
                      selectedSense,
                    ),
                  })
                : undefined
            }
            kind={selectedSense ? "primary" : "secondary"}
          >
            Continue
          </Button>
        </ScrollView>
      </SafeAreaView>
    );
  if (!card)
    return (
      <SafeAreaView style={styles.safe}>
        <Header label="Preferences saved" />
        <View style={styles.content}>
          <Text style={styles.kicker}>YOUR PLACE, YOUR WAY</Text>
          <Text style={styles.h2}>That’s your baseline.</Text>
          <Text style={styles.body}>
            These preferences stay with your profile until you choose to edit
            them.
          </Text>
          <Button onPress={() => set({ screen: "instructions" })}>
            Continue to tonight
          </Button>
        </View>
      </SafeAreaView>
    );
  return (
    <PreferenceSwipeCard card={card} preferences={preferences} set={set} />
  );
}
function Instructions() {
  const { set } = useApp();
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Tonight’s vibe"
        onBack={() => set({ screen: "profile" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.pill}>
          <View style={styles.liveDot} />
          <Text style={styles.pillText}>YOUR DAILY VIBE</Text>
        </View>
        <Text style={styles.h2}>Swipe how you feel about tonight.</Text>
        <Text style={styles.body}>
          Gut call — first reaction wins. Not sure? Hit Next and it comes back
          later.
        </Text>
        <View style={styles.swipeLegend}>
          {[
            ["arrow-up", "LOVE", colors.amber],
            ["arrow-forward", "UP FOR IT", colors.green],
            ["arrow-back", "NOT FOR ME", colors.muted],
            ["arrow-down", "HARD PASS", colors.danger],
          ].map(([icon, label, color]) => (
            <View style={styles.legend} key={label as string}>
              <Ionicons name={icon as any} size={18} color={color as string} />
              <Text style={styles.small}>{label}</Text>
            </View>
          ))}
        </View>
        <Button
          onPress={() =>
            set({
              screen: "assessment",
              assessmentIndex: 0,
              scores: {},
              actions: {},
              assessment: createAssessment(),
            })
          }
        >
          Let’s go
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
}
function Reveal() {
  const {
    set,
    scores,
    assessment,
    onboardingComplete,
    lastVibeName,
    reuseLastVibe,
    preferences,
  } = useApp();
  const name =
    reuseLastVibe && lastVibeName
      ? lastVibeName
      : vibeName(scores, latencyFirmness(assessment), assessment.chosenTop);
  const artwork = resolveRevealArtwork(name);
  const revealBadges = [
    (preferences.readings.FOOD?.score ?? 0) >= 70 ? "Foodie" : null,
    (preferences.readings.LIVE?.score ?? 0) >= 70 ? "Gig-Goer" : null,
    (preferences.readings.POL?.score ?? 0) >= 70 ? "Dressed For It" : null,
    (scores.ENRG ?? 0) >= 70 || (scores.CROWD ?? 0) >= 70 ? "Hype" : null,
    (preferences.readings.SCEN?.score ?? 0) >= 70 ? "Good Eye" : null,
    (preferences.readings.NOV?.score ?? 0) >= 70 ? "First Timer" : null,
    (preferences.readings.HERIT?.score ?? 0) >= 70 ? "Old Soul" : null,
  ].filter((badge): badge is string => Boolean(badge)).slice(0, 4);
  const opacity = useRef(new Animated.Value(0)).current;
  const translateY = useRef(new Animated.Value(18)).current;
  useEffect(() => {
    Animated.parallel([
      Animated.timing(opacity, {
        toValue: 1,
        duration: 700,
        useNativeDriver: true,
      }),
      Animated.timing(translateY, {
        toValue: 0,
        duration: 700,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();
  }, [name]);
  const finish = () =>
    set({
      screen: "discover",
      locked: false,
      onboardingComplete: true,
      lastVibeDate: localDateKey(),
      lastVibeName: name,
      reuseLastVibe: false,
    });
  return (
    <SafeAreaView style={styles.safe}>
      <Header label="Your result" />
      <ScrollView contentContainerStyle={styles.content}>
        <Animated.View style={{ opacity, transform: [{ translateY }] }}>
          <Text style={styles.kicker}>YOUR VIBE TODAY IS</Text>
          {artwork ? (
            <Animated.Image
              source={artwork}
              style={artworkStyles.revealArtwork}
              accessibilityLabel={`${name} vibe artwork`}
            />
          ) : (
            <View style={artworkStyles.revealPoster}>
              <Text style={styles.kicker}>TONIGHT’S LINE-UP</Text>
              <Text style={artworkStyles.posterTitle}>
                {name.toUpperCase()}
              </Text>
            </View>
          )}
          <Text style={styles.h1}>{name}</Text>
          <Text style={styles.body}>
            A room that meets your energy without making you explain it.
          </Text>
          <View style={styles.revealCard}>
            <Text style={styles.revealEyebrow}>BUILT FROM YOUR SWIPES</Text>
            <View style={styles.scoreRow}>
              {factors.map((f) => (
                <View key={f} style={styles.score}>
                  <Text style={styles.scoreValue}>
                    {Math.round(scores[f] ?? 50)}
                  </Text>
                  <Text style={styles.scoreName}>{f}</Text>
                </View>
              ))}
            </View>
          </View>
          {revealBadges.length > 0 ? <View style={styles.revealCard}><Text style={styles.revealEyebrow}>YOUR PROFILE SIGNALS</Text><View style={artworkStyles.badges}>{revealBadges.map((badge) => <View key={badge} style={artworkStyles.badgeWrap}><Image source={profileBadges[badge]} style={artworkStyles.badgeImage} accessibilityLabel={badge}/><Text style={artworkStyles.badgeLabel}>{badge}</Text></View>)}</View></View> : null}
        </Animated.View>
        <Button
          onPress={() =>
            onboardingComplete
              ? finish()
              : set({ screen: "profile", postVibeProfile: true })
          }
        >
          {onboardingComplete ? "Enter SHUFFL" : "Continue"}
        </Button>
        <Button kind="secondary" onPress={finish}>
          Skip for now
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
}
function Discover() {
  const { set, locked, scores, assessment, userName, skeleton } = useApp();
  const todayName = vibeName(
    scores,
    latencyFirmness(assessment),
    assessment.chosenTop,
  );
  const shape = skeleton.updatedAt ? { tags: skeleton.tags, stopCount: skeleton.stops } : chemistryV2([scores]);
  const vibeImage = resolveVibeArtwork(scores);
  return (
    <SafeAreaView style={styles.safe}>
      <Header label="Explore" />
      <ScrollView contentContainerStyle={styles.homeContent}>
        <View style={styles.homeTop}>
          <View>
            <Text style={styles.kicker}>DELHI NCR · TONIGHT</Text>
            <Text style={styles.homeTitle}>A night that fits.</Text>
          </View>
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Search people, places and rooms"
            onPress={() => set({ screen: "search" })}
            style={styles.iconButton}
          >
            <Ionicons name="search" size={22} color={colors.text} />
          </Pressable>
        </View>
        <Pressable
          onPress={() => set({ screen: "profileHome" })}
          style={artworkStyles.homeProfilePill}
        >
          <View style={styles.liveDot} />
          <Text style={artworkStyles.profilePillText}>
            {userName || "Your profile"}
            {locked ? " · vibe not set" : ` · ${todayName}`}
          </Text>
          <Ionicons name="chevron-forward" size={17} color={colors.muted} />
        </Pressable>
        {locked && (
          <View style={artworkStyles.homeLocked}>
            <Ionicons
              name="lock-closed-outline"
              size={27}
              color={colors.pink}
            />
            <Text style={styles.cardTitle}>
              Your night is still taking shape.
            </Text>
            <Text style={styles.small}>
              Play today’s swipe game to unlock your recommendations.
            </Text>
            <Button onPress={() => set({ screen: "instructions" })}>
              Play today’s vibe
            </Button>
          </View>
        )}
        {!locked && (
          <>
            <View style={artworkStyles.homeVibeHero}>
              <Image source={vibeImage} style={artworkStyles.homeVibeImage} />
              <View style={artworkStyles.homeVibeShade} />
              <View style={artworkStyles.homeVibeCopy}>
                <Text style={artworkStyles.homeEyebrow}>TONIGHT’S SHAPE</Text>
                <Text style={artworkStyles.homeVibeName}>{todayName}</Text>
                <Text style={artworkStyles.homeVibeMeta}>
                  {shape.tags[0] ?? "In Sync"} · {shape.stopCount}{" "}
                  {shape.stopCount === 1 ? "stop" : "stops"}
                </Text>
              </View>
              <Ionicons
                name="sparkles"
                size={25}
                color={colors.pink}
                style={artworkStyles.homeVibeSpark}
              />
            </View>
            <View style={artworkStyles.homeSectionHeader}>
              <View>
                <Text style={styles.sectionTitle}>
                  What’s on your wavelength
                </Text>
                <Text style={artworkStyles.shelfSubhead}>
                  Places matched to your profile
                </Text>
              </View>
              <Text style={artworkStyles.homeShelfLabel}>MATCHED FOR YOU</Text>
            </View>
            <ScrollView
              horizontal
              showsHorizontalScrollIndicator={false}
              contentContainerStyle={artworkStyles.venueShelf}
            >
              {venues.map((venue, index) => (
                <Pressable
                  key={venue.name}
                  onPress={() =>
                    set({
                      screen: "feature",
                      featureMode: "venue",
                      selectedVenueName: venue.name,
                    })
                  }
                  style={artworkStyles.homeVenueCard}
                >
                  <Image
                    source={venueArtwork[venue.name]}
                    style={artworkStyles.homeVenueImage}
                  />
                  <View style={artworkStyles.homeVenueShade} />
                  <View style={artworkStyles.homeVenueContent}>
                    <View style={artworkStyles.homeVenueTop}>
                      <Text style={artworkStyles.homeVenueArea}>
                        {venue.area.toUpperCase()}
                      </Text>
                      <Text
                        style={[
                          artworkStyles.homeVenueMatch,
                          {
                            color: [
                              colors.mint,
                              colors.cyan,
                              colors.pink,
                              colors.amber,
                            ][index],
                          },
                        ]}
                      >
                        {80 - index * 4}% MATCH
                      </Text>
                    </View>
                    <View>
                      <Text style={artworkStyles.homeVenueName}>
                        {venue.name.toUpperCase()}
                      </Text>
                      <Text style={artworkStyles.homeVenueMeta}>
                        {venue.type} · {venue.tag}
                      </Text>
                      <View style={artworkStyles.homeVenueAction}>
                        <Text style={artworkStyles.venueFooterText}>
                          VIEW PLACE
                        </Text>
                        <Ionicons
                          name="arrow-forward"
                          size={18}
                          color={colors.pink}
                        />
                      </View>
                    </View>
                  </View>
                </Pressable>
              ))}
            </ScrollView>
            <View style={artworkStyles.homeCityHeader}>
              <View>
                <Text style={styles.sectionTitle}>Around the city</Text>
                <Text style={artworkStyles.shelfSubhead}>
                  A live neighbourhood view, kept approximate
                </Text>
              </View>
              <Ionicons name="navigate-outline" size={21} color={colors.pink} />
            </View>
            <View style={artworkStyles.homeCityCard}>
              <View style={styles.mapPulse} />
              <View style={artworkStyles.cityPin}>
                <Ionicons name="location" size={22} color={colors.bg} />
              </View>
              <Text style={artworkStyles.cityTitle}>
                New Delhi is moving tonight.
              </Text>
              <Text style={styles.small}>
                Recommendations are based on your vibe, preferences and
                neighbourhood-level venue data.
              </Text>
              <Button
                kind="secondary"
                onPress={() => set({ screen: "search" })}
              >
                Explore places
              </Button>
            </View>
          </>
        )}
      </ScrollView>
      <Nav />
    </SafeAreaView>
  );
}
function HomeDashboard() {
  const { set, locked, scores, assessment, userName, userPronouns, avatarUri, lastVibeName, plan, skeleton } = useApp();
  const [venueFeed, setVenueFeed] = useState(venues);
  const [hostedRooms, setHostedRooms] = useState<RoomRecord[]>([]);
  useEffect(() => {
    let alive = true;
    getService().getDiscovery().then((items) => {
      if (alive && items.length) setVenueFeed(items);
    }).catch(() => undefined);
    return () => { alive = false; };
  }, []);
  useEffect(() => {
    let alive = true;
    getService().listHostedRooms().then((items) => {
      if (alive) setHostedRooms(items.filter((item) => item.status === 'hosted'));
    }).catch(() => {
      if (alive) setHostedRooms([]);
    });
    return () => { alive = false; };
  }, []);
  const todayName = vibeName(scores, latencyFirmness(assessment), assessment.chosenTop);
  const currentName = lastVibeName || todayName;
  const shape = skeleton.updatedAt ? { tags: skeleton.tags, stopCount: skeleton.stops } : chemistryV2([scores]);
  const vibeImage = resolveVibeArtwork(scores);
  const gated = () => set({ screen: lastVibeName ? 'dailyCheckin' : 'instructions' });
  const openVibe = () => locked ? gated() : set({ screen: 'reveal' });
  const initials = (userName || 'You').trim().split(/\s+/).map(part => part[0]).join('').slice(0, 2).toUpperCase();
  const recommendation = (venue: typeof venues[number], index: number) => <Pressable key={venue.name} accessibilityRole="button" accessibilityLabel={`Open ${venue.name} venue detail`} onPress={() => set({ screen: 'feature', featureMode: 'venue', selectedVenueName: venue.name })} style={artworkStyles.homeVenueCard}>
    <Image source={venueArtwork[venue.name] ?? homeCityArtwork} style={artworkStyles.homeVenueImage} accessibilityLabel={`${venue.name} artwork`} />
    <View style={artworkStyles.homeVenueShade} />
    <View style={artworkStyles.homeVenueContent}>
      <View style={artworkStyles.homeVenueTop}><Text style={artworkStyles.homeVenueArea}>{venue.area.toUpperCase()}</Text><Text style={[artworkStyles.homeVenueMatch, { color: [colors.mint, colors.cyan, colors.pink, colors.amber][index] }]}>{92 - index * 5}% MATCH</Text></View>
      <View><Text style={artworkStyles.homeVenueName}>{venue.name.toUpperCase()}</Text><Text style={artworkStyles.homeVenueMeta}>{venue.type} · {venue.tag}</Text><Text style={styles.small}>{index === 0 ? 'Good energy, still easy to talk' : index === 1 ? 'Space to roam and reset' : 'A room that knows the next song'}</Text><View style={artworkStyles.homeVenueAction}><Text style={artworkStyles.venueFooterText}>VIEW PLACE</Text><Ionicons name="arrow-forward" size={18} color={colors.pink} /></View></View>
    </View>
  </Pressable>;
  return <SafeAreaView style={styles.safe}>
    <View style={artworkStyles.dashboardHeader}>
      <Brand />
      <View style={artworkStyles.dashboardHeaderActions}>
        <Pressable accessibilityRole="button" accessibilityLabel="Search venues, rooms and activities" onPress={() => set({ screen: 'search' })} style={styles.iconButton}><Ionicons name="search" size={21} color={colors.text} /></Pressable>
        <Pressable accessibilityRole="button" accessibilityLabel="Open notifications" onPress={() => set({ screen: 'feature', featureMode: 'notifications' })} style={styles.iconButton}><Ionicons name="notifications-outline" size={21} color={colors.text} /></Pressable>
        <Pressable accessibilityRole="button" accessibilityLabel="Open profile" onPress={() => set({ screen: 'profileHome' })} style={artworkStyles.dashboardAvatar}>{avatarUri ? <Image source={{ uri: avatarUri }} style={artworkStyles.dashboardAvatarImage} /> : <Text style={artworkStyles.dashboardAvatarText}>{initials}</Text>}</Pressable>
      </View>
    </View>
    <ScrollView contentContainerStyle={styles.homeContent}>
      <Text style={styles.kicker}>TONIGHT · DELHI NCR</Text>
      <Text style={styles.homeTitle}>A night that fits.</Text>
      <Pressable accessibilityRole="button" accessibilityLabel="Open profile shortcut" onPress={() => set({ screen: 'profileHome' })} style={artworkStyles.homeProfilePill}><View style={styles.liveDot} /><Text style={artworkStyles.profilePillText}>{userName || 'Your profile'}{userPronouns ? ` · ${userPronouns}` : ''}</Text><Ionicons name="chevron-forward" size={17} color={colors.muted} /></Pressable>
      <Pressable accessibilityRole="button" accessibilityLabel="View today’s vibe" onPress={openVibe} style={artworkStyles.dashboardVibeHero}>
        <Image source={vibeImage} style={artworkStyles.dashboardVibeImage} accessibilityLabel={`${currentName} artwork`} /><View style={artworkStyles.dashboardVibeShade} />
        <View style={artworkStyles.dashboardVibeCopy}><Text style={artworkStyles.homeEyebrow}>{locked ? 'YOUR NEXT MOVE' : 'TONIGHT’S SHAPE'}</Text><Text style={artworkStyles.homeVibeName}>{locked ? (lastVibeName ? `MOST RECENT · ${lastVibeName}` : 'YOUR VIBE IS WAITING') : currentName}</Text><Text style={styles.small}>{locked ? 'Play the swipe game and get your vibe for the day to unlock this feature.' : `You’re looking for ${shape.tags[0]?.toLowerCase() ?? 'a room that feels alive'} tonight.`}</Text></View><Ionicons name={locked ? 'lock-closed-outline' : 'sparkles'} size={24} color={colors.pink} style={artworkStyles.homeVibeSpark} />
      </Pressable>
      {locked ? <View style={artworkStyles.dashboardLocked}><Text style={styles.cardTitle}>Tonight’s picks are locked</Text><Text style={styles.small}>Play the swipe game and get your vibe for the day to unlock this feature.</Text><Button onPress={gated}>Play today</Button></View> : <>
        <View style={artworkStyles.homeSectionHeader}><View><Text style={styles.sectionTitle}>TONIGHT’S PICKS</Text><Text style={artworkStyles.shelfSubhead}>Picked for your vibe</Text></View><Pressable accessibilityRole="button" onPress={() => set({ screen: 'search' })}><Text style={artworkStyles.homeShelfLabel}>SEE ALL</Text></Pressable></View>
        <ScrollView horizontal showsHorizontalScrollIndicator={false} contentContainerStyle={artworkStyles.venueShelf}>{venueFeed.map(recommendation)}</ScrollView>
        <View style={artworkStyles.dashboardSectionHeader}><View><Text style={styles.sectionTitle}>TONIGHT’S LINE-UP</Text><Text style={artworkStyles.shelfSubhead}>Built around your vibe</Text></View><Ionicons name="map-outline" size={20} color={colors.pink} /></View>
        {plan.exists ? <><Pressable accessibilityRole="button" onPress={() => set({ screen: 'feature', featureMode: plan.locked ? 'activePlan' : 'customOuting' })} style={artworkStyles.dashboardPlanCard}><View style={artworkStyles.dashboardPlanTop}><Text style={styles.cardTitle}>{plan.title || plan.style}</Text><Text style={artworkStyles.homeShelfLabel}>{plan.locked ? 'LOCKED' : 'DRAFT'}</Text></View>{plan.stops.slice(0, 2).map((stop, index) => <Text key={`${stop}-${index}`} style={styles.small}>{index + 1}. {stop}</Text>)}<Text style={styles.small}>{plan.durationHours} hours · Delhi NCR · {plan.locked ? 'Tap to view active plan' : 'Tap to review'}</Text><View style={artworkStyles.dashboardPlanActions}><Text style={artworkStyles.venueFooterText}>VIEW PLAN</Text><Ionicons name="arrow-forward" size={18} color={colors.pink} /></View></Pressable><View style={artworkStyles.planQuickActions}><Pressable accessibilityRole="button" onPress={() => set({ screen: 'feature', featureMode: 'customOuting' })}><Text style={artworkStyles.planActionText}>CUSTOM</Text></Pressable>{!plan.locked && <Pressable accessibilityRole="button" onPress={() => set({ screen: 'shuffl', plan: { ...plan, exists: false, locked: false, stops: [] } })}><Text style={artworkStyles.planActionText}>SHUFFLE</Text></Pressable>}<Pressable accessibilityRole="button" onPress={() => set({ screen: 'feature', featureMode: 'hostRoom' })}><Text style={artworkStyles.planActionText}>HOST THIS</Text></Pressable></View></> : <View style={artworkStyles.dashboardEmpty}><Text style={styles.cardTitle}>No plan yet</Text><Text style={styles.small}>Build your night from your vibe.</Text><Button onPress={() => set({ screen: 'shuffl' })}>Build my night</Button></View>}
        <View style={artworkStyles.dashboardSectionHeader}><View><Text style={styles.sectionTitle}>ROOMS LIVE NOW</Text><Text style={artworkStyles.shelfSubhead}>Find a night already forming</Text></View><Ionicons name="people-outline" size={20} color={colors.pink} /></View>
        {hostedRooms.length ? hostedRooms.slice(0, 2).map((room) => <Pressable key={room.id} accessibilityRole="button" accessibilityLabel={`Open ${room.title} room`} onPress={() => set({ screen: 'feature', featureMode: 'joinRoom' })} style={artworkStyles.dashboardRoomCard}><View style={artworkStyles.dashboardLive}><View style={styles.liveDot} /><Text style={artworkStyles.homeShelfLabel}>LIVE</Text></View><Text style={styles.cardTitle}>{room.title}</Text><Text style={styles.small}>{room.members?.length ?? 0} members · {room.stop_count ?? room.selected_stops?.length ?? 0} stops · requests open</Text><View style={artworkStyles.dashboardRoomMeta}><Text style={artworkStyles.venueFooterText}>OPEN ROOM</Text><Text style={artworkStyles.dashboardChemistry}>{room.stop_types?.join(' · ') || 'SHAPE YOUR NIGHT'}</Text></View></Pressable>) : <View style={artworkStyles.dashboardEmpty}><Text style={styles.cardTitle}>No rooms live right now</Text><Text style={styles.small}>Host a plan and invite people into a night that fits.</Text><Button onPress={() => set({ screen: 'feature', featureMode: 'hostRoom' })}>Host a room</Button></View>}
        <View style={artworkStyles.dashboardSectionHeader}><View><Text style={styles.sectionTitle}>EXPLORE</Text><Text style={artworkStyles.shelfSubhead}>See what Delhi is feeling tonight</Text></View><Ionicons name="pulse-outline" size={20} color={colors.pink} /></View>
        <View style={artworkStyles.exploreGrid}>{[['Hauz Khas', 'High energy · high crowd'], ['Khan Market', 'Polished · early evening'], ['Cyber Hub', 'Busy · late-night']].map(([area, copy]) => <Pressable key={area} accessibilityRole="button" onPress={() => set({ screen: 'search' })} style={artworkStyles.exploreCard}><Text style={artworkStyles.exploreArea}>{area}</Text><Text style={styles.small}>{copy}</Text><Ionicons name="arrow-forward" size={17} color={colors.pink} /></Pressable>)}</View>
        <ImageBackground source={homeCityArtwork} imageStyle={artworkStyles.homeCityImage} style={artworkStyles.homeCityCard}><View style={artworkStyles.homeCityShade} /><Text style={artworkStyles.cityTitle}>New Delhi is moving tonight.</Text><Text style={styles.small}>Neighbourhood-level recommendations, kept approximate.</Text><Button kind="secondary" onPress={() => set({ screen: 'search' })}>Explore places</Button></ImageBackground>
      </>}
    </ScrollView>
    {plan.locked ? <Pressable accessibilityRole="button" onPress={() => set({ screen: 'feature', featureMode: 'activePlan' })} style={artworkStyles.nowPlaying}><View><Text style={artworkStyles.homeShelfLabel}>NOW PLAYING</Text><Text style={styles.cardTitle}>{plan.title || 'Tonight, finally'}</Text></View><Text style={styles.small}>{plan.stops.length} stops · locked</Text></Pressable> : null}
    <View style={styles.nav}><Pressable accessibilityRole="button" accessibilityLabel="Home" onPress={() => set({ screen: 'discover' })} style={styles.navItem}><Ionicons name="home-outline" size={23} color={colors.pink} /><Text style={[styles.navText, { color: colors.pink }]}>Home</Text></Pressable><Pressable accessibilityRole="button" accessibilityLabel="Open SHUFFL planning" onPress={() => set({ screen: 'playMenu' })} style={styles.navPlayItem}><View style={artworkStyles.playNav}><Ionicons name="play" size={22} color={colors.bg} /></View><Text style={styles.navPlayLabel}>SHUFFL</Text></Pressable><Pressable accessibilityRole="button" accessibilityLabel="Open Social and Messages" onPress={() => set({ screen: 'feature', featureMode: 'inbox' })} style={styles.navItem}><Ionicons name="chatbubbles-outline" size={23} color={colors.muted} /><Text style={styles.navText}>Social</Text></Pressable></View>
  </SafeAreaView>;
}

function ShufflScreen() {
  const { set, locked, plan, skeleton } = useApp();
  const openPicker = useCallback(() => {
    if (locked) return;
    set({ screen: "feature", featureMode: "customOuting" });
  }, [locked, set]);
  return (
    <SafeAreaView style={styles.safe}>
      <Header label="SHUFFL" onBack={() => set({ screen: "discover" })} />
      <ScrollView contentContainerStyle={styles.content}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Add friends to your night"
          onPress={() => set({ screen: "feature", featureMode: "hostRoom" })}
          style={artworkStyles.lineupCard}
        >
          <Text style={styles.kicker}>TONIGHT</Text>
          <Text style={styles.h1}>Add friends to your night</Text>
          <Text style={styles.small}>Bring people into the same night after you shape it.</Text>
        </Pressable>
        <Pressable
          accessibilityRole="search"
          accessibilityLabel="Search through venues and rooms"
          onPress={() => set({ screen: "search" })}
          style={styles.input}
        >
          <Ionicons name="search" size={20} color={colors.muted} />
          <Text style={[styles.small, { flex: 1 }]}>Search through venues and rooms here</Text>
          <Ionicons name="arrow-forward" size={18} color={colors.pink} />
        </Pressable>
        <Text style={styles.sectionTitle}>Friends that want your kind of night today</Text>
        <View style={styles.surface}>
          <Text style={styles.cardTitle}>Your people appear here</Text>
          <Text style={styles.small}>Invite friends or start with your own shape.</Text>
          <Button kind="secondary" onPress={() => set({ screen: "feature", featureMode: "hostRoom" })}>Add friends</Button>
        </View>
        <Text style={styles.sectionTitle}>Ranked rooms</Text>
        <Pressable onPress={() => set({ screen: "rooms" })} style={styles.surface}>
          <Text style={styles.cardTitle}>Rooms that match your vibe</Text>
          <Text style={styles.small}>Browse public rooms and see the night they are shaping.</Text>
          <Text style={[styles.small, { color: colors.pink }]}>See all rooms →</Text>
        </Pressable>
        <Text style={styles.sectionTitle}>The night everyone drew</Text>
        <View style={styles.surface}>
          <Text style={styles.cardTitle}>{plan.exists ? plan.title : "No night selected yet"}</Text>
          <Text style={styles.small}>
            {plan.exists ? `${plan.stops.length} stop${plan.stops.length === 1 ? "" : "s"} · choose one venue per stop` : `${skeleton.stops} stop${skeleton.stops === 1 ? "" : "s"} · draw your shape first`}
          </Text>
          {plan.exists ? (
            <Button onPress={() => set({ screen: "feature", featureMode: plan.locked ? "activePlan" : "customOuting" })}>Choose venues</Button>
          ) : (
            <Button onPress={openPicker} disabled={locked}>Build my night</Button>
          )}
        </View>
        <Button kind="secondary" onPress={openPicker} disabled={locked}>Redraw skeleton</Button>
        <Button kind="ghost" onPress={() => set({ screen: "plans" })}>Past plans</Button>
      </ScrollView>
      <Nav />
    </SafeAreaView>
  );
}
type SearchVenue = {
  name: string;
  type: string;
  area: string;
  tag: string;
  color: string;
  scores: Record<string, number>;
};
function Search() {
  const { set } = useApp();
  const [query, setQuery] = useState("");
  const [selected, setSelected] = useState<string[]>([]);
  const [items, setItems] = useState<SearchVenue[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState(false);
  useEffect(() => {
    let alive = true;
    setLoading(true);
    getService()
      .getDiscovery()
      .then((result) => {
        if (!alive) return;
        const known = new Map(venues.map((venue) => [venue.name, venue]));
        setItems(
          result.map(
            (item) =>
              known.get(item.name) ?? {
                ...item,
                tag: "A place to make the night yours",
                color: colors.mint,
                scores: {},
              },
          ),
        );
        setLoadError(false);
      })
      .catch(() => {
        if (alive) {
          setItems([]);
          setLoadError(true);
        }
      })
      .finally(() => {
        if (alive) setLoading(false);
      });
    return () => {
      alive = false;
    };
  }, []);
  const filters = ["Nearby", "Budget · ₹₹", "Pub", "Live music", "Food", "Dressed-up"];
  const toggle = (filter: string) =>
    setSelected((current) =>
      current.includes(filter)
        ? current.filter((value) => value !== filter)
        : [...current, filter],
    );
  const results = useMemo(
    () =>
      items.filter((venue) => {
        const text =
          `${venue.name} ${venue.type} ${venue.area} ${venue.tag}`.toLowerCase();
        if (query.trim() && !text.includes(query.trim().toLowerCase()))
          return false;
        if (selected.includes("Pub") && venue.type !== "pub") return false;
        if (selected.includes("Live music") && venue.type !== "live room") return false;
        if (selected.includes("Food") && (venue.scores.FOOD ?? 0) < 60) return false;
        if (selected.includes("Dressed-up") && (venue.scores.POL ?? 0) < 60) return false;
        return true;
      }),
    [items, query, selected],
  );
  return (
    <SafeAreaView style={styles.safe}>
      <Header label="Search" onBack={() => set({ screen: "discover" })} />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.input}>
          <Ionicons name="search" size={20} color={colors.muted} />
          <TextInput
            accessibilityLabel="Search places"
            placeholder="Search places and areas"
            placeholderTextColor={colors.muted}
            value={query}
            onChangeText={setQuery}
            style={{ flex: 1, color: colors.text, padding: 0 }}
            returnKeyType="search"
          />
        </View>
        <Text style={styles.sectionTitle}>Filters</Text>
        {filters.map((filter) => (
          <Pressable
            accessibilityRole="checkbox"
            accessibilityState={{ checked: selected.includes(filter) }}
            onPress={() => toggle(filter)}
            key={filter}
            style={styles.filter}
          >
            <Text style={styles.cardTitle}>{filter}</Text>
            <Ionicons
              name={
                selected.includes(filter)
                  ? "checkmark-circle"
                  : "add-circle-outline"
              }
              size={22}
              color={selected.includes(filter) ? colors.mint : colors.muted}
            />
          </Pressable>
        ))}
        <Text style={styles.small}>
          Opening hours are checked live when a venue is opened. Distance stays approximate unless you enable location access.
        </Text>
        <Text style={styles.sectionTitle}>
          {loading ? "Finding places…" : `${results.length} places`}
        </Text>
        {loadError && (
          <Text accessibilityRole="alert" style={styles.small}>
            We could not refresh venues right now. Check your connection and try again.
          </Text>
        )}
        {results.map((venue) => (
          <Pressable
            key={venue.name}
            onPress={() =>
              set({
                screen: "feature",
                featureMode: "venue",
                selectedVenueName: venue.name,
              })
            }
            style={styles.venue}
          >
            <View
              style={[styles.venueArt, { backgroundColor: venue.color + "28" }]}
            >
              <Ionicons name="location-outline" size={27} color={venue.color} />
            </View>
            <View style={{ flex: 1 }}>
              <Text style={styles.cardTitle}>{venue.name}</Text>
              <Text style={styles.small}>
                {venue.type} · {venue.area}
              </Text>
              <Text style={[styles.small, { color: venue.color }]}>
                {venue.tag}
              </Text>
            </View>
            <Ionicons name="chevron-forward" size={20} color={colors.muted} />
          </Pressable>
        ))}
        {!results.length && (
          <Text style={styles.body}>
            No places match those choices. Try a nearby area or remove a filter.
          </Text>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}
function Plans() {
  const { set, plan } = useApp();
  return (
    <SafeAreaView style={styles.safe}>
      <Header label="Plans" />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>YOUR NIGHT</Text>
        <Text style={styles.h2}>
          {plan.exists ? plan.style : "A plan with a little movement."}
        </Text>
        {plan.exists ? (
          <View style={styles.planCard}>
            <View style={styles.planTop}>
              <Text style={styles.cardTitle}>
                {plan.locked ? "Plan locked" : "Plan draft"}
              </Text>
              <Text style={styles.tag}>{plan.locked ? "LOCKED" : "DRAFT"}</Text>
            </View>
            {plan.stops.map((stop, i) => (
              <View style={styles.stop} key={`${i}-${stop}`}>
                <View style={styles.stopDot}>
                  <Text style={styles.stopNo}>{i + 1}</Text>
                </View>
                <Text style={styles.cardTitle}>{stop}</Text>
              </View>
            ))}
          </View>
        ) : (
          <View style={styles.surface}>
            <Text style={styles.cardTitle}>No plan yet</Text>
            <Text style={styles.small}>
              Build a plan from your current vibe and place preferences. You can
              review it before locking.
            </Text>
          </View>
        )}
        <Button
          onPress={() => set({ screen: "feature", featureMode: "activePlan" })}
        >
          {plan.exists ? "Manage plan" : "Build a plan"}
        </Button>
        <Text style={styles.sectionTitle}>Past plans</Text>
        <View style={styles.surface}>
          <Text style={styles.small}>
            No completed plans have been saved yet.
          </Text>
        </View>
      </ScrollView>
      <Nav />
    </SafeAreaView>
  );
}
function Rooms() {
  const { set } = useApp();
  const [rooms, setRooms] = useState<RoomRecord[]>([]);
  useEffect(() => {
    let alive = true;
    getService().listHostedRooms().then((items) => {
      if (alive) setRooms(items.filter((room) => room.status === 'hosted'));
    }).catch(() => {
      if (alive) setRooms([]);
    });
    return () => { alive = false; };
  }, []);
  return (
    <SafeAreaView style={styles.safe}>
      <Header label="Rooms" />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>PEOPLE, NOT PROFILES</Text>
        <Text style={styles.h2}>Rooms built around a reason to go.</Text>
        {rooms.length ? rooms.map((room) => <View style={styles.roomCard} key={room.id}>
          <View style={styles.roomIcon}><Ionicons name="people" size={24} color={colors.mint} /></View>
          <Text style={styles.cardTitle}>{room.title}</Text>
          <Text style={styles.small}>{room.members?.length ?? 0} people · {room.stop_count ?? room.selected_stops?.length ?? 0} stops · requests open</Text>
          <Button onPress={() => set({ screen: "feature", featureMode: "joinRoom" })}>View room</Button>
        </View>) : <View style={styles.roomCard}>
          <View style={[styles.roomIcon, { backgroundColor: "#2B1D41" }]}><Ionicons name="moon-outline" size={24} color={colors.pink} /></View>
          <Text style={styles.cardTitle}>No hosted rooms yet</Text>
          <Text style={styles.small}>Rooms appear here after someone hosts a published plan.</Text>
          <Button kind="secondary" onPress={() => set({ screen: "feature", featureMode: "hostRoom" })}>Host a room</Button>
        </View>}
        <Button
          kind="secondary"
          onPress={() => set({ screen: "feature", featureMode: "joinRoom" })}
        >
          Find a room to join
        </Button>
      </ScrollView>
      <Nav />
    </SafeAreaView>
  );
}
function ProfileHome() {
  const {
    set,
    scores,
    assessment,
    userName,
    userPronouns,
    userBio,
    avatarUri,
    preferences,
    activeMusic,
  } = useApp();
  const todayName = vibeName(
    scores,
    latencyFirmness(assessment),
    assessment.chosenTop,
  );
  const chosen = Object.entries(preferences.readings)
    .filter(([, reading]) => (reading?.score ?? 0) >= 80)
    .slice(0, 3)
    .map(([factor]) => factor);
  const initials = (userName || "You")
    .trim()
    .split(/\s+/)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();
  const openEdit = () => set({ screen: "profile", postVibeProfile: true });
  useEffect(() => {
    let active = true;
    getService().getProfile().then((profile) => {
      if (!active) return;
      set({ userName: profile.name, userPronouns: profile.pronouns ?? "", userBio: profile.bio ?? "" });
    }).catch(() => undefined);
    return () => { active = false; };
  }, [set]);
  return (
    <SafeAreaView style={styles.safe}>
      <Header label="You" />
      <ScrollView contentContainerStyle={styles.content}>
        <View style={artworkStyles.profileHomeHero}>
          <Image
            source={profileHeaderArtwork}
            style={artworkStyles.profileHomeImage}
          />
          <View style={artworkStyles.profileHomeShade} />
          <View style={artworkStyles.profileHomeTop}>
            <Text style={artworkStyles.profileHeroEyebrow}>YOUR SHUFFL</Text>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Edit profile"
              onPress={openEdit}
              style={artworkStyles.profileEdit}
            >
              <Ionicons name="create-outline" size={17} color={colors.text} />
              <Text style={artworkStyles.profileEditText}>EDIT</Text>
            </Pressable>
          </View>
          <View style={artworkStyles.profileHomeAvatar}>
            {avatarUri ? (
              <Image
                source={{ uri: avatarUri }}
                style={artworkStyles.profileHomeAvatarImage}
              />
            ) : (
              <Text style={artworkStyles.profileAvatarInitials}>
                {initials}
              </Text>
            )}
          </View>
          <Text style={artworkStyles.profileHomeName}>
            {userName || "Your profile"}
          </Text>
          <Text style={artworkStyles.profileHomeMeta}>
            Delhi NCR{userPronouns ? ` · ${userPronouns}` : ""}
          </Text>
          {userBio ? (
            <Text style={artworkStyles.profileHomeBio}>{userBio}</Text>
          ) : null}
        </View>
        <View style={artworkStyles.profileStats}>
          <View>
            <Text style={artworkStyles.profileStatValue}>{chosen.length}</Text>
            <Text style={artworkStyles.profileStatLabel}>SIGNALS</Text>
          </View>
          <View>
            <Text style={artworkStyles.profileStatValue}>1</Text>
            <Text style={artworkStyles.profileStatLabel}>NIGHT SHAPED</Text>
          </View>
          <View>
            <Text style={artworkStyles.profileStatValue}>ON</Text>
            <Text style={artworkStyles.profileStatLabel}>DISCOVERABLE</Text>
          </View>
        </View>
        <View style={artworkStyles.profileSignalCard}>
          <View style={artworkStyles.profileSectionHeading}>
            <View>
              <Text style={styles.kicker}>TONIGHT’S SHAPE</Text>
              <Text style={styles.cardTitle}>{todayName}</Text>
            </View>
            <Ionicons name="sparkles" size={23} color={colors.pink} />
          </View>
          <Text style={styles.small}>
            A room that meets your energy without making you explain it.
          </Text>
        </View>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel="Open music picker"
          onPress={() => set({ screen: "feature", featureMode: "music" })}
          style={styles.menu}
        >
          <View style={artworkStyles.profileMenuIcon}>
            <Ionicons name="musical-notes-outline" size={18} color={colors.pink} />
          </View>
          <View style={{ flex: 1 }}>
            <Text style={styles.cardTitle}>{activeMusic || "Add your room soundtrack"}</Text>
            <Text style={styles.small}>These tunes are catered to your vibe today.</Text>
          </View>
          <Ionicons name="chevron-forward" size={20} color={colors.muted} />
        </Pressable>
        <View style={artworkStyles.profileHomeSection}>
          <Text style={styles.kicker}>YOUR SPACE</Text>
          {[
            "Vibe history",
            "Past plans",
            "Friends",
            "Privacy & safety",
            "Settings",
            "Support",
          ].map((x, i) => (
            <Pressable
              style={styles.menu}
              key={x}
              onPress={() => {
                if (i === 0) set({ screen: "feature", featureMode: "history" });
                else if (i === 1) set({ screen: "plans" });
                else if (i === 2) set({ screen: "rooms" });
                else if (i === 3)
                  set({ screen: "feature", featureMode: "privacy" });
                else if (i === 4)
                  set({ screen: "feature", featureMode: "settings" });
                else set({ screen: "feature", featureMode: "support" });
              }}
            >
              <View style={artworkStyles.profileMenuIcon}>
                <Ionicons
                  name={
                    (
                      [
                        "time-outline",
                        "map-outline",
                        "people-outline",
                        "shield-checkmark-outline",
                        "settings-outline",
                        "help-circle-outline",
                      ] as const
                    )[i]
                  }
                  size={18}
                  color={colors.pink}
                />
              </View>
              <Text style={styles.cardTitle}>{x}</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.muted} />
            </Pressable>
          ))}
        </View>
      </ScrollView>
      <Nav />
    </SafeAreaView>
  );
}
function Control() {
  const { set, reset } = useApp();
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Demo Control Centre"
        onBack={() => set({ screen: "discover" })}
      />
      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.body}>
          Developer-only controls for the first demo. These are local and
          reversible.
        </Text>
        <Text style={styles.sectionTitle}>Feed state</Text>
        <Button onPress={() => set({ locked: false, screen: "discover" })}>
          Switch to unlocked feed
        </Button>
        <Button
          kind="secondary"
          onPress={() => set({ locked: true, screen: "discover" })}
        >
          Switch to locked feed
        </Button>
        <Text style={styles.sectionTitle}>Journey shortcuts</Text>
        <Button
          kind="secondary"
          onPress={() =>
            set({
              screen: "assessment",
              assessmentIndex: 0,
              scores: {},
              actions: {},
              assessment: createAssessment(),
            })
          }
        >
          Simulate assessment
        </Button>
        <Button kind="secondary" onPress={() => set({ screen: "rooms" })}>
          Simulate room state
        </Button>
        <Button kind="secondary" onPress={() => set({ screen: "plans" })}>
          Simulate active plan
        </Button>
        <Text style={styles.sectionTitle}>Danger zone</Text>
        <Button kind="ghost" onPress={reset}>
          Reset all demo data
        </Button>
      </ScrollView>
    </SafeAreaView>
  );
}
function AssessmentStrict() {
  const { set, assessment } = useApp();
  const card = currentCard(assessment);
  const cardX = useRef(new Animated.Value(0)).current;
  const cardY = useRef(new Animated.Value(0)).current;
  const transitionBusy = useRef(false);
  const [swipeLabel, setSwipeLabel] = useState("");
  const progressFloor = useRef(8);
  const calculatedProgress = Math.min(
    100,
    Math.max(
      8,
      (assessment.cursor / Math.max(1, assessment.queue.length)) * 100,
    ),
  );
  progressFloor.current = Math.max(progressFloor.current, calculatedProgress);
  const swipeResponder = useRef(
    PanResponder.create({
      onMoveShouldSetPanResponder: (_event, gesture) =>
        Math.max(Math.abs(gesture.dx), Math.abs(gesture.dy)) > 14,
      onPanResponderRelease: (_event, gesture) => {
        if (Math.max(Math.abs(gesture.dx), Math.abs(gesture.dy)) < 42) return;
        if (transitionBusy.current) return;
        transitionBusy.current = true;
        const action: Action =
          Math.abs(gesture.dy) > Math.abs(gesture.dx)
            ? gesture.dy < 0
              ? "LOVE"
              : "HARD_PASS"
            : gesture.dx > 0
              ? "UP"
              : "DOWN";
        const label =
          action === "UP"
            ? "UP FOR IT"
            : action === "DOWN"
              ? "NOT FOR ME"
              : action === "LOVE"
                ? "LOVE IT"
                : "HARD PASS";
        setSwipeLabel(label);
        const targetX =
          Math.abs(gesture.dx) > Math.abs(gesture.dy)
            ? gesture.dx > 0
              ? 500
              : -500
            : 0;
        const targetY = targetX === 0 ? (gesture.dy > 0 ? 500 : -500) : 0;
        Animated.parallel([
          Animated.timing(cardX, {
            toValue: targetX,
            duration: 220,
            easing: Easing.out(Easing.cubic),
            useNativeDriver: true,
          }),
          Animated.timing(cardY, {
            toValue: targetY,
            duration: 220,
            easing: Easing.out(Easing.cubic),
            useNativeDriver: true,
          }),
        ]).start(({ finished }) => {
          if (finished)
            commitAssessment(answerCard(useApp.getState().assessment, action));
          else transitionBusy.current = false;
          cardX.setValue(0);
          cardY.setValue(0);
          setSwipeLabel("");
        });
      },
    }),
  ).current;
  useEffect(() => {
    if (!card || assessment.paused) return;
    const currentSource = vibeCardArtwork[card.id];
    const nextCard = assessment.queue[assessment.cursor + 1];
    const nextSource = nextCard ? vibeCardArtwork[nextCard.id] : undefined;
    [currentSource, nextSource].forEach((source) => {
      if (!source) return;
      const uri = Image.resolveAssetSource(source)?.uri;
      if (uri) void Image.prefetch(uri).catch(() => undefined);
    });
    const current = useApp.getState().assessment;
    const started = beginExposure(current);
    if (started !== current) useApp.getState().set({ assessment: started });
    if (
      started.exposures.filter((exposure) => exposure.card.id === card.id)
        .length >= 3
    )
      return;
    const timer = setTimeout(() => {
      const latest = useApp.getState().assessment;
      if (
        currentCard(latest)?.id === card.id &&
        !isRequiredAnswerExposure(latest)
      )
        useApp.getState().set({ assessment: deferCard(latest, "timeout") });
    }, 12000);
    return () => clearTimeout(timer);
  }, [card, assessment.paused]);
  useEffect(() => {
    if (!assessment.awayPrompt) return;
    const timer = setTimeout(() => {
      const latest = useApp.getState().assessment;
      if (latest.awayPrompt)
        useApp
          .getState()
          .set({ assessment: resolveAway(latest, "unanswered") });
    }, 5000);
    return () => clearTimeout(timer);
  }, [assessment.awayPrompt]);
  useEffect(() => {
    transitionBusy.current = false;
  }, [
    card?.id,
    assessment.awayPrompt,
    assessment.paused,
    assessment.forcedChoice,
  ]);
  if (assessment.awayPrompt)
    return (
      <SafeAreaView style={styles.safe}>
        <Header label="Daily vibe" />
        <View style={styles.content}>
          <Text style={styles.kicker}>CHECKING IN</Text>
          <Text style={styles.h2}>Are you there?</Text>
          <Text style={styles.body}>
            The deck is paused until you choose what to do.
          </Text>
          <Button
            onPress={() =>
              set({ assessment: resolveAway(assessment, "present") })
            }
          >
            Yes
          </Button>
          <Button
            kind="secondary"
            onPress={() => set({ assessment: resolveAway(assessment, "away") })}
          >
            No, I was away
          </Button>
        </View>
      </SafeAreaView>
    );
  if (assessment.paused)
    return (
      <SafeAreaView
        style={styles.safe}
        onTouchEnd={() =>
          set({ assessment: resumeAssessment(useApp.getState().assessment) })
        }
      >
        <Header label="Daily vibe" />
        <View style={styles.content}>
          <Text style={styles.kicker}>QUIZ PAUSED</Text>
          <Text style={styles.h2}>Ready when you are.</Text>
          <Text style={styles.body}>
            Your place in the deck is saved. Tap anywhere to continue.
          </Text>
          <Button
            onPress={() => set({ assessment: resumeAssessment(assessment) })}
          >
            Resume
          </Button>
        </View>
      </SafeAreaView>
    );
  if (assessment.forcedChoice)
    return (
      <SafeAreaView style={styles.safe}>
        <Header label="One last choice" />
        <View style={styles.content}>
          <Text style={styles.kicker}>LAST ONE</Text>
          <Text style={styles.h2}>
            If you could only keep one for tonight, which is the night?
          </Text>
          {assessment.forcedChoice.map((factor) => (
            <Pressable
              key={factor}
              style={styles.menu}
              onPress={() =>
                set({ assessment: answerForcedChoice(assessment, factor) })
              }
            >
              <Text style={styles.cardTitle}>{factor}</Text>
              <Ionicons name="chevron-forward" size={20} color={colors.mint} />
            </Pressable>
          ))}
        </View>
      </SafeAreaView>
    );
  if (!card) return <Reveal />;
  const copy = factorCopy[card.factor];
  const required = isRequiredAnswerExposure(assessment);
  const answer = (action: Action) => {
    if (transitionBusy.current) return;
    transitionBusy.current = true;
    commitAssessment(answerCard(useApp.getState().assessment, action));
  };
  const next = () => {
    if (transitionBusy.current) return;
    transitionBusy.current = true;
    set({
      assessment: deferCard(useApp.getState().assessment, "next"),
      assessmentIndex: useApp.getState().assessment.cursor,
    });
  };
  const back = () => {
    if (transitionBusy.current) return;
    transitionBusy.current = true;
    set({ assessment: backCard(useApp.getState().assessment) });
  };
  return (
    <SafeAreaView style={styles.safe}>
      <Header
        label="Daily vibe"
        onBack={() => set({ screen: "instructions" })}
      />
      <View style={styles.progress}>
        <View style={styles.progressTrack}>
          <View
            style={[
              styles.progressFill,
              { width: `${progressFloor.current}%` as `${number}%` },
            ]}
          />
        </View>
      </View>
      <ScrollView contentContainerStyle={styles.assessment}>
        <Animated.View
          {...swipeResponder.panHandlers}
          style={[
            artworkStyles.swipeGesture,
            {
              transform: [{ translateX: cardX }, { translateY: cardY }],
              opacity: cardX.interpolate({
                inputRange: [-500, 0, 500],
                outputRange: [0.45, 1, 0.45],
              }),
            },
          ]}
        >
          <VibeCardArtwork
            source={vibeCardArtwork[card.id]}
            label={copy.title}
          />
          {swipeLabel ? (
            <View pointerEvents="none" style={artworkStyles.swipeFeedback}>
              <Text style={artworkStyles.swipeFeedbackText}>{swipeLabel}</Text>
            </View>
          ) : null}
        </Animated.View>
        <Text style={styles.kicker}>TONIGHT · YOUR FIRST REACTION</Text>
        <Text style={styles.h2}>{copy.title}</Text>
        <Text style={styles.body}>{copy.subtitle}</Text>
        <View style={styles.swipes}>
          {(
            [
              ["LOVE", "arrow-up", colors.amber],
              ["UP", "arrow-forward", colors.green],
              ["DOWN", "arrow-back", colors.muted],
              ["HARD_PASS", "arrow-down", colors.danger],
            ] as const
          ).map(([label, icon, color]) => (
            <Pressable
              key={label}
              disabled={transitionBusy.current}
              onPress={() => answer(label)}
              style={[
                styles.swipe,
                transitionBusy.current && { opacity: 0.55 },
              ]}
            >
              <View style={[styles.swipeIcon, { borderColor: color }]}>
                <Ionicons name={icon as any} size={20} color={color} />
              </View>
              <Text style={[styles.swipeLabel, { color }]}>
                {label === "UP"
                  ? "UP FOR IT"
                  : label === "DOWN"
                    ? "NOT FOR ME"
                    : label.replace("_", " ")}
              </Text>
            </Pressable>
          ))}
        </View>
        <View style={artworkStyles.assessmentActions}>
          {!required && (
            <Button kind="secondary" onPress={next}>
              Next
            </Button>
          )}
          <Button kind="ghost" onPress={back}>
            Back
          </Button>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}
function AppContent() {
  assertReleaseScope();
  const [opening, setOpening] = useState(true);
  const screen = useApp((s) => s.screen);
  const featureMode = useApp((s) => s.featureMode);
  const hydrated = useApp((s) => s.hydrated);
  useEffect(() => {
    const timer = setTimeout(() => setOpening(false), 1650);
    void hydrateDemoState();
    void getService().getLatestSkeleton().then((latest) => {
      if (!latest) return;
      useApp.getState().set({
        skeleton: {
          stops: latest.stops,
          energy: latest.energy,
          crowd: latest.crowd,
          tags: latest.tags,
          stopDurations: latest.stop_durations,
          updatedAt: latest.created_at,
        },
      });
    }).catch(() => undefined);
    return () => clearTimeout(timer);
  }, []);
  if (opening) return <OpeningAnimation />;
  if (!hydrated)
    return (
      <SafeAreaView style={styles.safe}>
        <View style={[styles.hero, { alignItems: "center" }]}>
          <Brand />
          <Text style={styles.kicker}>YOUR NIGHT, YOUR WAY</Text>
        </View>
      </SafeAreaView>
    );
  if (screen === "welcome") return <Welcome />;
  if (screen === "intro") return <Intro />;
  if (screen === "login") return <Login />;
  if (screen === "profile") return <Profile />;
  if (screen === "preferenceIntro") return <PreferenceIntro />;
  if (screen === "preferences") return <Preferences />;
  if (screen === "instructions") return <Instructions />;
  if (screen === "dailyCheckin") return <DailyCheckin />;
  if (screen === "assessment") return <AssessmentStrict />;
  if (screen === "reveal") return <Reveal />;
  if (screen === "discover") return <HomeDashboard />;
  if (screen === "playMenu") return <PlayMenu />;
  if (screen === "shuffl") return <ShufflScreen />;
  if (screen === "search")
    return (
      <View style={styles.safe}>
        <Search />
        <Nav />
      </View>
    );
  if (screen === "plans") return <Plans />;
  if (screen === "rooms") return <Rooms />;
  if (screen === "profileHome") return <ProfileHome />;
  if (screen === "feature") return <FeatureScreen mode={featureMode} />;
  return <Control />;
}

export default function App() {
  return (
    <SafeAreaProvider>
      <AppContent />
    </SafeAreaProvider>
  );
}
const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: colors.bg },
  header: {
    height: 76,
    paddingHorizontal: 20,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  headerLabel: {
    color: colors.muted,
    fontSize: 13,
    letterSpacing: 1.5,
    textTransform: "uppercase",
  },
  brandWordmark: { width: 122, height: 30 },
  openingScreen: { flex: 1, alignItems: "center", justifyContent: "center", backgroundColor: "#050507" },
  openingAnimation: { width: "100%", maxWidth: 760, height: 340 },
  iconButton: {
    width: 44,
    height: 44,
    alignItems: "center",
    justifyContent: "center",
  },
  hero: { flex: 1, padding: 24, justifyContent: "center" },
  welcomeScreen: { flex: 1, padding: 20 },
  welcomeTop: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  welcomeStamp: {
    color: colors.muted,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 1.5,
  },
  welcomeHeroWrap: {
    height: 390,
    marginTop: 12,
    borderRadius: radius.lg,
    overflow: "hidden",
    backgroundColor: colors.surface,
  },
  welcomeCopy: { flex: 1, justifyContent: "flex-end", paddingTop: 20 },
  heroArt: {
    height: 250,
    alignItems: "center",
    justifyContent: "center",
    marginVertical: 10,
  },
  orbit: {
    position: "absolute",
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: 200,
    transform: [{ rotate: "28deg" }],
  },
  one: { width: 170, height: 170 },
  two: { width: 240, height: 120, borderColor: "#30352A" },
  three: { width: 300, height: 210, borderColor: "#37332B" },
  heroCore: {
    width: 148,
    height: 148,
    borderRadius: 74,
    backgroundColor: colors.surface,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 1,
    borderColor: colors.line,
  },
  coreText: {
    color: colors.text,
    fontSize: 19,
    textAlign: "center",
    lineHeight: 26,
    fontWeight: "600",
    letterSpacing: -0.3,
  },
  kicker: {
    color: colors.mint,
    fontSize: 11,
    letterSpacing: 1.8,
    fontWeight: "700",
    marginBottom: 12,
  },
  h1: {
    color: colors.text,
    fontSize: 42,
    lineHeight: 47,
    fontWeight: "700",
    letterSpacing: -1.4,
    marginBottom: 14,
  },
  h2: {
    color: colors.text,
    fontSize: 29,
    lineHeight: 36,
    fontWeight: "700",
    letterSpacing: -0.8,
    marginBottom: 12,
  },
  body: { color: colors.muted, fontSize: 16, lineHeight: 25, marginBottom: 22 },
  button: {
    minHeight: 56,
    borderRadius: radius.sm,
    backgroundColor: colors.mint,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 18,
    marginTop: 10,
  },
  buttonText: {
    color: colors.bg,
    fontSize: 15,
    fontWeight: "800",
    letterSpacing: 0.4,
  },
  secondary: {
    backgroundColor: colors.raised,
    borderWidth: 1,
    borderColor: colors.line,
  },
  ghost: { backgroundColor: "transparent" },
  content: { padding: 20, paddingBottom: 110 },
  homeContent: { padding: 20, paddingBottom: 125 },
  homeTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "flex-start",
  },
  homeTitle: {
    color: colors.text,
    fontSize: 35,
    lineHeight: 40,
    fontWeight: "900",
    letterSpacing: -1,
  },
  feature: {
    flexDirection: "row",
    gap: 14,
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  featureNo: {
    width: 34,
    height: 34,
    borderRadius: 17,
    backgroundColor: "#303526",
    alignItems: "center",
    justifyContent: "center",
  },
  featureNoText: { color: colors.mint, fontWeight: "800" },
  cardTitle: {
    color: colors.text,
    fontSize: 16,
    fontWeight: "700",
    marginBottom: 5,
  },
  small: { color: colors.muted, fontSize: 13, lineHeight: 19 },
  input: {
    height: 56,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
    paddingHorizontal: 16,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginVertical: 12,
  },
  inputText: { color: colors.text, fontSize: 15 },
  privacy: {
    color: colors.muted,
    textAlign: "center",
    fontSize: 12,
    marginTop: 18,
  },
  avatar: {
    width: 108,
    height: 108,
    borderRadius: 54,
    backgroundColor: colors.raised,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 14,
    borderWidth: 1,
    borderColor: colors.line,
  },
  avatarSmall: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: colors.raised,
    alignItems: "center",
    justifyContent: "center",
  },
  tags: { flexDirection: "row", gap: 8, flexWrap: "wrap", marginVertical: 16 },
  tag: {
    color: colors.mint,
    backgroundColor: "#303526",
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 20,
    fontSize: 12,
    fontWeight: "700",
  },
  surface: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radius.md,
    padding: 18,
    marginVertical: 10,
  },
  pill: {
    alignSelf: "flex-start",
    flexDirection: "row",
    gap: 8,
    alignItems: "center",
    backgroundColor: "#303526",
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 20,
    marginBottom: 18,
  },
  pillText: {
    color: colors.mint,
    fontSize: 11,
    fontWeight: "800",
    letterSpacing: 1,
  },
  liveDot: {
    width: 7,
    height: 7,
    borderRadius: 4,
    backgroundColor: colors.mint,
  },
  swipeLegend: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginVertical: 14,
  },
  legend: { alignItems: "center", gap: 6 },
  progress: { paddingHorizontal: 20 },
  progressTrack: {
    height: 5,
    backgroundColor: colors.raised,
    borderRadius: 3,
    marginBottom: 8,
  },
  progressFill: { height: 5, backgroundColor: colors.mint, borderRadius: 3 },
  stepTrack: {
    height: 5,
    backgroundColor: colors.raised,
    marginHorizontal: 20,
  },
  stepFill: { height: 5, backgroundColor: colors.pink, borderRadius: 3 },
  assessment: { padding: 20, flex: 1 },
  art: {
    height: 250,
    borderRadius: radius.lg,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 22,
    overflow: "hidden",
  },
  artHalo: {
    width: 160,
    height: 160,
    borderRadius: 80,
    borderWidth: 1,
    borderColor: "#FFFFFF25",
    position: "absolute",
  },
  artLabel: {
    position: "absolute",
    top: 16,
    left: 18,
    color: "#FFFFFF70",
    fontSize: 11,
    letterSpacing: 1,
  },
  swipes: {
    flexDirection: "row",
    justifyContent: "space-between",
    marginTop: 8,
  },
  swipe: {
    alignItems: "center",
    gap: 6,
    minWidth: 68,
    minHeight: 58,
    justifyContent: "center",
  },
  swipeIcon: {
    width: 48,
    height: 48,
    borderWidth: 1,
    borderRadius: 24,
    alignItems: "center",
    justifyContent: "center",
  },
  swipeLabel: {
    fontSize: 9,
    color: colors.muted,
    fontWeight: "800",
    letterSpacing: 0.5,
  },
  swipeHint: {
    color: colors.muted,
    textAlign: "center",
    fontSize: 12,
    marginTop: 6,
  },
  revealCard: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 18,
    marginVertical: 22,
  },
  revealEyebrow: {
    color: colors.muted,
    fontSize: 10,
    letterSpacing: 1.4,
    marginBottom: 18,
  },
  scoreRow: { flexDirection: "row", justifyContent: "space-between" },
  score: { alignItems: "center" },
  scoreValue: { color: colors.text, fontSize: 20, fontWeight: "800" },
  scoreName: { color: colors.muted, fontSize: 10, marginTop: 4 },
  feedTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  locked: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 24,
    alignItems: "center",
    marginVertical: 20,
  },
  lockedIcon: { marginBottom: 12 },
  vibeBanner: {
    backgroundColor: "#302D25",
    borderRadius: radius.md,
    padding: 18,
    marginVertical: 18,
    flexDirection: "row",
    justifyContent: "space-between",
  },
  sectionTitle: {
    color: colors.text,
    fontSize: 19,
    fontWeight: "800",
    marginTop: 22,
    marginBottom: 12,
  },
  venue: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 12,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginBottom: 10,
  },
  venueArt: {
    width: 62,
    height: 62,
    borderRadius: 14,
    alignItems: "center",
    justifyContent: "center",
  },
  map: {
    height: 150,
    borderRadius: radius.md,
    backgroundColor: "#242720",
    borderWidth: 1,
    borderColor: colors.line,
    alignItems: "center",
    justifyContent: "flex-end",
    padding: 16,
    overflow: "hidden",
  },
  mapPulse: {
    position: "absolute",
    width: 180,
    height: 180,
    borderRadius: 90,
    borderWidth: 18,
    borderColor: "#C7E36F22",
    top: -50,
    left: 80,
  },
  filter: {
    height: 58,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  planCard: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 18,
    marginTop: 10,
  },
  planTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  stop: {
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    marginVertical: 11,
  },
  stopDot: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: "#303526",
    alignItems: "center",
    justifyContent: "center",
  },
  stopNo: { color: colors.mint, fontWeight: "800" },
  roomCard: {
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 18,
    marginVertical: 7,
  },
  roomIcon: {
    width: 44,
    height: 44,
    borderRadius: 14,
    backgroundColor: "#303526",
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 12,
  },
  profileTop: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    marginBottom: 10,
  },
  menu: {
    height: 60,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  nav: {
    height: 84,
    flexShrink: 0,
    backgroundColor: "#171714",
    borderTopWidth: 1,
    borderTopColor: colors.line,
    flexDirection: "row",
    justifyContent: "space-around",
    alignItems: "center",
    paddingHorizontal: 18,
    paddingVertical: 5,
  },
  navItem: {
    alignItems: "center",
    justifyContent: "center",
    gap: 4,
    minWidth: 76,
    minHeight: 68,
    paddingVertical: 4,
  },
  navText: { color: colors.muted, fontSize: 11, fontWeight: "700" },
  navPlayItem: {
    alignItems: "center",
    justifyContent: "center",
    gap: 2,
    minWidth: 76,
    minHeight: 76,
  },
  navPlayLabel: {
    color: colors.pink,
    fontSize: 9,
    fontWeight: "900",
    letterSpacing: 1.2,
  },
});

const artworkStyles = StyleSheet.create({
  welcomeHero: { width: "100%", height: "100%" },
  loaderRing: {
    width: 24,
    height: 24,
    borderRadius: 12,
    borderWidth: 2,
    borderColor: colors.pink,
    borderTopColor: "transparent",
  },
  welcomeHeroShade: {
    ...StyleSheet.absoluteFill,
    backgroundColor: "#06060922",
  },
  welcomeHeroCopy: {
    ...StyleSheet.absoluteFill,
    alignItems: "center",
    justifyContent: "center",
  },
  playNav: {
    width: 52,
    height: 52,
    borderRadius: 26,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.pink,
    shadowColor: colors.pink,
    shadowOpacity: 0.28,
    shadowRadius: 12,
    elevation: 8,
  },
  playChoice: {
    minHeight: 88,
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    padding: 14,
    marginBottom: 12,
    borderRadius: radius.md,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
  },
  playChoiceIcon: {
    width: 48,
    height: 48,
    borderRadius: 16,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.raised,
  },
  hostJoinRow: { flexDirection: "row", gap: 10, marginBottom: 28 },
  hostJoinButton: {
    minHeight: 52,
    flex: 1,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: radius.sm,
    backgroundColor: colors.pink,
  },
  joinButton: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.pink,
  },
  hostJoinText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 2,
  },
  lineupCard: {
    borderWidth: 1,
    borderColor: colors.line,
    borderRadius: radius.lg,
    backgroundColor: colors.surface,
    padding: 18,
    marginVertical: 12,
  },
  lineupHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingBottom: 16,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  lineupStop: {
    minHeight: 78,
    flexDirection: "row",
    alignItems: "center",
    gap: 12,
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  lineupTime: {
    color: colors.pink,
    fontSize: 13,
    fontFamily: "monospace",
    fontWeight: "800",
  },
  lineupRule: { width: 2, height: 32, backgroundColor: colors.pink },
  lineupVenue: {
    color: colors.text,
    fontSize: 19,
    fontFamily: "sans-serif-condensed",
    fontWeight: "900",
    letterSpacing: 0.5,
  },
  planActions: { flexDirection: "row", gap: 10, marginVertical: 8 },
  textAction: {
    minHeight: 50,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "center",
    gap: 8,
  },
  textActionLabel: { color: colors.pink, fontSize: 14, fontWeight: "800" },
  heatmapCard: {
    marginTop: 24,
    padding: 18,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
  },
  profilePill: {
    minHeight: 42,
    alignSelf: "flex-start",
    maxWidth: "100%",
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 14,
    marginTop: 8,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
  },
  profilePillText: {
    color: colors.text,
    fontSize: 13,
    fontWeight: "700",
    marginRight: 4,
  },
  shelfSubhead: {
    color: colors.muted,
    fontSize: 13,
    marginTop: -5,
    marginBottom: 12,
  },
  venueShelf: { gap: 12, paddingRight: 20 },
  venuePoster: {
    width: 250,
    minHeight: 190,
    borderRadius: radius.md,
    borderWidth: 1,
    borderTopWidth: 4,
    borderColor: colors.line,
    padding: 16,
    backgroundColor: colors.surface,
    justifyContent: "space-between",
  },
  venuePosterTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  venueEyebrow: { flex: 1, marginBottom: 0, fontSize: 9 },
  venueName: {
    fontSize: 24,
    lineHeight: 28,
    fontFamily: "sans-serif-condensed",
    letterSpacing: 0.5,
    marginVertical: 10,
  },
  venueFooter: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderTopWidth: 1,
    borderTopColor: colors.line,
    paddingTop: 12,
    marginTop: 12,
  },
  venueFooterText: {
    color: colors.muted,
    fontSize: 10,
    fontWeight: "800",
    letterSpacing: 1.5,
  },
  profileInput: {
    minHeight: 56,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
    paddingHorizontal: 16,
    color: colors.text,
    fontSize: 16,
    marginVertical: 14,
  },
  profileHero: {
    minHeight: 360,
    borderRadius: 28,
    overflow: "hidden",
    backgroundColor: colors.surface,
    marginBottom: 24,
    padding: 20,
    justifyContent: "space-between",
  },
  wizardIntro: {
    padding: 20,
    borderRadius: 24,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    marginBottom: 18,
  },
  wizardAvatarRow: {
    flexDirection: "row",
    alignItems: "center",
    gap: 14,
    padding: 16,
    borderRadius: 20,
    backgroundColor: "#1B2117",
    borderWidth: 1,
    borderColor: "#3B4A2A",
    marginBottom: 28,
  },
  wizardAvatar: {
    width: 76,
    height: 76,
    borderRadius: 38,
    backgroundColor: "#242A1B",
    borderWidth: 2,
    borderColor: colors.mint,
    alignItems: "center",
    justifyContent: "center",
  },
  wizardAvatarImage: { width: "100%", height: "100%", borderRadius: 38 },
  wizardAvatarAdd: {
    position: "absolute",
    right: -3,
    bottom: -2,
    width: 26,
    height: 26,
    borderRadius: 13,
    backgroundColor: colors.mint,
    alignItems: "center",
    justifyContent: "center",
    borderWidth: 2,
    borderColor: colors.bg,
  },
  profileHeroImage: {
    ...StyleSheet.absoluteFill,
    width: "100%",
    height: "100%",
  },
  profileHeroOverlay: {
    ...StyleSheet.absoluteFill,
    backgroundColor: "#07070880",
  },
  profileHeroTop: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
  },
  profileHeroEyebrow: {
    color: colors.mint,
    fontSize: 10,
    letterSpacing: 1.7,
    fontWeight: "900",
  },
  profileHeroStatus: {
    flexDirection: "row",
    alignItems: "center",
    gap: 7,
    paddingHorizontal: 10,
    paddingVertical: 7,
    borderRadius: 16,
    backgroundColor: "#08090ACC",
  },
  profileHeroStatusText: {
    color: colors.text,
    fontSize: 9,
    fontWeight: "800",
    letterSpacing: 1,
  },
  profileAvatarButton: {
    alignSelf: "center",
    width: 138,
    height: 138,
    borderRadius: 69,
    borderWidth: 4,
    borderColor: colors.mint,
    backgroundColor: colors.raised,
    marginVertical: 18,
    elevation: 8,
    shadowColor: colors.mint,
    shadowOpacity: 0.3,
    shadowRadius: 18,
  },
  profileAvatarImage: { width: "100%", height: "100%", borderRadius: 69 },
  profileAvatarFallback: {
    flex: 1,
    borderRadius: 69,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#242A1B",
  },
  profileAvatarInitials: {
    color: colors.text,
    fontSize: 42,
    fontWeight: "900",
    letterSpacing: 1,
  },
  profileAvatarAdd: {
    position: "absolute",
    right: -3,
    bottom: 3,
    width: 34,
    height: 34,
    borderRadius: 17,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.mint,
    borderWidth: 3,
    borderColor: colors.bg,
  },
  profileHeroIdentity: { alignItems: "center" },
  profileHeroName: {
    color: colors.text,
    fontSize: 30,
    lineHeight: 36,
    fontWeight: "900",
    letterSpacing: -0.7,
  },
  profileHeroMeta: {
    color: colors.text,
    opacity: 0.75,
    fontSize: 13,
    marginTop: 5,
  },
  profileIntroRow: {
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "space-between",
    marginBottom: 12,
  },
  profileCompletion: {
    color: colors.pink,
    fontSize: 11,
    lineHeight: 15,
    fontWeight: "900",
    letterSpacing: 1.5,
    textAlign: "right",
  },
  profileSection: {
    padding: 18,
    borderRadius: 22,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    marginBottom: 12,
  },
  profileSectionHeading: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 3,
  },
  optional: {
    color: colors.muted,
    fontSize: 9,
    fontWeight: "900",
    letterSpacing: 1.2,
  },
  badgeWrap: { alignItems: "center", width: 78 },
  badgeLabel: {
    color: colors.muted,
    fontSize: 10,
    fontWeight: "700",
    textAlign: "center",
    marginTop: 5,
  },
  profileHomeHero: {
    minHeight: 370,
    borderRadius: 28,
    overflow: "hidden",
    backgroundColor: colors.surface,
    padding: 20,
    alignItems: "center",
    marginBottom: 14,
  },
  profileHomeImage: {
    ...StyleSheet.absoluteFill,
    width: "100%",
    height: "100%",
  },
  profileHomeShade: {
    ...StyleSheet.absoluteFill,
    backgroundColor: "#07070894",
  },
  profileHomeTop: {
    width: "100%",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  profileEdit: {
    flexDirection: "row",
    alignItems: "center",
    gap: 5,
    paddingHorizontal: 11,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: "#08090ACC",
  },
  profileEditText: {
    color: colors.text,
    fontSize: 10,
    fontWeight: "900",
    letterSpacing: 1,
  },
  profileHomeAvatar: {
    width: 122,
    height: 122,
    borderRadius: 61,
    marginTop: 30,
    marginBottom: 16,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#242A1B",
    borderWidth: 4,
    borderColor: colors.mint,
  },
  profileHomeAvatarImage: { width: "100%", height: "100%", borderRadius: 61 },
  profileHomeName: {
    color: colors.text,
    fontSize: 30,
    lineHeight: 36,
    fontWeight: "900",
  },
  profileHomeMeta: {
    color: colors.text,
    opacity: 0.75,
    fontSize: 13,
    marginTop: 5,
  },
  profileHomeBio: {
    color: colors.text,
    opacity: 0.9,
    fontSize: 14,
    lineHeight: 20,
    textAlign: "center",
    marginTop: 13,
    maxWidth: 280,
  },
  profileStats: {
    flexDirection: "row",
    justifyContent: "space-around",
    paddingVertical: 17,
    borderRadius: 20,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line,
    marginBottom: 14,
  },
  profileStatValue: {
    color: colors.text,
    fontSize: 20,
    fontWeight: "900",
    textAlign: "center",
  },
  profileStatLabel: {
    color: colors.muted,
    fontSize: 9,
    fontWeight: "900",
    letterSpacing: 1.1,
    marginTop: 5,
    textAlign: "center",
  },
  profileSignalCard: {
    padding: 18,
    borderRadius: 22,
    borderWidth: 1,
    borderColor: colors.pinkBorder,
    backgroundColor: "#261622",
    marginBottom: 25,
  },
  profileHomeSection: { paddingBottom: 25 },
  profileMenuIcon: {
    width: 34,
    height: 34,
    borderRadius: 12,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#321B27",
    marginRight: 12,
  },
  homeProfilePill: {
    minHeight: 48,
    alignSelf: "stretch",
    flexDirection: "row",
    alignItems: "center",
    gap: 10,
    paddingHorizontal: 14,
    marginTop: 2,
    marginBottom: 18,
    borderRadius: 17,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
  },
  homeLocked: {
    minHeight: 180,
    backgroundColor: colors.surface,
    borderRadius: 24,
    borderWidth: 1,
    borderColor: colors.line,
    padding: 20,
    alignItems: "center",
    justifyContent: "center",
    marginBottom: 22,
  },
  homeVibeHero: {
    height: 235,
    borderRadius: 25,
    overflow: "hidden",
    marginBottom: 26,
    backgroundColor: colors.surface,
  },
  homeVibeImage: { ...StyleSheet.absoluteFill, width: "100%", height: "100%" },
  homeVibeShade: { ...StyleSheet.absoluteFill, backgroundColor: "#06060972" },
  homeVibeCopy: { flex: 1, justifyContent: "flex-end", padding: 20 },
  homeEyebrow: {
    color: colors.mint,
    fontSize: 10,
    letterSpacing: 1.8,
    fontWeight: "900",
    marginBottom: 8,
  },
  homeVibeName: {
    color: colors.text,
    fontSize: 34,
    lineHeight: 37,
    fontWeight: "900",
    letterSpacing: -0.6,
  },
  homeVibeMeta: {
    color: colors.text,
    opacity: 0.82,
    fontSize: 13,
    marginTop: 8,
  },
  homeVibeSpark: { position: "absolute", right: 18, top: 18 },
  homeSectionHeader: {
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "space-between",
    marginBottom: 4,
  },
  dashboardHeader: {
    minHeight: 72,
    paddingHorizontal: 20,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderBottomWidth: 1,
    borderBottomColor: colors.line,
  },
  dashboardHeaderActions: { flexDirection: "row", alignItems: "center", gap: 4 },
  dashboardAvatar: { width: 38, height: 38, borderRadius: 19, backgroundColor: colors.raised, borderWidth: 2, borderColor: colors.pink, alignItems: "center", justifyContent: "center", overflow: "hidden" },
  dashboardAvatarImage: { width: "100%", height: "100%" },
  dashboardAvatarText: { color: colors.text, fontSize: 13, fontWeight: "900" },
  dashboardVibeHero: { height: 246, borderRadius: 25, overflow: "hidden", marginBottom: 16, backgroundColor: colors.surface },
  dashboardVibeImage: { ...StyleSheet.absoluteFill, width: "100%", height: "100%" },
  dashboardVibeShade: { ...StyleSheet.absoluteFill, backgroundColor: "#0606099A" },
  dashboardVibeCopy: { flex: 1, justifyContent: "flex-end", padding: 20, paddingRight: 45 },
  dashboardLocked: { padding: 18, borderRadius: 20, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.line, marginBottom: 20 },
  dashboardSectionHeader: { flexDirection: "row", alignItems: "flex-end", justifyContent: "space-between", marginTop: 18, marginBottom: 8 },
  dashboardPlanCard: { padding: 18, borderRadius: 22, borderWidth: 1, borderColor: colors.pinkBorder, backgroundColor: "#24131D", marginBottom: 8 },
  dashboardPlanTop: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginBottom: 10 },
  dashboardPlanActions: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", borderTopWidth: 1, borderTopColor: "#FFFFFF20", paddingTop: 12, marginTop: 12 },
  planQuickActions: { flexDirection: "row", justifyContent: "space-between", paddingHorizontal: 6, paddingVertical: 11, marginBottom: 4 },
  planActionText: { color: colors.pink, fontSize: 10, fontWeight: "900", letterSpacing: 1.1 },
  dashboardEmpty: { padding: 18, borderRadius: 22, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.surface, marginBottom: 8 },
  dashboardRoomCard: { padding: 18, borderRadius: 22, borderWidth: 1, borderColor: colors.line, backgroundColor: colors.surface, marginBottom: 8 },
  dashboardLive: { flexDirection: "row", alignItems: "center", gap: 7, marginBottom: 8 },
  dashboardRoomMeta: { flexDirection: "row", alignItems: "center", justifyContent: "space-between", marginTop: 14 },
  dashboardChemistry: { color: colors.cyan, fontSize: 9, fontWeight: "900", letterSpacing: 1 },
  exploreGrid: { flexDirection: "row", gap: 8, marginBottom: 8 },
  exploreCard: { flex: 1, minHeight: 118, padding: 13, borderRadius: 18, backgroundColor: colors.surface, borderWidth: 1, borderColor: colors.line, justifyContent: "space-between" },
  exploreArea: { color: colors.text, fontSize: 15, fontWeight: "900" },
  nowPlaying: { minHeight: 64, paddingHorizontal: 20, paddingVertical: 9, flexDirection: "row", alignItems: "center", justifyContent: "space-between", backgroundColor: colors.raised, borderTopWidth: 1, borderTopColor: colors.pinkBorder },
  homeCityImage: { borderRadius: 23 },
  homeCityShade: { ...StyleSheet.absoluteFill, backgroundColor: "#06060980" },
  homeShelfLabel: {
    color: colors.pink,
    fontSize: 9,
    fontWeight: "900",
    letterSpacing: 1.2,
    marginBottom: 15,
  },
  homeVenueCard: {
    width: 275,
    height: 235,
    borderRadius: 22,
    overflow: "hidden",
    borderWidth: 1,
    borderColor: colors.line,
    marginRight: 12,
    backgroundColor: colors.surface,
  },
  homeVenueImage: { ...StyleSheet.absoluteFill, width: "100%", height: "100%" },
  homeVenueShade: { ...StyleSheet.absoluteFill, backgroundColor: "#06060980" },
  homeVenueContent: { flex: 1, padding: 16, justifyContent: "space-between" },
  homeVenueTop: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
  },
  homeVenueArea: {
    color: colors.text,
    fontSize: 9,
    fontWeight: "900",
    letterSpacing: 1.3,
  },
  homeVenueMatch: { fontSize: 10, fontWeight: "900", letterSpacing: 0.7 },
  homeVenueName: {
    color: colors.text,
    fontSize: 24,
    lineHeight: 27,
    fontWeight: "900",
    letterSpacing: 0.6,
    marginBottom: 6,
  },
  homeVenueMeta: {
    color: colors.text,
    opacity: 0.8,
    fontSize: 12,
    lineHeight: 18,
  },
  homeVenueAction: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    borderTopWidth: 1,
    borderTopColor: "#FFFFFF28",
    paddingTop: 11,
    marginTop: 13,
  },
  homeCityHeader: {
    flexDirection: "row",
    alignItems: "flex-end",
    justifyContent: "space-between",
    marginTop: 18,
  },
  homeCityCard: {
    height: 210,
    borderRadius: 23,
    overflow: "hidden",
    backgroundColor: "#171C26",
    borderWidth: 1,
    borderColor: colors.line,
    padding: 18,
    justifyContent: "flex-end",
    marginTop: 7,
  },
  cityPin: {
    position: "absolute",
    top: 25,
    right: 28,
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: colors.pink,
    alignItems: "center",
    justifyContent: "center",
    elevation: 8,
  },
  cityTitle: {
    color: colors.text,
    fontSize: 23,
    fontWeight: "900",
    marginBottom: 7,
  },
  pronouns: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 8,
    marginTop: 10,
    marginBottom: 18,
  },
  pronounChoice: {
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
    borderRadius: 20,
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  pronounSelected: { borderColor: colors.pink, backgroundColor: "#351323" },
  preferenceImage: {
    width: "100%",
    height: 230,
    borderRadius: radius.lg,
    marginVertical: 12,
    backgroundColor: colors.surface,
  },
  preferenceSwipeCard: { borderRadius: radius.lg, overflow: "hidden" },
  preferenceImageFallback: {
    width: "100%",
    height: 230,
    marginVertical: 12,
    borderRadius: radius.lg,
    backgroundColor: "#201b12",
    borderWidth: 1,
    borderColor: colors.amber,
    alignItems: "center",
    justifyContent: "center",
    paddingHorizontal: 24,
  },
  preferenceImageFallbackTitle: {
    color: colors.text,
    fontSize: 17,
    fontWeight: "900",
    textAlign: "center",
    marginTop: 10,
  },
  preferenceImageFallbackCopy: {
    color: colors.muted,
    fontSize: 12,
    textAlign: "center",
    marginTop: 6,
  },
  preferenceSwipeFeedback: {
    position: "absolute",
    left: 18,
    top: 18,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: colors.pink,
  },
  preferenceSwipeFeedbackText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 1,
  },
  senseOption: {
    overflow: "hidden",
    borderRadius: radius.md,
    marginBottom: 14,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
  },
  senseSelected: { borderColor: colors.pink, backgroundColor: "#25121C" },
  senseCheck: { position: "absolute", right: 14, top: 14 },
  senseBoth: {
    minHeight: 56,
    paddingHorizontal: 16,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    marginBottom: 14,
  },
  senseImage: { width: "100%", height: 170 },
  senseLabel: { padding: 14 },
  badges: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10,
    marginVertical: 14,
  },
  badgeImage: {
    width: 64,
    height: 64,
    borderRadius: 16,
    backgroundColor: colors.surface,
  },
  revealArtwork: {
    width: "100%",
    height: 260,
    borderRadius: radius.lg,
    marginVertical: 14,
    backgroundColor: colors.surface,
  },
  revealPoster: {
    width: "100%",
    minHeight: 220,
    borderRadius: radius.lg,
    padding: 22,
    justifyContent: "flex-end",
    marginVertical: 14,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.pink,
  },
  posterTitle: {
    color: colors.text,
    fontSize: 34,
    fontFamily: "sans-serif-condensed",
    fontWeight: "900",
    letterSpacing: 1.2,
  },
  cardArtwork: {
    width: "100%",
    height: 330,
    borderRadius: radius.lg,
    marginBottom: 22,
    backgroundColor: colors.surface,
  },
  cardArtworkLoading: {
    ...StyleSheet.absoluteFill,
    height: 330,
    borderRadius: radius.lg,
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: colors.surface,
    gap: 10,
  },
  cardArtworkLoadingText: {
    color: colors.muted,
    fontSize: 12,
    letterSpacing: 0.4,
  },
  cardArtworkFallback: {
    ...StyleSheet.absoluteFill,
    height: 330,
    borderRadius: radius.lg,
    alignItems: "center",
    justifyContent: "center",
    padding: 24,
    backgroundColor: colors.surface,
  },
  swipeGesture: { borderRadius: radius.lg, overflow: "hidden" },
  swipeFeedback: {
    position: "absolute",
    left: 18,
    top: 18,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    backgroundColor: colors.pink,
  },
  swipeFeedbackText: {
    color: colors.text,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 1,
  },
  assessmentActions: { gap: 4, paddingBottom: 24 },
});
