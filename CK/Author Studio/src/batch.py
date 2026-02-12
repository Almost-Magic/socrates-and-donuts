"""
Author Studio - Batch Operations
Folder scanning, bulk analysis, and mass deployment
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading


class FolderScanner:
    """Scans folders for manuscript files."""
    
    SUPPORTED_EXTENSIONS = {'.pdf', '.epub', '.docx', '.txt', '.md', '.doc'}
    
    @staticmethod
    def scan_folder(folder_path: str, recursive: bool = True) -> List[Dict]:
        """
        Scan a folder for manuscript files.
        
        Args:
            folder_path: Path to the folder to scan
            recursive: Whether to scan subfolders
            
        Returns:
            List of file info dicts with path, name, size, extension
        """
        folder = Path(folder_path)
        if not folder.exists():
            raise ValueError(f"Folder not found: {folder_path}")
        
        if not folder.is_dir():
            raise ValueError(f"Not a folder: {folder_path}")
        
        files = []
        
        if recursive:
            pattern = '**/*'
        else:
            pattern = '*'
        
        for file_path in folder.glob(pattern):
            if file_path.is_file() and file_path.suffix.lower() in FolderScanner.SUPPORTED_EXTENSIONS:
                files.append({
                    'path': str(file_path),
                    'name': file_path.name,
                    'stem': file_path.stem,
                    'extension': file_path.suffix.lower(),
                    'size': file_path.stat().st_size,
                    'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
                    'folder': file_path.parent.name,
                    'full_folder': str(file_path.parent),
                    'modified': datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                })
        
        # Sort by folder then name
        files.sort(key=lambda x: (x['full_folder'], x['name']))
        
        return files
    
    @staticmethod
    def group_by_folder(files: List[Dict]) -> Dict[str, List[Dict]]:
        """Group files by their parent folder."""
        grouped = {}
        for f in files:
            folder = f['folder']
            if folder not in grouped:
                grouped[folder] = []
            grouped[folder].append(f)
        return grouped
    
    @staticmethod
    def get_summary(files: List[Dict]) -> Dict:
        """Get summary statistics for scanned files."""
        if not files:
            return {
                'total_files': 0,
                'total_size_mb': 0,
                'by_extension': {},
                'by_folder': {}
            }
        
        by_ext = {}
        by_folder = {}
        total_size = 0
        
        for f in files:
            ext = f['extension']
            folder = f['folder']
            
            by_ext[ext] = by_ext.get(ext, 0) + 1
            by_folder[folder] = by_folder.get(folder, 0) + 1
            total_size += f['size']
        
        return {
            'total_files': len(files),
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'by_extension': by_ext,
            'by_folder': by_folder,
            'folders_count': len(by_folder)
        }


class BatchProcessor:
    """Processes multiple books in batch."""
    
    def __init__(self, db, max_workers: int = 4):
        self.db = db
        self.max_workers = max_workers
        self.progress = {'current': 0, 'total': 0, 'status': 'idle', 'current_file': ''}
        self._lock = threading.Lock()
    
    def _update_progress(self, current: int, total: int, status: str, current_file: str = ''):
        with self._lock:
            self.progress = {
                'current': current,
                'total': total,
                'status': status,
                'current_file': current_file,
                'percent': round(current / total * 100) if total > 0 else 0
            }
    
    def get_progress(self) -> Dict:
        with self._lock:
            return self.progress.copy()
    
    def import_files(self, files: List[Dict], parse_func: Callable, 
                    skip_existing: bool = True) -> Dict:
        """
        Import multiple files into the database.
        
        Args:
            files: List of file info dicts from FolderScanner
            parse_func: Function to parse file content (from parsers module)
            skip_existing: Skip files already in database
            
        Returns:
            Results summary
        """
        results = {
            'imported': [],
            'skipped': [],
            'failed': [],
            'total': len(files)
        }
        
        # Get existing files
        existing_paths = set()
        if skip_existing:
            for book in self.db.get_all_books():
                if book.get('file_path'):
                    existing_paths.add(book['file_path'])
        
        self._update_progress(0, len(files), 'importing')
        
        for i, file_info in enumerate(files):
            file_path = file_info['path']
            self._update_progress(i + 1, len(files), 'importing', file_info['name'])
            
            # Skip if already imported
            if file_path in existing_paths:
                results['skipped'].append({
                    'file': file_info['name'],
                    'reason': 'Already imported'
                })
                continue
            
            try:
                # Parse file
                text, error = parse_func(file_path)
                if error:
                    results['failed'].append({
                        'file': file_info['name'],
                        'error': error
                    })
                    continue
                
                # Generate title from filename
                title = file_info['stem'].replace('_', ' ').replace('-', ' ').title()
                
                # Count words
                word_count = len(text.split()) if text else 0
                
                # Add to database
                book_id = self.db.add_book(
                    title=title,
                    file_path=file_path,
                    file_name=file_info['name'],
                    word_count=word_count,
                    raw_text=text
                )
                
                results['imported'].append({
                    'file': file_info['name'],
                    'title': title,
                    'book_id': book_id,
                    'word_count': word_count
                })
                
            except Exception as e:
                results['failed'].append({
                    'file': file_info['name'],
                    'error': str(e)
                })
        
        self._update_progress(len(files), len(files), 'complete')
        
        return results
    
    def analyze_all(self, book_ids: List[int] = None, analyzer_func: Callable = None) -> Dict:
        """
        Run Book DNA analysis on multiple books.
        
        Args:
            book_ids: List of book IDs to analyze (None = all unanalyzed)
            analyzer_func: The BookAnalyzer.generate_dna_profile function
            
        Returns:
            Results summary
        """
        if book_ids is None:
            # Get all unanalyzed books
            all_books = self.db.get_all_books()
            book_ids = [b['id'] for b in all_books if not b.get('dna_profile')]
        
        if not book_ids:
            return {'analyzed': [], 'failed': [], 'total': 0, 'message': 'No books to analyze'}
        
        results = {
            'analyzed': [],
            'failed': [],
            'total': len(book_ids)
        }
        
        self._update_progress(0, len(book_ids), 'analyzing')
        
        for i, book_id in enumerate(book_ids):
            book = self.db.get_book(book_id)
            if not book:
                results['failed'].append({'book_id': book_id, 'error': 'Book not found'})
                continue
            
            self._update_progress(i + 1, len(book_ids), 'analyzing', book.get('title', 'Unknown'))
            
            try:
                text = book.get('raw_text', '')
                if not text:
                    results['failed'].append({
                        'book_id': book_id,
                        'title': book.get('title'),
                        'error': 'No text content'
                    })
                    continue
                
                # Generate DNA profile
                dna = analyzer_func(text, book.get('title', 'Untitled'))
                
                # Update database
                self.db.update_book(
                    book_id,
                    dna_profile=dna,
                    chapter_count=dna.get('chapter_count', 0),
                    analyzed_at=datetime.now().isoformat()
                )
                
                results['analyzed'].append({
                    'book_id': book_id,
                    'title': book.get('title'),
                    'health_score': dna.get('health_score'),
                    'primary_genre': dna.get('primary_genre')
                })
                
            except Exception as e:
                results['failed'].append({
                    'book_id': book_id,
                    'title': book.get('title'),
                    'error': str(e)
                })
        
        self._update_progress(len(book_ids), len(book_ids), 'complete')
        
        return results
    
    def generate_all_metadata(self, book_ids: List[int] = None, 
                             keyword_func: Callable = None,
                             category_func: Callable = None,
                             pricing_func: Callable = None,
                             description_func: Callable = None) -> Dict:
        """
        Generate Amazon metadata for multiple books.
        
        Returns keywords, categories, pricing, and descriptions for all books.
        """
        if book_ids is None:
            all_books = self.db.get_all_books()
            book_ids = [b['id'] for b in all_books if b.get('dna_profile')]
        
        results = {
            'generated': [],
            'failed': [],
            'total': len(book_ids)
        }
        
        self._update_progress(0, len(book_ids), 'generating metadata')
        
        for i, book_id in enumerate(book_ids):
            book = self.db.get_book(book_id)
            if not book:
                continue
            
            self._update_progress(i + 1, len(book_ids), 'generating metadata', book.get('title', 'Unknown'))
            
            try:
                dna = book.get('dna_profile', {})
                genre = dna.get('primary_genre', 'literary')
                
                metadata = {
                    'book_id': book_id,
                    'title': book.get('title'),
                    'genre': genre
                }
                
                # Keywords
                if keyword_func:
                    keywords = keyword_func(genre)
                    metadata['keywords'] = keywords
                
                # Categories
                if category_func:
                    categories = category_func(genre)
                    metadata['categories'] = categories
                
                # Pricing
                if pricing_func:
                    pricing = pricing_func(
                        genre=genre,
                        page_count=book.get('word_count', 0) // 250,  # Rough page estimate
                        is_series=False,
                        is_new_author=True
                    )
                    metadata['pricing'] = pricing
                
                # Description
                if description_func:
                    # Create a mock listing for description generation
                    mock_listing = {
                        'asin': '',
                        'title': book.get('title', ''),
                        'subtitle': '',
                        'author': 'Author',
                        'description': dna.get('summary', {}).get('strengths', [''])[0] if dna.get('summary') else '',
                        'price': 0,
                        'currency': 'USD',
                        'categories': [],
                        'keywords': [],
                        'reviews_count': 0,
                        'rating': 0,
                        'rank': None,
                        'page_count': book.get('word_count', 0) // 250,
                        'publication_date': None,
                        'cover_url': None,
                        'fetched_at': datetime.now().isoformat()
                    }
                    description = description_func(mock_listing, dna, 'amazon')
                    metadata['description'] = description
                
                results['generated'].append(metadata)
                
            except Exception as e:
                results['failed'].append({
                    'book_id': book_id,
                    'title': book.get('title'),
                    'error': str(e)
                })
        
        self._update_progress(len(book_ids), len(book_ids), 'complete')
        
        return results


class BulkExporter:
    """Exports batch results in various formats."""
    
    @staticmethod
    def to_json(data: Dict, filepath: str) -> bool:
        """Export data to JSON file."""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Export error: {e}")
            return False
    
    @staticmethod
    def to_csv(books_metadata: List[Dict], filepath: str) -> bool:
        """Export book metadata to CSV for easy review."""
        try:
            import csv
            
            fieldnames = ['title', 'genre', 'suggested_price', 'keywords', 'categories', 'description_preview']
            
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for book in books_metadata:
                    row = {
                        'title': book.get('title', ''),
                        'genre': book.get('genre', ''),
                        'suggested_price': book.get('pricing', {}).get('suggested_price', ''),
                        'keywords': ', '.join(book.get('keywords', {}).get('backend_keywords', [])[:3]),
                        'categories': book.get('categories', {}).get('suggested_categories', [''])[0][:50],
                        'description_preview': book.get('description', '')[:100] + '...' if book.get('description') else ''
                    }
                    writer.writerow(row)
            
            return True
        except Exception as e:
            print(f"CSV export error: {e}")
            return False
    
    @staticmethod
    def generate_kdp_ready_package(books_metadata: List[Dict], output_folder: str) -> Dict:
        """
        Generate a KDP-ready package with all metadata organized by book.
        
        Creates a folder structure:
        output_folder/
            book-title-1/
                metadata.json
                description.txt
                keywords.txt
            book-title-2/
                ...
        """
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results = {'created': [], 'failed': []}
        
        for book in books_metadata:
            try:
                title = book.get('title', 'untitled')
                # Sanitize folder name
                safe_title = "".join(c for c in title if c.isalnum() or c in ' -_').strip()[:50]
                book_folder = output_path / safe_title
                book_folder.mkdir(exist_ok=True)
                
                # Write metadata.json
                with open(book_folder / 'metadata.json', 'w', encoding='utf-8') as f:
                    json.dump(book, f, indent=2)
                
                # Write description.txt
                if book.get('description'):
                    with open(book_folder / 'description.txt', 'w', encoding='utf-8') as f:
                        f.write(book['description'])
                
                # Write keywords.txt
                keywords = book.get('keywords', {}).get('backend_keywords', [])
                if keywords:
                    with open(book_folder / 'keywords.txt', 'w', encoding='utf-8') as f:
                        f.write('\n'.join(keywords))
                
                # Write categories.txt
                categories = book.get('categories', {}).get('suggested_categories', [])
                if categories:
                    with open(book_folder / 'categories.txt', 'w', encoding='utf-8') as f:
                        f.write('\n'.join(categories))
                
                # Write pricing.txt
                pricing = book.get('pricing', {})
                if pricing:
                    with open(book_folder / 'pricing.txt', 'w', encoding='utf-8') as f:
                        f.write(f"Suggested Price: ${pricing.get('suggested_price', 'N/A')}\n")
                        f.write(f"Royalty Rate: {pricing.get('royalty_at_suggested', {}).get('royalty_rate', 'N/A')}\n")
                        f.write(f"Royalty Per Sale: ${pricing.get('royalty_at_suggested', {}).get('royalty_per_sale', 'N/A')}\n")
                
                results['created'].append({
                    'title': title,
                    'folder': str(book_folder)
                })
                
            except Exception as e:
                results['failed'].append({
                    'title': book.get('title', 'unknown'),
                    'error': str(e)
                })
        
        return results


class DeploymentQueue:
    """Manages KDP deployment queue with approval workflow."""
    
    def __init__(self, db_path: str = None):
        self.queue = []
        self.history = []
        self.db_path = db_path or str(Path.home() / '.author_studio' / 'deployment_queue.json')
        self._load()
    
    def _load(self):
        """Load queue from disk."""
        try:
            if Path(self.db_path).exists():
                with open(self.db_path, 'r') as f:
                    data = json.load(f)
                    self.queue = data.get('queue', [])
                    self.history = data.get('history', [])
        except:
            pass
    
    def _save(self):
        """Save queue to disk."""
        try:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            with open(self.db_path, 'w') as f:
                json.dump({'queue': self.queue, 'history': self.history}, f, indent=2)
        except:
            pass
    
    def add_to_queue(self, book_id: int, title: str, changes: Dict) -> str:
        """
        Add a book to the deployment queue.
        
        Args:
            book_id: Database book ID
            title: Book title
            changes: Dict of changes to make (description, keywords, price, etc.)
            
        Returns:
            Queue item ID
        """
        item_id = f"deploy_{book_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        item = {
            'id': item_id,
            'book_id': book_id,
            'title': title,
            'changes': changes,
            'status': 'pending',  # pending, approved, rejected, deployed, failed
            'created_at': datetime.now().isoformat(),
            'approved_at': None,
            'deployed_at': None,
            'error': None
        }
        
        self.queue.append(item)
        self._save()
        
        return item_id
    
    def approve(self, item_id: str) -> bool:
        """Approve a queued item for deployment."""
        for item in self.queue:
            if item['id'] == item_id:
                item['status'] = 'approved'
                item['approved_at'] = datetime.now().isoformat()
                self._save()
                return True
        return False
    
    def reject(self, item_id: str, reason: str = None) -> bool:
        """Reject a queued item."""
        for item in self.queue:
            if item['id'] == item_id:
                item['status'] = 'rejected'
                item['error'] = reason
                self._save()
                return True
        return False
    
    def approve_all(self) -> int:
        """Approve all pending items."""
        count = 0
        for item in self.queue:
            if item['status'] == 'pending':
                item['status'] = 'approved'
                item['approved_at'] = datetime.now().isoformat()
                count += 1
        self._save()
        return count
    
    def get_pending(self) -> List[Dict]:
        """Get all pending items."""
        return [i for i in self.queue if i['status'] == 'pending']
    
    def get_approved(self) -> List[Dict]:
        """Get all approved items ready for deployment."""
        return [i for i in self.queue if i['status'] == 'approved']
    
    def mark_deployed(self, item_id: str) -> bool:
        """Mark an item as successfully deployed."""
        for item in self.queue:
            if item['id'] == item_id:
                item['status'] = 'deployed'
                item['deployed_at'] = datetime.now().isoformat()
                # Move to history
                self.history.append(item)
                self.queue.remove(item)
                self._save()
                return True
        return False
    
    def mark_failed(self, item_id: str, error: str) -> bool:
        """Mark an item as failed."""
        for item in self.queue:
            if item['id'] == item_id:
                item['status'] = 'failed'
                item['error'] = error
                self._save()
                return True
        return False
    
    def get_queue_summary(self) -> Dict:
        """Get summary of queue status."""
        return {
            'pending': len([i for i in self.queue if i['status'] == 'pending']),
            'approved': len([i for i in self.queue if i['status'] == 'approved']),
            'rejected': len([i for i in self.queue if i['status'] == 'rejected']),
            'failed': len([i for i in self.queue if i['status'] == 'failed']),
            'deployed_total': len(self.history),
            'total_in_queue': len(self.queue)
        }
    
    def clear_completed(self):
        """Remove deployed and rejected items from queue."""
        self.queue = [i for i in self.queue if i['status'] in ('pending', 'approved', 'failed')]
        self._save()
