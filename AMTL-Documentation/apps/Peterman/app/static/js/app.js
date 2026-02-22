/**
 * Peterman SPA Application
 * Handles all frontend logic including API calls, domain management, theme toggling, and UI updates.
 */

const API_BASE = '/api';
let state = { domains: [], currentDomain: null, theme: 'dark', helpContext: 'war-room' };

const HELP_CONTENT = {
    'war-room': { title: 'The War Room', content: '<p>The War Room is your command centre for all managed domains.</p>' },
    'domain-card': { title: 'Domain Card', content: '<p>Shows domain summary with Peterman Score, status, and key metrics.</p>' },
    'peterman-score': { title: 'Peterman Score', content: '<p>Composite 0-100 metric: LLM Share of Voice (25%), Semantic Gravity (20%), Technical (15%), Survivability (15%), Hallucination Debt (10%), Competitive (10%), Predictive (5%).</p><p>Colour: 0-40 red, 40-65 amber, 65-85 gold, 85-100 platinum.</p>' },
    'add-domain': { title: 'Adding a Domain', content: '<p>Enter domain name, display name, CMS type, and weekly budget.</p>' }
};

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    initEventListeners();
    loadDomains();
    initHelp();
});

function initTheme() {
    const savedTheme = localStorage.getItem('peterman-theme') || 'dark';
    document.body.setAttribute('data-theme', savedTheme);
    state.theme = savedTheme;
}

function initEventListeners() {
    // Theme toggle
    document.getElementById('theme-toggle').addEventListener('click', () => {
        const newTheme = state.theme === 'dark' ? 'light' : 'dark';
        document.body.setAttribute('data-theme', newTheme);
        localStorage.setItem('peterman-theme', newTheme);
        state.theme = newTheme;
    });
    
    // Add domain
    document.getElementById('add-domain-btn').addEventListener('click', () => document.getElementById('modal-overlay').classList.add('visible'));
    document.getElementById('close-modal').addEventListener('click', closeModal);
    document.getElementById('cancel-add').addEventListener('click', closeModal);
    document.getElementById('modal-overlay').addEventListener('click', (e) => { if (e.target === e.currentTarget) closeModal(); });
    document.getElementById('add-domain-form').addEventListener('submit', handleAddDomain);
    
    // Help
    document.getElementById('help-toggle').addEventListener('click', () => document.getElementById('help-panel').classList.toggle('visible'));
    document.getElementById('close-help').addEventListener('click', () => document.getElementById('help-panel').classList.remove('visible'));
    
    // Back to war room
    document.getElementById('back-to-war-room').addEventListener('click', showWarRoom);
    
    // Workflow action buttons
    document.getElementById('workflow-actions').addEventListener('click', handleWorkflowAction);
}

function closeModal() {
    document.getElementById('modal-overlay').classList.remove('visible');
    document.getElementById('add-domain-form').reset();
}

// ==================== Keyboard Navigation ====================

document.addEventListener('keydown', (e) => {
    // Don't handle if user is typing in an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA' || e.target.isContentEditable) {
        return;
    }
    
    // ? key → Open help panel
    if (e.key === '?' || (e.shiftKey && e.key === '/')) {
        e.preventDefault();
        document.getElementById('help-panel').classList.toggle('visible');
        showHelp(state.helpContext);
        return;
    }
    
    // Escape → Close any modal/panel
    if (e.key === 'Escape') {
        e.preventDefault();
        // Close help panel
        document.getElementById('help-panel').classList.remove('visible');
        // Close modal
        closeModal();
        return;
    }
    
    // a key → Jump to Approval Inbox
    if (e.key === 'a' || e.key === 'A') {
        e.preventDefault();
        if (state.currentDomain) {
            // If on domain detail, scroll to approvals
            const approvalsPanel = document.getElementById('approvals-content');
            if (approvalsPanel) {
                approvalsPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
                // Flash the panel
                approvalsPanel.parentElement.style.boxShadow = '0 0 0 2px var(--amtl-gold)';
                setTimeout(() => {
                    approvalsPanel.parentElement.style.boxShadow = '';
                }, 2000);
            }
        } else {
            // On war room - open add domain modal (closest equivalent)
            document.getElementById('modal-overlay').classList.add('visible');
        }
        showToast('Press A to access approvals', 'info');
        return;
    }
    
    // t key → Jump to Journey Timeline (or probes panel)
    if (e.key === 't' || e.key === 'T') {
        e.preventDefault();
        if (state.currentDomain) {
            const probesPanel = document.getElementById('probes-content');
            if (probesPanel) {
                probesPanel.scrollIntoView({ behavior: 'smooth', block: 'center' });
                probesPanel.parentElement.style.boxShadow = '0 0 0 2px var(--amtl-gold)';
                setTimeout(() => {
                    probesPanel.parentElement.style.boxShadow = '';
                }, 2000);
            }
        }
        showToast('Timeline: Probe history shown in Probes panel', 'info');
        return;
    }
    
    // r key → Refresh War Room data
    if (e.key === 'r' || e.key === 'R') {
        e.preventDefault();
        if (state.currentDomain) {
            refreshScore();
            loadAllPanels();
        } else {
            loadDomains();
        }
        showToast('Data refreshed', 'success');
        return;
    }
});

function initHelp() { showHelp('war-room'); }

function showHelp(context) {
    state.helpContext = context;
    const content = HELP_CONTENT[context];
    if (content) {
        document.getElementById('help-content').innerHTML = `<h4>${content.title}</h4>${content.content}`;
    }
}

// ==================== Domain Management ====================

async function loadDomains() {
    try {
        const response = await fetch(`${API_BASE}/domains`);
        const data = await response.json();
        state.domains = data.domains || [];
        renderDomains();
    } catch (error) {
        console.error('Failed to load domains:', error);
        showToast('Failed to load domains', 'error');
    }
}

async function handleAddDomain(e) {
    e.preventDefault();
    const domainData = {
        domain_name: document.getElementById('domain-name').value,
        display_name: document.getElementById('display-name').value || document.getElementById('domain-name').value,
        owner_label: document.getElementById('owner-label').value,
        cms_type: document.getElementById('cms-type').value,
        budget_weekly_aud: parseFloat(document.getElementById('budget').value) || 50
    };
    try {
        const response = await fetch(`${API_BASE}/domains`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(domainData)
        });
        if (!response.ok) throw new Error('Failed to add domain');
        const newDomain = await response.json();
        state.domains.push(newDomain);
        renderDomains();
        closeModal();
        showToast('Domain added successfully', 'success');
    } catch (error) {
        console.error('Failed to add domain:', error);
        showToast(error.message, 'error');
    }
}

// ==================== War Room ====================

async function renderDomains() {
    const grid = document.getElementById('domain-grid');
    const emptyState = document.getElementById('empty-state');
    
    if (state.domains.length === 0) {
        grid.innerHTML = '';
        emptyState.classList.add('visible');
        return;
    }
    
    emptyState.classList.remove('visible');
    
    const cards = await Promise.all(state.domains.map(async (d) => {
        const score = await getDomainScore(d.domain_id);
        return createDomainCard(d, score);
    }));
    
    grid.innerHTML = cards.join('');
    
    // Add click handlers for domain cards
    document.querySelectorAll('.domain-card').forEach(card => {
        card.addEventListener('click', () => {
            const domainId = card.dataset.domainId;
            showDomainDetail(domainId);
        });
    });
}

function createDomainCard(domain, score) {
    const totalScore = score?.total_score || 50;
    const scoreClass = getScoreClass(totalScore);
    const circumference = 2 * Math.PI * 45;
    const offset = circumference - (totalScore / 100) * circumference;
    
    return `
        <div class="domain-card" data-domain-id="${domain.domain_id}">
            <div class="domain-card-header">
                <div class="domain-info">
                    <h3>${escapeHtml(domain.display_name)}</h3>
                    <span class="domain-name">${escapeHtml(domain.domain_name)}</span>
                </div>
                <span class="domain-status ${domain.status}">${domain.status}</span>
            </div>
            <div class="score-gauge">
                <svg width="120" height="120">
                    <circle class="score-gauge-bg" cx="60" cy="60" r="45"/>
                    <circle class="score-gauge-fill ${scoreClass}" cx="60" cy="60" r="45" stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"/>
                </svg>
                <span class="score-value">${Math.round(totalScore)}</span>
            </div>
            <p class="score-label">Peterman Score</p>
            <div class="domain-meta">
                <span>${domain.probe_cadence || 'weekly'}</span>
                <span>$${domain.budget_weekly_aud || 50}/week</span>
            </div>
        </div>`;
}

// ==================== Domain Detail ====================

async function showDomainDetail(domainId) {
    const domain = state.domains.find(d => d.domain_id === domainId);
    if (!domain) return;
    
    state.currentDomain = domain;
    
    // Switch views
    document.getElementById('domain-grid').style.display = 'none';
    document.getElementById('empty-state').style.display = 'none';
    document.getElementById('domain-detail').style.display = 'block';
    document.getElementById('back-to-war-room').style.display = 'inline-flex';
    
    // Update header
    document.getElementById('page-title').textContent = domain.display_name;
    document.getElementById('page-subtitle').textContent = domain.domain_name;
    
    // Update domain info
    document.getElementById('detail-domain-name').textContent = domain.display_name;
    document.getElementById('detail-domain-url').textContent = domain.domain_name;
    document.getElementById('detail-status').textContent = domain.status;
    document.getElementById('detail-status').className = `domain-status ${domain.status}`;
    
    // Load score
    await refreshScore();
    
    // Load all panels
    await loadAllPanels();
}

function showWarRoom() {
    state.currentDomain = null;
    
    // Switch views
    document.getElementById('domain-detail').style.display = 'none';
    document.getElementById('domain-grid').style.display = 'grid';
    document.getElementById('back-to-war-room').style.display = 'none';
    
    // Reset header
    document.getElementById('page-title').textContent = 'The War Room';
    document.getElementById('page-subtitle').textContent = 'Multi-domain overview';
    
    // Reload domains to refresh scores
    loadDomains();
}

// ==================== Score ====================

async function getDomainScore(domainId) {
    try {
        const response = await fetch(`${API_BASE}/domains/${domainId}/score`);
        return await response.json();
    } catch { return null; }
}

async function refreshScore() {
    if (!state.currentDomain) return;
    
    const score = await getDomainScore(state.currentDomain.domain_id);
    if (!score) return;
    
    const totalScore = score.total_score || 50;
    const scoreClass = getScoreClass(totalScore);
    
    // Update gauge
    const circumference = 2 * Math.PI * 70;
    const offset = circumference - (totalScore / 100) * circumference;
    
    const circle = document.getElementById('detail-score-circle');
    circle.setAttribute('stroke-dasharray', circumference);
    circle.setAttribute('stroke-dashoffset', offset);
    circle.className = `score-gauge-fill ${scoreClass}`;
    
    document.getElementById('detail-score-value').textContent = Math.round(totalScore);
    
    // Update breakdown
    const breakdown = document.getElementById('score-breakdown');
    const components = score.components || {};
    
    breakdown.innerHTML = Object.entries(components).map(([key, data]) => `
        <div class="score-component">
            <span class="component-name">${key.replace(/_/g, ' ')}</span>
            <span class="component-score ${getScoreClass(data.score)}">${Math.round(data.score)}</span>
        </div>
    `).join('');
}

// ==================== Workflow Actions ====================

async function handleWorkflowAction(e) {
    const btn = e.target.closest('.btn-action');
    if (!btn || !state.currentDomain) return;
    
    const action = btn.dataset.action;
    const domainId = state.currentDomain.domain_id;
    
    showToast(`Running ${action}...`, 'info');
    
    try {
        switch (action) {
            case 'crawl':
                await runAction(`${API_BASE}/domains/${domainId}/crawl`, 'POST');
                showToast('Crawl completed!', 'success');
                break;
            case 'keywords':
                await runAction(`${API_BASE}/domains/${domainId}/suggest-keywords`, 'POST');
                showToast('Keywords generated!', 'success');
                break;
            case 'probe':
                await runAction(`${API_BASE}/domains/${domainId}/probe`, 'POST');
                showToast('Probe completed!', 'success');
                break;
            case 'hallucinations':
                await runAction(`${API_BASE}/domains/${domainId}/hallucinations/detect`, 'POST');
                showToast('Hallucination detection complete!', 'success');
                break;
            case 'briefs':
                // Just refresh the panel
                break;
            case 'approvals':
                // Just refresh the panel
                break;
            case 'score':
                await refreshScore();
                showToast('Score refreshed!', 'success');
                return;
        }
        
        // Refresh panels after action
        await loadAllPanels();
        await refreshScore();
        
    } catch (error) {
        console.error('Workflow action failed:', error);
        showToast(`Action failed: ${error.message}`, 'error');
    }
}

async function runAction(url, method) {
    const response = await fetch(url, { method });
    if (!response.ok) {
        const data = await response.json().catch(() => ({ error: 'Unknown error' }));
        throw new Error(data.error || 'Action failed');
    }
    return await response.json().catch(() => ({}));
}

// ==================== Panels ====================

async function loadAllPanels() {
    if (!state.currentDomain) return;
    
    const domainId = state.currentDomain.domain_id;
    
    // Load chambers
    loadChambers(domainId);
    
    // Load probes
    loadProbes(domainId);
    
    // Load keywords
    loadKeywords(domainId);
    
    // Load hallucinations
    loadHallucinations(domainId);
    
    // Load briefs
    loadBriefs(domainId);
    
    // Load approvals
    loadApprovals(domainId);
}

async function loadChambers(domainId) {
    try {
        const response = await fetch(`${API_BASE}/domains/${domainId}/chambers`);
        const data = await response.json();
        const content = document.getElementById('chambers-content');
        
        if (data.chambers && data.chambers.length > 0) {
            content.innerHTML = data.chambers.map(c => `
                <div class="chamber-item">
                    <span class="chamber-name">${escapeHtml(c.name)}</span>
                    <span class="chamber-status ${c.status}">${c.status}</span>
                </div>
            `).join('');
        } else {
            content.innerHTML = '<p class="empty-panel">No chambers yet. Run a probe to populate.</p>';
        }
    } catch (e) {
        document.getElementById('chambers-content').innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
}

async function loadProbes(domainId) {
    try {
        const response = await fetch(`${API_BASE}/domains/${domainId}/probes`);
        const data = await response.json();
        const content = document.getElementById('probes-content');
        
        if (data.probes && data.probes.length > 0) {
            content.innerHTML = data.probes.slice(0, 5).map(p => `
                <div class="probe-item">
                    <span class="probe-query">${escapeHtml(p.query)}</span>
                    <span class="probe-engine">${p.engine}</span>
                </div>
            `).join('');
        } else {
            content.innerHTML = '<p class="empty-panel">No probes yet. Run a probe to test LLM knowledge.</p>';
        }
    } catch (e) {
        document.getElementById('probes-content').innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
}

async function loadKeywords(domainId) {
    try {
        const response = await fetch(`${API_BASE}/domains/${domainId}/keywords`);
        const data = await response.json();
        const content = document.getElementById('keywords-content');
        
        if (data.keywords && data.keywords.length > 0) {
            content.innerHTML = data.keywords.slice(0, 10).map(k => `
                <div class="keyword-item">
                    <span class="keyword-query">${escapeHtml(k.query)}</span>
                    <span class="keyword-category">${k.category}</span>
                </div>
            `).join('');
        } else {
            content.innerHTML = '<p class="empty-panel">No keywords yet. Generate keywords from crawl.</p>';
        }
    } catch (e) {
        document.getElementById('keywords-content').innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
}

async function loadHallucinations(domainId) {
    try {
        const response = await fetch(`${API_BASE}/domains/${domainId}/hallucinations`);
        const data = await response.json();
        const content = document.getElementById('hallucinations-content');
        
        if (data.hallucinations && data.hallucinations.length > 0) {
            content.innerHTML = data.hallucinations.map(h => `
                <div class="hallucination-item">
                    <span class="hallu-type">${h.hallucination_type}</span>
                    <span class="hallu-severity ${h.severity}">${h.severity}</span>
                </div>
            `).join('');
        } else {
            content.innerHTML = '<p class="empty-panel">No hallucinations detected.</p>';
        }
    } catch (e) {
        document.getElementById('hallucinations-content').innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
}

async function loadBriefs(domainId) {
    try {
        const response = await fetch(`${API_BASE}/domains/${domainId}/briefs`);
        const data = await response.json();
        const content = document.getElementById('briefs-content');
        
        if (data.briefs && data.briefs.length > 0) {
            content.innerHTML = data.briefs.map(b => `
                <div class="brief-item">
                    <span class="brief-title">${escapeHtml(b.title)}</span>
                    <span class="brief-status ${b.status}">${b.status}</span>
                </div>
            `).join('');
        } else {
            content.innerHTML = '<p class="empty-panel">No briefs yet. Generate from hallucinations.</p>';
        }
    } catch (e) {
        document.getElementById('briefs-content').innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
}

async function loadApprovals(domainId) {
    try {
        const response = await fetch(`${API_BASE}/domains/${domainId}/approvals`);
        const data = await response.json();
        const content = document.getElementById('approvals-content');
        
        if (data.approvals && data.approvals.length > 0) {
            content.innerHTML = data.approvals.map(a => `
                <div class="approval-item">
                    <span class="approval-type">${a.item_type}</span>
                    <span class="approval-status ${a.status}">${a.status}</span>
                    <div class="approval-actions">
                        <button class="btn-small approve" data-id="${a.id}">✓</button>
                        <button class="btn-small decline" data-id="${a.id}">✗</button>
                    </div>
                </div>
            `).join('');
            
            // Add approval handlers
            content.querySelectorAll('.approve').forEach(btn => {
                btn.addEventListener('click', () => handleApproval(btn.dataset.id, 'approve'));
            });
            content.querySelectorAll('.decline').forEach(btn => {
                btn.addEventListener('click', () => handleApproval(btn.dataset.id, 'decline'));
            });
        } else {
            content.innerHTML = '<p class="empty-panel">No pending approvals.</p>';
        }
    } catch (e) {
        document.getElementById('approvals-content').innerHTML = `<p class="error">Error: ${e.message}</p>`;
    }
}

async function handleApproval(approvalId, action) {
    try {
        await runAction(`${API_BASE}/approvals/${approvalId}/${action}`, 'POST');
        showToast(`Approval ${action}ed!`, 'success');
        await loadApprovals(state.currentDomain.domain_id);
    } catch (e) {
        showToast(`Failed: ${e.message}`, 'error');
    }
}

// ==================== Utilities ====================

function getScoreClass(score) {
    if (score >= 85) return 'score-85-100';
    if (score >= 65) return 'score-65-85';
    if (score >= 40) return 'score-40-65';
    return 'score-0-40';
}

function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${escapeHtml(message)}</span>`;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}
