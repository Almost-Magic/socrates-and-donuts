"""
Peterman V4.1 — SearXNG Service
Almost Magic Tech Lab

Self-hosted meta-search engine integration.
Replaces: Google Search API ($5/1K), Bing API ($3/1K), NewsAPI ($49-$449/mo)
Cost: $0/month
"""
import httpx
import logging
from flask import current_app

logger = logging.getLogger(__name__)


class SearXNGService:
    """Interface to self-hosted SearXNG instance."""

    def __init__(self, base_url=None):
        self.base_url = base_url or "http://localhost:8888"

    # ----------------------------------------------------------
    # Search
    # ----------------------------------------------------------

    def search(self, query, categories=None, language="en-AU", page=1, max_results=10):
        """
        Search via SearXNG.

        Categories: general, news, science, it, images, videos, music, files, social media
        """
        params = {
            "q": query,
            "format": "json",
            "language": language,
            "pageno": page,
        }
        if categories:
            params["categories"] = categories

        try:
            with httpx.Client(timeout=30.0) as client:
                response = client.get(f"{self.base_url}/search", params=params)
                response.raise_for_status()
                data = response.json()

                results = data.get("results", [])[:max_results]
                return {
                    "results": [
                        {
                            "title": r.get("title", ""),
                            "url": r.get("url", ""),
                            "content": r.get("content", ""),
                            "engine": r.get("engine", ""),
                            "score": r.get("score", 0),
                            "published_date": r.get("publishedDate"),
                        }
                        for r in results
                    ],
                    "total": len(results),
                    "query": query,
                    "cost": 0.0,
                }
        except Exception as e:
            logger.error(f"SearXNG search error: {e}")
            return {"results": [], "total": 0, "query": query, "error": str(e), "cost": 0.0}

    def search_news(self, query, max_results=10):
        """Search news articles specifically."""
        return self.search(query, categories="news", max_results=max_results)

    def search_web(self, query, max_results=10):
        """General web search."""
        return self.search(query, categories="general", max_results=max_results)

    def search_science(self, query, max_results=10):
        """Search academic/scientific sources."""
        return self.search(query, categories="science", max_results=max_results)

    # ----------------------------------------------------------
    # SERP Analysis (for Chamber 4 Authority)
    # ----------------------------------------------------------

    def serp_check(self, keyword, brand_name, max_results=20):
        """
        Check where a brand appears in SERP results for a keyword.
        Returns position, competitors found, and SERP landscape.
        """
        results = self.search(keyword, max_results=max_results)

        if results.get("error"):
            return results

        brand_lower = brand_name.lower()
        brand_positions = []
        competitors_found = []

        for i, r in enumerate(results["results"]):
            title = r.get("title", "").lower()
            content = r.get("content", "").lower()
            url = r.get("url", "").lower()

            if brand_lower in title or brand_lower in content or brand_lower in url:
                brand_positions.append(i + 1)
            else:
                competitors_found.append({
                    "position": i + 1,
                    "title": r["title"],
                    "url": r["url"],
                })

        return {
            "keyword": keyword,
            "brand": brand_name,
            "brand_positions": brand_positions,
            "brand_in_top_3": any(p <= 3 for p in brand_positions),
            "brand_in_top_10": any(p <= 10 for p in brand_positions),
            "competitors_above": [c for c in competitors_found if c["position"] < (brand_positions[0] if brand_positions else 999)],
            "total_results": results["total"],
            "cost": 0.0,
        }

    # ----------------------------------------------------------
    # Competitor Monitoring (for Chamber 7)
    # ----------------------------------------------------------

    def monitor_competitor(self, competitor_name, max_results=10):
        """Search for recent news/content about a competitor."""
        return self.search_news(f'"{competitor_name}"', max_results=max_results)

    # ----------------------------------------------------------
    # Trend Detection (for Chamber 9)
    # ----------------------------------------------------------

    def search_trends(self, industry, topics=None, max_results=15):
        """Search for trending topics in an industry."""
        queries = [f"{industry} trends 2026", f"{industry} latest developments"]
        if topics:
            queries.extend([f"{industry} {t}" for t in topics[:3]])

        all_results = []
        for q in queries:
            result = self.search_news(q, max_results=5)
            all_results.extend(result.get("results", []))

        # Deduplicate by URL
        seen_urls = set()
        unique = []
        for r in all_results:
            if r["url"] not in seen_urls:
                seen_urls.add(r["url"])
                unique.append(r)

        return {
            "results": unique[:max_results],
            "total": len(unique),
            "industry": industry,
            "cost": 0.0,
        }

    # ----------------------------------------------------------
    # Health Check
    # ----------------------------------------------------------

    def health_check(self):
        """Check if SearXNG is running."""
        try:
            with httpx.Client(timeout=5.0) as client:
                response = client.get(f"{self.base_url}/search", params={"q": "test", "format": "json"})
                response.raise_for_status()
                return {"status": "ok", "url": self.base_url}
        except Exception as e:
            return {"status": "error", "error": str(e), "url": self.base_url}


# Singleton
searxng = SearXNGService()
