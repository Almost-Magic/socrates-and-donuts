"""
Elaine v4 — Configuration
Central configuration for all modules.

Almost Magic Tech Lab
"""

# ── Identity ──

ELAINE_NAME = "Maestro Elaine"
ELAINE_VERSION = "4.0"
ELAINE_NAMES = ["Elaine", "Suzie", "Maestro", "Suz"]
ELEVENLABS_VOICE_ID = "XQanfahzbl1YiUlZi5NW"

# ── Owner ──

OWNER_NAME = "Mani Padisetti"
COMPANY_NAME = "Almost Magic Tech Lab"
COMPANY_SHORT = "AMTL"

# ── Module Toggles ──

MODULES = {
    "thinking_frameworks": True,
    "gravity_v2": True,
    "constellation_v2": True,
    "cartographer_v2": True,
    "amplifier_v2": True,
    "sentinel_v2": True,
    "chronicle_v2": True,
    "voice": True,
    "innovator": True,
    "beast": True,
    "orchestrator": True,
}

# ── Server ──

HOST = "0.0.0.0"
PORT = 5000
DEBUG = True

# ── Paths ──

DATA_DIR = "./data"
LOGS_DIR = "./logs"

# ── Sentinel Defaults ──

SENTINEL_DEFAULT_GATE = 2
SENTINEL_AUTO_REVIEW = True

# ── Gravity Defaults ──

GRAVITY_RED_GIANT_THRESHOLD = 90
GRAVITY_DEFAULT_CAPACITY_HOURS = 8.0

# ── Cartographer Defaults ──

CARTOGRAPHER_MAX_SIGNALS_PER_DAY = 5
CARTOGRAPHER_DEFAULT_PHASE = "recovery"

# ── Amplifier Defaults ──

AMPLIFIER_OVEREXPOSURE_WEEKLY = 3
AMPLIFIER_OVEREXPOSURE_MONTHLY = 7

# ── Chronicle Defaults ──

CHRONICLE_DEFAULT_MEETING_DURATION = 45
CHRONICLE_COMMITMENT_AUTO_GRAVITY = True

# ── Innovator Defaults ──

INNOVATOR_AUTO_RESEARCH_THRESHOLD = 0.75
BEAST_DEFAULT_DEADLINE_DAYS = 5
