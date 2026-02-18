"""
ELAINE Phase 4: The Current — Continuous Intelligence Engine
Named after Mani's book "The Current Beneath the Boat"

Monitors interest areas across multiple sources and surfaces
content opportunities, trends, competitor movements, and ideas.
"""

import json
import sqlite3
import hashlib
import re
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
from urllib.parse import quote_plus

# Optional imports — graceful fallback
try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import feedparser
    HAS_FEEDPARSER = True
except ImportError:
    HAS_FEEDPARSER = False


# ─── Default Interest Areas for Almost Magic ───
DEFAULT_INTEREST_AREAS = [
    {
        "name": "AI Governance & Ethics",
        "keywords": ["AI governance", "AI ethics", "responsible AI", "AI regulation",
                      "AI Act", "ISO 42001", "AI safety", "algorithmic accountability"],
        "subreddits": ["artificial", "MachineLearning", "AIethics"],
        "rss_feeds": [
            "https://news.google.com/rss/search?q=AI+governance",
            "https://news.google.com/rss/search?q=AI+regulation+2025",
        ],
        "scholar_queries": ["AI governance framework", "responsible AI implementation"],
    },
    {
        "name": "Cybersecurity & ISO 27001",
        "keywords": ["cybersecurity trends", "ISO 27001", "zero trust",
                      "ransomware", "cyber insurance", "SMB security",
                      "ACSC", "Essential Eight"],
        "subreddits": ["cybersecurity", "netsec", "InfoSecNews"],
        "rss_feeds": [
            "https://news.google.com/rss/search?q=cybersecurity+Australia",
            "https://news.google.com/rss/search?q=ISO+27001",
        ],
        "scholar_queries": ["cybersecurity SMB", "ISO 27001 implementation challenges"],
    },
    {
        "name": "Digital Transformation for SMBs",
        "keywords": ["digital transformation SMB", "AI adoption small business",
                      "business intelligence SMB", "automation small business",
                      "Australian SMB technology"],
        "subreddits": ["smallbusiness", "startups", "Entrepreneur"],
        "rss_feeds": [
            "https://news.google.com/rss/search?q=SMB+digital+transformation",
            "https://news.google.com/rss/search?q=AI+small+business",
        ],
        "scholar_queries": ["digital transformation SME", "AI adoption barriers SMB"],
    },
    {
        "name": "AI Agents & Orchestration",
        "keywords": ["AI agents", "multi-agent systems", "agent orchestration",
                      "autonomous AI", "LLM agents", "agentic AI",
                      "Claude API", "GPT agents"],
        "subreddits": ["LocalLLaMA", "ChatGPT", "ClaudeAI"],
        "rss_feeds": [
            "https://news.google.com/rss/search?q=AI+agents+2025",
            "https://news.google.com/rss/search?q=agentic+AI",
        ],
        "scholar_queries": ["multi-agent orchestration LLM", "autonomous AI agents"],
    },
    {
        "name": "Publishing & Authorship",
        "keywords": ["self-publishing trends", "BookTok", "author marketing",
                      "book publishing AI", "indie author", "literary fiction trends"],
        "subreddits": ["selfpublish", "writing", "books", "BookTok"],
        "rss_feeds": [
            "https://news.google.com/rss/search?q=book+publishing+trends",
        ],
        "scholar_queries": ["self-publishing industry trends"],
    },
    {
        "name": "Philosophy & Mindfulness in Tech",
        "keywords": ["Vipassana technology", "mindful tech", "digital wellbeing",
                      "contemplative computing", "ethical technology",
                      "philosophy of AI"],
        "subreddits": ["Vipassana", "Meditation", "PhilosophyofTechnology"],
        "rss_feeds": [
            "https://news.google.com/rss/search?q=mindfulness+technology",
        ],
        "scholar_queries": ["contemplative practices technology leaders"],
    },
]

# ─── Content Opportunity Types ───
CONTENT_FORMATS = [
    "linkedin_post", "blog_article", "book_chapter_seed",
    "essay", "academic_paper_angle", "meme_concept",
    "cartoon_concept", "booktok_script", "podcast_topic",
    "newsletter_item", "client_insight_brief", "tweet_thread",
    "infographic_idea", "case_study_seed", "workshop_topic",
]


class TheCurrentEngine:
    """
    Continuous intelligence engine that monitors Mani's interest areas
    and surfaces content opportunities, trends, and competitor intelligence.
    """

    def __init__(self, db_path=None):
        self.db_path = db_path or str(Path.home() / ".elaine" / "the_current.db")
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self.interest_areas = DEFAULT_INTEREST_AREAS
        self._scan_thread = None
        self._running = False

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        # Interest areas configuration
        c.execute("""CREATE TABLE IF NOT EXISTS interest_areas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            config TEXT,
            enabled INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Raw discoveries from scanning
        c.execute("""CREATE TABLE IF NOT EXISTS discoveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            source_url TEXT,
            title TEXT,
            summary TEXT,
            content TEXT,
            author TEXT,
            interest_area TEXT,
            keywords_matched TEXT,
            relevance_score REAL DEFAULT 0.5,
            sentiment TEXT,
            content_hash TEXT UNIQUE,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            read INTEGER DEFAULT 0,
            starred INTEGER DEFAULT 0,
            archived INTEGER DEFAULT 0
        )""")

        # Content opportunities derived from discoveries
        c.execute("""CREATE TABLE IF NOT EXISTS content_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            discovery_id INTEGER,
            format TEXT NOT NULL,
            title TEXT NOT NULL,
            hook TEXT,
            outline TEXT,
            target_audience TEXT,
            urgency TEXT DEFAULT 'standard',
            status TEXT DEFAULT 'idea',
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (discovery_id) REFERENCES discoveries(id)
        )""")

        # Trend tracking
        c.execute("""CREATE TABLE IF NOT EXISTS trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            topic TEXT NOT NULL,
            interest_area TEXT,
            first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            mention_count INTEGER DEFAULT 1,
            velocity REAL DEFAULT 0,
            sources TEXT,
            summary TEXT,
            status TEXT DEFAULT 'emerging'
        )""")

        # Competitor tracking
        c.execute("""CREATE TABLE IF NOT EXISTS competitors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            website TEXT,
            linkedin_url TEXT,
            services TEXT,
            region TEXT,
            notes TEXT,
            last_scanned TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        # Competitor activity log
        c.execute("""CREATE TABLE IF NOT EXISTS competitor_activity (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competitor_id INTEGER,
            activity_type TEXT,
            title TEXT,
            summary TEXT,
            url TEXT,
            discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competitor_id) REFERENCES competitors(id)
        )""")

        # Scan log
        c.execute("""CREATE TABLE IF NOT EXISTS scan_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_type TEXT,
            interest_area TEXT,
            source TEXT,
            items_found INTEGER DEFAULT 0,
            status TEXT DEFAULT 'completed',
            duration_seconds REAL,
            error_message TEXT,
            scanned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")

        conn.commit()
        conn.close()

    # ─── RSS / News Scanning ───
    def scan_rss_feeds(self, interest_area=None):
        """Scan RSS feeds for new content in interest areas."""
        if not HAS_FEEDPARSER:
            return {"error": "feedparser not installed. Run: pip install feedparser"}

        results = []
        areas = [interest_area] if interest_area else self.interest_areas

        for area in areas:
            if isinstance(area, str):
                area = next((a for a in self.interest_areas if a['name'] == area), None)
                if not area:
                    continue

            for feed_url in area.get('rss_feeds', []):
                try:
                    start = time.time()
                    feed = feedparser.parse(feed_url)
                    for entry in feed.entries[:10]:
                        title = entry.get('title', '')
                        link = entry.get('link', '')
                        summary = entry.get('summary', '')[:500]
                        author = entry.get('author', '')

                        # Check keyword relevance
                        text = f"{title} {summary}".lower()
                        matched = [k for k in area['keywords']
                                   if k.lower() in text]

                        if matched:
                            content_hash = hashlib.md5(
                                f"{title}{link}".encode()
                            ).hexdigest()

                            discovery = self._save_discovery(
                                source='rss',
                                source_url=link,
                                title=title,
                                summary=summary,
                                author=author,
                                interest_area=area['name'],
                                keywords_matched=matched,
                                content_hash=content_hash
                            )
                            if discovery:
                                results.append(discovery)

                    duration = time.time() - start
                    self._log_scan('rss', area['name'], feed_url,
                                   len(results), duration)
                except Exception as e:
                    self._log_scan('rss', area['name'], feed_url,
                                   0, 0, str(e))
        return results

    # ─── Reddit Scanning ───
    def scan_reddit(self, interest_area=None):
        """Scan Reddit for trending discussions in interest areas."""
        if not HAS_REQUESTS:
            return {"error": "requests not installed. Run: pip install requests"}

        results = []
        areas = [interest_area] if interest_area else self.interest_areas

        headers = {'User-Agent': 'ELAINE/1.0 (Almost Magic Tech Lab)'}

        for area in areas:
            if isinstance(area, str):
                area = next((a for a in self.interest_areas if a['name'] == area), None)
                if not area:
                    continue

            for subreddit in area.get('subreddits', []):
                try:
                    start = time.time()
                    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15"
                    resp = requests.get(url, headers=headers, timeout=2)

                    if resp.status_code == 200:
                        data = resp.json()
                        posts = data.get('data', {}).get('children', [])

                        for post in posts:
                            pd = post.get('data', {})
                            title = pd.get('title', '')
                            selftext = pd.get('selftext', '')[:500]
                            permalink = f"https://reddit.com{pd.get('permalink', '')}"
                            author = pd.get('author', '')
                            score = pd.get('score', 0)

                            text = f"{title} {selftext}".lower()
                            matched = [k for k in area['keywords']
                                       if k.lower() in text]

                            if matched and score > 5:
                                content_hash = hashlib.md5(
                                    permalink.encode()
                                ).hexdigest()

                                discovery = self._save_discovery(
                                    source='reddit',
                                    source_url=permalink,
                                    title=title,
                                    summary=selftext,
                                    author=f"u/{author}",
                                    interest_area=area['name'],
                                    keywords_matched=matched,
                                    relevance_score=min(1.0, score / 100),
                                    content_hash=content_hash
                                )
                                if discovery:
                                    results.append(discovery)

                    duration = time.time() - start
                    self._log_scan('reddit', area['name'],
                                   f"r/{subreddit}", len(results), duration)
                    time.sleep(2)  # Rate limiting
                except Exception as e:
                    self._log_scan('reddit', area['name'],
                                   f"r/{subreddit}", 0, 0, str(e))
        return results

    # ─── Academic Paper Scanning ───
    def scan_academic(self, interest_area=None):
        """Scan Semantic Scholar for recent academic papers."""
        if not HAS_REQUESTS:
            return {"error": "requests not installed"}

        results = []
        areas = [interest_area] if interest_area else self.interest_areas

        for area in areas:
            if isinstance(area, str):
                area = next((a for a in self.interest_areas if a['name'] == area), None)
                if not area:
                    continue

            for query in area.get('scholar_queries', []):
                try:
                    start = time.time()
                    url = "https://api.semanticscholar.org/graph/v1/paper/search"
                    params = {
                        'query': query,
                        'limit': 10,
                        'fields': 'title,abstract,authors,year,url,citationCount',
                        'year': f"{datetime.now().year - 1}-{datetime.now().year}"
                    }
                    resp = requests.get(url, params=params, timeout=2)

                    if resp.status_code == 200:
                        data = resp.json()
                        for paper in data.get('data', []):
                            title = paper.get('title', '')
                            abstract = (paper.get('abstract') or '')[:500]
                            authors = ", ".join(
                                a.get('name', '') for a in
                                (paper.get('authors') or [])[:3]
                            )
                            paper_url = paper.get('url', '')

                            content_hash = hashlib.md5(
                                title.encode()
                            ).hexdigest()

                            discovery = self._save_discovery(
                                source='academic',
                                source_url=paper_url,
                                title=title,
                                summary=abstract,
                                author=authors,
                                interest_area=area['name'],
                                keywords_matched=[query],
                                relevance_score=min(1.0,
                                    (paper.get('citationCount', 0) + 1) / 50
                                ),
                                content_hash=content_hash
                            )
                            if discovery:
                                results.append(discovery)

                    duration = time.time() - start
                    self._log_scan('academic', area['name'], query,
                                   len(results), duration)
                    time.sleep(3)  # Rate limiting
                except Exception as e:
                    self._log_scan('academic', area['name'], query,
                                   0, 0, str(e))
        return results

    # ─── Google Books Scanning ───
    def scan_books(self, interest_area=None):
        """Scan Google Books API for new publications in interest areas."""
        if not HAS_REQUESTS:
            return {"error": "requests not installed"}

        results = []
        areas = [interest_area] if interest_area else self.interest_areas

        for area in areas:
            if isinstance(area, str):
                area = next((a for a in self.interest_areas if a['name'] == area), None)
                if not area:
                    continue

            for keyword in area.get('keywords', [])[:3]:
                try:
                    start = time.time()
                    url = "https://www.googleapis.com/books/v1/volumes"
                    params = {
                        'q': keyword,
                        'orderBy': 'newest',
                        'maxResults': 5,
                        'langRestrict': 'en'
                    }
                    resp = requests.get(url, params=params, timeout=2)

                    if resp.status_code == 200:
                        data = resp.json()
                        for item in data.get('items', []):
                            info = item.get('volumeInfo', {})
                            title = info.get('title', '')
                            authors = ", ".join(info.get('authors', []))
                            desc = (info.get('description') or '')[:500]
                            link = info.get('infoLink', '')

                            content_hash = hashlib.md5(
                                f"book:{title}:{authors}".encode()
                            ).hexdigest()

                            discovery = self._save_discovery(
                                source='books',
                                source_url=link,
                                title=f"📚 {title}",
                                summary=desc,
                                author=authors,
                                interest_area=area['name'],
                                keywords_matched=[keyword],
                                content_hash=content_hash
                            )
                            if discovery:
                                results.append(discovery)

                    duration = time.time() - start
                    self._log_scan('books', area['name'], keyword,
                                   len(results), duration)
                    time.sleep(1)
                except Exception as e:
                    self._log_scan('books', area['name'], keyword,
                                   0, 0, str(e))
        return results

    # ─── Full Scan ───
    def run_full_scan(self):
        """Run all scanners across all interest areas."""
        results = {
            'rss': self.scan_rss_feeds(),
            'reddit': self.scan_reddit(),
            'academic': self.scan_academic(),
            'books': self.scan_books(),
            'timestamp': datetime.now().isoformat()
        }
        total = sum(len(v) for v in results.values() if isinstance(v, list))
        results['total_new'] = total

        # After scanning, generate content opportunities
        if total > 0:
            self.generate_content_opportunities()
            self.detect_trends()

        return results

    # ─── Background Scanner ───
    def start_background_scan(self, interval_hours=6):
        """Start background scanning thread."""
        if self._running:
            return {"status": "already running"}

        self._running = True

        def _scan_loop():
            while self._running:
                try:
                    self.run_full_scan()
                except Exception as e:
                    print(f"[The Current] Scan error: {e}")
                time.sleep(interval_hours * 3600)

        self._scan_thread = threading.Thread(target=_scan_loop, daemon=True)
        self._scan_thread.start()
        return {"status": "started", "interval_hours": interval_hours}

    def stop_background_scan(self):
        self._running = False
        return {"status": "stopped"}

    # ─── Content Opportunity Generator ───
    def generate_content_opportunities(self, limit=20):
        """Analyse recent discoveries and suggest content formats."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Get unprocessed high-relevance discoveries
        c.execute("""SELECT * FROM discoveries
            WHERE id NOT IN (SELECT discovery_id FROM content_opportunities
                             WHERE discovery_id IS NOT NULL)
            AND relevance_score >= 0.3
            ORDER BY relevance_score DESC, discovered_at DESC
            LIMIT ?""", (limit,))
        discoveries = [dict(r) for r in c.fetchall()]

        opportunities = []
        for disc in discoveries:
            # Map discovery to content formats based on source and area
            formats = self._suggest_formats(disc)
            for fmt in formats:
                c.execute("""INSERT INTO content_opportunities
                    (discovery_id, format, title, hook, target_audience, urgency)
                    VALUES (?, ?, ?, ?, ?, ?)""",
                    (disc['id'], fmt['format'], fmt['title'],
                     fmt['hook'], fmt['audience'], fmt['urgency']))
                opportunities.append(fmt)

        conn.commit()
        conn.close()
        return opportunities

    def _suggest_formats(self, discovery):
        """Map a discovery to appropriate content formats."""
        formats = []
        source = discovery.get('source', '')
        area = discovery.get('interest_area', '')
        title = discovery.get('title', '')

        # LinkedIn post — almost everything becomes a LinkedIn post
        formats.append({
            'format': 'linkedin_post',
            'title': f"Insight: {title[:80]}",
            'hook': f"Something interesting from {source} about {area}...",
            'audience': 'SMB leaders, CISOs, tech leaders',
            'urgency': 'standard'
        })

        # Academic papers → essay or academic paper angle
        if source == 'academic':
            formats.append({
                'format': 'essay',
                'title': f"Analysis: {title[:80]}",
                'hook': f"New research on {area} — implications for Australian SMBs",
                'audience': 'Industry professionals',
                'urgency': 'standard'
            })

        # Reddit trending → meme/cartoon concept
        if source == 'reddit' and discovery.get('relevance_score', 0) > 0.5:
            formats.append({
                'format': 'meme_concept',
                'title': f"Meme idea: {title[:60]}",
                'hook': "Trending discussion that could become visual content",
                'audience': 'Social media followers',
                'urgency': 'time_sensitive'
            })

        # Books → book review or book chapter seed
        if source == 'books':
            formats.append({
                'format': 'book_chapter_seed',
                'title': f"Chapter seed from: {title[:60]}",
                'hook': f"New publication in {area} — potential chapter material",
                'audience': 'Readers, industry professionals',
                'urgency': 'standard'
            })

        # High relevance → blog article
        if discovery.get('relevance_score', 0) > 0.6:
            formats.append({
                'format': 'blog_article',
                'title': f"Deep Dive: {title[:70]}",
                'hook': f"Why {area} matters for your business right now",
                'audience': 'Almost Magic readers, prospects',
                'urgency': 'standard'
            })

        # Cybersecurity area → client insight brief
        if 'cyber' in area.lower() or 'security' in area.lower():
            formats.append({
                'format': 'client_insight_brief',
                'title': f"Client Brief: {title[:60]}",
                'hook': f"Security intelligence for client conversations",
                'audience': 'Existing clients',
                'urgency': 'high' if 'breach' in title.lower() or
                           'vulnerability' in title.lower() else 'standard'
            })

        # BookTok for publishing area
        if 'publish' in area.lower() or 'author' in area.lower():
            formats.append({
                'format': 'booktok_script',
                'title': f"BookTok: {title[:60]}",
                'hook': "60-second take on publishing trends",
                'audience': 'BookTok community, authors',
                'urgency': 'standard'
            })

        return formats

    # ─── Trend Detection ───
    def detect_trends(self):
        """Analyse discoveries for emerging trends."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # Get recent discoveries (last 7 days)
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        c.execute("""SELECT interest_area, keywords_matched, title
            FROM discoveries WHERE discovered_at >= ?""", (week_ago,))
        rows = c.fetchall()

        # Count keyword frequencies
        keyword_counts = {}
        for row in rows:
            area = row['interest_area']
            try:
                keywords = json.loads(row['keywords_matched'])
            except (json.JSONDecodeError, TypeError):
                keywords = []

            for kw in keywords:
                key = f"{area}::{kw}"
                keyword_counts[key] = keyword_counts.get(key, 0) + 1

        # Update or create trends
        for key, count in keyword_counts.items():
            if count >= 3:  # Threshold for trend
                area, topic = key.split("::", 1)
                c.execute("""SELECT id, mention_count FROM trends
                    WHERE topic = ? AND interest_area = ?""", (topic, area))
                existing = c.fetchone()

                if existing:
                    new_count = existing['mention_count'] + count
                    velocity = count / 7  # mentions per day
                    c.execute("""UPDATE trends
                        SET mention_count = ?, velocity = ?,
                            last_seen = ?, status = ?
                        WHERE id = ?""",
                        (new_count, velocity,
                         datetime.now().isoformat(),
                         'accelerating' if velocity > 1 else 'steady',
                         existing['id']))
                else:
                    c.execute("""INSERT INTO trends
                        (topic, interest_area, mention_count, velocity, status)
                        VALUES (?, ?, ?, ?, ?)""",
                        (topic, area, count, count / 7, 'emerging'))

        conn.commit()
        conn.close()

    # ─── Competitor Tracking ───
    def add_competitor(self, name, website=None, linkedin_url=None,
                       services=None, region='AU'):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""INSERT INTO competitors
            (name, website, linkedin_url, services, region)
            VALUES (?, ?, ?, ?, ?)""",
            (name, website, linkedin_url,
             json.dumps(services) if services else None, region))
        comp_id = c.lastrowid
        conn.commit()
        conn.close()
        return comp_id

    def get_competitors(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute("SELECT * FROM competitors ORDER BY name")
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    # ─── Persistence Helpers ───
    def _save_discovery(self, source, source_url, title, summary,
                        author, interest_area, keywords_matched,
                        content_hash, relevance_score=0.5, content=None):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""INSERT OR IGNORE INTO discoveries
                (source, source_url, title, summary, content, author,
                 interest_area, keywords_matched, relevance_score, content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (source, source_url, title, summary, content, author,
                 interest_area, json.dumps(keywords_matched),
                 relevance_score, content_hash))
            disc_id = c.lastrowid if c.rowcount > 0 else None
            conn.commit()
            conn.close()
            if disc_id:
                return {'id': disc_id, 'title': title, 'source': source,
                        'interest_area': interest_area}
        except Exception:
            pass
        return None

    def _log_scan(self, scan_type, interest_area, source,
                  items_found, duration, error=None):
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("""INSERT INTO scan_log
                (scan_type, interest_area, source, items_found,
                 status, duration_seconds, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (scan_type, interest_area, source, items_found,
                 'error' if error else 'completed', duration, error))
            conn.commit()
            conn.close()
        except Exception:
            pass

    # ─── Query Methods ───
    def get_discoveries(self, interest_area=None, source=None,
                        unread_only=False, starred_only=False, limit=50):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        where = ["archived = 0"]
        params = []
        if interest_area:
            where.append("interest_area = ?")
            params.append(interest_area)
        if source:
            where.append("source = ?")
            params.append(source)
        if unread_only:
            where.append("read = 0")
        if starred_only:
            where.append("starred = 1")
        params.append(limit)
        query = f"""SELECT * FROM discoveries
            WHERE {' AND '.join(where)}
            ORDER BY discovered_at DESC LIMIT ?"""
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_content_opportunities(self, format_type=None,
                                  status='idea', limit=30):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        where = []
        params = []
        if format_type:
            where.append("format = ?")
            params.append(format_type)
        if status:
            where.append("status = ?")
            params.append(status)
        params.append(limit)
        where_clause = f"WHERE {' AND '.join(where)}" if where else ""
        c.execute(f"""SELECT co.*, d.title as discovery_title,
            d.source, d.source_url
            FROM content_opportunities co
            LEFT JOIN discoveries d ON co.discovery_id = d.id
            {where_clause}
            ORDER BY co.created_at DESC LIMIT ?""", params)
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_trends(self, status=None, limit=20):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        if status:
            c.execute("""SELECT * FROM trends WHERE status = ?
                ORDER BY velocity DESC LIMIT ?""", (status, limit))
        else:
            c.execute("""SELECT * FROM trends
                ORDER BY velocity DESC LIMIT ?""", (limit,))
        rows = c.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    def get_morning_briefing(self):
        """Generate the morning briefing data."""
        yesterday = (datetime.now() - timedelta(days=1)).isoformat()

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        # New discoveries since yesterday
        c.execute("""SELECT COUNT(*) as count, interest_area
            FROM discoveries WHERE discovered_at >= ?
            GROUP BY interest_area""", (yesterday,))
        new_by_area = {r['interest_area']: r['count'] for r in c.fetchall()}

        # Top discoveries
        c.execute("""SELECT * FROM discoveries
            WHERE discovered_at >= ?
            ORDER BY relevance_score DESC LIMIT 10""", (yesterday,))
        top_discoveries = [dict(r) for r in c.fetchall()]

        # Accelerating trends
        c.execute("""SELECT * FROM trends
            WHERE status = 'accelerating'
            ORDER BY velocity DESC LIMIT 5""")
        hot_trends = [dict(r) for r in c.fetchall()]

        # Content opportunities
        c.execute("""SELECT * FROM content_opportunities
            WHERE status = 'idea' AND urgency = 'time_sensitive'
            ORDER BY created_at DESC LIMIT 5""")
        urgent_content = [dict(r) for r in c.fetchall()]

        # Scan health
        c.execute("""SELECT scan_type, COUNT(*) as count,
            SUM(CASE WHEN status = 'error' THEN 1 ELSE 0 END) as errors
            FROM scan_log WHERE scanned_at >= ?
            GROUP BY scan_type""", (yesterday,))
        scan_health = {r['scan_type']: {'count': r['count'],
                       'errors': r['errors']} for r in c.fetchall()}

        conn.close()

        return {
            'date': datetime.now().strftime('%A, %d %B %Y'),
            'new_discoveries': new_by_area,
            'total_new': sum(new_by_area.values()),
            'top_discoveries': top_discoveries,
            'hot_trends': hot_trends,
            'urgent_content': urgent_content,
            'scan_health': scan_health
        }

    def get_dashboard_data(self):
        """Get summary data for UI dashboard."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()

        c.execute("SELECT COUNT(*) FROM discoveries WHERE read = 0")
        unread = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM discoveries WHERE starred = 1")
        starred = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM content_opportunities WHERE status = 'idea'")
        opportunities = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM trends WHERE status IN ('emerging', 'accelerating')")
        active_trends = c.fetchone()[0]

        c.execute("SELECT COUNT(*) FROM competitors")
        competitors = c.fetchone()[0]

        # Last scan time
        c.execute("SELECT MAX(scanned_at) FROM scan_log")
        last_scan = c.fetchone()[0]

        conn.close()

        return {
            'unread_discoveries': unread,
            'starred': starred,
            'content_opportunities': opportunities,
            'active_trends': active_trends,
            'competitors_tracked': competitors,
            'last_scan': last_scan
        }
