"""
Author Studio - Phase 2: Amazon Integration
Amazon listing analysis and KDP automation
"""

import re
import json
import asyncio
from dataclasses import dataclass, asdict
from typing import Optional, Dict, List, Tuple
from datetime import datetime
from pathlib import Path


@dataclass
class AmazonListing:
    """Represents an Amazon book listing."""
    asin: str
    title: str
    subtitle: Optional[str]
    author: str
    description: str
    price: float
    currency: str
    categories: List[str]
    keywords: List[str]
    reviews_count: int
    rating: float
    rank: Optional[int]
    page_count: Optional[int]
    publication_date: Optional[str]
    cover_url: Optional[str]
    fetched_at: str
    
    def to_dict(self):
        return asdict(self)


class AmazonScraper:
    """Scrapes Amazon book listings."""
    
    AMAZON_DOMAINS = {
        'us': 'amazon.com',
        'uk': 'amazon.co.uk',
        'au': 'amazon.com.au',
        'ca': 'amazon.ca',
        'de': 'amazon.de',
        'fr': 'amazon.fr',
        'in': 'amazon.in',
    }
    
    @staticmethod
    def extract_asin(url_or_asin: str) -> Tuple[str, str]:
        """Extract ASIN and domain from URL or plain ASIN."""
        # If it's just an ASIN (10 chars, alphanumeric)
        if re.match(r'^[A-Z0-9]{10}$', url_or_asin.upper()):
            return url_or_asin.upper(), 'us'
        
        # Extract from URL
        asin_match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', url_or_asin, re.I)
        if asin_match:
            asin = asin_match.group(1).upper()
            # Detect domain
            domain = 'us'
            for code, dom in AmazonScraper.AMAZON_DOMAINS.items():
                if dom in url_or_asin:
                    domain = code
                    break
            return asin, domain
        
        raise ValueError(f"Could not extract ASIN from: {url_or_asin}")
    
    @staticmethod
    async def fetch_listing(url_or_asin: str) -> AmazonListing:
        """Fetch listing data from Amazon using Playwright."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("Playwright not installed. Run: pip install playwright && playwright install chromium")
        
        asin, domain = AmazonScraper.extract_asin(url_or_asin)
        amazon_domain = AmazonScraper.AMAZON_DOMAINS.get(domain, 'amazon.com')
        url = f"https://www.{amazon_domain}/dp/{asin}"
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            page = await context.new_page()
            
            await page.goto(url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(2000)  # Let JS render
            
            # Extract data
            listing = await AmazonScraper._extract_listing_data(page, asin)
            
            await browser.close()
            return listing
    
    @staticmethod
    async def _extract_listing_data(page, asin: str) -> AmazonListing:
        """Extract listing data from page."""
        
        async def safe_text(selector: str, default: str = "") -> str:
            try:
                el = await page.query_selector(selector)
                return (await el.inner_text()).strip() if el else default
            except:
                return default
        
        async def safe_attr(selector: str, attr: str, default: str = "") -> str:
            try:
                el = await page.query_selector(selector)
                return (await el.get_attribute(attr)) if el else default
            except:
                return default
        
        # Title
        title = await safe_text('#productTitle', 'Unknown Title')
        
        # Subtitle (often in title after colon)
        subtitle = None
        if ':' in title:
            parts = title.split(':', 1)
            title = parts[0].strip()
            subtitle = parts[1].strip() if len(parts) > 1 else None
        
        # Author
        author = await safe_text('.author a', '')
        if not author:
            author = await safe_text('#bylineInfo .author', 'Unknown Author')
        
        # Description
        description = await safe_text('#bookDescription_feature_div', '')
        if not description:
            description = await safe_text('#productDescription', '')
        
        # Price
        price_text = await safe_text('.kindle-price .a-color-price', '')
        if not price_text:
            price_text = await safe_text('#kindle-price', '')
        if not price_text:
            price_text = await safe_text('.a-price .a-offscreen', '0.00')
        
        price = 0.0
        currency = 'USD'
        price_match = re.search(r'([£$€₹])?\s*([\d,.]+)', price_text)
        if price_match:
            currency_symbol = price_match.group(1) or '$'
            currency_map = {'$': 'USD', '£': 'GBP', '€': 'EUR', '₹': 'INR'}
            currency = currency_map.get(currency_symbol, 'USD')
            price = float(price_match.group(2).replace(',', ''))
        
        # Rating
        rating_text = await safe_text('#acrPopover', '0')
        rating = 0.0
        rating_match = re.search(r'([\d.]+)\s*out of', rating_text)
        if rating_match:
            rating = float(rating_match.group(1))
        
        # Review count
        reviews_text = await safe_text('#acrCustomerReviewText', '0')
        reviews_count = 0
        reviews_match = re.search(r'([\d,]+)', reviews_text)
        if reviews_match:
            reviews_count = int(reviews_match.group(1).replace(',', ''))
        
        # Categories
        categories = []
        cat_elements = await page.query_selector_all('#wayfinding-breadcrumbs_feature_div a')
        for el in cat_elements[:5]:
            cat_text = await el.inner_text()
            if cat_text.strip():
                categories.append(cat_text.strip())
        
        # Cover URL
        cover_url = await safe_attr('#imgBlkFront', 'src', '')
        if not cover_url:
            cover_url = await safe_attr('#ebooksImgBlkFront', 'src', '')
        
        # Page count
        page_count = None
        details_text = await safe_text('#detailBullets_feature_div', '')
        pages_match = re.search(r'(\d+)\s*pages', details_text, re.I)
        if pages_match:
            page_count = int(pages_match.group(1))
        
        # Rank
        rank = None
        rank_match = re.search(r'#([\d,]+)\s*in\s*Kindle', details_text, re.I)
        if rank_match:
            rank = int(rank_match.group(1).replace(',', ''))
        
        return AmazonListing(
            asin=asin,
            title=title,
            subtitle=subtitle,
            author=author,
            description=description,
            price=price,
            currency=currency,
            categories=categories,
            keywords=[],  # Not publicly visible
            reviews_count=reviews_count,
            rating=rating,
            rank=rank,
            page_count=page_count,
            publication_date=None,
            cover_url=cover_url,
            fetched_at=datetime.now().isoformat()
        )


class ListingAnalyzer:
    """Analyzes Amazon listings and suggests improvements."""
    
    # Keyword suggestions by genre
    GENRE_KEYWORDS = {
        'thriller': ['psychological thriller', 'suspense', 'crime fiction', 'mystery thriller', 
                    'page turner', 'twists and turns', 'gripping', 'dark secrets'],
        'romance': ['love story', 'romantic', 'happily ever after', 'contemporary romance',
                   'emotional', 'heartwarming', 'second chance', 'small town romance'],
        'fantasy': ['epic fantasy', 'magic', 'sword and sorcery', 'fantasy adventure',
                   'mythical', 'quest', 'kingdoms', 'dragons'],
        'scifi': ['science fiction', 'space opera', 'dystopian', 'futuristic',
                 'technology', 'artificial intelligence', 'cyberpunk', 'alien'],
        'horror': ['supernatural horror', 'scary', 'haunted', 'psychological horror',
                  'dark fiction', 'nightmare', 'terrifying', 'ghost story'],
        'mystery': ['whodunit', 'detective', 'cozy mystery', 'amateur sleuth',
                   'murder mystery', 'puzzle', 'investigation', 'clues'],
        'literary': ['literary fiction', 'book club', 'contemporary fiction', 'family saga',
                    'character driven', 'thought provoking', 'beautifully written'],
        'medical': ['medical thriller', 'hospital drama', 'doctor', 'healthcare',
                   'medical mystery', 'pandemic', 'surgery', 'diagnosis']
    }
    
    @staticmethod
    def analyze(listing: AmazonListing, book_dna: Optional[Dict] = None) -> Dict:
        """Analyze listing and generate improvement suggestions."""
        suggestions = {
            'title': [],
            'description': [],
            'keywords': [],
            'price': [],
            'categories': [],
            'overall_score': 0,
            'issues': [],
            'quick_wins': []
        }
        
        score = 100
        
        # Title analysis
        if len(listing.title) < 20:
            suggestions['title'].append({
                'issue': 'Title may be too short',
                'suggestion': 'Consider adding a subtitle with keywords',
                'priority': 'medium'
            })
            score -= 5
        
        if len(listing.title) > 80:
            suggestions['title'].append({
                'issue': 'Title may be too long',
                'suggestion': 'Shorten for better visibility',
                'priority': 'low'
            })
            score -= 3
        
        if not listing.subtitle:
            suggestions['title'].append({
                'issue': 'No subtitle detected',
                'suggestion': 'Add a subtitle with genre keywords for discoverability',
                'priority': 'high'
            })
            suggestions['quick_wins'].append('Add a keyword-rich subtitle')
            score -= 10
        
        # Description analysis
        desc_length = len(listing.description)
        if desc_length < 500:
            suggestions['description'].append({
                'issue': f'Description is short ({desc_length} chars)',
                'suggestion': 'Expand to 1500-2000 characters for better conversion',
                'priority': 'high'
            })
            suggestions['quick_wins'].append('Expand book description')
            score -= 15
        elif desc_length < 1000:
            suggestions['description'].append({
                'issue': f'Description could be longer ({desc_length} chars)',
                'suggestion': 'Aim for 1500-2000 characters',
                'priority': 'medium'
            })
            score -= 8
        
        # Check for HTML formatting
        if '<' not in listing.description:
            suggestions['description'].append({
                'issue': 'Description lacks HTML formatting',
                'suggestion': 'Add <b>, <i>, <br> tags for better readability',
                'priority': 'medium'
            })
            score -= 5
        
        # Check for call to action
        cta_words = ['buy now', 'get your copy', 'download', 'read today', 'grab', 'click']
        has_cta = any(word in listing.description.lower() for word in cta_words)
        if not has_cta:
            suggestions['description'].append({
                'issue': 'No clear call-to-action',
                'suggestion': 'Add a compelling CTA at the end',
                'priority': 'medium'
            })
            score -= 5
        
        # Price analysis
        if listing.price > 0:
            if listing.price < 0.99:
                suggestions['price'].append({
                    'issue': 'Price below $0.99',
                    'suggestion': 'Consider $2.99-$4.99 for better royalty rates (70%)',
                    'priority': 'high'
                })
                score -= 10
            elif listing.price > 9.99:
                suggestions['price'].append({
                    'issue': 'Price above $9.99',
                    'suggestion': 'Only 35% royalty above $9.99. Consider lowering.',
                    'priority': 'medium'
                })
                score -= 5
        
        # Review analysis
        if listing.reviews_count < 10:
            suggestions['issues'].append('Low review count - prioritize getting reviews')
            score -= 10
        elif listing.reviews_count < 50:
            suggestions['issues'].append('Could benefit from more reviews')
            score -= 5
        
        if listing.rating < 4.0 and listing.reviews_count > 5:
            suggestions['issues'].append(f'Rating ({listing.rating}) below 4.0 - review feedback')
            score -= 10
        
        # Keyword suggestions based on DNA
        if book_dna:
            primary_genre = book_dna.get('primary_genre', 'literary')
            suggested_keywords = ListingAnalyzer.GENRE_KEYWORDS.get(primary_genre, [])
            suggestions['keywords'] = {
                'suggested': suggested_keywords[:7],
                'based_on': f"Book DNA detected: {primary_genre}",
                'tip': 'Use these in your 7 backend keyword slots'
            }
        
        # Category check
        if len(listing.categories) < 2:
            suggestions['categories'].append({
                'issue': 'Only visible in limited categories',
                'suggestion': 'Ensure you have selected 2 browse categories in KDP',
                'priority': 'medium'
            })
        
        suggestions['overall_score'] = max(0, score)
        
        return suggestions
    
    @staticmethod
    def generate_description(listing: AmazonListing, book_dna: Optional[Dict] = None, style: str = 'amazon') -> str:
        """Generate an optimized book description."""
        
        # Build hook based on genre
        genre = 'fiction'
        if book_dna:
            genre = book_dna.get('primary_genre', 'fiction')
        
        hooks = {
            'thriller': "What would you do if everything you believed was a lie?",
            'romance': "Sometimes love finds you when you least expect it...",
            'fantasy': "In a world where magic is forbidden...",
            'mystery': "When the truth is buried, the past always finds a way back...",
            'horror': "Some doors should never be opened...",
            'scifi': "In the year 2157, humanity faces its greatest challenge...",
            'literary': "A powerful story of love, loss, and redemption...",
            'medical': "In the sterile halls of Metropolitan Hospital, nothing is as it seems...",
        }
        
        hook = hooks.get(genre, "A captivating story that will stay with you...")
        
        if style == 'amazon':
            # Amazon HTML format
            template = f"""<b>{hook}</b>

<b>{listing.title}</b> is a {genre} novel that will keep you turning pages late into the night.

{listing.description[:500] if listing.description else 'An unforgettable story awaits...'}

<b>What readers are saying:</b>
★★★★★ "Couldn't put it down!"
★★★★★ "A must-read for {genre} fans"

<b>Perfect for readers who love:</b>
• Page-turning suspense
• Unforgettable characters  
• Surprising twists

<b>Scroll up and click "Buy Now" to start reading today!</b>

<i>Available in Kindle, paperback, and Kindle Unlimited.</i>"""
        
        else:
            # Plain text format
            template = f"""{hook}

{listing.title} is a {genre} novel that will keep you turning pages late into the night.

{listing.description[:500] if listing.description else 'An unforgettable story awaits...'}

Perfect for readers who love page-turning suspense, unforgettable characters, and surprising twists.

Get your copy today!"""
        
        return template


class KDPAutomation:
    """Automates KDP actions with Playwright."""
    
    def __init__(self, email: str = None, credentials_path: str = None):
        self.email = email
        self.credentials_path = credentials_path or Path.home() / '.author_studio' / 'kdp_session.json'
        self.browser = None
        self.page = None
    
    async def login(self, email: str, password: str) -> bool:
        """Log into KDP."""
        try:
            from playwright.async_api import async_playwright
        except ImportError:
            raise ImportError("Playwright not installed")
        
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(headless=False)  # Visible for 2FA
        self.context = await self.browser.new_context()
        self.page = await self.context.new_page()
        
        await self.page.goto('https://kdp.amazon.com/en_US/signin')
        await self.page.wait_for_timeout(2000)
        
        # Enter email
        await self.page.fill('#ap_email', email)
        await self.page.click('#continue')
        await self.page.wait_for_timeout(1000)
        
        # Enter password
        await self.page.fill('#ap_password', password)
        await self.page.click('#signInSubmit')
        
        # Wait for potential 2FA or dashboard
        await self.page.wait_for_timeout(5000)
        
        # Check if logged in
        if 'kdp.amazon.com' in self.page.url and 'signin' not in self.page.url:
            # Save session
            await self.context.storage_state(path=str(self.credentials_path))
            return True
        
        return False
    
    async def load_session(self) -> bool:
        """Load saved session."""
        if not self.credentials_path.exists():
            return False
        
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(storage_state=str(self.credentials_path))
            self.page = await self.context.new_page()
            
            await self.page.goto('https://kdp.amazon.com/en_US/bookshelf')
            await self.page.wait_for_timeout(3000)
            
            return 'bookshelf' in self.page.url
        except:
            return False
    
    async def get_book_list(self) -> List[Dict]:
        """Get list of books from KDP bookshelf."""
        if not self.page:
            raise RuntimeError("Not logged in")
        
        await self.page.goto('https://kdp.amazon.com/en_US/bookshelf')
        await self.page.wait_for_timeout(3000)
        
        books = []
        rows = await self.page.query_selector_all('[data-action="bookshelf-row-click"]')
        
        for row in rows:
            title_el = await row.query_selector('.book-title')
            asin_el = await row.query_selector('[data-asin]')
            
            title = await title_el.inner_text() if title_el else 'Unknown'
            asin = await asin_el.get_attribute('data-asin') if asin_el else None
            
            books.append({
                'title': title.strip(),
                'asin': asin
            })
        
        return books
    
    async def update_description(self, asin: str, new_description: str) -> Dict:
        """Update book description in KDP."""
        if not self.page:
            raise RuntimeError("Not logged in")
        
        # Navigate to book details
        # Note: KDP URLs vary, this is approximate
        edit_url = f'https://kdp.amazon.com/en_US/title-setup/{asin}'
        await self.page.goto(edit_url)
        await self.page.wait_for_timeout(3000)
        
        # Find and update description field
        desc_field = await self.page.query_selector('#book-description-textarea')
        if desc_field:
            await desc_field.fill('')
            await desc_field.fill(new_description)
            
            # Save (but don't publish - requires approval)
            save_btn = await self.page.query_selector('#save-and-continue')
            if save_btn:
                # Don't actually click - return preview
                return {
                    'success': True,
                    'action': 'preview',
                    'message': 'Description ready to update. Approve to save.',
                    'new_description': new_description
                }
        
        return {'success': False, 'error': 'Could not find description field'}
    
    async def close(self):
        """Close browser."""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()


# Synchronous wrappers for UI
def fetch_amazon_listing(url_or_asin: str) -> Dict:
    """Synchronous wrapper to fetch Amazon listing."""
    try:
        listing = asyncio.run(AmazonScraper.fetch_listing(url_or_asin))
        return {'success': True, 'listing': listing.to_dict()}
    except Exception as e:
        return {'success': False, 'error': str(e)}


def analyze_listing(listing_data: Dict, book_dna: Optional[Dict] = None) -> Dict:
    """Analyze a listing and return suggestions."""
    listing = AmazonListing(**listing_data)
    return ListingAnalyzer.analyze(listing, book_dna)


def generate_description(listing_data: Dict, book_dna: Optional[Dict] = None, style: str = 'amazon') -> str:
    """Generate optimized description."""
    listing = AmazonListing(**listing_data)
    return ListingAnalyzer.generate_description(listing, book_dna, style)
