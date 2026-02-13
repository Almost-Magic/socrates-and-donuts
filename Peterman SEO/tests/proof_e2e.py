"""
Proof E2E Test — Peterman V4.1
Playwright end-to-end test verifying the full user journey through the browser.

Requires: pip install playwright && playwright install chromium
Run:      python tests/proof_e2e.py
"""

import sys
import json
import subprocess
import time
import signal
import os
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.parent
RESULTS = {"passed": 0, "failed": 0, "tests": []}
BASE_URL = "http://localhost:5008"


def log_test(name, status, detail=""):
    icon = "PASS" if status == "pass" else "FAIL"
    RESULTS["tests"].append({"name": name, "status": status, "detail": detail})
    if status == "pass":
        RESULTS["passed"] += 1
    else:
        RESULTS["failed"] += 1
    print(f"  [{icon}] {name}" + (f" -- {detail}" if detail else ""))


def run_proof():
    print("=" * 60)
    print("  PROOF E2E TEST -- Peterman V4.1")
    print(f"  {datetime.now().strftime('%d %b %Y %H:%M:%S')}")
    print("=" * 60)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("\n  [SKIP] Playwright not installed. Install with:")
        print("         pip install playwright && playwright install chromium")
        print("=" * 60)
        return False

    # Start Flask server
    server = None
    try:
        print("\n  Starting Flask server on port 5008...")
        env = os.environ.copy()
        env["FLASK_ENV"] = "testing"
        server = subprocess.Popen(
            [sys.executable, "-c",
             "from app import app; app.run(host='127.0.0.1', port=5008, debug=False)"],
            cwd=str(PROJECT_ROOT),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
        )
        time.sleep(3)  # Wait for server startup

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 1440, "height": 900})
            page = context.new_page()

            print("\n  SECTION 1: Page Load & Navigation")

            # E01: Homepage loads
            response = page.goto(BASE_URL, timeout=10000)
            log_test("E01 Homepage loads", "pass" if response and response.status == 200 else "fail",
                     f"HTTP {response.status if response else 'no response'}")

            # E02: Title is correct
            title = page.title()
            log_test("E02 Page title", "pass" if "Peterman" in title else "fail", title)

            # E03: Sidebar exists
            sidebar = page.query_selector(".sidebar")
            log_test("E03 Sidebar rendered", "pass" if sidebar else "fail")

            # E04: Dashboard is default active page
            dash = page.query_selector("#page-dashboard.active")
            log_test("E04 Dashboard is active page", "pass" if dash else "fail")

            # E05: AMTL logo present
            logo = page.query_selector(".logo-icon")
            log_test("E05 AMTL logo present", "pass" if logo else "fail")

            # E06: All 10 chamber nav items
            nav_items = page.query_selector_all(".nav-item")
            log_test("E06 Navigation items (16+)", "pass" if len(nav_items) >= 16 else "fail",
                     f"Found {len(nav_items)}")

            print("\n  SECTION 2: Chamber Navigation")

            # E07-E16: Click through all 10 chamber pages
            chamber_pages = [
                ("E07", "perception", "Chamber 1: Perception"),
                ("E08", "semantic", "Chamber 2: Semantic"),
                ("E09", "vectormap", "Chamber 3: Vector Map"),
                ("E10", "authority", "Chamber 4: Authority"),
                ("E11", "survivability", "Chamber 5: Survivability"),
                ("E12", "machine", "Chamber 6: Machine"),
                ("E13", "amplifier", "Chamber 7: Amplifier"),
                ("E14", "proof", "Chamber 8: The Proof"),
                ("E15", "oracle", "Chamber 9: The Oracle"),
                ("E16", "forge", "Chamber 10: The Forge"),
            ]

            for tid, page_name, label in chamber_pages:
                nav_btn = page.query_selector(f'[data-page="{page_name}"]')
                if nav_btn:
                    nav_btn.click()
                    page.wait_for_timeout(300)
                    active_page = page.query_selector(f"#page-{page_name}.active")
                    log_test(f"{tid} {label}", "pass" if active_page else "fail")
                else:
                    log_test(f"{tid} {label}", "fail", "Nav button not found")

            print("\n  SECTION 3: Brand Management")

            # Navigate to brands page
            page.click('[data-page="brands"]')
            page.wait_for_timeout(500)

            # E17: Brands page loads
            brands_page = page.query_selector("#page-brands.active")
            log_test("E17 Brands page active", "pass" if brands_page else "fail")

            # E18: Add Brand button exists
            add_btn = page.query_selector('button:has-text("Add Brand")')
            log_test("E18 Add Brand button", "pass" if add_btn else "fail")

            # E19: Add Brand modal opens
            if add_btn:
                add_btn.click()
                page.wait_for_timeout(300)
                modal = page.query_selector("#addBrandModal.open")
                log_test("E19 Add Brand modal opens", "pass" if modal else "fail")
                # Close modal
                close_btn = page.query_selector("#addBrandModal .modal-close")
                if close_btn:
                    close_btn.click()
                    page.wait_for_timeout(200)
            else:
                log_test("E19 Add Brand modal opens", "fail", "No add button")

            print("\n  SECTION 4: Design System")

            # E20: Dark mode background
            bg = page.evaluate("() => getComputedStyle(document.body).backgroundColor")
            is_dark = "10" in bg or "14" in bg or "rgb(10" in bg
            log_test("E20 Dark mode active", "pass" if is_dark else "fail", bg)

            # E21: Gold accent present
            gold_elements = page.evaluate("""() => {
                const all = document.querySelectorAll('*');
                for (const el of all) {
                    const style = getComputedStyle(el);
                    if (style.color.includes('201') || style.backgroundColor.includes('201')) return true;
                }
                return document.querySelector('.btn-gold') !== null;
            }""")
            log_test("E21 Gold accent elements", "pass" if gold_elements else "fail")

            # E22: Sora font loaded
            font = page.evaluate("() => getComputedStyle(document.body).fontFamily")
            log_test("E22 Sora font", "pass" if "Sora" in font or "sora" in font.lower() else "fail", font[:50])

            print("\n  SECTION 5: API Health")

            # E23: Health endpoint
            health_resp = page.evaluate("""async () => {
                try {
                    const r = await fetch('/api/health');
                    return await r.json();
                } catch(e) { return null; }
            }""")
            log_test("E23 /api/health responds", "pass" if health_resp and health_resp.get("status") else "fail")

            # E24: Version in health
            log_test("E24 Version in health", "pass" if health_resp and health_resp.get("version") else "fail",
                     health_resp.get("version", "") if health_resp else "")

            # E25: Status endpoint
            status_resp = page.evaluate("""async () => {
                try {
                    const r = await fetch('/api/status');
                    return await r.json();
                } catch(e) { return null; }
            }""")
            log_test("E25 /api/status responds", "pass" if status_resp else "fail")

            print("\n  SECTION 6: SEO Ask + ELAINE Briefing")

            # E26: SEO Ask page navigable
            seo_nav = page.query_selector('[data-page="seoask"]')
            if seo_nav:
                seo_nav.click()
                page.wait_for_timeout(300)
                seo_page = page.query_selector("#page-seoask.active")
                log_test("E26 SEO Ask page loads", "pass" if seo_page else "fail")
            else:
                log_test("E26 SEO Ask page loads", "fail", "No nav button for seoask")

            # E27: SEO Ask has input textarea
            seo_input = page.query_selector("#seoQuery")
            log_test("E27 SEO Ask has query input", "pass" if seo_input else "fail")

            # E28: ELAINE briefing endpoint
            briefing_resp = page.evaluate("""async () => {
                try {
                    const r = await fetch('/api/elaine-briefing');
                    return await r.json();
                } catch(e) { return null; }
            }""")
            log_test("E28 /api/elaine-briefing responds", "pass" if briefing_resp and briefing_resp.get("service") == "peterman" else "fail")

            # Take screenshot
            screenshots_dir = PROJECT_ROOT / "tests" / "screenshots"
            screenshots_dir.mkdir(parents=True, exist_ok=True)
            page.click('[data-page="dashboard"]')
            page.wait_for_timeout(500)
            screenshot_path = screenshots_dir / f"proof_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            page.screenshot(path=str(screenshot_path), full_page=True)
            print(f"\n  Screenshot saved: {screenshot_path}")

            browser.close()

    except Exception as e:
        print(f"\n  [ERROR] {e}")
        log_test("E2E Execution", "fail", str(e))

    finally:
        if server:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()

    print("\n" + "=" * 60)
    total = RESULTS["passed"] + RESULTS["failed"]
    print(f"  RESULTS: {RESULTS['passed']}/{total} passed | {RESULTS['failed']} failed")
    pct = round(RESULTS["passed"] / max(total, 1) * 100, 1)
    print(f"  SCORE: {pct}%")
    status = "PROOF VERIFIED" if RESULTS["failed"] == 0 else "PROOF INCOMPLETE"
    print(f"  STATUS: {status}")
    print("=" * 60)

    # Save report
    report_dir = PROJECT_ROOT / "tests" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / f"proof_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_path, "w") as f:
        json.dump({"timestamp": datetime.now().isoformat(), "results": RESULTS, "score_pct": pct}, f, indent=2)
    print(f"\n  Report saved: {report_path}")

    return RESULTS["failed"] == 0


if __name__ == "__main__":
    success = run_proof()
    sys.exit(0 if success else 1)
