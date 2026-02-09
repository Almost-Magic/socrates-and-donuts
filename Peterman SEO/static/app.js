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
        perception: "Perception Scan",
        hallucinations: "Hallucination Tracker",
        sov: "Share of Voice",
        browser: "Browser LLM Sessions",
    };
    document.getElementById("pageTitle").textContent = titles[page] || page;

    // Load page-specific data
    if (page === "brands") loadBrands();
    if (page === "perception") populateBrandSelects();
    if (page === "hallucinations") populateBrandSelects();
    if (page === "sov") populateBrandSelects();
    if (page === "browser") loadBrowserStatus();
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
    const selects = ["scanBrandSelect", "halBrandSelect", "sovBrandSelect"];
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
