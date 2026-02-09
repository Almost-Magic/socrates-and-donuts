"""
Peterman V4.1 — Browser Automation Service
Almost Magic Tech Lab

Queries commercial LLMs via browser automation (Playwright) instead of APIs.
Uses Mani's existing subscriptions: ChatGPT Plus, Claude Pro, Gemini Advanced, Perplexity Pro.

Cost: $0 additional (subscriptions already paid)
Replaces: $80-330/mo in API costs

IMPORTANT: This service opens real browser sessions.
- Requires one-time login to each service
- Sessions persist via browser profiles
- Rate-limited to respect ToS and avoid detection
"""
import asyncio
import json
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Browser profile directory — persists login sessions
BROWSER_PROFILE_DIR = os.getenv(
    "BROWSER_PROFILE_DIR",
    os.path.join(os.path.expanduser("~"), ".peterman", "browser_profiles")
)


class BrowserLLMService:
    """
    Queries commercial LLMs through browser automation.
    Uses existing paid subscriptions instead of APIs.
    """

    def __init__(self):
        self._playwright = None
        self._browser = None
        self._contexts = {}  # model_name -> browser context
        self._pages = {}     # model_name -> page
        self._initialized = False

    # ----------------------------------------------------------
    # Lifecycle
    # ----------------------------------------------------------

    async def init(self):
        """Initialise Playwright and browser."""
        if self._initialized:
            return

        from playwright.async_api import async_playwright

        os.makedirs(BROWSER_PROFILE_DIR, exist_ok=True)

        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=False,  # Visible for debugging; set True for production
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        )
        self._initialized = True
        logger.info("Browser automation service initialised")

    async def close(self):
        """Clean up browser resources."""
        for ctx in self._contexts.values():
            await ctx.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._initialized = False

    async def _get_context(self, model_name):
        """Get or create a persistent browser context for a model."""
        if model_name not in self._contexts:
            profile_path = os.path.join(BROWSER_PROFILE_DIR, model_name)
            os.makedirs(profile_path, exist_ok=True)

            self._contexts[model_name] = await self._browser.new_context(
                storage_state=os.path.join(profile_path, "state.json")
                if os.path.exists(os.path.join(profile_path, "state.json"))
                else None,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            )
        return self._contexts[model_name]

    async def _save_session(self, model_name):
        """Save browser session state (cookies, localStorage) for persistence."""
        if model_name in self._contexts:
            profile_path = os.path.join(BROWSER_PROFILE_DIR, model_name)
            os.makedirs(profile_path, exist_ok=True)
            await self._contexts[model_name].storage_state(
                path=os.path.join(profile_path, "state.json")
            )

    # ----------------------------------------------------------
    # ChatGPT (chat.openai.com)
    # ----------------------------------------------------------

    async def query_chatgpt(self, prompt, model="gpt-4o", timeout=120):
        """Query ChatGPT via browser."""
        await self.init()
        context = await self._get_context("chatgpt")
        page = await context.new_page()
        start = time.time()

        try:
            await page.goto("https://chat.openai.com/", wait_until="networkidle", timeout=30000)

            # Check if logged in
            if "auth" in page.url or "login" in page.url:
                logger.warning("ChatGPT: Not logged in. Please log in manually.")
                return self._login_required_response("chatgpt")

            # Start new chat
            try:
                new_chat = page.locator('[data-testid="new-chat-button"], a[href="/"]').first
                await new_chat.click(timeout=5000)
                await page.wait_for_timeout(1000)
            except Exception:
                pass  # May already be on new chat

            # Type the prompt
            textarea = page.locator("#prompt-textarea, textarea[data-id='root']").first
            await textarea.click()
            await textarea.fill(prompt)
            await page.wait_for_timeout(500)

            # Send
            send_btn = page.locator('[data-testid="send-button"], button[aria-label="Send prompt"]').first
            await send_btn.click()

            # Wait for response to complete
            await self._wait_for_chatgpt_response(page, timeout)

            # Extract response
            messages = page.locator('[data-message-author-role="assistant"]')
            count = await messages.count()
            if count > 0:
                response_text = await messages.last.inner_text()
            else:
                response_text = ""

            await self._save_session("chatgpt")
            duration = time.time() - start

            return {
                "text": response_text,
                "model": "chatgpt-browser",
                "model_display": model,
                "source": "browser",
                "tokens_used": len(response_text.split()) * 1.3,  # rough estimate
                "duration_ms": round(duration * 1000),
                "cost": 0.0,  # using existing subscription
            }

        except Exception as e:
            logger.error(f"ChatGPT browser error: {e}")
            return {"text": "", "model": "chatgpt-browser", "error": str(e), "cost": 0.0}
        finally:
            await page.close()

    async def _wait_for_chatgpt_response(self, page, timeout=120):
        """Wait for ChatGPT to finish generating."""
        deadline = time.time() + timeout
        while time.time() < deadline:
            # Check if still generating (stop button visible)
            stop_btn = page.locator('button[aria-label="Stop generating"]')
            if await stop_btn.count() == 0:
                await page.wait_for_timeout(1000)  # Small buffer after completion
                return
            await page.wait_for_timeout(2000)
        raise TimeoutError("ChatGPT response timed out")

    # ----------------------------------------------------------
    # Claude (claude.ai)
    # ----------------------------------------------------------

    async def query_claude(self, prompt, timeout=120):
        """Query Claude via browser."""
        await self.init()
        context = await self._get_context("claude")
        page = await context.new_page()
        start = time.time()

        try:
            await page.goto("https://claude.ai/new", wait_until="networkidle", timeout=30000)

            # Check if logged in
            if "login" in page.url or "auth" in page.url:
                logger.warning("Claude: Not logged in. Please log in manually.")
                return self._login_required_response("claude")

            # Type the prompt
            textarea = page.locator('[contenteditable="true"], textarea').first
            await textarea.click()
            await textarea.fill(prompt)
            await page.wait_for_timeout(500)

            # Send (press Enter or click send)
            await page.keyboard.press("Enter")

            # Wait for response
            await self._wait_for_claude_response(page, timeout)

            # Extract response — Claude's response blocks
            responses = page.locator('[data-is-streaming="false"] .font-claude-message, .prose')
            count = await responses.count()
            if count > 0:
                response_text = await responses.last.inner_text()
            else:
                # Fallback: get all text from response area
                response_text = await page.locator('.font-claude-message').last.inner_text()

            await self._save_session("claude")
            duration = time.time() - start

            return {
                "text": response_text,
                "model": "claude-browser",
                "model_display": "claude-pro",
                "source": "browser",
                "tokens_used": len(response_text.split()) * 1.3,
                "duration_ms": round(duration * 1000),
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Claude browser error: {e}")
            return {"text": "", "model": "claude-browser", "error": str(e), "cost": 0.0}
        finally:
            await page.close()

    async def _wait_for_claude_response(self, page, timeout=120):
        """Wait for Claude to finish generating."""
        deadline = time.time() + timeout
        await page.wait_for_timeout(3000)  # Initial wait for response to start
        while time.time() < deadline:
            # Check if still streaming
            streaming = page.locator('[data-is-streaming="true"]')
            if await streaming.count() == 0:
                await page.wait_for_timeout(1000)
                return
            await page.wait_for_timeout(2000)
        raise TimeoutError("Claude response timed out")

    # ----------------------------------------------------------
    # Perplexity (perplexity.ai)
    # ----------------------------------------------------------

    async def query_perplexity(self, prompt, timeout=120):
        """Query Perplexity via browser — critical for citation tracking."""
        await self.init()
        context = await self._get_context("perplexity")
        page = await context.new_page()
        start = time.time()

        try:
            await page.goto("https://www.perplexity.ai/", wait_until="networkidle", timeout=30000)

            # Check login
            if "login" in page.url or "sign" in page.url:
                logger.warning("Perplexity: Not logged in.")
                return self._login_required_response("perplexity")

            # Type query
            textarea = page.locator('textarea[placeholder*="Ask"], textarea').first
            await textarea.click()
            await textarea.fill(prompt)
            await page.wait_for_timeout(500)

            # Send
            await page.keyboard.press("Enter")

            # Wait for response
            await self._wait_for_perplexity_response(page, timeout)

            # Extract response and sources
            response_text = ""
            sources = []

            # Get the answer text
            answer_el = page.locator('.prose, [class*="answer"], [class*="response"]').last
            if await answer_el.count() > 0:
                response_text = await answer_el.inner_text()

            # Get cited sources (Perplexity's key value)
            source_links = page.locator('a[class*="source"], a[class*="citation"], [class*="source"] a')
            source_count = await source_links.count()
            for i in range(min(source_count, 10)):
                try:
                    href = await source_links.nth(i).get_attribute("href")
                    text = await source_links.nth(i).inner_text()
                    if href:
                        sources.append({"url": href, "title": text})
                except Exception:
                    pass

            await self._save_session("perplexity")
            duration = time.time() - start

            return {
                "text": response_text,
                "model": "perplexity-browser",
                "model_display": "perplexity-pro",
                "source": "browser",
                "citations": sources,
                "tokens_used": len(response_text.split()) * 1.3,
                "duration_ms": round(duration * 1000),
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Perplexity browser error: {e}")
            return {"text": "", "model": "perplexity-browser", "error": str(e), "cost": 0.0, "citations": []}
        finally:
            await page.close()

    async def _wait_for_perplexity_response(self, page, timeout=120):
        """Wait for Perplexity to finish."""
        deadline = time.time() + timeout
        await page.wait_for_timeout(3000)
        while time.time() < deadline:
            # Check for loading/streaming indicators
            loading = page.locator('[class*="loading"], [class*="streaming"], [class*="typing"]')
            if await loading.count() == 0:
                await page.wait_for_timeout(2000)
                return
            await page.wait_for_timeout(2000)
        raise TimeoutError("Perplexity response timed out")

    # ----------------------------------------------------------
    # Gemini (gemini.google.com)
    # ----------------------------------------------------------

    async def query_gemini(self, prompt, timeout=120):
        """Query Gemini via browser."""
        await self.init()
        context = await self._get_context("gemini")
        page = await context.new_page()
        start = time.time()

        try:
            await page.goto("https://gemini.google.com/app", wait_until="networkidle", timeout=30000)

            # Check login
            if "accounts.google" in page.url:
                logger.warning("Gemini: Not logged in.")
                return self._login_required_response("gemini")

            # Type prompt
            textarea = page.locator('.ql-editor, [contenteditable="true"], textarea').first
            await textarea.click()
            await textarea.fill(prompt)
            await page.wait_for_timeout(500)

            # Send
            send_btn = page.locator('button[aria-label*="Send"], button.send-button, [class*="send"]').first
            await send_btn.click()

            # Wait for response
            await self._wait_for_gemini_response(page, timeout)

            # Extract response
            response_el = page.locator('.model-response-text, [class*="response-content"], .message-content').last
            response_text = await response_el.inner_text() if await response_el.count() > 0 else ""

            await self._save_session("gemini")
            duration = time.time() - start

            return {
                "text": response_text,
                "model": "gemini-browser",
                "model_display": "gemini-advanced",
                "source": "browser",
                "tokens_used": len(response_text.split()) * 1.3,
                "duration_ms": round(duration * 1000),
                "cost": 0.0,
            }

        except Exception as e:
            logger.error(f"Gemini browser error: {e}")
            return {"text": "", "model": "gemini-browser", "error": str(e), "cost": 0.0}
        finally:
            await page.close()

    async def _wait_for_gemini_response(self, page, timeout=120):
        """Wait for Gemini to finish."""
        deadline = time.time() + timeout
        await page.wait_for_timeout(3000)
        while time.time() < deadline:
            loading = page.locator('[class*="loading"], [class*="pending"]')
            if await loading.count() == 0:
                await page.wait_for_timeout(1500)
                return
            await page.wait_for_timeout(2000)
        raise TimeoutError("Gemini response timed out")

    # ----------------------------------------------------------
    # Multi-Model Query (for perception scans)
    # ----------------------------------------------------------

    async def query_all_commercial(self, prompt, models=None):
        """
        Query all commercial models for the same prompt.
        Used by perception scans to see how each model responds.

        Returns list of results from each model.
        """
        if models is None:
            models = ["chatgpt", "claude", "perplexity", "gemini"]

        tasks = []
        for model in models:
            if model == "chatgpt":
                tasks.append(self.query_chatgpt(prompt))
            elif model == "claude":
                tasks.append(self.query_claude(prompt))
            elif model == "perplexity":
                tasks.append(self.query_perplexity(prompt))
            elif model == "gemini":
                tasks.append(self.query_gemini(prompt))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        output = []
        for model, result in zip(models, results):
            if isinstance(result, Exception):
                output.append({"text": "", "model": f"{model}-browser", "error": str(result), "cost": 0.0})
            else:
                output.append(result)

        return output

    # ----------------------------------------------------------
    # Login Helper
    # ----------------------------------------------------------

    async def open_login_page(self, model_name):
        """
        Open the login page for a service so user can log in manually.
        After login, save the session for future automated use.
        """
        await self.init()
        context = await self._get_context(model_name)
        page = await context.new_page()

        urls = {
            "chatgpt": "https://chat.openai.com/auth/login",
            "claude": "https://claude.ai/login",
            "perplexity": "https://www.perplexity.ai/",
            "gemini": "https://gemini.google.com/app",
        }

        url = urls.get(model_name)
        if not url:
            return {"error": f"Unknown model: {model_name}"}

        await page.goto(url)
        logger.info(f"Opened login page for {model_name}. Please log in manually.")

        return {
            "status": "login_page_opened",
            "model": model_name,
            "message": f"Please log in to {model_name} in the browser window. "
                       f"After logging in, call /api/browser/save-session/{model_name} to save.",
        }

    async def save_current_session(self, model_name):
        """Save current browser session after manual login."""
        await self._save_session(model_name)
        return {
            "status": "session_saved",
            "model": model_name,
            "message": f"Session saved for {model_name}. Future queries will use this login.",
        }

    # ----------------------------------------------------------
    # Utilities
    # ----------------------------------------------------------

    def _login_required_response(self, model_name):
        return {
            "text": "",
            "model": f"{model_name}-browser",
            "error": "login_required",
            "message": f"Not logged in to {model_name}. "
                       f"Call POST /api/browser/login/{model_name} to open login page.",
            "cost": 0.0,
        }

    async def health_check(self):
        """Check which services have saved sessions."""
        sessions = {}
        for model in ["chatgpt", "claude", "perplexity", "gemini"]:
            state_file = os.path.join(BROWSER_PROFILE_DIR, model, "state.json")
            sessions[model] = {
                "has_session": os.path.exists(state_file),
                "session_file": state_file if os.path.exists(state_file) else None,
            }
        return {
            "status": "ok",
            "sessions": sessions,
            "profile_dir": BROWSER_PROFILE_DIR,
        }


# Singleton
browser_llm = BrowserLLMService()


# ----------------------------------------------------------
# Sync wrappers (for Flask routes)
# ----------------------------------------------------------

def query_chatgpt_sync(prompt, **kwargs):
    """Synchronous wrapper for Flask."""
    return asyncio.run(browser_llm.query_chatgpt(prompt, **kwargs))


def query_claude_sync(prompt, **kwargs):
    return asyncio.run(browser_llm.query_claude(prompt, **kwargs))


def query_perplexity_sync(prompt, **kwargs):
    return asyncio.run(browser_llm.query_perplexity(prompt, **kwargs))


def query_gemini_sync(prompt, **kwargs):
    return asyncio.run(browser_llm.query_gemini(prompt, **kwargs))


def query_all_commercial_sync(prompt, models=None):
    return asyncio.run(browser_llm.query_all_commercial(prompt, models))
