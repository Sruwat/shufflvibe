const state = { view: "overview", page: 1, pageSize: 200, venues: [], total: 0, editing: null, pipeline: null, catalogueLocked: false };
const photoObjectUrls = new Set();
const $ = (selector) => document.querySelector(selector);
const apiBase = new URLSearchParams(location.search).get("api") || "";

function token() { return localStorage.getItem("shuffl_admin_token") || ""; }
function headers(json = false) { const value = { ...(json ? { "Content-Type": "application/json" } : {}) }; if (token()) value["X-Admin-Token"] = token(); return value; }
async function api(path, options = {}) { const isJson = Boolean(options.body) && !(options.body instanceof FormData); const response = await fetch(`${apiBase}${path}`, { ...options, headers: { ...headers(isJson), ...(options.headers || {}) } }); if (!response.ok) throw new Error(await response.text() || `Request failed (${response.status})`); return response.headers.get("content-type")?.includes("json") ? response.json() : response.blob(); }
async function hydratePhotoImages(root = document) { const images = [...root.querySelectorAll("[data-photo-name]")]; await Promise.all(images.map(async (image) => { try { const blob = await api(`/v1/admin/live/photo?name=${encodeURIComponent(image.dataset.photoName)}`); const url = URL.createObjectURL(blob); photoObjectUrls.add(url); image.src = url; if (image.dataset.photoTarget === "background") image.style.backgroundImage = `url("${url}")`; image.classList.add("photo-loaded"); } catch { image.classList.add("photo-failed"); image.setAttribute("aria-label", "Photo unavailable"); } })); }
function revokePhotoObjectUrls() { photoObjectUrls.forEach((url) => URL.revokeObjectURL(url)); photoObjectUrls.clear(); }
function toast(message) { const node = $("#toast"); node.textContent = message; node.classList.add("show"); setTimeout(() => node.classList.remove("show"), 2600); }
function escapeHtml(value) { return String(value ?? "").replace(/[&<>'"]/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;" }[char])); }
function statusPill(value) { const text = value || "unknown"; const kind = /verified|admitted/i.test(text) ? "green" : /reject/i.test(text) ? "red" : /update|insufficient|process/i.test(text) ? "orange" : "gray"; return `<span class="pill ${kind}">${escapeHtml(text.replaceAll("_", " "))}</span>`; }
function sourceHealth(row) { const identity = row.venue_identity?.[0] || {}; if (row.venue_media?.length || row.photos?.length) return "SHUFFL media attached"; if (identity.official_url || row.official_url) return "Official source verified"; if (row.google_live_cache || row.google_data_status === "cached") return "Google cached"; return "Needs source review"; }
function firstName(row) { return row.display_name || row.official_name || row.admin_override?.manual_vibe || "Live Google venue"; }
function manual(row, key) { return (row.admin_override || {})[key] ?? row[key] ?? ""; }
function labelize(value) { return String(value || "").replaceAll("_", " ").replace(/\b\w/g, (char) => char.toUpperCase()); }
function scalar(value) { if (value === null || value === undefined || value === "") return "—"; if (typeof value === "boolean") return value ? "Yes" : "No"; return String(value); }
function valueHtml(value) { if (Array.isArray(value) || (value && typeof value === "object")) return `<pre class="detail-json">${escapeHtml(JSON.stringify(value, null, 2))}</pre>`; return `<span>${escapeHtml(scalar(value))}</span>`; }
function detailCard(title, value, className = "") { return `<article class="detail-card ${className}"><header><h4>${escapeHtml(labelize(title))}</h4></header><div class="detail-card-body">${valueHtml(value)}</div></article>`; }
function renderLiveSection(payload) {
  if (!payload?.google_live) return `<section class="live-error"><strong>Live Google enrichment unavailable.</strong><span>Stored pipeline evidence is still shown below.</span></section>`;
  const live = payload.google_live; const ai = payload.ai_insight || {}; const reviews = (live.reviews || []).slice(0, 3);
  const photos = (live.photos || []).slice(0, 8).filter((photo) => photo?.name).map((photo) => `<img data-photo-name="${escapeHtml(photo.name)}" src="" alt="${escapeHtml(live.name || "Venue photo")}" loading="lazy" />`).join("");
  const hours = live.opening_hours?.weekdayDescriptions || live.opening_hours?.periods || live.opening_hours || {};
  const reviewHtml = reviews.length ? reviews.map((review) => `<blockquote>${escapeHtml(review.text?.text || review.text || "")}${review.relativePublishTimeDescription ? `<cite>${escapeHtml(review.relativePublishTimeDescription)}</cite>` : ""}</blockquote>`).join("") : `<p class="muted">No review excerpts returned in this live response.</p>`;
  const aiScores = ai.scores || ai.deterministic_scores?.scores || {};
  return `<section class="live-section"><div class="detail-section-head"><div><p class="kicker">DISPLAY-TIME ENRICHMENT</p><h3>Google live + Gemini insight</h3></div><span class="live-badge">Not persisted</span></div><div class="live-facts"><div><span class="live-label">CURRENT NAME</span><strong>${escapeHtml(live.name || "—")}</strong><small>${escapeHtml(live.address || "—")}</small></div><div class="live-stat"><b>${escapeHtml(scalar(live.rating))}</b><span>Google rating</span></div><div class="live-stat"><b>${escapeHtml(scalar(live.review_count))}</b><span>review count</span></div><div class="live-stat"><b>${escapeHtml(scalar(live.price_level))}</b><span>price level</span></div></div><div class="live-subgrid"><article><h4>Opening hours</h4>${valueHtml(hours)}</article><article><h4>Gemini / derived scores</h4>${valueHtml(aiScores)}<small class="live-provider">Provider: ${escapeHtml(ai.provider || "unavailable")}</small></article><article><h4>Live review evidence</h4><div class="review-excerpts">${reviewHtml}</div></article></div>${photos ? `<div class="photo-strip">${photos}</div>` : `<div class="photo-empty">No Google photos returned for this place.</div>`}<p class="live-policy">Google name, address, coordinates, hours, rating, reviews and photos are fetched for this preview only and are not written to MySQL.</p></section>`;
}
function renderCachedGoogleSection(row) {
  const live = row.google_live_cache;
  if (!live) return "";
  const name = live.displayName?.text || row.display_name || "Venue";
  const photos = (live.photos || []).slice(0, 10).map((photo) => photo?.name ? `<img data-photo-name="${escapeHtml(photo.name)}" src="" alt="${escapeHtml(name)}" loading="lazy" />` : "").join("");
  const reviews = (live.reviews || []).slice(0, 5).map((review) => `<blockquote>${escapeHtml(review.text?.text || review.text || "")}</blockquote>`).join("");
  return `<section class="live-section cached-google-section"><div class="detail-section-head"><div><p class="kicker">CACHED GOOGLE DISPLAY DATA</p><h3>${escapeHtml(name)}</h3></div><span class="live-badge">Retrieved ${escapeHtml(row.google_live_retrieved_at || "")}</span></div><div class="live-facts"><div><span class="live-label">ADDRESS</span><strong>${escapeHtml(live.formattedAddress || "—")}</strong></div><div class="live-stat"><b>${escapeHtml(scalar(live.rating))}</b><span>Google rating</span></div><div class="live-stat"><b>${escapeHtml(scalar(live.userRatingCount))}</b><span>ratings</span></div><div class="live-stat"><b>${escapeHtml(scalar(live.priceLevel))}</b><span>price level</span></div></div><div class="live-subgrid"><article><h4>Opening hours</h4>${valueHtml(live.regularOpeningHours || {})}</article><article><h4>Structured fields</h4>${valueHtml({ primaryType: live.primaryType, types: live.types, websiteUri: live.websiteUri, phone: live.nationalPhoneNumber, businessStatus: live.businessStatus })}</article><article><h4>Review evidence</h4><div class="review-excerpts">${reviews || `<p class="muted">No reviews returned.</p>`}</div></article></div>${photos ? `<div class="photo-strip">${photos}</div>` : `<div class="photo-empty">No photos returned.</div>`}<p class="live-policy">Google content is cached for admin review and remains display-only; SHUFFL-owned media/rights are managed separately.</p></section>`;
}

function renderDetailSections(row) {
  const sections = [
    ["Core record", { venue_id: row.venue_id, google_place_id: row.google_place_id, display_name: row.display_name, city: row.city, area: row.area, admission_status: row.admission_status, verification_status: row.verification_status, updated_at: row.updated_at }],
    ["Pipeline facts", { discovered_type: row.discovered_type, discovered_city: row.discovered_city, discovered_area: row.discovered_area, google_lookup_url: row.google_lookup_url, admission_decision: row.admission_decision, admission_reasons: row.admission_reasons, exclusion_reasons: row.exclusion_reasons }],
    ["Identity & hours", { venue_identity: row.venue_identity || [], venue_hours: row.venue_hours || [], venue_time_slots: row.venue_time_slots || [] }],
    ["SHUFFL intelligence", { venue_scores: row.venue_scores || [], venue_tags: row.venue_tags || [], gold_list: row.gold_list || [] }],
    ["Evidence & provenance", { venue_sources: row.venue_sources || [], official_url: row.official_url, google_data_status: row.google_data_status, google_photo_rights: row.google_photo_rights, evidence_audit: row.evidence_audit || row.normalized?.evidence_audit || {}, google_fields_policy: "Google identity, address, hours, rating, reviews and photos are fetched live; only provenance is stored." }],
    ["Score audit", { venue_scores: row.venue_scores || [], score_evidence_audit: row.score_evidence_audit || [], score_policy: "Every factor needs evidence or an explicit not_specialised flag before admission." }],
    ["Media & rights", { venue_media: row.venue_media || [], media_policy: "Only SHUFFL-owned/licensed media is durable. Google photos are preview-only." }],
    ["History", row.venue_history || []],
    ["Manual override", row.admin_override || {}],
  ];
  return sections.map(([title, values]) => `<section class="detail-section"><div class="detail-section-head"><div><p class="kicker">${escapeHtml(title.toUpperCase())}</p><h3>${escapeHtml(title)}</h3></div><span class="detail-count">${Object.keys(values || {}).length} fields</span></div><div class="detail-grid">${Object.entries(values || {}).map(([key, value]) => detailCard(key, value, Array.isArray(value) || (value && typeof value === "object") ? "wide-detail" : "")).join("")}</div></section>`).join("");
}

function setView(view) { state.view = view; document.querySelectorAll(".view").forEach((node) => node.classList.toggle("hidden", node.id !== `${view}View`)); document.querySelectorAll(".nav-item").forEach((node) => node.classList.toggle("active", node.dataset.view === view)); $("#pageTitle").textContent = view === "overview" ? "Good evening, admin." : view === "venues" ? "Venue catalogue." : view === "users" ? "User directory." : view === "rooms" ? "Night rooms." : view === "reports" ? "Reports and moderation." : view === "guide" ? "How this works." : "Export center."; if (view === "venues") loadVenues(); if (view === "users") loadUsers(); if (view === "rooms") loadRooms(); if (view === "reports") loadReports(); }

async function loadSummary() { const summary = await api("/v1/admin/summary"); state.catalogueLocked = Boolean(summary.pipeline_locked); $("#navVenueCount").textContent = summary.venues ?? "—"; $("#navUserCount").textContent = summary.users ?? "—"; const admitted = summary.by_admission?.Admitted || 0; const pending = summary.by_admission?.["Insufficient evidence"] || 0; const rejected = summary.by_admission?.Rejected || 0; $("#metrics").innerHTML = [["Total candidates", summary.venues, state.catalogueLocked ? "Catalogue frozen" : "Synced from pipeline"], ["Admitted", admitted, "Ready for app"], ["Needs review", pending, "Editorial queue"], ["Rejected", rejected, "Held out of app"]].map(([label, value, note]) => `<article class="metric"><span class="metric-label">${label}</span><strong class="metric-value">${value}</strong><div class="metric-note">${note}</div></article>`).join(""); $("#syncButton").disabled = state.catalogueLocked; $("#syncButton").textContent = state.catalogueLocked ? "✓ Catalogue locked" : "↻ Sync pipeline"; $("#syncButton").title = state.catalogueLocked ? "Automated sync is disabled while the catalogue is locked" : "Run the venue pipeline"; const total = Math.max(1, summary.venues); $("#coverage").innerHTML = [["Admitted", admitted, "green"], ["Needs review", pending, "orange"], ["Rejected", rejected, "red"]].map(([label, value, color]) => `<div class="coverage-line"><header><span>${label}</span><span>${value} · ${Math.round(value / total * 100)}%</span></header><div class="bar"><i style="width:${Math.max(2, value / total * 100)}%;background:${color === "orange" ? "#e38c43" : color === "red" ? "#bd625c" : "#1c725a"}"></i></div></div>`).join(""); }

async function loadPipelineStatus() {
  try {
    const catalogue = await api("/v1/admin/summary");
    if (catalogue.pipeline_locked) {
      state.pipeline = null;
      $("#pipelineNavStatus").textContent = "LOCKED";
      $("#pipelineStatusBadge").textContent = "CATALOGUE LOCKED";
      $("#pipelineStatusBadge").className = "pipeline-status-badge pipeline-locked";
      $("#pipelineSummary").innerHTML = `<strong>Catalogue locked</strong><span>${Number(catalogue.venues || 0).toLocaleString()} venue records frozen for launch</span><small>Manual admin edits remain available; automated pipeline sync is disabled.</small>`;
      return;
    }
    const result = await api("/v1/admin/pipeline/runs?limit=10");
    const runs = result.items || [];
    const latest = runs[0] || null;
    state.pipeline = latest;
    const status = latest?.status || "NOT RUN";
    const label = status === "RUNNING" ? "RUNNING" : status === "SUCCEEDED" ? "HEALTHY" : status === "FAILED" ? "FAILED" : status === "PARTIAL" ? "PARTIAL" : status;
    $("#pipelineNavStatus").textContent = label;
    $("#pipelineStatusBadge").textContent = label;
    $("#pipelineStatusBadge").className = `pipeline-status-badge pipeline-${status.toLowerCase()}`;
    const summary = latest?.summary || {};
    const failed = latest?.error_count ?? summary.failed ?? 0;
    const updated = latest?.finished_at || latest?.started_at || "No run recorded";
    $("#pipelineSummary").innerHTML = latest ? `<strong>${escapeHtml(label)}</strong><span>${Number(latest.processed || 0).toLocaleString()} processed · ${Number(failed || 0).toLocaleString()} failed</span><small>Last activity: ${escapeHtml(updated)}</small>${status === "FAILED" ? `<button type="button" class="button secondary" id="retryLatestPipeline">Retry failed run</button>` : ""}` : `<span>No pipeline run recorded yet.</span>`;
    $("#retryLatestPipeline")?.addEventListener("click", () => retryPipeline(latest.run_id));
  } catch (error) {
    $("#pipelineNavStatus").textContent = "ERROR";
    $("#pipelineStatusBadge").textContent = "ERROR";
    $("#pipelineStatusBadge").className = "pipeline-status-badge pipeline-failed";
    $("#pipelineSummary").innerHTML = `<span>Pipeline status unavailable.</span><button type="button" class="button ghost" id="retryPipelineStatus">Retry status</button>`;
    $("#retryPipelineStatus")?.addEventListener("click", loadPipelineStatus);
  }
}

async function retryPipeline(runId) {
  if (!runId) return;
  const button = $("#retryLatestPipeline");
  if (button) { button.disabled = true; button.textContent = "Retrying…"; }
  try { await api(`/v1/admin/pipeline/runs/${encodeURIComponent(runId)}/retry`, { method: "POST" }); toast("Pipeline retry queued"); await loadPipelineStatus(); } catch (error) { toast(`Retry failed: ${error.message}`); if (button) { button.disabled = false; button.textContent = "Retry failed run"; } }
}

async function loadAttention() { const data = await api("/v1/admin/venues?verification=in_process&page_size=5"); $("#attentionList").innerHTML = data.items.length ? data.items.map((row) => `<div class="attention-row"><div class="venue-initial">${escapeHtml(firstName(row).slice(0, 1).toUpperCase())}</div><div class="attention-copy"><strong>${escapeHtml(firstName(row))}</strong><small>${escapeHtml(row.area || row.city)} · ${escapeHtml(row.admission_status)}</small></div>${statusPill(row.verification_status)}<button class="row-action" data-edit="${escapeHtml(row.venue_id)}">Edit</button></div>`).join("") : `<div class="attention-row"><div class="attention-copy"><strong>Nothing waiting.</strong><small>All editorial records are up to date.</small></div></div>`; document.querySelectorAll("[data-edit]").forEach((node) => node.addEventListener("click", () => openEditor(node.dataset.edit))); }

async function loadVenues() { const query = new URLSearchParams({ page: state.page, page_size: state.pageSize, search: $("#venueSearch").value, status: $("#statusFilter").value, verification: $("#verificationFilter").value }); try { const data = await api(`/v1/admin/venues?${query}`); state.venues = data.items; state.total = data.total; $("#venueCountLabel").textContent = `${data.total.toLocaleString()} records`; $("#pageLabel").textContent = `Page ${data.page} of ${Math.max(1, Math.ceil(data.total / data.page_size))}`; $("#venueTable").innerHTML = data.items.map((row) => { const source = sourceHealth(row); return `<tr><td><span class="venue-name">${escapeHtml(firstName(row))}</span><span class="venue-id">${escapeHtml(row.google_place_id || row.venue_id)}</span></td><td>${escapeHtml(row.area || row.city || "—")}</td><td>${statusPill(row.admission_status)}</td><td>${statusPill(row.verification_status)}</td><td class="source-state">${escapeHtml(source)}</td><td class="row-actions"><button class="row-action" data-preview="${escapeHtml(row.venue_id)}">Preview</button><button class="row-action" data-edit="${escapeHtml(row.venue_id)}">Edit</button></td></tr>`; }).join("") || `<tr><td colspan="6"><div class="empty">No venues match this filter.</div></td></tr>`; document.querySelectorAll("[data-preview]").forEach((node) => node.addEventListener("click", () => openEditor(node.dataset.preview, "preview"))); document.querySelectorAll("[data-edit]").forEach((node) => node.addEventListener("click", () => openEditor(node.dataset.edit, "edit"))); } catch (error) { toast(error.message); } }

async function loadUsers() { try { const params = new URLSearchParams({ search: $("#userSearch")?.value || "", status: $("#userStatusFilter")?.value || "" }); const data = await api(`/v1/admin/users?${params}`); const rows = data.items || []; $("#userTable").innerHTML = rows.length ? rows.map((row) => `<tr><td><span class="venue-name">${escapeHtml(row.display_name || "Unnamed user")}</span><span class="venue-id">${escapeHtml(row.email || row.user_id)}</span></td><td>${statusPill(row.role)}</td><td>${statusPill(row.status)}</td><td>${escapeHtml(row.last_seen_at || "—")}</td><td>${escapeHtml(row.created_at || "—")}</td><td class="row-actions"><select class="inline-select" data-user-status="${escapeHtml(row.user_id)}"><option value="active" ${row.status === "active" ? "selected" : ""}>Active</option><option value="disabled" ${row.status === "disabled" ? "selected" : ""}>Disabled</option><option value="suspended" ${row.status === "suspended" ? "selected" : ""}>Suspended</option></select><button class="row-action danger-action" data-user-reset="${escapeHtml(row.user_id)}">Reset</button></td></tr>`).join("") : `<tr><td colspan="6"><div class="empty">No users match this filter.</div></td></tr>`; document.querySelectorAll("[data-user-status]").forEach((node) => node.addEventListener("change", () => updateUser(node.dataset.userStatus, { status: node.value }))); document.querySelectorAll("[data-user-reset]").forEach((node) => node.addEventListener("click", () => updateUser(node.dataset.userReset, { status: "active" }))); } catch (error) { $("#userTable").innerHTML = `<tr><td colspan="6"><div class="empty">Users unavailable: ${escapeHtml(error.message)}</div></td></tr>`; } }

async function updateUser(userId, payload) { if (payload.reset) { if (!window.confirm("Reset this account's onboarding and revoke all sessions?")) { return; } try { await api(`/v1/admin/users/${encodeURIComponent(userId)}/reset`, { method: "POST" }); toast("Account reset and sessions revoked"); await loadUsers(); } catch (error) { toast(`Account reset failed: ${error.message}`); } return; } if (!window.confirm(payload.status === "active" ? "Restore this account?" : `Set account status to ${payload.status}?`)) { await loadUsers(); return; } try { await api(`/v1/admin/users/${encodeURIComponent(userId)}`, { method: "PATCH", body: JSON.stringify(payload) }); toast("User status updated and sessions handled"); await loadUsers(); } catch (error) { toast(`User update failed: ${error.message}`); await loadUsers(); } }

async function loadRooms() { try { const data = await api("/v1/admin/rooms"); const rows = data.items || []; $("#roomTable").innerHTML = rows.length ? rows.map((row) => `<tr><td><span class="venue-name">${escapeHtml(row.title || row.id || "Unnamed room")}</span><span class="venue-id">${escapeHtml(row.id || "—")}</span></td><td>${escapeHtml(row.owner_id || "—")}</td><td>${escapeHtml(row.member_count ?? 0)}</td><td>${statusPill(row.plan_locked ? "locked" : row.plan_id ? "draft" : "no plan")}</td><td>${escapeHtml(row.updated_at || "—")}</td></tr>`).join("") : `<tr><td colspan="5"><div class="empty">No rooms have been created yet.</div></td></tr>`; } catch (error) { $("#roomTable").innerHTML = `<tr><td colspan="5"><div class="empty">Rooms unavailable: ${escapeHtml(error.message)}</div></td></tr>`; } }

async function loadReports() { try { const status = $("#reportStatusFilter")?.value || ""; const query = status ? `?status=${encodeURIComponent(status)}` : ""; const data = await api(`/v1/admin/reports${query}`); const rows = data.items || []; $("#reportTable").innerHTML = rows.length ? rows.map((row) => `<tr><td><span class="venue-name">${escapeHtml(row.reason || row.report_type || "Report")}</span><span class="venue-id">${escapeHtml(row.id || row.report_id || "—")}</span></td><td>${escapeHtml(row.reporter_id || "—")}</td><td>${escapeHtml(row.target_id || row.target_type || "—")}</td><td>${statusPill(row.status || "received")}</td><td>${escapeHtml(row.created_at || "—")}</td><td class="row-actions"><select class="inline-select" data-report-status="${escapeHtml(row.id || row.report_id)}"><option value="received" ${row.status === "received" ? "selected" : ""}>Received</option><option value="reviewing" ${row.status === "reviewing" ? "selected" : ""}>Reviewing</option><option value="resolved" ${row.status === "resolved" ? "selected" : ""}>Resolved</option><option value="dismissed" ${row.status === "dismissed" ? "selected" : ""}>Dismissed</option></select></td></tr>`).join("") : `<tr><td colspan="6"><div class="empty">No reports match this filter.</div></td></tr>`; document.querySelectorAll("[data-report-status]").forEach((node) => node.addEventListener("change", () => updateReport(node.dataset.reportStatus, node.value))); } catch (error) { $("#reportTable").innerHTML = `<tr><td colspan="6"><div class="empty">Reports unavailable: ${escapeHtml(error.message)}</div></td></tr>`; } }
async function updateReport(reportId, status) { try { await api(`/v1/admin/reports/${encodeURIComponent(reportId)}`, { method: "PATCH", body: JSON.stringify({ status }) }); toast("Report status updated and audit logged"); await loadReports(); } catch (error) { toast(`Report update failed: ${error.message}`); await loadReports(); } }

async function loadMediaLibrary() {
  const query = new URLSearchParams({ page: state.mediaPage || 1, page_size: 60, search: $("#mediaSearch")?.value || "" });
  try {
    const data = await api(`/v1/admin/media?${query}`);
    state.mediaTotal = data.total || 0;
    $("#mediaCountLabel").textContent = `${Number(data.total || 0).toLocaleString()} owned assets`;
    $("#mediaPageLabel").textContent = `Page ${data.page} of ${Math.max(1, Math.ceil(data.total / data.page_size))}`;
    $("#mediaNavCount").textContent = String(data.total || 0);
    $("#mediaGrid").innerHTML = (data.items || []).map((item) => `<article class="media-card"><div class="media-thumb"><img src="${escapeHtml(item.url)}" alt="${escapeHtml(item.alt_text || item.venue_name || "Venue media")}" loading="lazy" /><span class="media-badge">${item.is_cover ? "Cover" : escapeHtml(item.rights_status || "Rights pending")}</span></div><div class="media-card-copy"><p class="kicker">${escapeHtml(item.area || item.city || "Delhi NCR")}</p><h3>${escapeHtml(item.venue_name || item.venue_id)}</h3><p class="muted">${escapeHtml(item.alt_text || "No alt text")}</p><small>${escapeHtml(item.source_type || "admin_upload")} · ${escapeHtml(item.media_type || "image")}</small><div class="media-card-actions"><button class="row-action" data-media-cover="${escapeHtml(item.media_id)}" data-media-venue="${escapeHtml(item.venue_id)}" ${item.is_cover ? "disabled" : ""}>${item.is_cover ? "Cover selected" : "Make cover"}</button><button class="row-action danger-action" data-media-delete="${escapeHtml(item.media_id)}" data-media-venue="${escapeHtml(item.venue_id)}">Delete</button></div></div></article>`).join("") || `<div class="empty">No owned media yet. Upload an image from a venue’s Media & rights panel.</div>`;
    document.querySelectorAll("[data-media-cover]").forEach((node) => node.addEventListener("click", () => setMediaCover(node.dataset.mediaVenue, node.dataset.mediaCover)));
    document.querySelectorAll("[data-media-delete]").forEach((node) => node.addEventListener("click", () => deleteMedia(node.dataset.mediaVenue, node.dataset.mediaDelete)));
  } catch (error) { toast(`Media library unavailable: ${error.message}`); }
}
async function setMediaCover(venueId, mediaId) { try { await api(`/v1/admin/venues/${encodeURIComponent(venueId)}/media/${encodeURIComponent(mediaId)}/cover`, { method: "POST" }); toast("Cover image updated"); await loadMediaLibrary(); } catch (error) { toast(`Could not set cover: ${error.message}`); } }
async function deleteMedia(venueId, mediaId) { if (!window.confirm("Delete this owned media asset?")) return; try { await api(`/v1/admin/venues/${encodeURIComponent(venueId)}/media/${encodeURIComponent(mediaId)}`, { method: "DELETE" }); toast("Media deleted"); await loadMediaLibrary(); } catch (error) { toast(`Could not delete media: ${error.message}`); } }
async function openMediaUpload() { try { const data = await api("/v1/admin/venues?page=1&page_size=200&publication=PUBLISHED"); const select = $("#mediaVenueSelect"); select.innerHTML = `<option value="">Choose a venue</option>` + (data.items || []).map((row) => `<option value="${escapeHtml(row.venue_id)}">${escapeHtml(firstName(row))} · ${escapeHtml(row.area || row.city || "Delhi NCR")}</option>`).join(""); $("#mediaUploadForm").reset(); $("#mediaUploadState").textContent = ""; $("#mediaUploadDialog").showModal(); } catch (error) { toast(`Could not load venues for upload: ${error.message}`); } }
async function submitMediaUpload(event) { event.preventDefault(); const file = $("#mediaFile")?.files?.[0]; const venueId = $("#mediaVenueSelect")?.value; if (!file || !venueId) { toast("Choose a venue and image first"); return; } const button = $("#submitMediaUpload"); button.disabled = true; $("#mediaUploadState").textContent = "Uploading…"; const body = new FormData(); body.append("file", file); body.append("alt_text", $("#mediaAltText").value.trim()); body.append("rights_status", $("#mediaRights").value); try { await api(`/v1/admin/venues/${encodeURIComponent(venueId)}/media`, { method: "POST", body }); $("#mediaUploadDialog").close(); toast("Owned media uploaded and rights recorded"); await loadMediaLibrary(); } catch (error) { $("#mediaUploadState").textContent = "Upload failed"; toast(`Media upload failed: ${error.message}`); } finally { button.disabled = false; } }

async function loadSettings() {
  try {
    const data = await api("/v1/admin/settings");
    const checks = [["Database", data.database?.status === "ok", data.database_configured ? "Configured and reachable" : "Local fallback"], ["Google Places", data.google_places_configured, data.google_places_configured ? "Key configured" : "Key missing"], ["Google login", data.google_login_configured, data.google_login_configured ? "OAuth client configured" : "Client ID missing"], ["Gemini", data.gemini_configured, data.gemini_configured ? "Key configured" : "Optional fallback active"], ["Admin auth", data.admin_auth_configured, data.admin_auth_configured ? "Configured" : "Development-only"], ["CORS", data.cors_origins_configured, data.cors_origins_configured ? "Allow-list configured" : "Development defaults"], ["Pipeline", !data.pipeline_locked, data.pipeline_locked ? "Catalogue locked" : "Sync enabled"]];
    $("#settingsState").innerHTML = `<article class="panel guide-card settings-summary"><div class="settings-title"><div><p class="kicker">RUNTIME</p><h3>${data.ready ? "Ready for configured environment" : "Attention required"}</h3></div>${statusPill(data.ready ? "ready" : "needs attention")}</div><p class="muted">Environment: ${escapeHtml(data.environment)} · Opening hours: live at display time · Google reviews persisted: No</p></article><section class="settings-checks">${checks.map(([label, ok, note]) => `<article class="panel settings-check"><span class="settings-dot ${ok ? "ok" : "warn"}"></span><div><strong>${escapeHtml(label)}</strong><small>${escapeHtml(note)}</small></div></article>`).join("")}</section><article class="panel settings-controls"><div><p class="kicker">SAFE OPERATIONS</p><h3>Dashboard controls</h3><p class="muted">These values are persisted in MySQL. Secret keys remain on the server.</p></div><label class="setting-toggle"><input id="pipelineLockSetting" type="checkbox" ${data.pipeline_locked ? "checked" : ""} /><span>Lock venue pipeline</span></label><label>Backup retention days<input id="backupRetentionSetting" type="number" min="1" max="365" value="${escapeHtml(data.backup_retention_days ?? 30)}" /></label><button class="button primary" id="saveSettingsButton">Save operational settings</button></article>${(data.errors?.length || data.warnings?.length) ? `<article class="panel guide-card settings-alert"><h3>Configuration notes</h3>${[...(data.errors || []).map((item) => `<p class="settings-error">Error · ${escapeHtml(item)}</p>`), ...(data.warnings || []).map((item) => `<p class="settings-warning">Warning · ${escapeHtml(item)}</p>`)].join("")}</article>` : ""}`;
    $("#saveSettingsButton")?.addEventListener("click", saveSettings);
  } catch (error) { $("#settingsState").innerHTML = `<div class="panel guide-card"><h3>Settings unavailable</h3><p>${escapeHtml(error.message)}</p></div>`; }
}

async function saveSettings() { const button = $("#saveSettingsButton"); if (button) { button.disabled = true; button.textContent = "Saving…"; } try { await api("/v1/admin/settings", { method: "PATCH", body: JSON.stringify({ pipeline_locked: Boolean($("#pipelineLockSetting")?.checked), backup_retention_days: Number($("#backupRetentionSetting")?.value || 30) }) }); toast("Operational settings saved and audited"); await Promise.all([loadSettings(), loadSummary(), loadPipelineStatus()]); } catch (error) { toast(`Settings save failed: ${error.message}`); } finally { if (button) { button.disabled = false; button.textContent = "Save operational settings"; } } }

async function openEditor(venueId, mode = "edit") { try { const row = await api(`/v1/admin/venues/${encodeURIComponent(venueId)}`); state.editing = row; state.mode = mode; const identity = row.venue_identity?.[0] || {}; let live = null; if (!row.google_live_cache) { try { live = await api(`/v1/admin/venues/${encodeURIComponent(venueId)}/live`); } catch (error) { toast(`Live Google enrichment unavailable: ${error.message}`); } } $("#dialogTitle").textContent = `${mode === "preview" ? "Preview" : "Edit"}: ${firstName(row)}`; $("#dialogIdentity").textContent = identity.official_address || `${row.area || ""}, ${row.city || ""}`; $("#dialogPlaceId").textContent = row.google_place_id || row.venue_id; $("#dialogMapLink").href = row.google_lookup_url || "#"; $("#detailSections").innerHTML = `${row.google_live_cache ? renderCachedGoogleSection(row) : renderLiveSection(live)}${renderDetailSections(row)}`; $("#editVerification").value = manual(row, "verification_status") || "in_process"; $("#editOperator").value = manual(row, "operator_class") || "unknown"; $("#editFitout").value = manual(row, "fit_out_status") || "unknown"; $("#editYear").value = manual(row, "fit_out_year") || ""; $("#editVibe").value = manual(row, "manual_vibe"); $("#editTags").value = Array.isArray(manual(row, "manual_tags")) ? manual(row, "manual_tags").join(", ") : manual(row, "manual_tags"); $("#editHours").value = typeof manual(row, "manual_opening_hours") === "object" ? JSON.stringify(manual(row, "manual_opening_hours"), null, 2) : manual(row, "manual_opening_hours"); $("#editNotes").value = manual(row, "manual_notes"); ["#editVerification", "#editOperator", "#editFitout", "#editYear", "#editVibe", "#editTags", "#editHours", "#editNotes"].forEach((selector) => { $(selector).disabled = mode === "preview"; }); const saveButton = $("#saveVenue"); saveButton.hidden = mode === "preview"; saveButton.style.display = mode === "preview" ? "none" : ""; saveButton.setAttribute("aria-hidden", mode === "preview" ? "true" : "false"); saveButton.tabIndex = mode === "preview" ? -1 : 0; $("#saveState").textContent = mode === "preview" ? "Preview mode · no changes will be saved" : ""; $("#venueDialog").showModal(); } catch (error) { toast(error.message); } }

async function saveVenue(event) { event.preventDefault(); if (!state.editing) return; let hours = $("#editHours").value.trim(); try { hours = hours ? JSON.parse(hours) : {}; } catch { toast("Opening hours must be valid JSON, e.g. {\"Friday\":\"18:00–02:00\"}"); return; } const payload = { verification_status: $("#editVerification").value, operator_class: $("#editOperator").value, fit_out_status: $("#editFitout").value, fit_out_year: $("#editYear").value ? Number($("#editYear").value) : null, manual_vibe: $("#editVibe").value, manual_tags: $("#editTags").value.split(",").map((value) => value.trim()).filter(Boolean), manual_opening_hours: hours, manual_notes: $("#editNotes").value }; $("#saveState").textContent = "Saving…"; try { await api(`/v1/admin/venues/${encodeURIComponent(state.editing.venue_id)}`, { method: "PATCH", body: JSON.stringify(payload) }); $("#venueDialog").close(); toast("Venue updated and audit logged"); await Promise.all([loadSummary(), loadAttention(), state.view === "venues" ? loadVenues() : Promise.resolve()]); } catch (error) { $("#saveState").textContent = "Save failed"; toast(error.message); } }

async function syncPipeline() { if (state.catalogueLocked) { toast("Catalogue is locked; pipeline sync is disabled."); return; } $("#syncButton").disabled = true; $("#syncButton").textContent = "Queueing…"; try { await api("/v1/admin/pipeline/runs", { method: "POST", body: JSON.stringify({ max_rows: 5000 }) }); toast("Pipeline run queued"); await loadPipelineStatus(); } catch (error) { toast(`Pipeline could not start: ${error.message}`); } finally { $("#syncButton").disabled = state.catalogueLocked; $("#syncButton").textContent = state.catalogueLocked ? "✓ Catalogue locked" : "↻ Sync pipeline"; } }

document.querySelectorAll("[data-view]").forEach((node) => node.addEventListener("click", () => setView(node.dataset.view))); document.querySelectorAll("[data-view-target]").forEach((node) => node.addEventListener("click", () => setView(node.dataset.viewTarget))); $("#saveToken").addEventListener("click", () => { localStorage.setItem("shuffl_admin_token", $("#tokenInput").value); toast("Token saved for this browser"); }); $("#tokenInput").value = token(); $("#syncButton").addEventListener("click", syncPipeline); $("#venueForm").addEventListener("submit", saveVenue); $("#refreshVenues").addEventListener("click", () => { state.page = 1; loadVenues(); }); $("#venueSearch").addEventListener("input", () => { clearTimeout(window.searchTimer); window.searchTimer = setTimeout(() => { state.page = 1; loadVenues(); }, 280); }); $("#statusFilter").addEventListener("change", () => { state.page = 1; loadVenues(); }); $("#verificationFilter").addEventListener("change", () => { state.page = 1; loadVenues(); }); $("#prevPage").addEventListener("click", () => { if (state.page > 1) { state.page -= 1; loadVenues(); } }); $("#nextPage").addEventListener("click", () => { if (state.page < Math.ceil(state.total / state.pageSize)) { state.page += 1; loadVenues(); } });

async function loadOptions() { try { const options = await api("/v1/admin/options"); [["#cityFilter", options.cities], ["#stateFilter", options.states], ["#areaFilter", options.areas]].forEach(([selector, values]) => { const node = $(selector); if (!node) return; const label = selector.includes("city") ? "All cities" : selector.includes("state") ? "All states" : "All areas"; node.innerHTML = `<option value="">${label}</option>` + (values || []).map((value) => `<option value="${escapeHtml(value)}">${escapeHtml(value)}</option>`).join(""); }); } catch (error) { toast(`Could not load area filters: ${error.message}`); } }
async function createVenue(event) { event.preventDefault(); const payload = { display_name: $("#newName").value.trim(), google_place_id: $("#newPlaceId").value.trim() || null, discovered_type: $("#newType").value.trim() || "venue", city: $("#newCity").value.trim() || "New Delhi", state: $("#newState").value.trim() || "Delhi", area: $("#newArea").value.trim(), metro_name: $("#newMetro").value.trim(), metro_distance_km: $("#newMetroDistance").value ? Number($("#newMetroDistance").value) : null, official_url: $("#newWebsite").value.trim(), menu_url: $("#newMenu").value.trim(), booking_url: $("#newBooking").value.trim(), social_urls: $("#newSocial").value.split("\n").map((value) => value.trim()).filter(Boolean), manual_vibe: $("#newVibe").value.trim(), manual_tags: $("#newTags").value.split(",").map((value) => value.trim()).filter(Boolean), manual_notes: $("#newNotes").value.trim() }; if (!payload.display_name) return; $("#createState").textContent = "Saving…"; try { await api("/v1/admin/venues", { method: "POST", body: JSON.stringify(payload) }); $("#createDialog").close(); $("#createForm").reset(); toast("Venue added to MySQL"); await loadOptions(); state.page = 1; if (state.view === "venues") await loadVenues(); } catch (error) { $("#createState").textContent = "Could not save"; toast(error.message); } }
async function importVenueFile(event) { const file = event.target.files?.[0]; if (!file) return; const body = new FormData(); body.append("file", file); try { const result = await api("/v1/admin/import", { method: "POST", body }); toast(`Imported ${result.created} new, updated ${result.updated}, skipped ${result.skipped}`); await loadOptions(); state.page = 1; if (state.view === "venues") await loadVenues(); } catch (error) { toast(`Import failed: ${error.message}`); } finally { event.target.value = ""; } }
async function loadVenues() { const query = new URLSearchParams({ page: state.page, page_size: state.pageSize, search: $("#venueSearch").value, city: $("#cityFilter").value, state: $("#stateFilter").value, area: $("#areaFilter").value, status: $("#statusFilter").value, verification: $("#verificationFilter").value }); try { const data = await api(`/v1/admin/venues?${query}`); state.venues = data.items; state.total = data.total; $("#venueCountLabel").textContent = `${data.total.toLocaleString()} records`; $("#pageLabel").textContent = `Page ${data.page} of ${Math.max(1, Math.ceil(data.total / data.page_size))}`; $("#venueTable").innerHTML = data.items.map((row) => { const source = sourceHealth(row); return `<tr><td><span class="venue-name">${escapeHtml(firstName(row))}</span><span class="venue-id">${escapeHtml(row.google_place_id || row.venue_id)}</span></td><td>${escapeHtml(row.area || row.city || "—")}</td><td>${statusPill(row.admission_status)}</td><td>${statusPill(row.verification_status)}</td><td class="source-state">${escapeHtml(source)}</td><td class="row-actions"><button class="row-action" data-preview="${escapeHtml(row.venue_id)}">Preview</button><button class="row-action" data-edit="${escapeHtml(row.venue_id)}">Edit</button></td></tr>`; }).join("") || `<tr><td colspan="6"><div class="empty">No venues match this filter.</div></td></tr>`; document.querySelectorAll("[data-preview]").forEach((node) => node.addEventListener("click", () => openEditor(node.dataset.preview, "preview"))); document.querySelectorAll("[data-edit]").forEach((node) => node.addEventListener("click", () => openEditor(node.dataset.edit, "edit"))); } catch (error) { toast(error.message); } }
$("#addVenueButton").addEventListener("click", () => $("#createDialog").showModal()); $("#createForm").addEventListener("submit", createVenue); $("#importVenueButton").addEventListener("click", () => $("#venueFileInput").click()); $("#venueFileInput").addEventListener("change", importVenueFile); ["#cityFilter", "#stateFilter", "#areaFilter"].forEach((selector) => $(selector).addEventListener("change", () => { state.page = 1; loadVenues(); }));
Promise.all([loadSummary(), loadAttention(), loadOptions(), loadPipelineStatus()]).catch((error) => toast(`Admin API unavailable: ${error.message}`));

// Lifecycle actions are deliberately separate from Save draft. The server is
// the authority for eligibility and publication validation.
const publicationFilter = document.querySelector("#publicationFilter");
if (publicationFilter) {
  const requestApi = api;
  api = async (path, options = {}) => {
    if (path.startsWith("/v1/admin/venues?") && publicationFilter.value) {
      path += `&publication=${encodeURIComponent(publicationFilter.value)}`;
    }
    return requestApi(path, options);
  };
  publicationFilter.addEventListener("change", () => { state.page = 1; loadVenues(); });
}

const baseSetView = setView;
setView = (view) => {
  if (["pipeline", "media", "settings", "rooms", "reports"].includes(view)) {
    state.view = view;
    document.querySelectorAll(".view").forEach((node) => node.classList.toggle("hidden", node.id !== `${view}View`));
    document.querySelectorAll(".nav-item").forEach((node) => node.classList.toggle("active", node.dataset.view === view));
    $("#pageTitle").textContent = view === "pipeline" ? "Pipeline control center." : view === "media" ? "Media library." : view === "settings" ? "Settings." : view === "rooms" ? "Night rooms." : "Reports and moderation.";
    if (view === "media") loadMediaLibrary();
    if (view === "settings") loadSettings();
    if (view === "rooms") loadRooms();
    if (view === "reports") loadReports();
    return;
  }
  baseSetView(view);
};

$("#refreshMedia")?.addEventListener("click", () => loadMediaLibrary());
$("#refreshSettings")?.addEventListener("click", () => loadSettings());
$("#refreshUsers")?.addEventListener("click", () => loadUsers());
$("#userStatusFilter")?.addEventListener("change", () => loadUsers());
$("#userSearch")?.addEventListener("input", () => { clearTimeout(window.userSearchTimer); window.userSearchTimer = setTimeout(loadUsers, 280); });
$("#refreshRooms")?.addEventListener("click", () => loadRooms());
$("#refreshReports")?.addEventListener("click", () => loadReports());
$("#reportStatusFilter")?.addEventListener("change", () => loadReports());
$("#mediaSearch")?.addEventListener("input", () => {
  clearTimeout(window.mediaSearchTimer);
  window.mediaSearchTimer = setTimeout(() => { state.mediaPage = 1; loadMediaLibrary(); }, 280);
});
$("#prevMediaPage")?.addEventListener("click", () => { if ((state.mediaPage || 1) > 1) { state.mediaPage -= 1; loadMediaLibrary(); } });
$("#nextMediaPage")?.addEventListener("click", () => { if ((state.mediaPage || 1) < Math.ceil((state.mediaTotal || 0) / 60)) { state.mediaPage = (state.mediaPage || 1) + 1; loadMediaLibrary(); } });
$("#openMediaUpload")?.addEventListener("click", openMediaUpload);
$("#mediaUploadForm")?.addEventListener("submit", submitMediaUpload);

const baseOpenEditor = openEditor;
openEditor = async (venueId, mode = "edit") => {
  await baseOpenEditor(venueId, mode);
  const locked = mode === "preview";
  $("#publishVenue").disabled = locked || state.editing?.publication_status === "PUBLISHED";
  $("#unpublishVenue").disabled = locked || state.editing?.publication_status !== "PUBLISHED";
};

async function transitionVenue(action) {
  if (!state.editing) return;
  const label = action === "publish" ? "publish" : "unpublish";
  if (!window.confirm(`Are you sure you want to ${label} this venue?`)) return;
  try {
    const updated = await api(`/v1/admin/venues/${encodeURIComponent(state.editing.venue_id)}/${action}`, { method: "POST" });
    state.editing = updated;
    $("#venueDialog").close();
    toast(action === "publish" ? "Venue published to the mobile catalog" : "Venue unpublished from the mobile catalog");
    await Promise.all([loadSummary(), loadAttention(), state.view === "venues" ? loadVenues() : Promise.resolve()]);
  } catch (error) {
    toast(error.message);
  }
}

$("#publishVenue").addEventListener("click", () => transitionVenue("publish"));
$("#unpublishVenue").addEventListener("click", () => transitionVenue("unpublish"));

// Premium catalogue presentation: the same server page can be inspected as a
// dense operational list or as visual venue cards without changing the data.
function renderVenueGrid() {
  const grid = $("#venueGrid");
  if (!grid) return;
  grid.innerHTML = (state.venues || []).map((row) => {
    const identity = row.venue_identity?.[0] || {};
    const image = row.photos?.[0] || row.venue_media?.find((item) => item.is_cover)?.url || "";
    const googlePhoto = row.google_live_cache?.photos?.find((item) => item?.name)?.name;
    const imageMarkup = image ? `style="background-image:url('${escapeHtml(image)}')"` : googlePhoto ? `data-photo-name="${escapeHtml(googlePhoto)}" data-photo-target="background"` : "";
    return `<article class="venue-card"><div class="venue-card-art" ${imageMarkup}><span>${escapeHtml((row.publication_status || "DRAFT").replaceAll("_", " "))}</span></div><div class="venue-card-copy"><p class="kicker">${escapeHtml(row.area || row.city || "DELHI")}</p><h3>${escapeHtml(firstName(row))}</h3><p>${escapeHtml(row.discovered_type || identity.primary_type || "Venue")} · ${escapeHtml(row.verification_status || "in process")}</p><div class="venue-card-actions"><button class="row-action" data-preview="${escapeHtml(row.venue_id)}">Preview</button><button class="row-action" data-edit="${escapeHtml(row.venue_id)}">Studio</button></div></div></article>`;
  }).join("") || `<div class="empty">No venues match this filter.</div>`;
  grid.querySelectorAll("[data-preview]").forEach((node) => node.addEventListener("click", () => openEditor(node.dataset.preview, "preview")));
  grid.querySelectorAll("[data-edit]").forEach((node) => node.addEventListener("click", () => openEditor(node.dataset.edit, "edit")));
  hydratePhotoImages(grid);
}
const baseLoadVenuesForGrid = loadVenues;
loadVenues = async (...args) => { await baseLoadVenuesForGrid(...args); renderVenueGrid(); };
$("#listViewButton")?.addEventListener("click", () => { $("#venueList").classList.remove("hidden"); $("#venueGrid").classList.add("hidden"); $("#listViewButton").classList.add("active"); $("#gridViewButton").classList.remove("active"); });
$("#gridViewButton")?.addEventListener("click", () => { $("#venueList").classList.add("hidden"); $("#venueGrid").classList.remove("hidden"); $("#gridViewButton").classList.add("active"); $("#listViewButton").classList.remove("active"); renderVenueGrid(); });

// Studio tabs are injected at runtime so the existing dialog remains backward
// compatible with saved links and keeps all data in one accessible surface.
function installStudioTabs() {
  const dialog = $("#venueDialog");
  if (!dialog || $("#studioTabs")) return;
  const tabs = document.createElement("nav");
  tabs.id = "studioTabs"; tabs.className = "studio-tabs"; tabs.setAttribute("aria-label", "Venue studio tabs");
  tabs.innerHTML = ["Overview", "Evidence & scores", "Media & rights", "History"].map((label, index) => `<button type="button" class="${index === 0 ? "active" : ""}" data-studio-tab="${index}">${label}</button>`).join("");
  dialog.querySelector(".live-card")?.after(tabs);
  tabs.querySelectorAll("button").forEach((button) => button.addEventListener("click", () => {
    tabs.querySelectorAll("button").forEach((item) => item.classList.toggle("active", item === button));
    const sections = [...$("#detailSections").children];
    sections.forEach((section, index) => { section.hidden = Number(button.dataset.studioTab) > 0 && index !== Number(button.dataset.studioTab) - 1; });
  }));
}
const studioOpenEditor = openEditor;
openEditor = async (...args) => { await studioOpenEditor(...args); installStudioTabs(); };

const cachedOpenEditor = openEditor;
openEditor = async (...args) => {
  revokePhotoObjectUrls();
  await cachedOpenEditor(...args);
  await hydratePhotoImages($("#detailSections"));
};

// Explicitly close both dialogs. Preventing the default submit is important:
// otherwise the required venue-name field blocks the × button with native
// validation instead of closing the modal.
["#venueDialog", "#createDialog", "#mediaUploadDialog"].forEach((selector) => {
  const dialog = $(selector);
  if (!dialog) return;
  dialog.querySelector(".close")?.addEventListener("click", (event) => {
    event.preventDefault();
    event.stopPropagation();
    if (dialog.open) dialog.close("cancel");
  });
  dialog.addEventListener("cancel", (event) => {
    event.preventDefault();
    if (dialog.open) dialog.close("cancel");
  });
  dialog.addEventListener("close", () => revokePhotoObjectUrls());
});

async function loadConfiguredAreaList() {
  try {
    const result = await api("/v1/admin/areas");
    const node = $("#areaFilter");
    if (!node) return;
    node.innerHTML = `<option value="">All areas (${result.items.length})</option>` + (result.items || []).map((item) => `<option value="${escapeHtml(item.area)}">${escapeHtml(item.area)} · ${escapeHtml(item.city || "NCR")} (${item.venue_count || 0})</option>`).join("");
  } catch (error) {
    toast(`Could not load configured area list: ${error.message}`);
  }
}
loadConfiguredAreaList();
document.addEventListener("click", (event) => { const target = event.target.closest("[data-user-reset]"); if (!target) return; event.stopImmediatePropagation(); updateUser(target.dataset.userReset, { reset: true }); }, true);
async function deleteAdminUser(userId) { if (!window.confirm("Soft-delete this account? Personal data will be anonymised and sessions revoked.")) return; try { await api(`/v1/admin/users/${encodeURIComponent(userId)}`, { method: "DELETE" }); toast("Account soft-deleted"); await loadUsers(); } catch (error) { toast(`Account deletion failed: ${error.message}`); } }
const userTableObserver = new MutationObserver(() => { document.querySelectorAll("#userTable tr").forEach((row) => { const status = row.querySelector("[data-user-status]"); if (!status || row.querySelector("[data-user-delete]")) return; const userId = status.dataset.userStatus; const button = document.createElement("button"); button.type = "button"; button.className = "row-action danger-action"; button.dataset.userDelete = userId; button.textContent = "Delete"; row.querySelector(".row-actions")?.appendChild(button); }); });
userTableObserver.observe(document.querySelector("#userTable"), { childList: true });
document.addEventListener("click", (event) => { const target = event.target.closest("[data-user-delete]"); if (!target) return; event.stopImmediatePropagation(); deleteAdminUser(target.dataset.userDelete); }, true);
