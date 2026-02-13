"""
Signal Hunter -- LinkedIn Intelligence Engine
Port: 8420
Almost Magic Tech Lab

Track LinkedIn profiles, engagement metrics, and generate AI-powered
intelligence briefs via Ollama (routed through The Supervisor).
Manual data entry only -- no LinkedIn scraping.
"""

import json
import logging
import os
import sqlite3
import sys
import time
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from flask import Flask, jsonify, request, render_template

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")
logger = logging.getLogger("signal")

app = Flask(__name__)
app.config["JSON_SORT_KEYS"] = False

# ── Config ────────────────────────────────────────────────────────
PORT = int(os.environ.get("SIGNAL_PORT", 8420))
SUPERVISOR_URL = os.environ.get("SUPERVISOR_URL", "http://localhost:9000")
OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
SIGNAL_MODEL = os.environ.get("SIGNAL_MODEL", "llama3.2:3b")
LLM_TIMEOUT = 15
LLM_MAX_TOKENS = 300

DB_PATH = os.environ.get(
    "SIGNAL_DB_PATH",
    str(Path.home() / ".signal" / "signal.db"),
)

# ── Database ──────────────────────────────────────────────────────

def _init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        headline TEXT DEFAULT '',
        company TEXT DEFAULT '',
        linkedin_url TEXT DEFAULT '',
        notes TEXT DEFAULT '',
        tags TEXT DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS engagements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
        post_url TEXT DEFAULT '',
        post_content TEXT DEFAULT '',
        engagement_type TEXT DEFAULT 'post',
        reactions INTEGER DEFAULT 0,
        comments INTEGER DEFAULT 0,
        shares INTEGER DEFAULT 0,
        post_date TEXT DEFAULT '',
        recorded_at TEXT NOT NULL,
        notes TEXT DEFAULT ''
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        profile_id INTEGER NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
        analysis_text TEXT NOT NULL,
        model_used TEXT DEFAULT '',
        via TEXT DEFAULT '',
        ollama_ok INTEGER DEFAULT 1,
        created_at TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()


def _db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys=ON")
    conn.row_factory = sqlite3.Row
    return conn


_init_db()

# ── LLM Helper ───────────────────────────────────────────────────

def _call_llm(prompt, timeout=LLM_TIMEOUT):
    payload = json.dumps({
        "model": SIGNAL_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": LLM_MAX_TOKENS},
    }).encode("utf-8")

    for base_url, via in [(SUPERVISOR_URL, "supervisor"), (OLLAMA_URL, "ollama-direct")]:
        try:
            req = Request(
                f"{base_url}/api/generate",
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(req, timeout=timeout) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data.get("response", "").strip()
                if text:
                    return text, SIGNAL_MODEL, via, True
        except Exception as e:
            logger.warning("LLM via %s failed: %s", via, e)
            continue
    return "", SIGNAL_MODEL, "offline", False


def _llm_reachable():
    try:
        req = Request(f"{SUPERVISOR_URL}/api/health", method="GET")
        with urlopen(req, timeout=3) as resp:
            return resp.status < 400
    except Exception:
        pass
    try:
        req = Request(f"{OLLAMA_URL}/api/tags", method="GET")
        with urlopen(req, timeout=3) as resp:
            return resp.status < 400
    except Exception:
        pass
    return False


def _now():
    return datetime.now(timezone.utc).isoformat()


# ── Routes: Health ────────────────────────────────────────────────

@app.route("/api/health")
def health():
    conn = _db()
    profiles = conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]
    engagements = conn.execute("SELECT COUNT(*) FROM engagements").fetchone()[0]
    conn.close()
    return jsonify({
        "status": "healthy",
        "service": "signal",
        "version": "1.0.0",
        "profiles": profiles,
        "engagements": engagements,
        "llm": {
            "connected": _llm_reachable(),
            "model": SIGNAL_MODEL,
            "supervisor": SUPERVISOR_URL,
        },
        "timestamp": _now(),
    })


# ── Routes: Web UI ────────────────────────────────────────────────

@app.route("/")
def root():
    return render_template("index.html")


# ── Routes: Profiles CRUD ─────────────────────────────────────────

@app.route("/api/profiles", methods=["GET"])
def list_profiles():
    search = request.args.get("search", "").strip()
    company = request.args.get("company", "").strip()
    tag = request.args.get("tag", "").strip()

    conn = _db()
    query = "SELECT * FROM profiles WHERE 1=1"
    params = []
    if search:
        query += " AND (name LIKE ? OR headline LIKE ? OR company LIKE ?)"
        s = f"%{search}%"
        params.extend([s, s, s])
    if company:
        query += " AND company LIKE ?"
        params.append(f"%{company}%")
    if tag:
        query += " AND tags LIKE ?"
        params.append(f"%{tag}%")
    query += " ORDER BY updated_at DESC"

    rows = conn.execute(query, params).fetchall()
    profiles = []
    for r in rows:
        eng_count = conn.execute(
            "SELECT COUNT(*) FROM engagements WHERE profile_id=?", (r["id"],)
        ).fetchone()[0]
        last_analysis = conn.execute(
            "SELECT created_at FROM analyses WHERE profile_id=? ORDER BY created_at DESC LIMIT 1",
            (r["id"],),
        ).fetchone()
        profiles.append({
            **dict(r),
            "engagement_count": eng_count,
            "last_analysis": last_analysis[0] if last_analysis else None,
        })
    conn.close()
    return jsonify({"profiles": profiles, "total": len(profiles)})


@app.route("/api/profiles", methods=["POST"])
def create_profile():
    data = request.get_json(silent=True) or {}
    name = data.get("name", "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400

    now = _now()
    conn = _db()
    c = conn.execute(
        "INSERT INTO profiles (name,headline,company,linkedin_url,notes,tags,created_at,updated_at) "
        "VALUES (?,?,?,?,?,?,?,?)",
        (
            name,
            data.get("headline", "").strip(),
            data.get("company", "").strip(),
            data.get("linkedin_url", "").strip(),
            data.get("notes", "").strip(),
            data.get("tags", "").strip(),
            now, now,
        ),
    )
    conn.commit()
    pid = c.lastrowid
    row = conn.execute("SELECT * FROM profiles WHERE id=?", (pid,)).fetchone()
    conn.close()
    return jsonify(dict(row)), 201


@app.route("/api/profiles/<int:pid>", methods=["GET"])
def get_profile(pid):
    conn = _db()
    row = conn.execute("SELECT * FROM profiles WHERE id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Profile not found"}), 404
    eng_count = conn.execute(
        "SELECT COUNT(*) FROM engagements WHERE profile_id=?", (pid,)
    ).fetchone()[0]
    last_analysis = conn.execute(
        "SELECT analysis_text, created_at FROM analyses WHERE profile_id=? ORDER BY created_at DESC LIMIT 1",
        (pid,),
    ).fetchone()
    conn.close()
    result = {**dict(row), "engagement_count": eng_count}
    if last_analysis:
        result["latest_analysis"] = {
            "text": last_analysis["analysis_text"],
            "created_at": last_analysis["created_at"],
        }
    return jsonify(result)


@app.route("/api/profiles/<int:pid>", methods=["PUT"])
def update_profile(pid):
    conn = _db()
    row = conn.execute("SELECT * FROM profiles WHERE id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Profile not found"}), 404

    data = request.get_json(silent=True) or {}
    conn.execute(
        "UPDATE profiles SET name=?,headline=?,company=?,linkedin_url=?,notes=?,tags=?,updated_at=? WHERE id=?",
        (
            data.get("name", row["name"]).strip() or row["name"],
            data.get("headline", row["headline"]).strip(),
            data.get("company", row["company"]).strip(),
            data.get("linkedin_url", row["linkedin_url"]).strip(),
            data.get("notes", row["notes"]).strip(),
            data.get("tags", row["tags"]).strip(),
            _now(), pid,
        ),
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM profiles WHERE id=?", (pid,)).fetchone()
    conn.close()
    return jsonify(dict(updated))


@app.route("/api/profiles/<int:pid>", methods=["DELETE"])
def delete_profile(pid):
    conn = _db()
    row = conn.execute("SELECT * FROM profiles WHERE id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Profile not found"}), 404
    conn.execute("DELETE FROM profiles WHERE id=?", (pid,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": pid})


# ── Routes: Engagements ───────────────────────────────────────────

@app.route("/api/profiles/<int:pid>/engagements", methods=["GET"])
def list_engagements(pid):
    conn = _db()
    row = conn.execute("SELECT id FROM profiles WHERE id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Profile not found"}), 404
    rows = conn.execute(
        "SELECT * FROM engagements WHERE profile_id=? ORDER BY recorded_at DESC", (pid,)
    ).fetchall()
    conn.close()
    return jsonify({"engagements": [dict(r) for r in rows], "total": len(rows)})


@app.route("/api/profiles/<int:pid>/engagements", methods=["POST"])
def create_engagement(pid):
    conn = _db()
    row = conn.execute("SELECT id FROM profiles WHERE id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Profile not found"}), 404

    data = request.get_json(silent=True) or {}
    c = conn.execute(
        "INSERT INTO engagements (profile_id,post_url,post_content,engagement_type,"
        "reactions,comments,shares,post_date,recorded_at,notes) VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            pid,
            data.get("post_url", "").strip(),
            data.get("post_content", "").strip(),
            data.get("engagement_type", "post").strip(),
            int(data.get("reactions", 0)),
            int(data.get("comments", 0)),
            int(data.get("shares", 0)),
            data.get("post_date", "").strip(),
            _now(),
            data.get("notes", "").strip(),
        ),
    )
    conn.commit()
    eng = conn.execute("SELECT * FROM engagements WHERE id=?", (c.lastrowid,)).fetchone()
    conn.close()
    return jsonify(dict(eng)), 201


@app.route("/api/engagements/<int:eid>", methods=["DELETE"])
def delete_engagement(eid):
    conn = _db()
    row = conn.execute("SELECT id FROM engagements WHERE id=?", (eid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Engagement not found"}), 404
    conn.execute("DELETE FROM engagements WHERE id=?", (eid,))
    conn.commit()
    conn.close()
    return jsonify({"deleted": eid})


# ── Routes: Analysis ──────────────────────────────────────────────

def _build_analysis_prompt(profile, engagements):
    eng_summary = ""
    if engagements:
        total_r = sum(e["reactions"] for e in engagements)
        total_c = sum(e["comments"] for e in engagements)
        types = dict(Counter(e["engagement_type"] for e in engagements))
        excerpts = [e["post_content"][:200] for e in engagements[:5] if e["post_content"]]
        eng_summary = (
            f"\nEngagement data: {len(engagements)} tracked items. "
            f"Total reactions: {total_r}, comments: {total_c}. "
            f"Types: {types}."
        )
        if excerpts:
            eng_summary += f"\nRecent content: {'; '.join(excerpts)}"

    return (
        "You are Signal Hunter, a LinkedIn intelligence analyst for Almost Magic Tech Lab. "
        "Analyse this profile for business intelligence.\n\n"
        f"Name: {profile['name']}\n"
        f"Headline: {profile['headline']}\n"
        f"Company: {profile['company']}\n"
        f"Notes: {profile['notes']}\n"
        f"Tags: {profile['tags']}\n"
        f"{eng_summary}\n\n"
        "Provide a concise 3-5 sentence intelligence brief: "
        "1) Their likely priorities and interests, "
        "2) Potential engagement angle for AMTL, "
        "3) Content strategy recommendation. "
        "Australian English. Be direct and practical."
    )


@app.route("/api/profiles/<int:pid>/analyze", methods=["POST"])
def analyze_profile(pid):
    conn = _db()
    profile = conn.execute("SELECT * FROM profiles WHERE id=?", (pid,)).fetchone()
    if not profile:
        conn.close()
        return jsonify({"error": "Profile not found"}), 404

    engagements = conn.execute(
        "SELECT * FROM engagements WHERE profile_id=? ORDER BY recorded_at DESC LIMIT 20",
        (pid,),
    ).fetchall()

    prompt = _build_analysis_prompt(dict(profile), [dict(e) for e in engagements])

    start = time.time()
    text, model, via, ok = _call_llm(prompt)
    elapsed = round(time.time() - start, 1)

    if not text:
        text = (
            f"Analysis unavailable -- Ollama is offline. "
            f"Profile: {profile['name']} ({profile['company']}). "
            f"Tracked engagements: {len(engagements)}. "
            f"Connect the LLM and try again."
        )

    conn.execute(
        "INSERT INTO analyses (profile_id,analysis_text,model_used,via,ollama_ok,created_at) "
        "VALUES (?,?,?,?,?,?)",
        (pid, text, model, via, int(ok), _now()),
    )
    conn.commit()
    conn.close()

    return jsonify({
        "analysis": text,
        "model": model,
        "via": via,
        "ollama_ok": ok,
        "profile_id": pid,
        "elapsed_s": elapsed,
    })


@app.route("/api/profiles/<int:pid>/analyses", methods=["GET"])
def list_analyses(pid):
    conn = _db()
    row = conn.execute("SELECT id FROM profiles WHERE id=?", (pid,)).fetchone()
    if not row:
        conn.close()
        return jsonify({"error": "Profile not found"}), 404
    rows = conn.execute(
        "SELECT * FROM analyses WHERE profile_id=? ORDER BY created_at DESC", (pid,)
    ).fetchall()
    conn.close()
    return jsonify({"analyses": [dict(r) for r in rows], "total": len(rows)})


# ── Routes: Dashboard ─────────────────────────────────────────────

@app.route("/api/dashboard")
def dashboard():
    conn = _db()
    total_profiles = conn.execute("SELECT COUNT(*) FROM profiles").fetchone()[0]
    total_engagements = conn.execute("SELECT COUNT(*) FROM engagements").fetchone()[0]
    total_analyses = conn.execute("SELECT COUNT(*) FROM analyses").fetchone()[0]

    recent = conn.execute(
        "SELECT a.analysis_text, a.created_at, a.via, p.name "
        "FROM analyses a JOIN profiles p ON a.profile_id=p.id "
        "ORDER BY a.created_at DESC LIMIT 5"
    ).fetchall()

    top = conn.execute(
        "SELECT p.id, p.name, p.company, COUNT(e.id) as eng_count "
        "FROM profiles p LEFT JOIN engagements e ON p.id=e.profile_id "
        "GROUP BY p.id ORDER BY eng_count DESC LIMIT 5"
    ).fetchall()

    conn.close()
    return jsonify({
        "total_profiles": total_profiles,
        "total_engagements": total_engagements,
        "total_analyses": total_analyses,
        "recent_analyses": [
            {"name": r["name"], "text": r["analysis_text"][:200], "created_at": r["created_at"], "via": r["via"]}
            for r in recent
        ],
        "top_engaged": [
            {"id": t["id"], "name": t["name"], "company": t["company"], "engagement_count": t["eng_count"]}
            for t in top
        ],
        "timestamp": _now(),
    })


# ── Startup ───────────────────────────────────────────────────────

if __name__ == "__main__":
    logger.info("Signal Hunter starting on port %d", PORT)
    app.run(host="0.0.0.0", port=PORT, debug=False)
