"""
Author Studio - Keyword Research & Pricing
Non-fiction + Fiction genres
"""

import re
from typing import Dict, List
from collections import Counter


class KeywordResearcher:
    """Keyword research for Amazon."""
    
    KEYWORD_DATABASE = {
        'business': {
            'primary': ['business book', 'entrepreneurship', 'leadership', 'management', 'small business', 'startup', 'business strategy'],
            'secondary': ['success', 'growth mindset', 'corporate', 'executive', 'professional development', 'career', 'workplace'],
            'comp_authors': ['Simon Sinek', 'Jim Collins', 'Peter Drucker', 'Seth Godin', 'Patrick Lencioni'],
            'trending': ['remote work', 'digital transformation', 'AI in business', 'future of work', 'sustainable business']
        },
        'self-help': {
            'primary': ['self help', 'personal development', 'self improvement', 'motivation', 'personal growth', 'success habits'],
            'secondary': ['mindset', 'productivity', 'confidence', 'goal setting', 'life coaching', 'transformation', 'empowerment'],
            'comp_authors': ['James Clear', 'Brene Brown', 'Tony Robbins', 'Mel Robbins', 'Mark Manson'],
            'trending': ['atomic habits', 'morning routine', 'dopamine detox', 'mindfulness', 'mental health']
        },
        'spirituality': {
            'primary': ['spirituality', 'spiritual growth', 'mindfulness', 'meditation', 'consciousness', 'enlightenment'],
            'secondary': ['inner peace', 'awakening', 'soul', 'wisdom', 'presence', 'divine', 'sacred'],
            'comp_authors': ['Eckhart Tolle', 'Thich Nhat Hanh', 'Deepak Chopra', 'Ram Dass', 'Michael Singer'],
            'trending': ['spiritual awakening', 'manifestation', 'law of attraction', 'energy healing', 'chakras']
        },
        'poetry': {
            'primary': ['poetry', 'poems', 'poetry collection', 'verse', 'contemporary poetry', 'modern poetry'],
            'secondary': ['love poems', 'inspirational poetry', 'nature poetry', 'healing poetry', 'spoken word'],
            'comp_authors': ['Rupi Kaur', 'Lang Leav', 'Atticus', 'R.H. Sin', 'Nayyirah Waheed'],
            'trending': ['instagram poetry', 'instapoetry', 'short poems', 'poetry for healing', 'self love poetry']
        },
        'memoir': {
            'primary': ['memoir', 'autobiography', 'personal story', 'life story', 'true story', 'biography'],
            'secondary': ['inspiring story', 'overcoming adversity', 'personal journey', 'family saga', 'coming of age'],
            'comp_authors': ['Michelle Obama', 'Tara Westover', 'Trevor Noah', 'Mary Karr', 'Frank McCourt'],
            'trending': ['celebrity memoir', 'trauma memoir', 'immigrant story', 'addiction recovery', 'mental health memoir']
        },
        'technology': {
            'primary': ['technology', 'artificial intelligence', 'AI', 'tech', 'digital', 'innovation', 'future technology'],
            'secondary': ['machine learning', 'automation', 'data science', 'cybersecurity', 'blockchain', 'digital transformation'],
            'comp_authors': ['Yuval Noah Harari', 'Kai-Fu Lee', 'Max Tegmark', 'Nick Bostrom', 'Walter Isaacson'],
            'trending': ['ChatGPT', 'generative AI', 'AI ethics', 'tech trends', 'future of AI', 'climate tech']
        },
        'health': {
            'primary': ['health', 'wellness', 'nutrition', 'fitness', 'healthy living', 'mental health'],
            'secondary': ['diet', 'exercise', 'weight loss', 'healing', 'holistic health', 'longevity', 'sleep'],
            'comp_authors': ['Matthew Walker', 'Michael Greger', 'Andrew Huberman', 'Mark Hyman', 'Rhonda Patrick'],
            'trending': ['gut health', 'intermittent fasting', 'cold therapy', 'biohacking', 'mental wellness']
        },
        'philosophy': {
            'primary': ['philosophy', 'philosophical', 'stoicism', 'ethics', 'wisdom', 'life philosophy'],
            'secondary': ['meaning of life', 'existential', 'mindfulness', 'ancient wisdom', 'practical philosophy'],
            'comp_authors': ['Ryan Holiday', 'Marcus Aurelius', 'Alain de Botton', 'Massimo Pigliucci'],
            'trending': ['stoicism', 'practical philosophy', 'modern philosophy', 'philosophy for life', 'daily stoic']
        },
        'thriller': {
            'primary': ['psychological thriller', 'crime thriller', 'mystery thriller', 'suspense thriller', 'domestic thriller'],
            'secondary': ['page turner', 'twists and turns', 'unreliable narrator', 'dark secrets', 'gripping'],
            'comp_authors': ['Gillian Flynn', 'Paula Hawkins', 'Ruth Ware', 'A.J. Finn', 'Lisa Jewell'],
            'trending': ['book club thriller', 'psychological suspense', 'murder mystery', 'crime fiction']
        },
        'romance': {
            'primary': ['contemporary romance', 'romantic comedy', 'small town romance', 'second chance romance'],
            'secondary': ['happily ever after', 'love story', 'heartwarming', 'emotional', 'steamy romance'],
            'comp_authors': ['Colleen Hoover', 'Emily Henry', 'Tessa Bailey', 'Ali Hazelwood'],
            'trending': ['booktok romance', 'spicy romance', 'forced proximity', 'grumpy sunshine']
        },
        'fantasy': {
            'primary': ['epic fantasy', 'fantasy romance', 'urban fantasy', 'dark fantasy', 'high fantasy'],
            'secondary': ['magic system', 'chosen one', 'quest fantasy', 'sword and sorcery'],
            'comp_authors': ['Sarah J Maas', 'Brandon Sanderson', 'Rebecca Yarros', 'Jennifer L Armentrout'],
            'trending': ['romantasy', 'fae romance', 'dragon fantasy', 'fourth wing']
        },
        'mystery': {
            'primary': ['cozy mystery', 'detective mystery', 'amateur sleuth', 'police procedural', 'whodunit'],
            'secondary': ['murder mystery', 'small town mystery', 'series', 'clever detective'],
            'comp_authors': ['Agatha Christie', 'Louise Penny', 'Richard Osman', 'Janet Evanovich'],
            'trending': ['cozy mystery series', 'british mystery', 'locked room mystery']
        },
        'scifi': {
            'primary': ['science fiction', 'space opera', 'dystopian', 'hard science fiction', 'military scifi'],
            'secondary': ['futuristic', 'alien contact', 'artificial intelligence', 'post apocalyptic'],
            'comp_authors': ['Andy Weir', 'Blake Crouch', 'Martha Wells', 'Adrian Tchaikovsky'],
            'trending': ['cli fi', 'hopepunk', 'cozy scifi', 'found family scifi']
        },
        'literary': {
            'primary': ['literary fiction', 'contemporary fiction', 'book club fiction', 'family saga'],
            'secondary': ['character driven', 'thought provoking', 'beautifully written', 'emotional journey'],
            'comp_authors': ['Celeste Ng', 'Amor Towles', 'Fredrik Backman', 'Ann Patchett'],
            'trending': ['upmarket fiction', 'dual timeline', 'multigenerational']
        },
    }
    
    STOP_WORDS = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'it', 'as', 'be', 'this', 'that', 'from'}
    
    @staticmethod
    def get_genre_keywords(genre: str) -> Dict:
        genre_key = genre.lower().replace('-', '').replace('_', '')
        if genre_key == 'selfhelp':
            genre_key = 'self-help'
        
        if genre_key in KeywordResearcher.KEYWORD_DATABASE:
            data = KeywordResearcher.KEYWORD_DATABASE[genre_key]
            return {
                'genre': genre,
                'primary_keywords': data['primary'],
                'secondary_keywords': data['secondary'],
                'comp_authors': data['comp_authors'],
                'trending_keywords': data['trending'],
            }
        return {'genre': genre, 'primary_keywords': ['book'], 'secondary_keywords': [], 'comp_authors': [], 'trending_keywords': []}
    
    @staticmethod
    def generate_backend_keywords(genre: str, book_title: str = '', themes: List[str] = None) -> List[str]:
        keywords = []
        data = KeywordResearcher.get_genre_keywords(genre)
        
        if data['primary_keywords']:
            keywords.append(data['primary_keywords'][0])
        if data.get('trending_keywords'):
            keywords.append(data['trending_keywords'][0])
        if data.get('comp_authors'):
            keywords.append(f"books like {data['comp_authors'][0]}")
        for kw in data.get('secondary_keywords', [])[:2]:
            keywords.append(kw)
        if themes:
            for t in themes[:2]:
                keywords.append(t)
        while len(keywords) < 7:
            keywords.append(f"{genre} book")
        return keywords[:7]


class CategoryFinder:
    """Find Amazon categories."""
    
    CATEGORY_MAP = {
        'business': ['Kindle Store > Kindle eBooks > Business & Money > Management & Leadership', 'Kindle Store > Kindle eBooks > Business & Money > Entrepreneurship'],
        'self-help': ['Kindle Store > Kindle eBooks > Self-Help > Personal Transformation', 'Kindle Store > Kindle eBooks > Self-Help > Motivational'],
        'spirituality': ['Kindle Store > Kindle eBooks > Religion & Spirituality > Spirituality', 'Kindle Store > Kindle eBooks > Religion & Spirituality > New Age'],
        'poetry': ['Kindle Store > Kindle eBooks > Literature & Fiction > Poetry', 'Books > Literature & Fiction > Poetry'],
        'memoir': ['Kindle Store > Kindle eBooks > Biographies & Memoirs > Memoirs', 'Books > Biographies & Memoirs > Memoirs'],
        'technology': ['Kindle Store > Kindle eBooks > Computers & Technology', 'Books > Computers & Technology > Computer Science > AI'],
        'health': ['Kindle Store > Kindle eBooks > Health, Fitness & Dieting', 'Books > Health, Fitness & Dieting > Mental Health'],
        'philosophy': ['Kindle Store > Kindle eBooks > Politics & Social Sciences > Philosophy', 'Books > Self-Help > Philosophy'],
        'thriller': ['Kindle Store > Kindle eBooks > Mystery, Thriller & Suspense > Thrillers > Psychological'],
        'romance': ['Kindle Store > Kindle eBooks > Romance > Contemporary'],
        'fantasy': ['Kindle Store > Kindle eBooks > Science Fiction & Fantasy > Fantasy'],
        'mystery': ['Kindle Store > Kindle eBooks > Mystery, Thriller & Suspense > Mystery'],
        'scifi': ['Kindle Store > Kindle eBooks > Science Fiction & Fantasy > Science Fiction'],
        'literary': ['Kindle Store > Kindle eBooks > Literature & Fiction > Literary Fiction'],
    }
    
    @staticmethod
    def suggest_categories(genre: str, subgenres: List[str] = None) -> Dict:
        genre_key = genre.lower().replace('-', '')
        categories = CategoryFinder.CATEGORY_MAP.get(genre_key, ['Kindle Store > Kindle eBooks > Nonfiction'])
        return {'genre': genre, 'suggested_categories': categories, 'tip': 'Select 2 categories in KDP'}


class PricingOptimizer:
    """Pricing intelligence."""
    
    GENRE_PRICES = {
        'business': 4.99, 'self-help': 4.99, 'spirituality': 3.99, 'poetry': 2.99,
        'memoir': 4.99, 'technology': 5.99, 'health': 4.99, 'philosophy': 4.99,
        'thriller': 3.99, 'romance': 3.99, 'fantasy': 4.99, 'mystery': 3.99,
        'scifi': 4.99, 'literary': 4.99,
    }
    
    @staticmethod
    def calculate_royalty(price: float, delivery_cost: float = 0.15) -> Dict:
        if price < 2.99:
            rate, royalty = 0.35, price * 0.35
        elif price <= 9.99:
            rate, royalty = 0.70, (price - delivery_cost) * 0.70
        else:
            rate, royalty = 0.35, price * 0.35
        return {'price': price, 'royalty_rate': f"{int(rate*100)}%", 'royalty_per_sale': round(royalty, 2)}
    
    @staticmethod
    def suggest_price(genre: str, page_count: int = None, is_series: bool = False, is_new_author: bool = True) -> Dict:
        genre_key = genre.lower().replace('-', '')
        base = PricingOptimizer.GENRE_PRICES.get(genre_key, 3.99)
        if is_new_author:
            base -= 1.00
        if page_count and page_count > 400:
            base += 1.00
        elif page_count and page_count < 150:
            base -= 1.00
        if is_series:
            base -= 0.50
        suggested = max(2.99, min(9.99, base))
        return {
            'suggested_price': suggested,
            'royalty_at_suggested': PricingOptimizer.calculate_royalty(suggested),
            'tip': '$2.99-$9.99 earns 70% royalty'
        }
