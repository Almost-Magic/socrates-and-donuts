/**
 * Peterman V4.1 — Frontend Application
 * Almost Magic Tech Lab
 */

const API = "";  // Same origin

// ── State ────────────────────────────────────────────────
let brands = [];
let currentPage = "dashboard";

// ── Init ─────────────────────────────────────────────────
document.addEventListener("DOMContentLoaded", () => {
    loadDashboard();
    loadBrands();
});

// ── Navigation ───────────────────────────────────────────
function navigateTo(page) {
    currentPage = page;
    document.querySelectorAll(".page").forEach(p => p.classList.remove("active"));
    document.querySelectorAll(".nav-item").forEach(n => n.classList.remove("active"));

    const pageEl = document.getElementById("page-" + page);
    const navEl = document.querySelector(`[data-page="${page}"]`);
    if (pageEl) pageEl.classList.add("active");
    if (navEl) navEl.classList.add("active");

    const titles = {
        dashboard: "Dashboard",
        brands: "Brand Profiles",
        perception: "Chamber 1: Perception Scan",
        semantic: "Chamber 2: Semantic Core",
        vectormap: "Chamber 3: Neural Vector Map",
        authority: "Chamber 4: Authority Engine",
        survivability: "Chamber 5: Survivability Lab",
        machine: "Chamber 6: Machine Interface",
        amplifier: "Chamber 7: Amplifier",
        proof: "Chamber 8: The Proof",
        oracle: "Chamber 9: The Oracle",
        forge: "Chamber 10: The Forge",
        hallucinations: "Hallucination Tracker",
        sov: "Share of Voice",
        browser: "Browser LLM Sessions",
        seoask: "SEO Ask",
    };
    document.getElementById("pageTitle").textContent = titles[page] || page;

    // Load page-specific data
    if (page === "brands") loadBrands();
    if (page === "browser") loadBrowserStatus();
    populateBrandSelects();
}

// ── API Helpers ──────────────────────────────────────────
async function apiGet(path) {
    try {
        const res = await fetch(API + path);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return await res.json();
    } catch (e) {
        console.error("API GET error:", path, e);
        return null;
    }
}

async function apiPost(path, body) {
    try {
        const res = await fetch(API + path, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || `HTTP ${res.status}`);
        }
        return await res.json();
    } catch (e) {
        console.error("API POST error:", path, e);
        toast(e.message, "error");
        return null;
    }
}

async function apiPut(path, body) {
    try {
        const res = await fetch(API + path, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body),
        });
        return await res.json();
    } catch (e) {
        console.error("API PUT error:", path, e);
        return null;
    }
}

async function apiDelete(path) {
    try {
        const res = await fetch(API + path, { method: "DELETE" });
        return await res.json();
    } catch (e) {
        console.error("API DELETE error:", path, e);
        return null;
    }
}

// ── Dashboard ────────────────────────────────────────────
async function loadDashboard() {
    // Health check
    const health = await apiGet("/api/health");
    if (health) {
        document.getElementById("appVersion").textContent = "V" + (health.version || "4.1.0");
    }

    // System status
    const status = await apiGet("/api/status");
    if (status) {
        const dot = document.getElementById("systemDot");
        const label = document.getElementById("systemLabel");

        const deps = status.dependencies || {};
        const pgOk = deps.postgresql?.status === "ok";
        const ollamaOk = deps.ollama?.status === "ok";

        if (pgOk && ollamaOk) {
            dot.className = "badge-dot ok";
            label.textContent = "All systems go";
        } else if (pgOk || ollamaOk) {
            dot.className = "badge-dot warn";
            label.textContent = "Partial";
        } else {
            dot.className = "badge-dot error";
            label.textContent = "Degraded";
        }

        // Stats
        document.getElementById("statStatus").textContent = status.status === "ok" ? "Online" : "Degraded";
        document.getElementById("statUptime").textContent = status.uptime_seconds
            ? formatDuration(status.uptime_seconds)
            : "--";

        // Dependencies
        setDepStatus("depPg", deps.postgresql);
        setDepStatus("depOllama", deps.ollama);
        setDepStatus("depSearxng", deps.searxng);
        setDepStatus("depSnitcher", deps.snitcher);
    } else {
        document.getElementById("systemDot").className = "badge-dot error";
        document.getElementById("systemLabel").textContent = "Offline";
        document.getElementById("statStatus").textContent = "Offline";
        document.getElementById("statUptime").textContent = "API unreachable";

        setDepStatus("depPg", { status: "unknown" });
        setDepStatus("depOllama", { status: "unknown" });
        setDepStatus("depSearxng", { status: "unknown" });
        setDepStatus("depSnitcher", { status: "unknown" });
    }

    // Brand count
    const brandsData = await apiGet("/api/brands");
    if (brandsData) {
        brands = brandsData.brands || [];
        document.getElementById("statBrands").textContent = brands.length;
    }

    document.getElementById("statScans").textContent = "--";
    document.getElementById("statHallucinations").textContent = "--";
}

function setDepStatus(elId, dep) {
    const el = document.getElementById(elId);
    if (!dep || !el) return;
    const s = dep.status || "unknown";
    if (s === "ok") {
        el.textContent = "Connected";
        el.className = "dep-status ok";
    } else if (s === "not_configured") {
        el.textContent = "Not configured";
        el.className = "dep-status warn";
    } else if (s === "unknown") {
        el.textContent = "Unknown";
        el.className = "dep-status warn";
    } else {
        el.textContent = "Disconnected";
        el.className = "dep-status error";
    }
}

function formatDuration(seconds) {
    if (seconds < 60) return Math.round(seconds) + "s";
    if (seconds < 3600) return Math.round(seconds / 60) + "m";
    return Math.round(seconds / 3600) + "h " + Math.round((seconds % 3600) / 60) + "m";
}

// ── Brands ───────────────────────────────────────────────
async function loadBrands() {
    const data = await apiGet("/api/brands");
    if (!data) return;

    brands = data.brands || [];
    const panel = document.getElementById("brandsPanel");

    if (brands.length === 0) {
        panel.innerHTML = '<p class="empty-state">No brands configured. Add your first brand to start monitoring.</p>';
        return;
    }

    panel.innerHTML = '<div class="brand-grid">' + brands.map(b => `
        <div class="brand-card" onclick="openBrandDetail(${b.id})">
            <div class="brand-card-header">
                <div>
                    <div class="brand-card-name">${esc(b.name)}</div>
                    <div class="brand-card-meta">${esc(b.domain || "No domain")} &middot; ${esc(b.industry || "No industry")}</div>
                </div>
                <span class="tag tag-gold">${esc(b.tier || "growth")}</span>
            </div>
            ${b.is_client_zero ? '<span class="tag tag-info" style="margin-bottom:8px;">Client Zero</span>' : ""}
            <div class="brand-card-stats">
                <div class="brand-card-stat"><strong>${b.keyword_count || 0}</strong> keywords</div>
                <div class="brand-card-stat"><strong>${b.competitor_count || 0}</strong> competitors</div>
                <div class="brand-card-stat"><strong>${esc(b.scan_frequency || "weekly")}</strong> scans</div>
            </div>
        </div>
    `).join("") + '</div>';

    populateBrandSelects();
}

function showAddBrandModal() {
    document.getElementById("addBrandModal").classList.add("open");
}

function closeModal(id) {
    document.getElementById(id).classList.remove("open");
}

async function createBrand(e) {
    e.preventDefault();
    const brand = {
        name: document.getElementById("brandName").value,
        domain: document.getElementById("brandDomain").value,
        industry: document.getElementById("brandIndustry").value,
        description: document.getElementById("brandDescription").value,
        tier: document.getElementById("brandTier").value,
        scan_frequency: document.getElementById("brandFreq").value,
        is_client_zero: document.getElementById("brandClientZero").checked,
    };

    const result = await apiPost("/api/brands", brand);
    if (result) {
        toast("Brand created: " + brand.name, "success");
        closeModal("addBrandModal");
        document.getElementById("addBrandForm").reset();
        loadBrands();
        loadDashboard();
    }
}

async function openBrandDetail(brandId) {
    const data = await apiGet(`/api/brands/${brandId}/dashboard`);
    if (!data) return;

    const b = data.brand;
    const stats = data.stats;

    document.getElementById("brandDetailTitle").textContent = b.name;
    document.getElementById("brandDetailBody").innerHTML = `
        <div class="stat-grid" style="margin-bottom:16px;">
            <div class="stat-card">
                <div class="stat-label">Keywords</div>
                <div class="stat-value">${stats.approved_keywords}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Competitors</div>
                <div class="stat-value">${stats.competitors}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Hallucinations</div>
                <div class="stat-value">${stats.active_hallucinations}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Recent Scans</div>
                <div class="stat-value">${stats.recent_scans}</div>
            </div>
        </div>
        <div style="display:flex; gap:8px; margin-bottom:16px;">
            <span class="tag tag-gold">${esc(b.tier)}</span>
            <span class="tag tag-muted">${esc(b.scan_frequency)} scans</span>
            ${b.is_client_zero ? '<span class="tag tag-info">Client Zero</span>' : ""}
        </div>
        <p style="font-size:13px; color:var(--text-muted); margin-bottom:16px;">${esc(b.description || "No description")}</p>

        <h4 style="font-size:13px; margin-bottom:8px; color:var(--text);">Add Keyword</h4>
        <div style="display:flex; gap:8px; margin-bottom:16px;">
            <input type="text" id="kwInput" placeholder="Enter keyword" style="flex:1; padding:8px 12px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); color:var(--text); font-family:var(--font); font-size:13px;">
            <button class="btn btn-gold btn-small" onclick="addKeyword(${b.id})">Add</button>
        </div>

        <h4 style="font-size:13px; margin-bottom:8px; color:var(--text);">Add Competitor</h4>
        <div style="display:flex; gap:8px; margin-bottom:16px;">
            <input type="text" id="compInput" placeholder="Competitor name" style="flex:1; padding:8px 12px; background:var(--surface); border:1px solid var(--border); border-radius:var(--radius); color:var(--text); font-family:var(--font); font-size:13px;">
            <button class="btn btn-outline btn-small" onclick="addCompetitor(${b.id})">Add</button>
        </div>

        <div style="display:flex; gap:8px;">
            <button class="btn btn-gold" onclick="closeModal('brandDetailModal'); navigateTo('perception'); document.getElementById('scanBrandSelect').value=${b.id};">Run Scan</button>
            <button class="btn btn-danger btn-small" onclick="archiveBrand(${b.id})">Archive</button>
        </div>
    `;
    document.getElementById("brandDetailModal").classList.add("open");
}

async function addKeyword(brandId) {
    const kw = document.getElementById("kwInput").value.trim();
    if (!kw) return;
    const result = await apiPost(`/api/brands/${brandId}/keywords`, { keyword: kw, category: "primary" });
    if (result) {
        toast("Keyword added: " + kw, "success");
        document.getElementById("kwInput").value = "";
        openBrandDetail(brandId);
    }
}

async function addCompetitor(brandId) {
    const name = document.getElementById("compInput").value.trim();
    if (!name) return;
    const result = await apiPost(`/api/brands/${brandId}/competitors`, { name });
    if (result) {
        toast("Competitor added: " + name, "success");
        document.getElementById("compInput").value = "";
        openBrandDetail(brandId);
    }
}

async function archiveBrand(brandId) {
    if (!confirm("Archive this brand?")) return;
    await apiDelete(`/api/brands/${brandId}`);
    toast("Brand archived", "info");
    closeModal("brandDetailModal");
    loadBrands();
    loadDashboard();
}

// ── Brand Select Dropdowns ───────────────────────────────
function populateBrandSelects() {
    const selects = [
        "scanBrandSelect", "halBrandSelect", "sovBrandSelect",
        "semanticBrandSelect", "vectorBrandSelect", "authBrandSelect",
        "survBrandSelect", "techBrandSelect", "ampBrandSelect",
        "proofBrandSelect", "oracleBrandSelect", "forgeBrandSelect",
        "seoBrandSelect",
    ];
    selects.forEach(id => {
        const el = document.getElementById(id);
        if (!el) return;
        const current = el.value;
        el.innerHTML = '<option value="">Select a brand...</option>' +
            brands.map(b => `<option value="${b.id}">${esc(b.name)}</option>`).join("");
        if (current) el.value = current;
    });
}

// ── Perception Scan ──────────────────────────────────────
async function runPerceptionScan() {
    const brandId = document.getElementById("scanBrandSelect").value;
    const depth = document.getElementById("scanDepth").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }

    const btn = document.getElementById("scanBtn");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Scanning...';

    const result = await apiPost(`/api/scan/perception/${brandId}`, { depth });

    btn.disabled = false;
    btn.textContent = "Run Perception Scan";

    if (result && result.scan) {
        const scan = result.scan;
        const summary = scan.summary || {};
        const scores = scan.scores || {};

        document.getElementById("scanResultsPanel").style.display = "";
        document.getElementById("scanResults").innerHTML = `
            <div class="scan-summary">
                <div class="scan-metric">
                    <div class="scan-metric-value">${summary.mention_rate || 0}%</div>
                    <div class="scan-metric-label">Mention Rate</div>
                </div>
                <div class="scan-metric">
                    <div class="scan-metric-value">${scores.accuracy || 0}</div>
                    <div class="scan-metric-label">Accuracy</div>
                </div>
                <div class="scan-metric">
                    <div class="scan-metric-value">${scores.sentiment || 0}</div>
                    <div class="scan-metric-label">Sentiment</div>
                </div>
                <div class="scan-metric">
                    <div class="scan-metric-value">${summary.hallucinations_found || 0}</div>
                    <div class="scan-metric-label">Hallucinations</div>
                </div>
                <div class="scan-metric">
                    <div class="scan-metric-value">${summary.total_responses || 0}</div>
                    <div class="scan-metric-label">Responses</div>
                </div>
                <div class="scan-metric">
                    <div class="scan-metric-value">${scan.api_calls || 0}</div>
                    <div class="scan-metric-label">API Calls</div>
                </div>
            </div>
            ${result.hallucinations && result.hallucinations.length > 0 ? `
            <h4 style="font-size:13px; margin:16px 0 8px;">Detected Hallucinations</h4>
            <table class="data-table">
                <thead><tr><th>Claim</th><th>Severity</th><th>Category</th><th>Model</th></tr></thead>
                <tbody>
                    ${result.hallucinations.map(h => `
                        <tr>
                            <td>${esc(h.hallucinated_claim)}</td>
                            <td><span class="severity-${h.severity}">${h.severity}</span></td>
                            <td>${esc(h.category || "--")}</td>
                            <td>${esc(h.model)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>` : ""}
            <p style="font-size:12px; color:var(--text-muted); margin-top:12px;">
                Scan completed in ${scan.completed_at ? "completed" : "running"} | Cost: $${(scan.estimated_cost || 0).toFixed(4)}
            </p>
        `;
        toast(result.message || "Scan complete", "success");
    }

    // Reload scan history
    loadScanHistory(brandId);
}

async function loadScanHistory(brandId) {
    if (!brandId) brandId = document.getElementById("scanBrandSelect").value;
    if (!brandId) return;

    const data = await apiGet(`/api/scan/perception/${brandId}/history`);
    if (!data || !data.scans || data.scans.length === 0) {
        document.getElementById("scanHistory").innerHTML = '<p class="empty-state">No scan history.</p>';
        return;
    }

    document.getElementById("scanHistory").innerHTML = `
        <table class="data-table">
            <thead><tr><th>Date</th><th>Status</th><th>Mention Rate</th><th>Accuracy</th><th>Hallucinations</th><th>Depth</th></tr></thead>
            <tbody>
                ${data.scans.map(s => {
                    const sum = s.summary || {};
                    const scores = s.scores || {};
                    return `<tr>
                        <td>${formatDate(s.created_at)}</td>
                        <td><span class="tag ${s.status === "completed" ? "tag-success" : s.status === "failed" ? "tag-error" : "tag-warning"}">${s.status}</span></td>
                        <td>${sum.mention_rate || "--"}%</td>
                        <td>${scores.accuracy || "--"}</td>
                        <td>${sum.hallucinations_found || 0}</td>
                        <td>${s.depth || "standard"}</td>
                    </tr>`;
                }).join("")}
            </tbody>
        </table>
    `;
}

// ── Hallucinations ───────────────────────────────────────
async function loadHallucinations() {
    const brandId = document.getElementById("halBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }

    const data = await apiGet(`/api/hallucinations/${brandId}`);
    const panel = document.getElementById("halPanel");

    if (!data || !data.hallucinations || data.hallucinations.length === 0) {
        panel.innerHTML = '<p class="empty-state">No hallucinations detected for this brand.</p>';
        document.getElementById("inertiaPanel").style.display = "none";
        return;
    }

    panel.innerHTML = `
        <table class="data-table">
            <thead><tr><th>Claim</th><th>Severity</th><th>Category</th><th>Status</th><th>Times Seen</th><th>Model</th></tr></thead>
            <tbody>
                ${data.hallucinations.map(h => `
                    <tr>
                        <td style="max-width:300px;">${esc(h.hallucinated_claim)}</td>
                        <td><span class="severity-${h.severity}">${h.severity}</span></td>
                        <td>${esc(h.category || "--")}</td>
                        <td><span class="tag ${h.status === "resolved" ? "tag-success" : h.status === "persistent" ? "tag-error" : "tag-warning"}">${h.status}</span></td>
                        <td>${h.times_seen}</td>
                        <td>${esc(h.model)}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;

    // Load inertia report
    const inertia = await apiGet(`/api/hallucinations/${brandId}/inertia`);
    if (inertia) {
        document.getElementById("inertiaPanel").style.display = "";
        document.getElementById("inertiaBody").innerHTML = `
            <div class="stat-grid">
                <div class="stat-card">
                    <div class="stat-label">Total</div>
                    <div class="stat-value">${inertia.total_hallucinations}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Active</div>
                    <div class="stat-value">${inertia.active}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Persistent</div>
                    <div class="stat-value severity-high">${inertia.persistent}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Inertia</div>
                    <div class="stat-value">${inertia.avg_inertia_score}</div>
                </div>
            </div>
        `;
    }
}

// ── Share of Voice ───────────────────────────────────────
async function loadSoV() {
    const brandId = document.getElementById("sovBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }

    // Trust class
    const trust = await apiGet(`/api/trust-class/${brandId}`);
    if (trust && trust.trust_classes) {
        document.getElementById("sovStats").style.display = "";
        const tc = trust.trust_classes;
        const total = trust.total_responses || 1;
        const pct = trust.percentages || {};

        document.getElementById("sovTrustClass").textContent = trust.dominant_class || "--";
        document.getElementById("sovTrustClass").style.color =
            trust.dominant_class === "authority" ? "var(--gold)" :
            trust.dominant_class === "reference" ? "var(--info)" :
            trust.dominant_class === "passing" ? "var(--text-muted)" : "var(--error)";

        document.getElementById("trustClassPanel").innerHTML = `
            <div class="trust-bar">
                <div class="trust-bar-seg authority" style="width:${pct.authority || 0}%">${pct.authority || 0}%</div>
                <div class="trust-bar-seg reference" style="width:${pct.reference || 0}%">${pct.reference || 0}%</div>
                <div class="trust-bar-seg passing" style="width:${pct.passing || 0}%">${pct.passing || 0}%</div>
                <div class="trust-bar-seg absent" style="width:${pct.absent || 0}%">${pct.absent || 0}%</div>
            </div>
            <div style="display:flex; gap:16px; margin-top:12px; font-size:12px; flex-wrap:wrap;">
                <span style="color:var(--gold);">Authority: ${tc.authority || 0}</span>
                <span style="color:var(--info);">Reference: ${tc.reference || 0}</span>
                <span style="color:var(--text-muted);">Passing: ${tc.passing || 0}</span>
                <span style="color:var(--error);">Absent: ${tc.absent || 0}</span>
            </div>
            <p style="font-size:12px; color:var(--text-muted); margin-top:12px;">Based on ${total} LLM responses from scan #${trust.scan_id}</p>
        `;
    } else {
        document.getElementById("trustClassPanel").innerHTML = '<p class="empty-state">No trust class data. Run a perception scan first.</p>';
    }

    // Velocity
    const velocity = await apiGet(`/api/sov/${brandId}/velocity`);
    if (velocity) {
        const v = velocity.velocity || 0;
        document.getElementById("sovVelocity").textContent = (v > 0 ? "+" : "") + v;
        document.getElementById("sovVelocity").style.color = v > 0 ? "var(--success)" : v < 0 ? "var(--error)" : "var(--text-muted)";
        document.getElementById("sovMentionRate").textContent = (velocity.current_mention_rate || 0) + "%";
    }
}

// ── Browser LLMs ─────────────────────────────────────────
async function loadBrowserStatus() {
    const data = await apiGet("/api/browser/status");
    const panel = document.getElementById("browserSessions");

    if (!data || data.error) {
        panel.innerHTML = '<p class="empty-state">Browser automation service unavailable. Playwright may not be installed.</p>';
        return;
    }

    const sessions = data.sessions || {};
    panel.innerHTML = '<div class="session-grid">' + Object.entries(sessions).map(([name, info]) => `
        <div class="session-card">
            <div class="session-card-name">${name}</div>
            <div class="session-card-status">
                ${info.has_session
                    ? '<span class="tag tag-success">Session Active</span>'
                    : '<span class="tag tag-muted">No Session</span>'}
            </div>
            ${!info.has_session
                ? `<button class="btn btn-outline btn-small" onclick="loginBrowser('${name}')">Login</button>`
                : `<button class="btn btn-outline btn-small" onclick="testQuery('${name}')">Test</button>`}
        </div>
    `).join("") + '</div>';
}

async function loginBrowser(model) {
    toast(`Opening ${model} login page...`, "info");
    await apiPost(`/api/browser/login/${model}`, {});
}

async function testQuery(model) {
    toast(`Testing ${model}...`, "info");
    const result = await apiPost(`/api/browser/query/${model}`, { prompt: "What is Almost Magic Tech Lab?" });
    if (result && result.text) {
        toast(`${model}: ${result.text.substring(0, 100)}...`, "success");
    }
}

async function queryAllBrowser() {
    const prompt = document.getElementById("browserPrompt").value.trim();
    if (!prompt) { toast("Enter a prompt", "warning"); return; }

    document.getElementById("browserResults").innerHTML = '<div class="loading-overlay"><span class="spinner"></span> Querying all models...</div>';

    const result = await apiPost("/api/browser/query/all", { prompt });
    if (result && result.results) {
        document.getElementById("browserResults").innerHTML = result.results.map(r => `
            <div class="panel" style="margin-bottom:12px;">
                <div class="panel-header"><h3>${esc(r.model || "Unknown")}</h3></div>
                <div class="panel-body">
                    ${r.error
                        ? `<span class="tag tag-error">${esc(r.error)}</span>`
                        : `<p style="font-size:13px; white-space:pre-wrap;">${esc(r.text || "No response")}</p>`}
                </div>
            </div>
        `).join("");
    } else {
        document.getElementById("browserResults").innerHTML = '<p class="empty-state">Query failed.</p>';
    }
}

// ── Chamber 2: Semantic Core ─────────────────────────────
async function runSemanticScan() {
    const brandId = document.getElementById("semanticBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("semanticBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Scanning...';
    const result = await apiPost(`/api/scan/semantic/${brandId}`, {});
    btn.disabled = false; btn.textContent = "Run Semantic Fingerprint";
    if (result && result.fingerprint) {
        const fp = result.fingerprint;
        document.getElementById("semanticStats").style.display = "";
        document.getElementById("semThemes").textContent = (fp.key_themes || []).length;
        document.getElementById("semTone").textContent = fp.tone || "--";
        document.getElementById("semDrift").textContent = "Baseline";
        document.getElementById("semanticPanel").innerHTML = `
            <div style="margin-bottom:12px;"><strong>Key Themes:</strong> ${(fp.key_themes || []).map(t => `<span class="tag tag-gold">${esc(t)}</span>`).join(" ")}</div>
            <div style="margin-bottom:12px;"><strong>Tone:</strong> ${esc(fp.tone || "--")} | <strong>Positioning:</strong> ${esc(fp.positioning || "--")}</div>
            <div style="margin-bottom:12px;"><strong>Differentiators:</strong> ${(fp.differentiators || []).map(d => `<span class="tag tag-info">${esc(d)}</span>`).join(" ")}</div>
            <p style="font-size:12px; color:var(--text-muted);">Fingerprint ID: ${fp.id} | Created: ${formatDate(fp.created_at)}</p>
        `;
        toast(result.message || "Semantic scan complete", "success");
    }
    loadDriftHistory(brandId);
}

async function loadDriftHistory(brandId) {
    const data = await apiGet(`/api/drift/${brandId}`);
    if (data && data.drift_events && data.drift_events.length > 0) {
        document.getElementById("semDrift").textContent = data.drift_events.length;
        document.getElementById("driftPanel").innerHTML = data.drift_events.map(d => `
            <div class="panel" style="margin-bottom:8px; padding:12px; background:var(--surface); border-radius:var(--radius);">
                <strong>${esc(d.drift_type || "drift")}</strong> (${formatDate(d.detected_at)})
                <div style="font-size:12px; margin-top:4px;">Added: ${(d.themes_added || []).join(", ") || "none"} | Removed: ${(d.themes_removed || []).join(", ") || "none"}</div>
            </div>
        `).join("");
    }
}

// ── Chamber 3: Neural Vector Map ─────────────────────────
async function runVectorMap() {
    const brandId = document.getElementById("vectorBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("vectorBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Mapping...';
    const result = await apiPost(`/api/vectormap/${brandId}/generate`, {});
    btn.disabled = false; btn.textContent = "Generate Vector Map";
    if (result && result.map) {
        const m = result.map;
        document.getElementById("vectorPanel").innerHTML = `
            <div style="margin-bottom:12px;"><strong>Brand:</strong> ${esc(m.brand)} | <strong>Dimensions:</strong> ${m.dimensions || 768}</div>
            ${(m.competitors || []).map(c => `
                <div style="padding:8px 12px; background:var(--surface); border-radius:var(--radius); margin-bottom:6px; display:flex; justify-content:space-between;">
                    <span>${esc(c.name)}</span>
                    <span>Similarity: <strong style="color:var(--gold);">${(c.similarity * 100).toFixed(1)}%</strong> | Distance: ${c.distance.toFixed(3)}</span>
                </div>
            `).join("") || '<p class="empty-state">No competitors to map against. Add competitors first.</p>'}
        `;
        toast(result.message || "Vector map generated", "success");
    }
}

// ── Chamber 4: Authority Engine ──────────────────────────
async function runAuthorityScan() {
    const brandId = document.getElementById("authBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("authBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Scanning...';
    const result = await apiPost(`/api/authority/${brandId}/scan`, {});
    btn.disabled = false; btn.textContent = "Run Authority Scan";
    if (result && result.scan) {
        const sum = result.scan.summary || {};
        document.getElementById("authStats").style.display = "";
        document.getElementById("authScore").textContent = result.scan.scores?.authority_score || "--";
        document.getElementById("authTop3").textContent = sum.in_top_3 || 0;
        document.getElementById("authTop10").textContent = sum.in_top_10 || 0;
        document.getElementById("authGaps").textContent = sum.gaps || 0;
        const results = result.results || [];
        document.getElementById("authPanel").innerHTML = results.length > 0 ? `
            <table class="data-table">
                <thead><tr><th>Keyword</th><th>Position</th><th>Top 3</th><th>Top 10</th><th>Score</th></tr></thead>
                <tbody>${results.map(r => `
                    <tr>
                        <td>${esc(r.keyword)}</td>
                        <td>${r.brand_position || "Not found"}</td>
                        <td>${r.in_top_3 ? '<span style="color:var(--success);">Yes</span>' : '<span style="color:var(--error);">No</span>'}</td>
                        <td>${r.in_top_10 ? '<span style="color:var(--success);">Yes</span>' : '<span style="color:var(--error);">No</span>'}</td>
                        <td>${r.authority_score || 0}</td>
                    </tr>
                `).join("")}</tbody>
            </table>
        ` : '<p class="empty-state">No keywords to check. Add approved keywords first.</p>';
        toast(result.message || "Authority scan complete", "success");
    }
}

// ── Chamber 5: Survivability Lab ─────────────────────────
async function runSurvivabilityTest() {
    const brandId = document.getElementById("survBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("survBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Testing...';
    const result = await apiPost(`/api/survivability/${brandId}/test`, {});
    btn.disabled = false; btn.textContent = "Run Survivability Test";
    if (result && result.scan) {
        const sum = result.scan.summary || {};
        document.getElementById("survStats").style.display = "";
        document.getElementById("survScore").textContent = result.scan.scores?.survivability_score || "--";
        document.getElementById("survPreserved").textContent = sum.preserved || 0;
        document.getElementById("survDistorted").textContent = sum.distorted || 0;
        const results = result.results || [];
        document.getElementById("survPanel").innerHTML = results.length > 0 ? `
            <table class="data-table">
                <thead><tr><th>Content</th><th>Accuracy</th><th>Preserved</th><th>Notes</th></tr></thead>
                <tbody>${results.map(r => `
                    <tr>
                        <td>${esc(r.content_type)}</td>
                        <td><strong>${r.recall_accuracy || 0}%</strong></td>
                        <td>${r.preserved ? '<span style="color:var(--success);">Yes</span>' : '<span style="color:var(--error);">No</span>'}</td>
                        <td style="font-size:12px;">${esc(r.distortion_notes || "")}</td>
                    </tr>
                `).join("")}</tbody>
            </table>
        ` : '<p class="empty-state">Add brand description, tagline, or value propositions first.</p>';
        toast(result.message || "Survivability test complete", "success");
    }
}

// ── Chamber 6: Machine Interface ─────────────────────────
async function runTechnicalAudit() {
    const brandId = document.getElementById("techBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("techBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Auditing...';
    const result = await apiPost(`/api/technical/${brandId}/audit`, {});
    btn.disabled = false; btn.textContent = "Run Technical Audit";
    if (result && result.audit) {
        const a = result.audit;
        document.getElementById("techStats").style.display = "";
        document.getElementById("techScore").textContent = a.score || 0;
        document.getElementById("techIssues").textContent = (a.issues || []).length;
        const checks = [
            { label: "JSON-LD Structured Data", ok: a.has_jsonld, priority: "high" },
            { label: "OpenGraph Meta Tags", ok: a.has_opengraph, priority: "medium" },
            { label: "XML Sitemap", ok: a.has_sitemap, priority: "medium" },
            { label: "Robots.txt", ok: a.has_robots, priority: "low" },
            { label: "Schema.org Types", ok: (a.schema_types || []).length > 0, priority: "high" },
        ];
        document.getElementById("techChecklist").innerHTML = checks.map(c => `
            <div style="display:flex; align-items:center; gap:10px; padding:8px 0; border-bottom:1px solid var(--border);">
                <span style="color:${c.ok ? 'var(--success)' : 'var(--error)'}; font-size:16px;">${c.ok ? '&#10003;' : '&#10007;'}</span>
                <span style="flex:1;">${c.label}</span>
                <span class="tag ${c.priority === 'high' ? 'tag-error' : c.priority === 'medium' ? 'tag-warning' : 'tag-muted'}">${c.priority}</span>
            </div>
        `).join("");
        if ((a.issues || []).length > 0) {
            document.getElementById("techIssuesPanel").innerHTML = (a.issues || []).map(i => `
                <div style="padding:8px 12px; margin-bottom:6px; background:var(--surface); border-radius:var(--radius); border-left:3px solid ${i.severity === 'high' ? 'var(--error)' : i.severity === 'medium' ? 'var(--warning)' : 'var(--text-muted)'};">
                    <strong>${esc(i.type)}</strong>: ${esc(i.message)}
                </div>
            `).join("");
        }
        toast(`Technical audit complete. Score: ${a.score}/100`, "success");
    }
}

// ── Chamber 7: Amplifier ─────────────────────────────────
async function runAmplifierScan() {
    const brandId = document.getElementById("ampBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("ampBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Analysing...';
    const result = await apiPost(`/api/amplifier/${brandId}/scan`, {});
    btn.disabled = false; btn.textContent = "Run Citation Analysis";
    if (result && result.scan) {
        const sum = result.scan.summary || {};
        document.getElementById("ampStats").style.display = "";
        document.getElementById("ampScore").textContent = sum.avg_citation_score || "--";
        document.getElementById("ampCited").textContent = `${sum.brand_cited || 0}/${sum.queries || 0}`;
        document.getElementById("ampQueries").textContent = sum.queries || 0;
        const results = result.results || [];
        document.getElementById("ampPanel").innerHTML = results.length > 0 ? `
            <table class="data-table">
                <thead><tr><th>Query</th><th>Cited</th><th>Score</th><th>Context</th></tr></thead>
                <tbody>${results.map(r => `
                    <tr>
                        <td style="max-width:250px;">${esc(r.query)}</td>
                        <td>${r.brand_cited ? '<span style="color:var(--success);">Yes</span>' : '<span style="color:var(--error);">No</span>'}</td>
                        <td>${r.citation_score || 0}</td>
                        <td style="font-size:12px;">${esc(r.citation_context || "")}</td>
                    </tr>
                `).join("")}</tbody>
            </table>
        ` : '<p class="empty-state">No citation data yet.</p>';
        toast(result.message || "Amplifier scan complete", "success");
    }
    loadShadow(brandId);
}

async function loadShadow(brandId) {
    const data = await apiGet(`/api/amplifier/${brandId}/shadow`);
    if (data && data.shadows && data.shadows.length > 0) {
        document.getElementById("shadowPanel").innerHTML = data.shadows.map(s => `
            <div style="display:flex; justify-content:space-between; padding:8px 12px; background:var(--surface); border-radius:var(--radius); margin-bottom:4px;">
                <span>${esc(s.brand)}</span>
                <span style="color:var(--warning);"><strong>${s.appearances}</strong> appearances</span>
            </div>
        `).join("");
    }
}

// ── Chamber 8: The Proof ─────────────────────────────────
async function fetchVisitors() {
    const brandId = document.getElementById("proofBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("proofBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Fetching...';
    const result = await apiPost(`/api/proof/${brandId}/visitors`, {});
    btn.disabled = false; btn.textContent = "Fetch Visitors";
    if (result) {
        document.getElementById("proofStats").style.display = "";
        document.getElementById("proofTotal").textContent = result.total || 0;
        document.getElementById("proofHot").textContent = result.hot || 0;
        document.getElementById("proofWarm").textContent = result.warm || 0;
        document.getElementById("proofCool").textContent = result.cool || 0;
        const leads = result.leads || [];
        document.getElementById("proofPanel").innerHTML = leads.length > 0 ? `
            <table class="data-table">
                <thead><tr><th>Company</th><th>Industry</th><th>Score</th><th>Tier</th><th>Visits</th></tr></thead>
                <tbody>${leads.map(l => `
                    <tr>
                        <td><strong>${esc(l.company_name)}</strong><br><span style="font-size:11px; color:var(--text-muted);">${esc(l.company_domain || "")}</span></td>
                        <td>${esc(l.industry || "--")}</td>
                        <td>${l.lead_score}</td>
                        <td><span class="tag ${l.lead_tier === 'hot' ? 'tag-error' : l.lead_tier === 'warm' ? 'tag-warning' : 'tag-muted'}">${l.lead_tier}</span></td>
                        <td>${l.visit_count}</td>
                    </tr>
                `).join("")}</tbody>
            </table>
        ` : '<p class="empty-state">No visitors found. Ensure Snitcher is configured and the brand has a domain.</p>';
        toast(`${result.total || 0} leads fetched, ${result.hot || 0} hot`, "success");
    }
}

// ── Chamber 9: The Oracle ────────────────────────────────
async function runOracleScan() {
    const brandId = document.getElementById("oracleBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("oracleBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Scanning...';
    const result = await apiPost(`/api/oracle/${brandId}/scan`, {});
    btn.disabled = false; btn.textContent = "Scan for Trends";
    if (result && result.scan) {
        const sum = result.scan.summary || {};
        document.getElementById("oracleStats").style.display = "";
        document.getElementById("oracleSignals").textContent = sum.signals_found || 0;
        document.getElementById("oracleUrgent").textContent = sum.high_urgency || 0;
        const signals = result.signals || [];
        document.getElementById("oraclePanel").innerHTML = signals.length > 0 ? `
            <table class="data-table">
                <thead><tr><th>Signal</th><th>Type</th><th>Urgency</th><th>Relevance</th><th>Recommendation</th></tr></thead>
                <tbody>${signals.map(s => `
                    <tr>
                        <td>${esc(s.title)}</td>
                        <td><span class="tag ${s.signal_type === 'opportunity' ? 'tag-success' : s.signal_type === 'threat' ? 'tag-error' : 'tag-info'}">${s.signal_type}</span></td>
                        <td><span class="tag ${s.urgency === 'critical' ? 'tag-error' : s.urgency === 'high' ? 'tag-warning' : 'tag-muted'}">${s.urgency}</span></td>
                        <td>${s.relevance_score}</td>
                        <td style="font-size:12px;">${esc(s.recommendation || "")}</td>
                    </tr>
                `).join("")}</tbody>
            </table>
        ` : '<p class="empty-state">No signals detected.</p>';
        toast(result.message || "Oracle scan complete", "success");
    }
    loadForecast(brandId);
}

async function loadForecast(brandId) {
    const data = await apiGet(`/api/oracle/${brandId}/forecast`);
    if (data) {
        const color = data.outlook === "positive" ? "var(--success)" : data.outlook === "cautious" ? "var(--warning)" : "var(--text-muted)";
        document.getElementById("oracleOutlook").textContent = data.outlook || "--";
        document.getElementById("oracleOutlook").style.color = color;
        document.getElementById("forecastPanel").innerHTML = `
            <div class="stat-grid" style="margin-bottom:12px;">
                <div class="stat-card"><div class="stat-label">Opportunities</div><div class="stat-value" style="color:var(--success);">${data.opportunities || 0}</div></div>
                <div class="stat-card"><div class="stat-label">Threats</div><div class="stat-value" style="color:var(--error);">${data.threats || 0}</div></div>
                <div class="stat-card"><div class="stat-label">Trends</div><div class="stat-value" style="color:var(--info);">${data.trends || 0}</div></div>
            </div>
        `;
    }
}

// ── Chamber 10: The Forge ────────────────────────────────
async function runForge() {
    const brandId = document.getElementById("forgeBrandSelect").value;
    if (!brandId) { toast("Select a brand first", "warning"); return; }
    const btn = document.getElementById("forgeBtn");
    btn.disabled = true; btn.innerHTML = '<span class="spinner"></span> Forging...';
    const result = await apiPost(`/api/forge/${brandId}/generate`, {});
    btn.disabled = false; btn.textContent = "Generate Briefs";
    if (result) {
        const sum = result.scan?.summary || {};
        document.getElementById("forgeStats").style.display = "";
        document.getElementById("forgeTotal").textContent = sum.briefs_generated || 0;
        document.getElementById("forgeCorrections").textContent = sum.correction || 0;
        document.getElementById("forgeAuthority").textContent = sum.authority || 0;
        const briefs = result.briefs || [];
        document.getElementById("forgePanel").innerHTML = briefs.length > 0 ? briefs.map(b => `
            <div style="padding:12px; background:var(--surface); border-radius:var(--radius); margin-bottom:8px; border-left:3px solid var(--gold);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
                    <strong>${esc(b.title)}</strong>
                    <div>
                        <span class="tag tag-gold">${esc(b.brief_type)}</span>
                        <span class="tag tag-info">${esc(b.gap_source)}</span>
                    </div>
                </div>
                <div style="font-size:12px; color:var(--text-muted); margin-bottom:8px;">Keyword: ${esc(b.target_keyword || "--")}</div>
                ${(b.outline || []).length > 0 ? `<ul style="font-size:12px; padding-left:16px;">${b.outline.map(o => `<li>${esc(o)}</li>`).join("")}</ul>` : ""}
                <div style="display:flex; gap:6px; margin-top:8px;">
                    <button class="btn btn-gold btn-small" onclick="generateContent(${brandId}, ${b.id})">Generate Content</button>
                    <button class="btn btn-outline btn-small" onclick="approveBrief(${brandId}, ${b.id})">Approve</button>
                </div>
            </div>
        `).join("") : '<p class="empty-state">No briefs generated. Run perception or authority scans first to identify gaps.</p>';
        toast(result.message || "Forge complete", "success");
    }
    loadPipeline(brandId);
}

async function generateContent(brandId, briefId) {
    toast("Generating content...", "info");
    const result = await apiPost(`/api/forge/${brandId}/briefs/${briefId}/generate`, {});
    if (result && result.brief) {
        toast("Content generated for: " + result.brief.title, "success");
        runForge();
    }
}

async function approveBrief(brandId, briefId) {
    const result = await apiPut(`/api/forge/${brandId}/briefs/${briefId}/approve`, {});
    if (result) {
        toast("Brief approved", "success");
        runForge();
    }
}

async function loadPipeline(brandId) {
    const data = await apiGet(`/api/forge/${brandId}/pipeline`);
    if (data) {
        document.getElementById("forgePublished").textContent = data.published || 0;
    }
}

// ── Toast Notifications ──────────────────────────────────
function toast(message, type = "info") {
    const container = document.getElementById("toastContainer");
    const el = document.createElement("div");
    el.className = `toast ${type}`;
    el.textContent = message;
    container.appendChild(el);
    setTimeout(() => { el.style.opacity = "0"; setTimeout(() => el.remove(), 300); }, 4000);
}

// ── Utilities ────────────────────────────────────────────
function esc(text) {
    if (!text) return "";
    const div = document.createElement("div");
    div.textContent = String(text);
    return div.innerHTML;
}

function formatDate(iso) {
    if (!iso) return "--";
    const d = new Date(iso);
    return d.toLocaleDateString("en-AU", { day: "numeric", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

// ── SEO Ask ─────────────────────────────────────────────
async function runSeoAsk() {
    const query = document.getElementById("seoQuery").value.trim();
    if (!query) { toast("Type your SEO question first", "warning"); return; }

    const brandId = document.getElementById("seoBrandSelect").value || undefined;
    const btn = document.getElementById("seoAskBtn");
    btn.disabled = true;
    btn.innerHTML = '<span class="spinner"></span> Analysing...';

    const result = await apiPost("/api/seo/ask", { query, brand_id: brandId ? parseInt(brandId) : null });

    btn.disabled = false;
    btn.textContent = "Ask Peterman";

    if (!result) return;

    document.getElementById("seoResultPanel").style.display = "";

    if (result.llm_status === "unavailable") {
        // Fallback: show raw SERP data
        document.getElementById("seoResultBody").innerHTML = `
            <div style="padding:12px; background:var(--surface); border-radius:var(--radius); border-left:3px solid var(--warning); margin-bottom:12px;">
                <strong>AI unavailable</strong> — ${esc(result.message)}
            </div>
            ${result.keywords?.from_serp?.length ? `
                <h4 style="font-size:13px; margin-bottom:8px;">Keywords from SERP</h4>
                <div style="display:flex; flex-wrap:wrap; gap:6px;">
                    ${result.keywords.from_serp.map(k => `<span class="tag tag-gold">${esc(k)}</span>`).join("")}
                </div>
            ` : ""}
        `;
    } else {
        const a = result.analysis || {};
        document.getElementById("seoResultBody").innerHTML = `
            ${a.summary ? `<p style="font-size:14px; margin-bottom:16px; line-height:1.6;">${esc(a.summary)}</p>` : ""}

            ${a.keywords ? `
            <div style="margin-bottom:16px;">
                <h4 style="font-size:13px; margin-bottom:8px;">Keywords</h4>
                ${a.keywords.primary ? `<div style="margin-bottom:6px;"><strong style="font-size:12px;">Primary:</strong> ${a.keywords.primary.map(k => `<span class="tag tag-gold">${esc(k)}</span>`).join(" ")}</div>` : ""}
                ${a.keywords.long_tail ? `<div style="margin-bottom:6px;"><strong style="font-size:12px;">Long-tail:</strong> ${a.keywords.long_tail.map(k => `<span class="tag tag-info">${esc(k)}</span>`).join(" ")}</div>` : ""}
                ${a.keywords.questions ? `<div><strong style="font-size:12px;">Questions:</strong> ${a.keywords.questions.map(k => `<span class="tag tag-muted">${esc(k)}</span>`).join(" ")}</div>` : ""}
            </div>` : ""}

            ${a.meta_tags ? `
            <div style="margin-bottom:16px;">
                <h4 style="font-size:13px; margin-bottom:8px;">Recommended Meta Tags</h4>
                <div style="background:var(--surface); padding:12px; border-radius:var(--radius); font-family:var(--font-mono, monospace); font-size:12px;">
                    <div style="margin-bottom:4px;"><span style="color:var(--gold);">title:</span> ${esc(a.meta_tags.title || "")}</div>
                    <div style="margin-bottom:4px;"><span style="color:var(--gold);">description:</span> ${esc(a.meta_tags.description || "")}</div>
                    <div style="margin-bottom:4px;"><span style="color:var(--gold);">h1:</span> ${esc(a.meta_tags.h1 || "")}</div>
                    <div style="margin-bottom:4px;"><span style="color:var(--gold);">og:title:</span> ${esc(a.meta_tags.og_title || "")}</div>
                    <div><span style="color:var(--gold);">og:description:</span> ${esc(a.meta_tags.og_description || "")}</div>
                </div>
            </div>` : ""}

            ${a.content_score ? `
            <div style="margin-bottom:16px;">
                <h4 style="font-size:13px; margin-bottom:8px;">Content Score</h4>
                <div class="stat-grid">
                    <div class="stat-card">
                        <div class="stat-label">Opportunity</div>
                        <div class="stat-value" style="color:${a.content_score.opportunity_score >= 70 ? 'var(--success)' : a.content_score.opportunity_score >= 40 ? 'var(--warning)' : 'var(--error)'};">${a.content_score.opportunity_score || 0}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Competition</div>
                        <div class="stat-value">${esc(a.content_score.competition_level || "--")}</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-label">Difficulty</div>
                        <div class="stat-value">${esc(a.content_score.estimated_difficulty || "--")}</div>
                    </div>
                </div>
                ${a.content_score.recommendation ? `<p style="font-size:13px; margin-top:8px; color:var(--text-secondary);">${esc(a.content_score.recommendation)}</p>` : ""}
            </div>` : ""}

            ${a.content_analysis ? `
            <div style="margin-bottom:16px;">
                <h4 style="font-size:13px; margin-bottom:8px;">Content Analysis</h4>
                ${a.content_analysis.content_gaps ? `<div style="margin-bottom:6px;"><strong style="font-size:12px;">Gaps:</strong><ul style="font-size:12px; padding-left:16px;">${a.content_analysis.content_gaps.map(g => `<li>${esc(g)}</li>`).join("")}</ul></div>` : ""}
                ${a.content_analysis.recommended_topics ? `<div><strong style="font-size:12px;">Recommended topics:</strong><ul style="font-size:12px; padding-left:16px;">${a.content_analysis.recommended_topics.map(t => `<li>${esc(t)}</li>`).join("")}</ul></div>` : ""}
            </div>` : ""}

            ${a.action_items ? `
            <div>
                <h4 style="font-size:13px; margin-bottom:8px;">Action Items</h4>
                <ol style="font-size:13px; padding-left:16px;">
                    ${a.action_items.map(i => `<li style="margin-bottom:4px;">${esc(i)}</li>`).join("")}
                </ol>
            </div>` : ""}

            <p style="font-size:11px; color:var(--text-muted); margin-top:16px;">
                Model: ${esc(result.model || "")} | Tokens: ${result.tokens_used || 0} | Cost: $0.00 (local)
            </p>
        `;
        toast("SEO analysis complete", "success");
    }

    // Show SERP results
    if (result.serp_results && result.serp_results.length > 0) {
        document.getElementById("seoSerpPanel").style.display = "";
        document.getElementById("seoSerpBody").innerHTML = `
            <table class="data-table">
                <thead><tr><th>Title</th><th>URL</th><th>Engine</th></tr></thead>
                <tbody>
                    ${result.serp_results.map(r => `
                        <tr>
                            <td>${esc(r.title)}</td>
                            <td style="font-size:11px; max-width:300px; overflow:hidden; text-overflow:ellipsis;"><a href="${esc(r.url)}" target="_blank" style="color:var(--info);">${esc(r.url)}</a></td>
                            <td>${esc(r.engine || "")}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    }
}
