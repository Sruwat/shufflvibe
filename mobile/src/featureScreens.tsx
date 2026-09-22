import React, { useEffect, useState } from 'react';
import { Pressable, SafeAreaView, ScrollView, StyleSheet, Switch, Text, TextInput, View } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from './theme';
import { FeatureMode, useApp } from './store';
import { factors, preferences as preferenceFactors, venues } from './data';
import { getService, JoinerScores, JoinRequestRecord, PrivacySettings, RoomRecord } from './services';
import { latencyFirmness } from './fullEngine';

const reportReasons = ['Harassment', 'Spam or scam', 'Inappropriate content', 'Safety concern', 'Something else'];

function VenueDetailScreen() {
  const { selectedVenueName, set } = useApp();
  const venue = venues.find(item => item.name === selectedVenueName) ?? { name: selectedVenueName, type: 'Demo venue', area: 'Delhi NCR', tag: 'A place to make the night yours', color: '#20DDA9', scores: {} };
  const strengths = Object.entries(venue.scores).sort(([, a], [, b]) => b - a).slice(0, 3);
  return <SafeAreaView style={styles.safe}><FeatureHeader label="VENUE DETAIL" onBack={() => set({ screen: 'discover' })}/><ScrollView contentContainerStyle={styles.content}><View style={[styles.heroIcon, { backgroundColor: venue.color + '25' }]}><Ionicons name="location" size={34} color={venue.color}/></View><Text style={styles.eyebrow}>{venue.area.toUpperCase()} · {venue.type.toUpperCase()}</Text><Text style={styles.title}>{venue.name}</Text><Text style={styles.body}>{venue.tag}. A seeded demo venue profile; live opening status, booking, and map routing are not connected in this build.</Text><Text style={styles.eyebrow}>WHY IT MAY FIT</Text>{strengths.map(([factor, score]) => <View key={factor} style={styles.route}><Text style={styles.routeText}>{factor}</Text><Text style={styles.secondaryText}>{score}/100 · strong match</Text></View>)}<View style={styles.roomCard}><Text style={styles.routeText}>Place details</Text><Text style={styles.secondaryText}>Preference scores are demo data. Your exact location is never requested on this page.</Text></View><FeatureButton label="Open plan builder" onPress={() => set({ screen: 'feature', featureMode: 'activePlan' })}/><FeatureButton label="Back to discovery" onPress={() => set({ screen: 'discover' })} secondary/></ScrollView></SafeAreaView>;
}

function ReportSafetyScreen() {
  const { set } = useApp();
  const service = React.useMemo(() => getService(), []);
  const [targetId, setTargetId] = useState('demo-user-2');
  const [reason, setReason] = useState(reportReasons[0]);
  const [details, setDetails] = useState('');
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState('');
  const [blocked, setBlocked] = useState(false);
  useEffect(() => { let mounted = true; service.getBlockedUsers().then(items => { if (mounted) setBlocked(items.includes(targetId.trim())); }).catch(() => undefined); return () => { mounted = false; }; }, [service, targetId]);
  const submit = async () => {
    if (!targetId.trim()) { setMessage('Enter the profile ID you want to report.'); return; }
    setBusy(true); setMessage('');
    try { const result = await service.submitReport(targetId.trim(), `${reason}${details.trim() ? `: ${details.trim()}` : ''}`); setMessage(`Report received · ${result.id}`); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Could not submit report. Try again.'); }
    finally { setBusy(false); }
  };
  const toggleBlock = async () => {
    if (!targetId.trim()) { setMessage('Enter the profile ID you want to block.'); return; }
    setBusy(true); setMessage('');
    try { const result = blocked ? await service.unblockUser(targetId.trim()) : await service.blockUser(targetId.trim()); setBlocked(result.blocked); setMessage(result.blocked ? 'Profile blocked in this SHUFFL account.' : 'Profile unblocked.'); }
    catch (error) { setMessage(error instanceof Error ? error.message : 'Could not update block state.'); }
    finally { setBusy(false); }
  };
  return <SafeAreaView style={styles.safe}><FeatureHeader label="SAFETY" onBack={() => set({ screen: 'feature', featureMode: 'visitor' })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>REPORT & BLOCK</Text><Text style={styles.title}>Your safety comes first</Text><Text style={styles.body}>Reports are recorded for review. Blocking is an account-level demo state; because this build has no sign-in or server authorization, it cannot enforce blocks across real accounts.</Text><Text style={styles.fieldLabel}>PROFILE ID</Text><TextInput accessibilityLabel="Profile ID to report or block" autoCapitalize="none" value={targetId} onChangeText={setTargetId} style={styles.input} placeholder="Profile ID" placeholderTextColor={colors.muted}/><Text style={styles.fieldLabel}>WHY ARE YOU REPORTING?</Text>{reportReasons.map(item => <Pressable key={item} accessibilityRole="radio" accessibilityState={{ selected: reason === item }} onPress={() => setReason(item)} style={[styles.reason, reason === item && styles.reasonSelected]}><Text style={styles.routeText}>{item}</Text><Ionicons name={reason === item ? 'radio-button-on' : 'radio-button-off'} size={20} color={reason === item ? colors.mint : colors.muted}/></Pressable>)}<TextInput accessibilityLabel="Optional report details" value={details} onChangeText={setDetails} style={[styles.input, styles.multiline]} placeholder="Optional details (do not include exact location)" placeholderTextColor={colors.muted} multiline maxLength={1600} textAlignVertical="top"/><FeatureButton label={busy ? 'Submitting…' : 'Submit report'} onPress={submit}/><FeatureButton label={busy ? 'Please wait…' : blocked ? 'Unblock this profile' : 'Block this profile'} onPress={toggleBlock} secondary/>{message ? <Text accessibilityRole="alert" style={styles.notice}>{message}</Text> : null}<Text style={styles.disclaimer}>Only include information needed to understand the safety concern. This demo does not notify or contact an external moderation team.</Text></ScrollView></SafeAreaView>;
}

const content: Record<FeatureMode, { eyebrow: string; title: string; body: string; action: string; next?: FeatureMode; icon: keyof typeof Ionicons.glyphMap }> = {
  venue:{eyebrow:'VENUE DETAIL',title:'Sidecar, GK-2',body:'Buzzy, easy to settle into · Greater Kailash II. Venue media, review notes, pinboard, and preference fit are kept together here.',action:'Add to plan',next:'activePlan',icon:'location-outline'},
  activePlan:{eyebrow:'PERSONAL PLAN',title:'Settle Then Roam',body:'Friday · 8:30 PM – 12:30 AM. Three stops, travel time, approximate arrival windows, and the reason each stop made the cut.',action:'Lock plan',next:'arrival',icon:'map-outline'},
  arrival:{eyebrow:'ACTIVE PLAN',title:'You have arrived',body:'Location sharing is off by default. Arrival is a private state for your plan, not an exact location signal to other people.',action:'End plan',next:'feedback',icon:'flag-outline'},
  feedback:{eyebrow:'STOP FEEDBACK',title:'How did this stop feel?',body:'Rate the room, the conversation, and whether it delivered what the plan promised. Feedback improves venue confidence.',action:'Save feedback',next:'activePlan',icon:'star-outline'},
  hostRoom:{eyebrow:'HOST A ROOM',title:'Give the night a reason',body:'Add co-hosts, choose a room plan, set visibility, and publish. Exact locations stay hidden until the plan consent state allows them.',action:'Add co-hosts',next:'joinRequests',icon:'people-outline'},
  joinRequests:{eyebrow:'JOIN REQUESTS',title:'People who want in',body:'Review requests, see compatibility bands, and accept people without exposing anyone’s exact location.',action:'Open capsule',next:'capsule',icon:'person-add-outline'},
  capsule:{eyebrow:'CAPSULE',title:'A smaller circle inside the room',body:'Members approve before joining. The capsule can be invite-only, friends-only, or opened to the room.',action:'Approve member',next:'chat',icon:'lock-open-outline'},
  notifications:{eyebrow:'NOTIFICATIONS',title:'Stay in the loop',body:'Room requests, plan changes, approvals, and support updates live here. No silent social state changes.',action:'Open inbox',next:'inbox',icon:'notifications-outline'},
  inbox:{eyebrow:'INBOX',title:'Your conversations',body:'Direct messages and group conversations stay separate from the plan. Unread state is explicit.',action:'Open group chat',next:'chat',icon:'mail-outline'},
  chat:{eyebrow:'GROUP CHAT',title:'Friday room',body:'Talk through arrival, plan edits, and the next stop. The demo uses local seeded messages and keeps private content scoped.',action:'View active plan',next:'activePlan',icon:'chatbubbles-outline'},
  visitor:{eyebrow:'VISITOR PROFILE',title:'Someone from the room',body:'See shared vibe context, mutual rooms, and safety controls. No exact location or unrestricted private content is shown.',action:'Report or block',next:'report',icon:'person-outline'},
  editProfile:{eyebrow:'EDIT PROFILE',title:'Keep it current',body:'Update your name, bio, pronouns, photo, preferences, and privacy choices. Vibe history remains immutable per session.',action:'Save profile',next:'history',icon:'create-outline'},
  history:{eyebrow:'VIBE HISTORY',title:'Your nights have a shape',body:'Review frozen daily names, preference badges, and past plans without rewriting history when the population centre changes.',action:'Open past plans',next:'activePlan',icon:'time-outline'},
  privacy:{eyebrow:'PRIVACY & SAFETY',title:'You choose what is shared',body:'Location is off by default. Presence is approximate. Per-plan consent, report, block, and data contribution controls are visible.',action:'Open settings',next:'settings',icon:'shield-checkmark-outline'},
  settings:{eyebrow:'SETTINGS',title:'Make SHUFFL yours',body:'Demo mode, notifications, privacy, support, account, and accessibility preferences are all reachable from one place.',action:'Privacy & safety',next:'privacy',icon:'settings-outline'},
  report:{eyebrow:'SAFETY',title:'Report or block',body:'Choose a reason, block immediately if needed, and send a report for review. The user is not notified of the report details.',action:'Send report',next:'settings',icon:'flag-outline'},
  joinRoom:{eyebrow:'FIND A ROOM',title:'Join a night with a reason',body:'Browse hosted rooms and ask to join. Hosts review requests before anyone is added.',action:'Browse hosted rooms',icon:'people-outline'},
  support:{eyebrow:'SUPPORT',title:'Need a hand?',body:'Account help, safety questions, and plan issues are routed to a clear support state instead of dead-ending.',action:'Back to settings',next:'settings',icon:'help-circle-outline'},
};

function FeatureButton({ label, onPress, secondary = false }: { label: string; onPress: () => void; secondary?: boolean }) { return <Pressable onPress={onPress} style={secondary ? styles.secondary : styles.primary}><Text style={secondary ? styles.secondaryText : styles.primaryText}>{label}</Text></Pressable>; }
function FeatureHeader({ label, onBack }: { label: string; onBack: () => void }) { return <View style={styles.header}><Pressable onPress={onBack} style={styles.back}><Ionicons name="arrow-back" size={22} color={colors.text}/></Pressable><Text style={styles.headerLabel}>{label}</Text><Ionicons name="sparkles-outline" size={22} color={colors.mint}/></View>; }
function HostRoomScreen() {
  const { room, plan, preferences: preferenceState, scores, set } = useApp();
  const [confirm, setConfirm] = useState<'create' | 'host' | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const addCohost = () => set({ room: { ...room, cohosts: ['Bela'], members: ['Aarav', 'Bela'] } });
  const createPlan = async () => {
    if (!room.cohosts.length && confirm !== 'create') return setConfirm('create');
    if (busy) return;
    setBusy(true); setError('');
    try {
      const service = getService();
      const vibeScores = Object.fromEntries(factors.map((factor) => [factor, scores[factor] ?? 50]));
      const preferenceScores = Object.fromEntries(preferenceFactors.map((factor) => [factor, preferenceState.readings[factor]?.score ?? 50]));
      const generated = await service.generatePlan({ scores: vibeScores, preferences: preferenceScores, pol_sense: preferenceState.sense ?? 'both', members: room.members });
      const createdRoom = room.id ? { id: room.id } : await service.createRoom(room.name, room.members);
      set({ room: { ...room, id: createdRoom.id }, plan: { ...plan, id: generated.id, exists: true, locked: false, style: generated.style, stops: generated.stops, chemistry: generated.chemistry } });
      setConfirm(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not create the plan. Please try again.');
    } finally { setBusy(false); }
  };
  const host = async () => {
    if (!plan.exists || !room.id || !plan.id || busy) return;
    if (!room.cohosts.length && confirm !== 'host') return setConfirm('host');
    setBusy(true); setError('');
    try {
      await getService().hostRoom(room.id, plan.id);
      set({ room: { ...room, public: true }, plan: { ...plan, locked: true } });
      setConfirm(null);
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not host this room. Please try again.');
    } finally { setBusy(false); }
  };
  const confirmAction = () => confirm === 'host' ? host() : createPlan();
  return <SafeAreaView style={styles.safe}><FeatureHeader label="HOST A ROOM" onBack={() => set({ screen: 'control' })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>ROOM SETUP</Text><Text style={styles.title}>{room.name}</Text><Text style={styles.body}>{room.public ? 'Room is public. The plan and chemistry are now frozen for everyone who joins.' : 'Build the room privately, make the plan, then host it when the room is ready.'}</Text><View style={styles.routeList}>{room.members.map(member => <View key={member} style={styles.route}><Text style={styles.routeText}>{member} · today’s vibe</Text><Text style={styles.secondaryText}>{member === 'Aarav' ? 'HOST' : 'CO-HOST'}</Text></View>)}</View>{!room.public && !plan.exists && !room.cohosts.length && <FeatureButton label="Add a co-host" onPress={addCohost}/>} {!room.public && !plan.exists && <FeatureButton label={busy ? 'Building plan…' : 'Create plan'} onPress={createPlan} secondary={!!room.cohosts.length}/>} {error ? <Text accessibilityRole="alert" style={styles.secondaryText}>{error}</Text> : null}{confirm && <View style={styles.route}><Text style={styles.body}>{confirm === 'host' ? 'You will not be able to add co-hosts after hosting this room. Continue?' : 'This plan is just for you because you have not added co-hosts. Continue?'}</Text><FeatureButton label={busy ? 'Please wait…' : 'Continue'} onPress={confirmAction}/><FeatureButton label="Cancel" onPress={() => setConfirm(null)} secondary/></View>} {plan.exists && <View style={styles.routeList}><Text style={styles.eyebrow}>{plan.style} · {plan.locked ? 'LOCKED' : 'PRIVATE DRAFT'}</Text>{plan.stops.map((stop, index) => <View key={`${index}-${stop}`} style={styles.route}><Text style={styles.routeText}>{index + 1}. {stop}</Text></View>)}</View>} {plan.exists && !room.public && <FeatureButton label={busy ? 'Hosting…' : 'Host room'} onPress={host}/>} {room.public && <FeatureButton label="Open join requests" onPress={() => set({ screen: 'feature', featureMode: 'joinRequests' })} secondary/>} {plan.exists && <FeatureButton label="View plan" onPress={() => set({ screen: 'feature', featureMode: 'activePlan' })} secondary/>}</ScrollView></SafeAreaView>;
}
function ArrivalScreen() {
  const { plan, set } = useApp();
  const [consented, setConsented] = useState(false);
  const [allowed, setAllowed] = useState(false);
  const [loading, setLoading] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    if (!plan.id || !plan.exists) return () => { active = false; };
    setLoading(true);
    Promise.all([getService().getPrivacy(), getService().getPlanLocationConsent(plan.id)]).then(([privacy, consent]) => {
      if (active) { setAllowed(privacy.location_sharing); setConsented(consent.approved); }
    }).catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : 'Could not load arrival consent.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, [plan.id, plan.exists]);
  const toggleConsent = async () => {
    if (!plan.id || busy) return;
    setBusy(true); setError('');
    try { const result = await getService().savePlanLocationConsent(plan.id, !consented); setConsented(result.approved); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not update consent.'); }
    finally { setBusy(false); }
  };
  return <SafeAreaView style={styles.safe}><FeatureHeader label="ARRIVAL & CONSENT" onBack={() => set({ screen: 'feature', featureMode: 'activePlan' })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>PLAN CHECK-IN</Text><Text style={styles.title}>You have arrived</Text><Text style={styles.body}>The demo does not read GPS or expose exact coordinates. You can separately opt in to approximate presence for this plan.</Text>{!plan.exists || !plan.id ? <Text style={styles.secondaryText}>Create a plan before setting arrival consent.</Text> : <View style={styles.route}><View style={{ flex: 1, paddingRight: 12 }}><Text style={styles.routeText}>Approximate presence for this plan</Text><Text style={styles.secondaryText}>{loading ? 'Checking saved consent…' : allowed ? consented ? 'Shared as approximate presence' : 'Not shared' : 'Turn on per-plan permission in Privacy & Safety first'}</Text></View><Switch value={consented} disabled={loading || busy || !allowed} onValueChange={toggleConsent} trackColor={{ false: '#35413F', true: '#32D6B0' }} thumbColor={consented ? '#07100E' : '#E8EFEC'} accessibilityLabel="Approximate presence for this plan"/></View>}{error ? <Text accessibilityRole="alert" style={styles.secondaryText}>{error}</Text> : null}{!allowed && plan.id ? <FeatureButton label="Open Privacy & Safety" onPress={() => set({ screen: 'feature', featureMode: 'privacy' })} secondary/> : null}<FeatureButton label="End plan" onPress={() => set({ screen: 'feature', featureMode: 'feedback' })}/></ScrollView></SafeAreaView>;
}

function PrivacySafetyScreen() {
  const { set } = useApp();
  const [settings, setSettings] = useState<PrivacySettings | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  useEffect(() => {
    let active = true;
    getService().getPrivacy().then((result) => { if (active) setSettings(result); }).catch((cause) => { if (active) setError(cause instanceof Error ? cause.message : 'Could not load privacy settings.'); }).finally(() => { if (active) setLoading(false); });
    return () => { active = false; };
  }, []);
  const update = (patch: Partial<PrivacySettings>) => { if (!settings) return; setSettings({ ...settings, ...patch }); setMessage(''); };
  const cycleVisibility = (key: string) => {
    if (!settings) return;
    const current = settings.visibility[key] ?? 'friends';
    const next = current === 'everyone' ? 'friends' : current === 'friends' ? 'nobody' : 'everyone';
    update({ visibility: { ...settings.visibility, [key]: next } });
  };
  const save = async () => {
    if (!settings || saving) return;
    setSaving(true); setError(''); setMessage('');
    try { setSettings(await getService().savePrivacy(settings)); setMessage('Your privacy settings are saved.'); }
    catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not save privacy settings.'); }
    finally { setSaving(false); }
  };
  const row = (title: string, detail: string, value: boolean, onChange: (value: boolean) => void) => <View key={title} style={styles.route}><View style={{ flex: 1, paddingRight: 16 }}><Text style={styles.routeText}>{title}</Text><Text style={styles.secondaryText}>{detail}</Text></View><Switch value={value} onValueChange={onChange} trackColor={{ false: '#35413F', true: '#32D6B0' }} thumbColor={value ? '#07100E' : '#E8EFEC'} accessibilityLabel={title}/></View>;
  return <SafeAreaView style={styles.safe}><FeatureHeader label="PRIVACY & SAFETY" onBack={() => set({ screen: 'control' })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>YOUR CONTROLS</Text><Text style={styles.title}>You choose what is shared</Text><Text style={styles.body}>Exact location is not shown to other members. Presence is approximate, and plan-level sharing still requires consent.</Text>{loading ? <Text style={styles.secondaryText}>Loading your saved choices…</Text> : !settings ? <Text accessibilityRole="alert" style={styles.secondaryText}>{error || 'Privacy settings are unavailable.'}</Text> : <>
    {row('Allow per-plan location sharing', 'Off by default. This does not enable sharing for a plan without your consent.', settings.location_sharing, (value) => update({ location_sharing: value }))}
    {row('Approximate group presence', 'Share a broad arrival/presence state, never an exact position.', settings.approximate_presence, (value) => update({ approximate_presence: value }))}
    {row('Discoverability', 'Allow your profile to appear in eligible room and discovery surfaces.', settings.discoverability, (value) => update({ discoverability: value }))}
    <Text style={styles.eyebrow}>WHO CAN SEE WHAT</Text>
    {(['profile', 'vibe', 'plans'] as const).map((key) => <Pressable key={key} accessibilityRole="button" accessibilityLabel={`Change ${key} visibility`} onPress={() => cycleVisibility(key)} style={styles.route}><View><Text style={styles.routeText}>{key === 'profile' ? 'Profile' : key === 'vibe' ? 'Vibe context' : 'Plans'}</Text><Text style={styles.secondaryText}>Tap to change access</Text></View><Text style={styles.secondaryText}>{settings.visibility[key] ?? 'friends'} ›</Text></Pressable>)}
    {error ? <Text accessibilityRole="alert" style={styles.secondaryText}>{error}</Text> : null}{message ? <Text accessibilityRole="alert" style={styles.secondaryText}>{message}</Text> : null}<FeatureButton label={saving ? 'Saving…' : 'Save privacy choices'} onPress={save}/>
  </>}<FeatureButton label="Report or block someone" onPress={() => set({ screen: 'feature', featureMode: 'report' })} secondary/></ScrollView></SafeAreaView>;
}

function ActivePlanScreen() {
  const { room, plan, scores, preferences: preferenceState, set } = useApp();
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const generate = async () => {
    if (busy || plan.locked || room.public) return;
    setBusy(true); setError('');
    try {
      const vibeScores = Object.fromEntries(factors.map((factor) => [factor, scores[factor] ?? 50]));
      const preferenceScores = Object.fromEntries(preferenceFactors.map((factor) => [factor, preferenceState.readings[factor]?.score ?? 50]));
      const generated = await getService().generatePlan({ scores: vibeScores, preferences: preferenceScores, pol_sense: preferenceState.sense ?? 'both', members: room.members });
      set({ plan: { ...plan, id: generated.id, exists: true, locked: false, style: generated.style, stops: generated.stops, chemistry: generated.chemistry } });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not build a plan. Please try again.');
    } finally { setBusy(false); }
  };
  const lock = async () => {
    if (!plan.id || busy || plan.locked || room.public) return;
    setBusy(true); setError('');
    try {
      await getService().lockPlan(plan.id);
      set({ plan: { ...plan, locked: true } });
    } catch (cause) {
      setError(cause instanceof Error ? cause.message : 'Could not lock this plan. Please try again.');
    } finally { setBusy(false); }
  };
  return <SafeAreaView style={styles.safe}>
    <FeatureHeader label="ACTIVE PLAN" onBack={() => set({ screen: 'control' })}/>
    <ScrollView contentContainerStyle={styles.content}>
      <Text style={styles.eyebrow}>{room.public ? 'HOSTED PLAN' : plan.exists ? 'PRIVATE PLAN' : 'PLAN BUILDER'}</Text>
      <Text style={styles.title}>{plan.exists ? plan.style : 'Your night, shaped around you'}</Text>
      <Text style={styles.body}>{room.public ? 'This plan is frozen for the hosted room.' : plan.locked ? 'This plan is locked. Its chemistry and stops will not change.' : plan.exists ? 'Review the selected stops. Refresh recalculates from your current vibe and preference answers.' : 'No plan has been created yet. Build one from your completed vibe and preference answers.'}</Text>
      {plan.exists ? plan.stops.map((stop, index) => <View key={`${index}-${stop}`} style={styles.route}><Text style={styles.routeText}>{index + 1}. {stop}</Text><Text style={styles.secondaryText}>{index === 0 ? 'START' : 'NEXT STOP'}</Text></View>) : <View style={styles.route}><Text style={styles.secondaryText}>Your plan will appear here after generation.</Text></View>}
      {error ? <Text accessibilityRole="alert" style={styles.secondaryText}>{error}</Text> : null}
      {!plan.exists && <FeatureButton label={busy ? 'Building plan…' : 'Build my plan'} onPress={generate}/>}
      {plan.exists && !plan.locked && !room.public && <FeatureButton label={busy ? 'Locking…' : 'Lock this plan'} onPress={lock}/>}
      {plan.exists && !plan.locked && !room.public && <FeatureButton label={busy ? 'Recalculating…' : 'Refresh from my answers'} onPress={generate} secondary/>}
      {!plan.exists && <FeatureButton label="Set up a hosted room" onPress={() => set({ screen: 'feature', featureMode: 'hostRoom' })} secondary/>}
      {plan.exists && <FeatureButton label="Mark arrival" onPress={() => set({ screen: 'feature', featureMode: 'arrival' })} secondary/>}
    </ScrollView>
  </SafeAreaView>;
}
function JoinRoomScreen() {
  const { set, scores, assessment } = useApp();
  const service = React.useMemo(() => getService(), []);
  const [rooms, setRooms] = useState<RoomRecord[]>([]);
  const [requests, setRequests] = useState<Record<string, JoinRequestRecord>>({});
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const joinerScores = React.useMemo(() => { const vector = Object.fromEntries(factors.map(factor => [factor, scores[factor] ?? 50])) as JoinerScores; vector.latency_firmness = latencyFirmness(assessment); return vector; }, [scores, assessment]);
  useEffect(() => { let active = true; service.listHostedRooms().then(async items => { if (!active) return; const [fits, existing] = await Promise.all([Promise.all(items.map(async room => [room.id, await service.getRoomEligibility(room.id, joinerScores)] as const)), Promise.all(items.map(async room => [room.id, (await service.getJoinRequests(room.id, 'all')).find(item => item.member_id === 'demo-visitor')] as const))]); if (!active) return; const fitByRoom = Object.fromEntries(fits); setRooms(items.map(room => ({ ...room, join_eligibility: fitByRoom[room.id] }))); setRequests(Object.fromEntries(existing.filter((entry): entry is readonly [string, JoinRequestRecord] => Boolean(entry[1])).map(([roomId, item]) => [roomId, item]))); }).catch(cause => { if (active) setError(cause instanceof Error ? cause.message : 'Could not load hosted rooms.'); }); return () => { active = false; }; }, [service, joinerScores]);
  const requestJoin = async (room: RoomRecord) => { setBusy(true); setError(''); try { const result = await service.requestToJoin(room.id, 'demo-visitor', 'I would like to join this room.', joinerScores); setRequests(current => ({ ...current, [room.id]: result })); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not request to join.'); } finally { setBusy(false); } };
  return <SafeAreaView style={styles.safe}><FeatureHeader label="FIND A ROOM" onBack={() => set({ screen: 'rooms' })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>HOSTED NIGHTS</Text><Text style={styles.title}>Find your people</Text><Text style={styles.body}>Every hosted night is checked against your vibe bend before a request can be sent. Venue preferences help rank stops; they never decide admission.</Text>{rooms.map(room => { const existing = requests[room.id]; const fit = room.join_eligibility; return <View key={room.id} style={styles.roomCard}><Text style={styles.routeText}>{room.title}</Text><Text style={styles.secondaryText}>{room.members?.length ?? 0} members · {room.status}</Text>{room.stop_types?.length ? <Text style={styles.secondaryText}>{room.stop_count} stop{room.stop_count === 1 ? '' : 's'} · {room.stop_types.join(' → ')}</Text> : null}{fit?.eligible ? <Text style={styles.notice}>Vibe fit · every stop and the night’s ROAM count are inside your bend</Text> : <Text style={styles.secondaryText}>Not a fit for this frozen plan{fit?.reasons?.length ? ': ' + fit.reasons.join(' · ') : ' · eligibility unavailable'}</Text>}{existing ? <Text style={styles.notice}>{existing.status === 'pending' ? 'Request sent · waiting for host' : 'Request ' + existing.status}</Text> : fit?.eligible ? <FeatureButton label={busy ? 'Sending…' : 'Request to join'} onPress={() => requestJoin(room)}/> : null}</View>; })}{!rooms.length && !error && <View style={styles.route}><Text style={styles.body}>No hosted rooms are available right now.</Text></View>}{error ? <Text accessibilityRole="alert" style={styles.notice}>{error}</Text> : null}<FeatureButton label="Host a room instead" onPress={() => set({ screen: 'feature', featureMode: 'hostRoom' })} secondary/></ScrollView></SafeAreaView>;
}
function JoinRequestsScreen() {
  const { room, set } = useApp();
  const service = React.useMemo(() => getService(), []);
  const [requests, setRequests] = useState<JoinRequestRecord[]>([]);
  const [busyId, setBusyId] = useState('');
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const reload = React.useCallback(async () => { if (!room.id) { setRequests([]); return; } try { setRequests(await service.getJoinRequests(room.id)); setError(''); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not load join requests.'); } }, [room.id, service]);
  useEffect(() => { void reload(); }, [reload]);
  const decide = async (request: JoinRequestRecord, status: 'accepted' | 'declined') => { if (!room.id || busyId) return; setBusyId(request.id); setError(''); setNotice(''); try { const result = await service.decideJoinRequest(room.id, request.id, status); setRequests(items => items.filter(item => item.id !== request.id)); if (status === 'accepted') set({ room: { ...room, members: [...new Set([...room.members, request.member_id])], accepted: [...new Set([...room.accepted, request.member_id])] } }); setNotice(status === 'accepted' ? request.member_id + ' joined. Hosted plan remains frozen.' : 'Request declined.'); if (!result.plan_frozen) setNotice('Request updated.'); } catch (cause) { setError(cause instanceof Error ? cause.message : 'Could not resolve this request.'); } finally { setBusyId(''); } };
  return <SafeAreaView style={styles.safe}><FeatureHeader label="JOIN REQUESTS" onBack={() => set({ screen: 'feature', featureMode: 'hostRoom' })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>{room.public ? 'ROOM IS HOSTED' : 'ROOM NOT HOSTED'}</Text><Text style={styles.title}>People who want in</Text><Text style={styles.body}>Review each request explicitly. Accepting adds the requester’s member ID and keeps the hosted plan unchanged. Full spec plan-fit screening is not yet implemented.</Text>{error ? <Text accessibilityRole="alert" style={styles.notice}>{error}</Text> : null}{notice ? <Text accessibilityRole="alert" style={styles.notice}>{notice}</Text> : null}{requests.map(request => <View key={request.id} style={styles.requestCard}><Text style={styles.routeText}>{request.member_id}</Text><Text style={styles.secondaryText}>{request.note || 'No note provided'}</Text><Text style={styles.disclaimer}>Requests can only enter this queue after the frozen-plan shape-fit gate passes. Preference fit never gates admission.</Text><View style={styles.requestActions}><Pressable accessibilityRole="button" accessibilityLabel={'Accept request from ' + request.member_id} disabled={!!busyId} onPress={() => decide(request, 'accepted')}><Ionicons name="checkmark-circle" size={30} color={colors.mint}/></Pressable><Pressable accessibilityRole="button" accessibilityLabel={'Decline request from ' + request.member_id} disabled={!!busyId} onPress={() => decide(request, 'declined')}><Ionicons name="close-circle" size={30} color={colors.danger}/></Pressable></View></View>)}{!requests.length && !error && <View style={styles.route}><Text style={styles.body}>No pending join requests.</Text></View>}<FeatureButton label="Refresh requests" onPress={() => void reload()} secondary/><FeatureButton label="Open capsule" onPress={() => set({ screen: 'feature', featureMode: 'capsule' })} secondary/></ScrollView></SafeAreaView>;
}
function CapsuleScreen() { const { capsule, set } = useApp(); const approve = (member: string) => set({ capsule: { ...capsule, approvals: { ...capsule.approvals, [member]: true } } }); return <SafeAreaView style={styles.safe}><FeatureHeader label="CAPSULE" onBack={() => set({ screen: 'feature', featureMode: 'joinRequests' })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>SHUFFL CAPSULE</Text><Text style={styles.title}>A smaller circle inside the room</Text><Text style={styles.body}>Everyone approves before the capsule request reaches the host. Exact locations stay hidden until the room consent state allows them.</Text>{capsule.members.map(member => <View key={member} style={styles.route}><View><Text style={styles.routeText}>{member}</Text><Text style={styles.secondaryText}>{capsule.approvals[member] ? 'APPROVED' : 'WAITING FOR APPROVAL'}</Text></View>{!capsule.approvals[member] && <Pressable onPress={() => approve(member)}><Ionicons name="checkmark-circle-outline" size={28} color={colors.mint}/></Pressable>}</View>)}<FeatureButton label={capsule.members.every(member => capsule.approvals[member]) ? 'Request to join room' : 'Waiting for capsule approval'} onPress={() => set({ screen: 'feature', featureMode: 'notifications' })}/></ScrollView></SafeAreaView>; }
function ChatScreen() { const { set } = useApp(); const [sent, setSent] = useState(false); return <SafeAreaView style={styles.safe}><FeatureHeader label="GROUP CHAT" onBack={() => set({ screen: 'feature', featureMode: 'inbox' })}/><ScrollView contentContainerStyle={styles.content}><Text style={styles.eyebrow}>FRIDAY ROOM</Text><Text style={styles.title}>Talk through the night</Text><View style={styles.route}><Text style={styles.routeText}>Aarav</Text><Text style={styles.secondaryText}>Should we start at Sidecar?</Text></View><View style={styles.route}><Text style={styles.routeText}>Bela</Text><Text style={styles.secondaryText}>The plan is in. I’m in for the first stop.</Text></View>{sent && <View style={styles.route}><Text style={styles.routeText}>You</Text><Text style={styles.secondaryText}>I’ll share arrival details privately.</Text></View>}<FeatureButton label={sent ? 'Message sent' : 'Send arrival message'} onPress={() => setSent(true)}/><FeatureButton label="View active plan" onPress={() => set({ screen: 'feature', featureMode: 'activePlan' })} secondary/></ScrollView></SafeAreaView>; }

export function FeatureScreen({ mode }: { mode: FeatureMode }) {
  const { set } = useApp();
  if (mode === 'venue') return <VenueDetailScreen/>;
  if (mode === 'privacy') return <PrivacySafetyScreen/>;
  if (mode === 'arrival') return <ArrivalScreen/>;
  if (mode === 'hostRoom') return <HostRoomScreen/>;
  if (mode === 'activePlan') return <ActivePlanScreen/>;
  if (mode === 'joinRequests') return <JoinRequestsScreen/>;
  if (mode === 'joinRoom') return <JoinRoomScreen/>;
  if (mode === 'capsule') return <CapsuleScreen/>;
  if (mode === 'chat') return <ChatScreen/>;
  if (mode === 'report') return <ReportSafetyScreen/>;
  const item = content[mode];
  const go = () => item.next ? set({ screen: 'feature', featureMode: item.next }) : set({ screen: 'profileHome' });
  return <SafeAreaView style={styles.safe}><View style={styles.header}><Pressable onPress={() => set({ screen: 'control' })} style={styles.back}><Ionicons name="arrow-back" size={22} color={colors.text}/></Pressable><Text style={styles.headerLabel}>{item.eyebrow}</Text><Ionicons name={item.icon} size={22} color={colors.mint}/></View><ScrollView contentContainerStyle={styles.content}><View style={styles.heroIcon}><Ionicons name={item.icon} size={34} color={colors.mint}/></View><Text style={styles.eyebrow}>{item.eyebrow}</Text><Text style={styles.title}>{item.title}</Text><Text style={styles.body}>{item.body}</Text><Pressable onPress={go} style={styles.primary}><Text style={styles.primaryText}>{item.action}</Text></Pressable>{mode==='settings'&&<View style={styles.routeList}>{(Object.keys(content) as FeatureMode[]).map((route)=><Pressable key={route} onPress={()=>set({screen:'feature',featureMode:route})} style={styles.route}><Text style={styles.routeText}>{content[route].eyebrow}</Text><Ionicons name="chevron-forward" size={18} color={colors.muted}/></Pressable>)}</View>}<Pressable onPress={() => set({ screen: 'feature', featureMode: 'settings' })} style={styles.secondary}><Text style={styles.secondaryText}>Open feature hub</Text></Pressable></ScrollView></SafeAreaView>;
}

const styles = StyleSheet.create({safe:{flex:1,backgroundColor:colors.bg},header:{height:76,paddingHorizontal:20,flexDirection:'row',alignItems:'center',justifyContent:'space-between'},back:{width:44,height:44,alignItems:'center',justifyContent:'center'},headerLabel:{color:colors.muted,fontSize:12,letterSpacing:1.3},content:{padding:20,paddingBottom:100},heroIcon:{width:72,height:72,borderRadius:24,backgroundColor:'#12332D',alignItems:'center',justifyContent:'center',marginBottom:24},eyebrow:{color:colors.mint,fontSize:11,letterSpacing:1.7,fontWeight:'800',marginBottom:12},title:{color:colors.text,fontSize:34,lineHeight:40,fontWeight:'800',marginBottom:14},body:{color:colors.muted,fontSize:16,lineHeight:24,marginBottom:24},primary:{minHeight:54,borderRadius:16,backgroundColor:colors.mint,alignItems:'center',justifyContent:'center',marginTop:8},primaryText:{color:colors.bg,fontWeight:'800',fontSize:15},roomCard:{padding:16,borderWidth:1,borderColor:colors.line,borderRadius:18,backgroundColor:colors.raised,marginBottom:14},requestCard:{padding:14,borderWidth:1,borderColor:colors.line,borderRadius:14,marginBottom:12},requestActions:{flexDirection:'row',justifyContent:'flex-end',gap:20,marginTop:8},routeList:{marginTop:18,borderTopWidth:1,borderTopColor:colors.line},route:{minHeight:50,borderBottomWidth:1,borderBottomColor:colors.line,flexDirection:'row',alignItems:'center',justifyContent:'space-between'},fieldLabel:{color:colors.mint,fontSize:11,letterSpacing:1.4,fontWeight:'800',marginTop:18,marginBottom:8},input:{minHeight:50,borderRadius:14,borderWidth:1,borderColor:colors.line,backgroundColor:colors.raised,paddingHorizontal:14,color:colors.text,fontSize:15,marginBottom:8},multiline:{minHeight:104,paddingTop:12},reason:{minHeight:48,flexDirection:'row',alignItems:'center',justifyContent:'space-between',paddingHorizontal:12,borderWidth:1,borderColor:colors.line,borderRadius:12,marginBottom:8},reasonSelected:{borderColor:colors.mint,backgroundColor:'#102923'},notice:{color:colors.mint,fontSize:14,lineHeight:20,marginTop:16},disclaimer:{color:colors.muted,fontSize:12,lineHeight:18,marginTop:16},routeText:{color:colors.text,fontSize:13,fontWeight:'700',letterSpacing:.5},secondary:{minHeight:54,borderRadius:16,backgroundColor:colors.raised,borderWidth:1,borderColor:colors.line,alignItems:'center',justifyContent:'center',marginTop:12},secondaryText:{color:colors.text,fontWeight:'700',fontSize:15}});
