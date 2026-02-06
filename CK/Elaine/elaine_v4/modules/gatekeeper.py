"""
Elaine v4 — Gatekeeper
The last line of defence before anything leaves Mani's desk.

Intercepts:
1. Emails (Outlook COM automation / file watcher)
2. Files in outbound folders (watchdog)
3. Chat messages (API hook)
4. Social media posts (API hook)
5. Proposals and documents (file watcher)

For each intercepted item:
- Sentinel scans for trust/quality issues
- Compassion checks if the tone matches the emotional context
- Communication engine suggests structural improvements
- Returns: CLEAR / REVIEW / HOLD with specific guidance

Not a blocker — a safety net. Mani can always override.
But Elaine never lets something leave without checking.

"The best Chief of Staff catches the email you'd regret at 2am."

Patentable: Pre-Transmission Quality Assurance with Multi-Dimensional Trust Analysis

Almost Magic Tech Lab — Patentable IP
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional

logger = logging.getLogger("elaine.gatekeeper")


# ── Enums ────────────────────────────────────────────────────────

class GateVerdict(str, Enum):
    CLEAR = "clear"           # Good to send
    REVIEW = "review"         # Minor issues — check before sending
    HOLD = "hold"             # Significant issues — do NOT send yet
    OVERRIDE = "override"     # Mani sent it anyway (logged for learning)


class ContentChannel(str, Enum):
    EMAIL = "email"
    FILE = "file"
    CHAT = "chat"
    SOCIAL = "social"
    PROPOSAL = "proposal"
    PRESENTATION = "presentation"


class ContentPriority(str, Enum):
    ROUTINE = "routine"       # Internal, low stakes
    STANDARD = "standard"     # Normal external
    SENSITIVE = "sensitive"   # Client-facing, pricing, legal
    CRITICAL = "critical"     # Board, investor, public, media


# ── Data Models ──────────────────────────────────────────────────

@dataclass
class GateCheck:
    """Result of a single gate check."""
    gate_name: str             # "sentinel", "compassion", "communication"
    passed: bool
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    score: float = 1.0        # 0-1


@dataclass
class GateResult:
    """Full gatekeeper result for an outbound item."""
    item_id: str
    channel: ContentChannel
    priority: ContentPriority
    verdict: GateVerdict
    title: str = ""
    recipient: str = ""
    checks: list[GateCheck] = field(default_factory=list)
    overall_score: float = 1.0
    summary: str = ""
    override_reason: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class WatchedFolder:
    """A folder being monitored for outbound files."""
    path: str
    channel: ContentChannel
    priority: ContentPriority
    file_extensions: list[str] = field(default_factory=lambda: [".docx", ".pdf", ".pptx", ".xlsx"])
    active: bool = True


@dataclass
class OutlookRule:
    """An Outlook interception rule."""
    name: str
    folder: str = "Outbox"        # Which Outlook folder to watch
    recipient_pattern: str = ""    # e.g., "@client.com"
    subject_pattern: str = ""      # e.g., "proposal"
    priority: ContentPriority = ContentPriority.STANDARD
    active: bool = True


# ── Priority Detection ───────────────────────────────────────────

SENSITIVE_KEYWORDS = [
    "pricing", "price", "quote", "fee", "cost", "rate",
    "contract", "agreement", "terms", "nda", "confidential",
    "proposal", "sow", "scope of work",
    "iso", "certification", "compliance", "audit",
    "legal", "liability", "indemnity",
]

CRITICAL_KEYWORDS = [
    "board", "investor", "shareholder", "media", "press",
    "public statement", "announcement", "sec ", "asic",
    "termination", "litigation", "dispute",
]

SENSITIVE_RECIPIENTS = [
    "@gov.au", "@minister", "@parliament",
    "@asx.com", "@asic.gov",
]


# ── The Gatekeeper ───────────────────────────────────────────────

class Gatekeeper:
    """
    Pre-transmission quality assurance.
    Checks everything before it leaves — emails, files, posts.
    """

    def __init__(self, sentinel=None, compassion=None, communication=None):
        self.sentinel = sentinel
        self.compassion = compassion
        self.communication = communication

        self._history: list[GateResult] = []
        self._overrides: list[GateResult] = []
        self._watched_folders: list[WatchedFolder] = []
        self._outlook_rules: list[OutlookRule] = []
        self._items_checked: int = 0
        self._items_held: int = 0

        # Default watched folders
        self._watched_folders.append(WatchedFolder(
            path=os.path.expanduser("~/Documents/Outbound"),
            channel=ContentChannel.FILE,
            priority=ContentPriority.STANDARD,
        ))
        self._watched_folders.append(WatchedFolder(
            path=os.path.expanduser("~/Documents/Proposals"),
            channel=ContentChannel.PROPOSAL,
            priority=ContentPriority.SENSITIVE,
            file_extensions=[".docx", ".pdf"],
        ))

        # Default Outlook rules
        self._outlook_rules.append(OutlookRule(
            name="All outbound",
            folder="Outbox",
            priority=ContentPriority.STANDARD,
        ))
        self._outlook_rules.append(OutlookRule(
            name="Client proposals",
            subject_pattern="proposal",
            priority=ContentPriority.SENSITIVE,
        ))
        self._outlook_rules.append(OutlookRule(
            name="Government/regulatory",
            recipient_pattern="@gov",
            priority=ContentPriority.CRITICAL,
        ))

    # ── Priority Detection ────────────────────────────────────

    def detect_priority(self, content: str, recipient: str = "",
                         channel: ContentChannel = ContentChannel.EMAIL) -> ContentPriority:
        """Auto-detect how sensitive this content is."""
        text_lower = content.lower()
        recipient_lower = recipient.lower()

        # Critical overrides
        if any(k in text_lower for k in CRITICAL_KEYWORDS):
            return ContentPriority.CRITICAL
        if any(r in recipient_lower for r in SENSITIVE_RECIPIENTS):
            return ContentPriority.CRITICAL

        # Sensitive detection
        if any(k in text_lower for k in SENSITIVE_KEYWORDS):
            return ContentPriority.SENSITIVE
        if channel in (ContentChannel.PROPOSAL, ContentChannel.PRESENTATION):
            return ContentPriority.SENSITIVE

        # File type hints
        if channel == ContentChannel.SOCIAL:
            return ContentPriority.SENSITIVE  # Public = always sensitive

        return ContentPriority.STANDARD

    # ── The Main Gate ─────────────────────────────────────────

    def check(self, content: str, title: str = "", recipient: str = "",
              channel: ContentChannel = ContentChannel.EMAIL,
              priority: ContentPriority = None,
              emotional_context: str = "") -> GateResult:
        """
        Full gatekeeper check on outbound content.
        Returns verdict: CLEAR, REVIEW, or HOLD.
        """
        self._items_checked += 1

        if priority is None:
            priority = self.detect_priority(content, recipient, channel)

        item_id = f"gate-{self._items_checked:04d}"
        checks = []

        # ── 1. Sentinel Check (trust/quality) ────────────────
        sentinel_check = self._run_sentinel(content, title, recipient, priority)
        checks.append(sentinel_check)

        # ── 2. Compassion Check (tone/context) ───────────────
        compassion_check = self._run_compassion(content, emotional_context)
        checks.append(compassion_check)

        # ── 3. Communication Check (structure) ───────────────
        comm_check = self._run_communication(content, channel)
        checks.append(comm_check)

        # ── Calculate Overall Verdict ─────────────────────────
        overall_score = sum(c.score for c in checks) / len(checks)

        # Verdict thresholds vary by priority
        if priority == ContentPriority.CRITICAL:
            hold_threshold = 0.85
            review_threshold = 0.95
        elif priority == ContentPriority.SENSITIVE:
            hold_threshold = 0.70
            review_threshold = 0.85
        else:
            hold_threshold = 0.50
            review_threshold = 0.70

        if overall_score < hold_threshold:
            verdict = GateVerdict.HOLD
            self._items_held += 1
        elif overall_score < review_threshold:
            verdict = GateVerdict.REVIEW
        else:
            verdict = GateVerdict.CLEAR

        # Generate summary
        all_issues = []
        for c in checks:
            all_issues.extend(c.issues)

        if verdict == GateVerdict.CLEAR:
            summary = "All checks passed. Clear to send."
        elif verdict == GateVerdict.REVIEW:
            summary = f"Minor issues detected ({len(all_issues)}). Review before sending: {'; '.join(all_issues[:3])}"
        else:
            summary = f"Hold — {len(all_issues)} issues found. {'; '.join(all_issues[:3])}"

        result = GateResult(
            item_id=item_id,
            channel=channel,
            priority=priority,
            verdict=verdict,
            title=title,
            recipient=recipient,
            checks=checks,
            overall_score=round(overall_score, 3),
            summary=summary,
        )

        self._history.append(result)
        logger.info(f"GATE: {verdict.value} | {channel.value} | {priority.value} | "
                     f"score={overall_score:.2f} | '{title[:40]}'")
        return result

    # ── Individual Gate Checks ────────────────────────────────

    def _run_sentinel(self, content: str, title: str, recipient: str,
                       priority: ContentPriority) -> GateCheck:
        """Run Sentinel trust review."""
        if not self.sentinel:
            return GateCheck("sentinel", True, score=1.0)

        is_public = priority in (ContentPriority.CRITICAL, ContentPriority.SENSITIVE)
        has_pricing = any(k in content.lower() for k in ["pricing", "price", "fee", "cost", "rate", "quote"])

        audit = self.sentinel.review(
            content=content,
            title=title,
            document_type="outbound",
            recipient=recipient,
            has_pricing=has_pricing,
            is_public=is_public,
        )

        issues = [item.issue for item in audit.risk_items[:5]]
        score = audit.weighted_trust_score / 100.0  # Normalise to 0-1

        return GateCheck(
            gate_name="sentinel",
            passed=audit.verdict.value in ("pass", "conditional"),
            issues=issues,
            suggestions=[f"Trust score: {audit.weighted_trust_score}/100"],
            score=max(0.0, min(1.0, score)),
        )

    def _run_compassion(self, content: str, emotional_context: str) -> GateCheck:
        """Check if tone matches emotional context."""
        if not self.compassion:
            return GateCheck("compassion", True, score=1.0)

        context = self.compassion.detect_context(content)
        response = self.compassion.frame_response(context)

        issues = []
        score = 1.0

        # Flag mismatches
        if response.breathing_room and len(content) > 500:
            issues.append("Emotional context suggests brevity — this message may be too long")
            score -= 0.15

        if not response.should_push and any(
            w in content.lower() for w in ["urgent", "asap", "immediately", "deadline"]
        ):
            issues.append(f"Context is '{context.value}' — pushing urgency may not land well right now")
            score -= 0.20

        if context.value == "grief" and len(content.split()) > 100:
            issues.append("In grief context: less words, more presence. Consider trimming significantly.")
            score -= 0.25

        return GateCheck(
            gate_name="compassion",
            passed=len(issues) == 0,
            issues=issues,
            suggestions=[f"Detected context: {context.value}, recommended tone: {response.tone.value}"],
            score=max(0.0, score),
        )

    def _run_communication(self, content: str, channel: ContentChannel) -> GateCheck:
        """Check communication structure."""
        if not self.communication:
            return GateCheck("communication", True, score=1.0)

        issues = []
        suggestions = []
        score = 1.0

        words = content.split()
        sentences = content.split(".")

        # Basic structural checks
        if len(words) > 500 and channel == ContentChannel.EMAIL:
            issues.append(f"Email is {len(words)} words — consider if this should be a document instead")
            score -= 0.10

        if len(words) > 50 and channel == ContentChannel.CHAT:
            issues.append(f"Chat message is {len(words)} words — too long for chat. Break up or move to email.")
            score -= 0.15

        # Check if answer comes first (Pyramid Principle)
        first_sentence = sentences[0].strip() if sentences else ""
        question_words = ["what", "why", "how", "when", "who", "where"]
        if first_sentence and first_sentence.split()[0].lower() in question_words:
            issues.append("Opens with a question — consider leading with your recommendation (Pyramid Principle)")
            score -= 0.10

        # Suggest frameworks based on channel
        from modules.communication import CommunicationType, AudienceLevel
        channel_map = {
            ContentChannel.EMAIL: CommunicationType.EMAIL,
            ContentChannel.PROPOSAL: CommunicationType.PROPOSAL,
            ContentChannel.PRESENTATION: CommunicationType.PRESENTATION,
            ContentChannel.SOCIAL: CommunicationType.LINKEDIN,
        }
        ct = channel_map.get(channel, CommunicationType.EMAIL)
        suggested = self.communication.suggest_frameworks(ct, AudienceLevel.MANAGER)
        suggestions.append(f"Suggested frameworks: {', '.join(suggested)}")

        return GateCheck(
            gate_name="communication",
            passed=len(issues) == 0,
            issues=issues,
            suggestions=suggestions,
            score=max(0.0, score),
        )

    # ── Override ──────────────────────────────────────────────

    def override(self, item_id: str, reason: str = "") -> Optional[GateResult]:
        """
        Mani overrides a HOLD or REVIEW verdict.
        Logged for learning — Sentinel adapts over time.
        """
        for result in self._history:
            if result.item_id == item_id:
                result.verdict = GateVerdict.OVERRIDE
                result.override_reason = reason
                self._overrides.append(result)
                logger.info(f"GATE OVERRIDE: {item_id} — {reason[:60]}")
                return result
        return None

    # ── File Watcher Configuration ────────────────────────────

    def add_watched_folder(self, path: str, channel: ContentChannel,
                            priority: ContentPriority,
                            extensions: list[str] = None) -> WatchedFolder:
        """Add a folder to monitor for outbound files."""
        folder = WatchedFolder(
            path=path, channel=channel, priority=priority,
            file_extensions=extensions or [".docx", ".pdf", ".pptx"],
        )
        self._watched_folders.append(folder)
        logger.info(f"Watching folder: {path}")
        return folder

    def get_watched_folders(self) -> list[dict]:
        return [
            {"path": f.path, "channel": f.channel.value,
             "priority": f.priority.value, "extensions": f.file_extensions,
             "active": f.active}
            for f in self._watched_folders
        ]

    # ── Outlook Rules Configuration ───────────────────────────

    def add_outlook_rule(self, name: str, recipient_pattern: str = "",
                          subject_pattern: str = "",
                          priority: ContentPriority = ContentPriority.STANDARD) -> OutlookRule:
        """Add an Outlook interception rule."""
        rule = OutlookRule(
            name=name, recipient_pattern=recipient_pattern,
            subject_pattern=subject_pattern, priority=priority,
        )
        self._outlook_rules.append(rule)
        logger.info(f"Outlook rule added: {name}")
        return rule

    def get_outlook_rules(self) -> list[dict]:
        return [
            {"name": r.name, "folder": r.folder,
             "recipient": r.recipient_pattern,
             "subject": r.subject_pattern,
             "priority": r.priority.value, "active": r.active}
            for r in self._outlook_rules
        ]

    # ── Outlook COM Integration Helpers ───────────────────────

    def get_outlook_hook_script(self) -> str:
        """
        Returns a Python script for Outlook COM automation.
        Run this as a background process to intercept outbound emails.
        """
        return '''
"""
Elaine Gatekeeper — Outlook Hook
Run as: python outlook_hook.py
Requires: pywin32 (pip install pywin32)
Monitors Outlook Outbox and checks emails before sending.
"""

import win32com.client
import requests
import time

ELAINE_URL = "http://127.0.0.1:5000"

def check_email(subject, body, recipient):
    """Send to Elaine Gatekeeper for review."""
    try:
        r = requests.post(f"{ELAINE_URL}/api/gatekeeper/check", json={
            "content": body,
            "title": subject,
            "recipient": recipient,
            "channel": "email",
        }, timeout=5)
        return r.json()
    except Exception as e:
        print(f"Gatekeeper unavailable: {e}")
        return {"verdict": "clear", "summary": "Gatekeeper offline — sending anyway"}

def monitor_outbox():
    """Watch Outlook Outbox for new emails."""
    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    outbox = namespace.GetDefaultFolder(4)  # 4 = Outbox

    print("Elaine Gatekeeper watching Outlook Outbox...")

    seen = set()
    while True:
        for item in outbox.Items:
            if item.EntryID not in seen:
                seen.add(item.EntryID)
                recipients = "; ".join([r.Address for r in item.Recipients])
                result = check_email(item.Subject, item.Body, recipients)

                if result.get("verdict") == "hold":
                    print(f"⛔ HOLD: {item.Subject}")
                    print(f"   {result.get('summary', '')}")
                    # Move to Drafts for review
                    drafts = namespace.GetDefaultFolder(16)  # 16 = Drafts
                    item.Move(drafts)
                elif result.get("verdict") == "review":
                    print(f"⚠️  REVIEW: {item.Subject}")
                    print(f"   {result.get('summary', '')}")
                else:
                    print(f"✅ CLEAR: {item.Subject}")

        time.sleep(2)  # Check every 2 seconds

if __name__ == "__main__":
    monitor_outbox()
'''

    def get_file_watcher_script(self) -> str:
        """
        Returns a Python script for file system monitoring.
        Run as: python file_watcher.py
        Requires: watchdog (pip install watchdog)
        """
        return '''
"""
Elaine Gatekeeper — File Watcher
Run as: python file_watcher.py
Requires: watchdog (pip install watchdog)
Monitors outbound folders and checks files before they leave.
"""

import os
import time
import requests
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ELAINE_URL = "http://127.0.0.1:5000"
WATCH_FOLDERS = [
    os.path.expanduser("~/Documents/Outbound"),
    os.path.expanduser("~/Documents/Proposals"),
]
EXTENSIONS = {".docx", ".pdf", ".pptx", ".xlsx", ".txt", ".md"}


class GatekeeperHandler(FileSystemEventHandler):
    def on_created(self, event):
        if event.is_directory:
            return
        ext = os.path.splitext(event.src_path)[1].lower()
        if ext not in EXTENSIONS:
            return

        print(f"New file detected: {os.path.basename(event.src_path)}")

        # Read file content (text-based only for now)
        content = ""
        if ext in (".txt", ".md"):
            with open(event.src_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        try:
            r = requests.post(f"{ELAINE_URL}/api/gatekeeper/check", json={
                "content": content or f"[File: {os.path.basename(event.src_path)}]",
                "title": os.path.basename(event.src_path),
                "channel": "file",
            }, timeout=5)
            result = r.json()
            verdict = result.get("verdict", "clear")

            if verdict == "hold":
                print(f"  ⛔ HOLD: {result.get('summary', '')}")
            elif verdict == "review":
                print(f"  ⚠️  REVIEW: {result.get('summary', '')}")
            else:
                print(f"  ✅ CLEAR")
        except Exception as e:
            print(f"  Gatekeeper unavailable: {e}")


def main():
    observer = Observer()
    handler = GatekeeperHandler()

    for folder in WATCH_FOLDERS:
        os.makedirs(folder, exist_ok=True)
        observer.schedule(handler, folder, recursive=False)
        print(f"Watching: {folder}")

    observer.start()
    print("Elaine Gatekeeper file watcher running...")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main()
'''

    # ── Reporting ────────────────────────────────────────────

    def status(self) -> dict:
        hold_count = sum(1 for r in self._history if r.verdict == GateVerdict.HOLD)
        review_count = sum(1 for r in self._history if r.verdict == GateVerdict.REVIEW)
        clear_count = sum(1 for r in self._history if r.verdict == GateVerdict.CLEAR)
        return {
            "items_checked": self._items_checked,
            "items_held": self._items_held,
            "overrides": len(self._overrides),
            "verdicts": {"clear": clear_count, "review": review_count, "hold": hold_count},
            "watched_folders": len(self._watched_folders),
            "outlook_rules": len(self._outlook_rules),
        }

    def get_history(self, limit: int = 20) -> list[dict]:
        return [
            {
                "item_id": r.item_id,
                "channel": r.channel.value,
                "priority": r.priority.value,
                "verdict": r.verdict.value,
                "title": r.title,
                "score": r.overall_score,
                "summary": r.summary,
                "timestamp": r.timestamp.isoformat(),
            }
            for r in self._history[-limit:]
        ]
