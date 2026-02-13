"""Proof Test — ELAINE: Chief of Staff E2E.

Playwright end-to-end tests for ELAINE's web UI, chat, tools panel, and API.
Requires ELAINE running on :5000.
"""

import requests
from playwright.sync_api import expect


BASE = "http://localhost:5000"


# ── API Tests ──────────────────────────────────────────────────


def test_health_from_browser(page):
    """Health endpoint loads in browser."""
    page.goto(f"{BASE}/api/health")
    content = page.locator("body").inner_text()
    assert "healthy" in content
    assert "ELAINE" in content


def test_api_tools_returns_registry():
    """Tool registry returns all AMTL services."""
    resp = requests.get(f"{BASE}/api/tools", timeout=10)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 10
    ids = [t["id"] for t in data["tools"]]
    assert "workshop" in ids
    assert "supervisor" in ids
    assert "elaine" in ids
    assert "ollama" in ids


def test_api_tools_health_returns_statuses():
    """Service health check returns structured data."""
    resp = requests.get(f"{BASE}/api/tools/health", timeout=60)
    assert resp.status_code == 200
    data = resp.json()
    assert "services" in data
    assert "running" in data
    assert data["total"] >= 10
    # ELAINE itself should be running
    assert data["services"]["elaine"]["status"] == "running"


# ── Web UI Tests ───────────────────────────────────────────────


def test_ui_loads_with_title(page):
    """ELAINE web UI loads with correct title."""
    page.goto(BASE)
    expect(page).to_have_title("Elaine — Chief of Staff")


def test_ui_dashboard_shows_modules(page):
    """Dashboard shows module count and grid."""
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(5000)

    # Modules count should be a number (not the default em-dash)
    modules_el = page.locator("#dModules")
    text = modules_el.inner_text()
    # Allow for slow API loading
    assert text.isdigit(), f"Modules count not loaded, got: {repr(text)}"
    assert int(text) >= 10


def test_ui_dashboard_shows_services(page):
    """Dashboard shows AMTL Services card."""
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    # Services count should appear
    svc_el = page.locator("#dSvcCount")
    text = svc_el.inner_text()
    assert text != "—", "Services count not loaded"


def test_ui_sidebar_has_tools(page):
    """Sidebar has Tools navigation item."""
    page.goto(BASE)
    tools_nav = page.locator('[data-p="tools"]')
    expect(tools_nav).to_be_visible()
    expect(tools_nav).to_contain_text("Tools")


def test_ui_tools_panel_loads(page):
    """Tools panel shows service cards when clicked."""
    page.goto(BASE)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    # Navigate to tools
    page.locator('[data-p="tools"]').click()
    page.wait_for_timeout(5000)

    # Tools grid should have cards
    grid = page.locator("#toolsGrid")
    cards = grid.locator(".tool-card")
    count = cards.count()
    assert count >= 5, f"Expected at least 5 tool cards, got {count}"


def test_ui_chat_panel_loads(page):
    """Chat panel has input, send button, and greeting."""
    page.goto(BASE)
    page.locator('[data-p="chat"]').click()

    # Chat input exists
    chat_input = page.locator("#chatIn")
    expect(chat_input).to_be_visible()

    # Send button exists
    send_btn = page.locator("#sendBtn")
    expect(send_btn).to_be_visible()

    # Greeting message exists
    hello = page.locator("#chatHello")
    expect(hello).to_be_visible()


def test_ui_chat_sends_message(page):
    """Chat sends a message and shows user bubble."""
    page.goto(BASE)
    page.locator('[data-p="chat"]').click()
    page.wait_for_timeout(500)

    # Type and send
    page.locator("#chatIn").fill("Hello Elaine")
    page.locator("#sendBtn").click()

    # User message bubble should appear
    user_msgs = page.locator(".msg.user")
    expect(user_msgs.first).to_be_visible()
    expect(user_msgs.first.locator(".msg-bubble")).to_contain_text("Hello Elaine")


def test_ui_dark_light_toggle(page):
    """Theme toggle switches between dark and light."""
    page.goto(BASE)

    # Default is dark
    html = page.locator("html")
    expect(html).to_have_attribute("data-theme", "dark")

    # Click toggle
    page.locator("#themeBtn").click()
    expect(html).to_have_attribute("data-theme", "light")

    # Click again to go back
    page.locator("#themeBtn").click()
    expect(html).to_have_attribute("data-theme", "dark")


def test_ui_navigation_switches_panels(page):
    """Clicking sidebar items switches visible panels."""
    page.goto(BASE)

    panels = ["chat", "tools", "gravity", "gatekeeper", "sentinel", "learning", "constellation"]
    for panel_name in panels:
        page.locator(f'[data-p="{panel_name}"]').click()
        panel = page.locator(f"#p-{panel_name}")
        expect(panel).to_be_visible()


def test_ui_responsive_title_changes(page):
    """Page title changes when navigating between panels."""
    page.goto(BASE)

    page.locator('[data-p="chat"]').click()
    expect(page.locator("#pageTitle")).to_have_text("Chat with Elaine")

    page.locator('[data-p="tools"]').click()
    expect(page.locator("#pageTitle")).to_have_text("AMTL Tools")

    page.locator('[data-p="dashboard"]').click()
    expect(page.locator("#pageTitle")).to_have_text("Dashboard")
