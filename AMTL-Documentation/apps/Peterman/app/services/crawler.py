"""
Domain Crawler for Peterman.

Crawls domain websites and extracts business intelligence.
Per DEC-003: Uses Claude CLI for business summarisation.
"""

import logging
import re
import json
from datetime import datetime
from typing import Optional, Dict, List
from urllib.parse import urljoin, urlparse
from uuid import UUID

import requests
from bs4 import BeautifulSoup

from app.config import config
from app.models.database import get_session
from app.models.domain import Domain

# Lazy import to avoid circular import
def _get_claude_cli():
    from app.services.ai_engine import call_claude_cli
    return call_claude_cli

logger = logging.getLogger(__name__)

# Crawl limits
MAX_PAGES = 50
REQUEST_TIMEOUT = 30
USER_AGENT = 'Peterman/2.0.0 (Brand Intelligence Engine; +https://peterman.ai)'

# CMS detection patterns
CMS_PATTERNS = {
    'wordpress': [
        r'/wp-content/',
        r'/wp-includes/',
        r'wp-embed',
        r'wordpress',
    ],
    'webflow': [
        r'webflow\.io',
        r'w-embed',
        r'/css/.*webflow',
    ],
    'ghost': [
        r'ghost\.org',
        r'/ghost/',
        r'ghost-',
    ],
    'shopify': [
        r'shopify\.com',
        r'shopifycdn',
        r'myshopify',
    ],
    'squarespace': [
        r'squarespace\.com',
        r'squarespace\.io',
    ],
    'wix': [
        r'wixsite\.com',
        r'wix\.com',
        r'wixstatic',
    ],
    'craftcms': [
        r'craftcms',
        r'/cpresources/',
    ],
    'drupal': [
        r'drupal',
        r'/sites/default/',
    ],
    'joomla': [
        r'joomla',
        r'/templates/',
    ],
    'static': [
        r'\.html?$',
        r'\.htm$',
    ],
}


def detect_cms(soup: BeautifulSoup, url: str, html: str) -> Optional[str]:
    """Detect CMS type from page content.
    
    Args:
        soup: BeautifulSoup object.
        url: Current URL.
        html: Raw HTML.
        
    Returns:
        CMS type string or None.
    """
    html_lower = html.lower()
    soup_str = str(soup).lower()
    
    for cms, patterns in CMS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, html_lower) or re.search(pattern, soup_str):
                logger.info(f"Detected CMS: {cms}")
                return cms
    
    # Check meta generators
    generator = soup.find('meta', attrs={'name': 'generator'})
    if generator and generator.get('content'):
        content = generator['content'].lower()
        for cms in ['wordpress', 'ghost', 'shopify', 'squarespace', 'wix', 'drupal', 'joomla']:
            if cms in content:
                return cms
    
    return 'custom'


def extract_schema(soup: BeautifulSoup) -> List[Dict]:
    """Extract schema.org structured data.
    
    Args:
        soup: BeautifulSoup object.
        
    Returns:
        List of schema objects.
    """
    schemas = []
    
    for script in soup.find_all('script', type='application/ld+json'):
        try:
            data = json.loads(script.string)
            schemas.append(data)
        except (json.JSONDecodeError, TypeError):
            continue
    
    return schemas


def extract_metadata(soup: BeautifulSoup) -> Dict:
    """Extract meta tags and Open Graph data.
    
    Args:
        soup: BeautifulSoup object.
        
    Returns:
        Metadata dictionary.
    """
    metadata = {
        'title': None,
        'description': None,
        'keywords': None,
        'og_title': None,
        'og_description': None,
        'og_image': None,
        'author': None,
    }
    
    # Title
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.get_text().strip()
    
    # Meta description
    desc_tag = soup.find('meta', attrs={'name': 'description'})
    if desc_tag:
        metadata['description'] = desc_tag.get('content', '').strip()
    
    # Keywords
    kw_tag = soup.find('meta', attrs={'name': 'keywords'})
    if kw_tag:
        metadata['keywords'] = kw_tag.get('content', '').strip()
    
    # Open Graph
    og_title = soup.find('meta', property='og:title')
    if og_title:
        metadata['og_title'] = og_title.get('content', '').strip()
    
    og_desc = soup.find('meta', property='og:description')
    if og_desc:
        metadata['og_description'] = og_desc.get('content', '').strip()
    
    og_image = soup.find('meta', property='og:image')
    if og_image:
        metadata['og_image'] = og_image.get('content', '').strip()
    
    # Author
    author = soup.find('meta', attrs={'name': 'author'})
    if author:
        metadata['author'] = author.get('content', '').strip()
    
    return metadata


def extract_headings(soup: BeautifulSoup) -> Dict:
    """Extract H1 and H2 headings.
    
    Args:
        soup: BeautifulSoup object.
        
    Returns:
        Dictionary with h1 and h2 lists.
    """
    headings = {'h1': [], 'h2': []}
    
    for tag in soup.find_all('h1'):
        text = tag.get_text().strip()
        if text:
            headings['h1'].append(text)
    
    for tag in soup.find_all('h2'):
        text = tag.get_text().strip()
        if text:
            headings['h2'].append(text)
    
    return headings


def extract_links(soup: BeautifulSoup, base_url: str) -> List[Dict]:
    """Extract internal and external links.
    
    Args:
        soup: BeautifulSoup object.
        base_url: Base URL for resolving relative links.
        
    Returns:
        List of link dictionaries.
    """
    links = []
    base_domain = urlparse(base_url).netloc
    
    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(base_url, href)
        parsed = urlparse(full_url)
        
        link_type = 'internal' if parsed.netloc == base_domain or not parsed.netloc else 'external'
        
        links.append({
            'url': full_url,
            'text': a.get_text().strip()[:200],
            'type': link_type,
            'domain': parsed.netloc
        })
    
    return links


def extract_text_content(soup: BeautifulSoup, max_length: int = 10000) -> str:
    """Extract main text content from page.
    
    Args:
        soup: BeautifulSoup object.
        max_length: Maximum text length.
        
    Returns:
        Extracted text content.
    """
    # Remove script and style elements
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    # Get main content
    main = soup.find('main') or soup.find('article') or soup.body
    
    if main:
        text = main.get_text(separator='\n', strip=True)
    else:
        text = soup.get_text(separator='\n', strip=True)
    
    # Clean up whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    
    return text[:max_length]


def crawl_page(url: str) -> Optional[Dict]:
    """Crawl a single page.
    
    Args:
        url: URL to crawl.
        
    Returns:
        Page data dictionary or None on failure.
    """
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT, allow_redirects=True)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        page_data = {
            'url': url,
            'status_code': response.status_code,
            'metadata': extract_metadata(soup),
            'headings': extract_headings(soup),
            'links': extract_links(soup, url)[:50],  # Limit links
            'schema': extract_schema(soup),
            'text_content': extract_text_content(soup),
            'cms_detected': None,  # Set in batch crawl
            'crawled_at': datetime.utcnow().isoformat(),
        }
        
        return page_data
        
    except Exception as e:
        logger.warning(f"Failed to crawl {url}: {e}")
        return None


def crawl_domain(domain_id: UUID, domain_url: str) -> Dict:
    """Crawl a domain and extract business intelligence.
    
    Args:
        domain_id: UUID of the domain.
        domain_url: Domain URL to crawl.
        
    Returns:
        Crawl results with pages and business summary.
    """
    session = get_session()
    
    try:
        # Normalise URL
        if not domain_url.startswith(('http://', 'https://')):
            domain_url = f'https://{domain_url}'
        
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        # First pass: crawl homepage
        logger.info(f"Starting crawl of {domain_url}")
        homepage_data = crawl_page(domain_url)
        
        if not homepage_data:
            raise RuntimeError(f"Failed to crawl homepage: {domain_url}")
        
        # Detect CMS
        response = requests.get(domain_url, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(response.text, 'html.parser')
        cms_type = detect_cms(soup, domain_url, response.text)
        
        # Update domain with CMS type
        domain.cms_type = cms_type
        
        # Collect all internal links
        internal_links = [l['url'] for l in homepage_data.get('links', []) if l['type'] == 'internal']
        
        # Second pass: crawl subpages (up to MAX_PAGES)
        crawled_pages = [homepage_data]
        urls_to_crawl = internal_links[:MAX_PAGES - 1]
        
        for url in urls_to_crawl:
            if len(crawled_pages) >= MAX_PAGES:
                break
            
            page_data = crawl_page(url)
            if page_data:
                crawled_pages.append(page_data)
                # Add any new internal links
                new_links = [l['url'] for l in page_data.get('links', []) 
                            if l['type'] == 'internal' and l['url'] not in [p['url'] for p in crawled_pages]]
                urls_to_crawl.extend(new_links[:5])
        
        # Generate business summary using Claude CLI
        business_summary = generate_business_summary(crawled_pages, domain_url)
        
        # Prepare crawl data for storage
        crawl_data = {
            'homepage': homepage_data,
            'pages': crawled_pages,
            'cms_detected': cms_type,
            'pages_crawled': len(crawled_pages),
            'business_summary': business_summary,
            'crawl_completed_at': datetime.utcnow().isoformat(),
        }
        
        # Store crawl data as JSONB
        domain.crawl_data = crawl_data
        domain.status = 'active'
        
        session.commit()
        
        logger.info(f"Crawl complete for {domain_url}: {len(crawled_pages)} pages")
        
        return {
            'domain_id': str(domain_id),
            'domain_name': domain_url,
            'cms_type': cms_type,
            'pages_crawled': len(crawled_pages),
            'business_summary': business_summary,
        }
        
    except Exception as e:
        session.rollback()
        logger.error(f"Crawl failed for {domain_id}: {e}")
        raise
        
    finally:
        session.close()


def generate_business_summary(pages: List[Dict], domain_url: str) -> Dict:
    """Generate business summary using Claude CLI.
    
    Args:
        pages: List of crawled page data.
        domain_url: Domain URL.
        
    Returns:
        Business summary dictionary.
    """
    # Prepare summary data from pages
    homepage = pages[0] if pages else {}
    metadata = homepage.get('metadata', {})
    headings = homepage.get('headings', {})
    text_content = homepage.get('text_content', '')[:3000]
    
    # Build prompt for Claude
    prompt = f"""Analyze this website and provide a business summary.

Domain: {domain_url}

Page Title: {metadata.get('title', 'N/A')}
Meta Description: {metadata.get('description', 'N/A')}

H1 Headings:
{chr(10).join(headings.get('h1', [])[:5])}

H2 Headings:
{chr(10).join(headings.get('h2', [])[:10])}

Page Content (first 3000 chars):
{text_content}

Provide a JSON response with:
1. "what_they_do": One sentence describing what the business does
2. "target_audience": Who their ideal customers are
3. "key_services": Array of 3-5 main services/products
4. "unique_value": What makes them different from competitors
5. "industry": Primary industry/vertical
6. "location": Location info if visible (city, country)
7. "brand_voice": Tone/style (e.g., "professional", "friendly", "innovative")

Respond ONLY with valid JSON, no other text."""

    system_prompt = "You are Peterman, a brand intelligence analysis tool. Analyze websites and extract key business information accurately."
    
    try:
        call_claude_cli = _get_claude_cli()
        result = call_claude_cli(prompt, system_prompt, timeout=60)
        
        # Parse JSON response
        # Handle potential markdown code blocks
        result = result.strip()
        if result.startswith('```json'):
            result = result[7:]
        if result.startswith('```'):
            result = result[3:]
        if result.endswith('```'):
            result = result[:-3]
        
        summary = json.loads(result.strip())
        
        return {
            'what_they_do': summary.get('what_they_do', 'Unknown'),
            'target_audience': summary.get('target_audience', 'Unknown'),
            'key_services': summary.get('key_services', []),
            'unique_value': summary.get('unique_value', 'Unknown'),
            'industry': summary.get('industry', 'Unknown'),
            'location': summary.get('location'),
            'brand_voice': summary.get('brand_voice', 'Unknown'),
            'generated_at': datetime.utcnow().isoformat(),
        }
        
    except json.JSONDecodeError as e:
        logger.warning(f"Failed to parse Claude summary: {e}")
        return {
            'what_they_do': 'Analysis pending',
            'target_audience': 'Unknown',
            'key_services': [],
            'unique_value': 'Unknown',
            'industry': 'Unknown',
            'location': None,
            'brand_voice': 'Unknown',
            'error': str(e),
        }
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return {
            'what_they_do': 'Analysis failed',
            'error': str(e),
        }


def trigger_crawl(domain_id: UUID) -> Dict:
    """Trigger a crawl for a domain.
    
    Args:
        domain_id: UUID of the domain.
        
    Returns:
        Crawl results.
    """
    session = get_session()
    
    try:
        domain = session.query(Domain).filter_by(domain_id=domain_id).first()
        if not domain:
            raise ValueError(f"Domain not found: {domain_id}")
        
        return crawl_domain(domain_id, domain.domain_name)
        
    finally:
        session.close()
