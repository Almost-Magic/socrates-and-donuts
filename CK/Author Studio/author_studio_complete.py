"""
Author Studio - Complete Edition (Phases 1-5)
Linear/Vercel Style UI

Main Tabs: Library | Metadata | Keywords | Quality | Marketing | Analytics | Muse | Business | Export

Marketing: BookTok | Instagram | Scheduler | Email (Listmonk) | Promo Sites | Amazon Ads | Reviews
Analytics: Sentiment | Keyword Rank | Competitors | Reader Avatar | What Changed | LinkedIn
Muse: Dashboard | Inbox Monitor | File Watcher | Idea Generator | Pattern Lab | Content Calendar
Business: Backlist | Series Bible | Characters | KDP Export | Rights | ARIA
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import re
import os
import threading
import imaplib
import email
from email.header import decode_header
from pathlib import Path
from datetime import datetime, timedelta
import csv
import webbrowser
import hashlib
import time

class AuthorStudio:
    def __init__(self, root):
        self.root = root
        self.root.title("Author Studio")
        self.root.geometry("1500x950")
        
        # Linear/Vercel Design System
        self.colors = {
            'bg': '#000000',
            'surface': '#0A0A0A',
            'surface_hover': '#111111',
            'surface_raised': '#141414',
            'border': '#1A1A1A',
            'border_focus': '#333333',
            'text': '#EDEDED',
            'text_secondary': '#888888',
            'text_muted': '#555555',
            'accent': '#7C3AED',
            'accent_hover': '#6D28D9',
            'accent_subtle': '#7C3AED22',
            'success': '#10B981',
            'warning': '#F59E0B',
            'error': '#EF4444',
            'blue': '#3B82F6',
            'cyan': '#06B6D4',
        }
        
        self.root.configure(bg=self.colors['bg'])
        
        # Data stores
        self.books = []
        self.current_book = None
        self.scheduled_posts = []
        self.keyword_history = {}
        self.competitors = []
        self.reader_avatars = []
        self.snapshots = {}
        self.linkedin_campaigns = []
        
        # Muse data
        self.muse_ideas = []
        self.muse_inbox_items = []
        self.muse_file_changes = []
        self.muse_patterns = []
        self.muse_watching = False
        self.muse_inbox_monitoring = False
        self.watch_folders = []
        self.file_hashes = {}
        self.muse_scan_interval = 300  # 5 minutes
        
        # Phase 5 - Business data
        self.royalties = []
        self.series_data = []
        self.characters = []
        self.rights = []
        self.aria_reports = []
        
        self.imap_config = {
            'server': '', 'port': 993, 'email': '', 'password': '',
            'folder': 'INBOX', 'keywords': ['book', 'writing', 'publish', 'author', 'review',
                                             'manuscript', 'reader', 'amazon', 'kindle', 'AI',
                                             'cybersecurity', 'consulting', 'client']
        }
        
        self.listmonk_config = {
            'url': 'http://localhost:9000', 'username': 'admin', 'password': '', 'lists': []
        }
        
        self.promo_sites = [
            {'name': 'BookBub', 'url': 'https://partners.bookbub.com', 'genres': 'All', 'cost': 'Paid', 'lead_days': 30},
            {'name': 'Freebooksy', 'url': 'https://www.freebooksy.com/for-authors/', 'genres': 'All', 'cost': '$80-160', 'lead_days': 14},
            {'name': 'Bargain Booksy', 'url': 'https://www.bargainbooksy.com/for-authors/', 'genres': 'All', 'cost': '$40-80', 'lead_days': 14},
            {'name': 'Robin Reads', 'url': 'https://robinreads.com/submit/', 'genres': 'All', 'cost': '$30-60', 'lead_days': 7},
            {'name': 'Book Gorilla', 'url': 'https://www.bookgorilla.com/advertise', 'genres': 'All', 'cost': '$50-75', 'lead_days': 7},
            {'name': 'eReader News Today', 'url': 'https://ereadernewstoday.com/bargain-ebook-submission/', 'genres': 'All', 'cost': '$30-150', 'lead_days': 14},
            {'name': 'Book Barbarian', 'url': 'https://www.bookbarbarian.com/for-authors/', 'genres': 'SFF', 'cost': '$10-20', 'lead_days': 7},
            {'name': 'Fussy Librarian', 'url': 'https://www.thefussylibrarian.com/promote-your-book', 'genres': 'All', 'cost': '$12-52', 'lead_days': 3},
            {'name': 'BookSends', 'url': 'https://booksends.com/advertise/', 'genres': 'All', 'cost': '$10-50', 'lead_days': 3},
            {'name': 'Written Word Media', 'url': 'https://www.writtenwordmedia.com/', 'genres': 'All', 'cost': '$20-200', 'lead_days': 7},
        ]
        
        # File paths
        self.data_dir = Path.home() / '.author_studio'
        self.data_dir.mkdir(exist_ok=True)
        self.data_file = self.data_dir / 'books.json'
        self.schedule_file = self.data_dir / 'schedule.json'
        self.config_file = self.data_dir / 'config.json'
        self.analytics_file = self.data_dir / 'analytics.json'
        self.linkedin_file = self.data_dir / 'linkedin.json'
        self.muse_file = self.data_dir / 'muse.json'
        self.business_file = self.data_dir / 'business.json'
        
        self.load_data()
        self.setup_styles()
        self.create_ui()
        
        # Clean shutdown
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
    def on_close(self):
        self.muse_watching = False
        self.muse_inbox_monitoring = False
        self.save_muse_data()
        self.root.destroy()
        
    # ═══════════════════════════════════════════════════════════════
    # STYLES
    # ═══════════════════════════════════════════════════════════════
    
    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=self.colors['bg'])
        
        for name, cfg in {
            'TLabel': {'fg': self.colors['text'], 'font': ('SF Pro Display', 11)},
            'Title.TLabel': {'fg': self.colors['text'], 'font': ('SF Pro Display', 24, 'bold')},
            'Heading.TLabel': {'fg': self.colors['text'], 'font': ('SF Pro Display', 14, 'bold')},
            'Subtitle.TLabel': {'fg': self.colors['text_secondary'], 'font': ('SF Pro Display', 13)},
            'Muted.TLabel': {'fg': self.colors['text_muted'], 'font': ('SF Pro Display', 10)},
            'Success.TLabel': {'fg': self.colors['success'], 'font': ('SF Pro Display', 11)},
            'Warning.TLabel': {'fg': self.colors['warning'], 'font': ('SF Pro Display', 11)},
            'Error.TLabel': {'fg': self.colors['error'], 'font': ('SF Pro Display', 11)},
            'Accent.TLabel': {'fg': self.colors['accent'], 'font': ('SF Pro Display', 11)},
            'Blue.TLabel': {'fg': self.colors['blue'], 'font': ('SF Pro Display', 11)},
            'Cyan.TLabel': {'fg': self.colors['cyan'], 'font': ('SF Pro Display', 11)},
        }.items():
            style.configure(name, background=self.colors['bg'], foreground=cfg['fg'], font=cfg['font'])
        
        style.configure('TButton', background=self.colors['surface'], foreground=self.colors['text'],
                       font=('SF Pro Display', 11), borderwidth=0, padding=(16, 10))
        style.map('TButton', background=[('active', self.colors['surface_hover'])])
        style.configure('Accent.TButton', background=self.colors['accent'], foreground='#FFFFFF',
                       font=('SF Pro Display', 11, 'bold'), borderwidth=0, padding=(20, 12))
        style.map('Accent.TButton', background=[('active', self.colors['accent_hover'])])
        style.configure('Ghost.TButton', background=self.colors['bg'], foreground=self.colors['text_secondary'],
                       font=('SF Pro Display', 11), borderwidth=0, padding=(12, 8))
        style.map('Ghost.TButton', foreground=[('active', self.colors['text'])])
        style.configure('Small.TButton', background=self.colors['surface'], foreground=self.colors['text_secondary'],
                       font=('SF Pro Display', 9), borderwidth=0, padding=(10, 6))
        
        style.configure('TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('TNotebook.Tab', background=self.colors['bg'], foreground=self.colors['text_muted'],
                       font=('SF Pro Display', 11), padding=(20, 12), borderwidth=0)
        style.map('TNotebook.Tab', background=[('selected', self.colors['bg'])],
                 foreground=[('selected', self.colors['text'])])
        style.configure('Sub.TNotebook', background=self.colors['bg'], borderwidth=0)
        style.configure('Sub.TNotebook.Tab', background=self.colors['bg'], foreground=self.colors['text_muted'],
                       font=('SF Pro Display', 10), padding=(14, 8), borderwidth=0)
        style.map('Sub.TNotebook.Tab', background=[('selected', self.colors['bg'])],
                 foreground=[('selected', self.colors['accent'])])
        
        style.configure('Treeview', background=self.colors['surface'], foreground=self.colors['text'],
                       fieldbackground=self.colors['surface'], borderwidth=0, font=('SF Pro Display', 11), rowheight=32)
        style.configure('Treeview.Heading', background=self.colors['bg'], foreground=self.colors['text_muted'],
                       font=('SF Pro Display', 10), borderwidth=0)
        style.map('Treeview', background=[('selected', self.colors['accent'])], foreground=[('selected', '#FFFFFF')])
    
    # ═══════════════════════════════════════════════════════════════
    # UI HELPERS
    # ═══════════════════════════════════════════════════════════════
    
    def create_entry(self, parent, variable=None, width=None):
        frame = tk.Frame(parent, bg=self.colors['border'], padx=1, pady=1)
        entry = tk.Entry(frame, textvariable=variable, bg=self.colors['surface'],
                        fg=self.colors['text'], insertbackground=self.colors['text'],
                        font=('SF Pro Display', 11), borderwidth=0, highlightthickness=0)
        if width: entry.configure(width=width)
        entry.pack(fill='x', padx=8, pady=8)
        entry.bind('<FocusIn>', lambda e: frame.configure(bg=self.colors['border_focus']))
        entry.bind('<FocusOut>', lambda e: frame.configure(bg=self.colors['border']))
        return frame
    
    def create_text_area(self, parent, height=10):
        frame = tk.Frame(parent, bg=self.colors['border'], padx=1, pady=1)
        text = tk.Text(frame, bg=self.colors['surface'], fg=self.colors['text'],
                      insertbackground=self.colors['text'], font=('SF Mono', 11),
                      height=height, wrap='word', borderwidth=0, highlightthickness=0, padx=12, pady=10)
        text.pack(fill='both', expand=True)
        text.bind('<FocusIn>', lambda e: frame.configure(bg=self.colors['border_focus']))
        text.bind('<FocusOut>', lambda e: frame.configure(bg=self.colors['border']))
        return text
    
    def create_card(self, parent, padding=16):
        return tk.Frame(parent, bg=self.colors['surface'], padx=padding, pady=padding)
    
    def create_radio_row(self, parent, label, variable, options, bg=None):
        frame = ttk.Frame(parent) if bg is None else tk.Frame(parent, bg=bg)
        bg_c = bg or self.colors['bg']
        tk.Label(frame, text=label, bg=bg_c, fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left')
        for text, val in options:
            tk.Radiobutton(frame, text=text, variable=variable, value=val, bg=bg_c,
                          fg=self.colors['text_secondary'], selectcolor=self.colors['surface'],
                          activebackground=bg_c, font=('SF Pro Display', 10),
                          borderwidth=0, highlightthickness=0).pack(side='left', padx=(12, 0))
        return frame
    
    def gt(self, w): return w.get('1.0', 'end-1c').strip()
    def st(self, w, t): w.delete('1.0', 'end'); w.insert('1.0', t)
    def cp(self, w):
        t = self.gt(w) if not isinstance(w, str) else w
        if t: self.root.clipboard_clear(); self.root.clipboard_append(t)
    def gb(self):
        if self.current_book is not None and self.current_book < len(self.books): return self.books[self.current_book]
        return {'title': 'Your Book', 'author': 'Mani Padisetti', 'description': '', 'keywords': []}
    def gbt(self): return self.gb().get('title', 'Your Book')
    
    # ═══════════════════════════════════════════════════════════════
    # MAIN UI
    # ═══════════════════════════════════════════════════════════════
    
    def create_ui(self):
        main = ttk.Frame(self.root, padding=30)
        main.pack(fill='both', expand=True)
        header = ttk.Frame(main); header.pack(fill='x', pady=(0, 24))
        ttk.Label(header, text="Author Studio", style='Title.TLabel').pack(side='left')
        ttk.Label(header, text=f"{len(self.books)} books", style='Subtitle.TLabel').pack(side='left', padx=(20, 0), pady=(8, 0))
        
        # Muse status indicator in header
        self.muse_indicator = ttk.Label(header, text="⬤ Muse: Off", style='Muted.TLabel')
        self.muse_indicator.pack(side='right', padx=(0, 10))
        
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill='both', expand=True)
        
        self.create_library_tab()
        self.create_metadata_tab()
        self.create_keywords_tab()
        self.create_quality_tab()
        self.create_marketing_tab()
        self.create_analytics_tab()
        self.create_muse_tab()
        self.create_business_tab()
        self.create_export_tab()
    
    # ═══════════════════════════════════════════════════════════════
    # LIBRARY TAB
    # ═══════════════════════════════════════════════════════════════
    
    def create_library_tab(self):
        tab = ttk.Frame(self.notebook, padding=20); self.notebook.add(tab, text='  Library  ')
        actions = ttk.Frame(tab); actions.pack(fill='x', pady=(0, 20))
        ttk.Button(actions, text="Add book", style='Accent.TButton', command=self.add_book).pack(side='left')
        ttk.Button(actions, text="Import folder", style='Ghost.TButton', command=self.import_folder).pack(side='left', padx=(12, 0))
        ttk.Button(actions, text="Import CSV", style='Ghost.TButton', command=self.import_csv).pack(side='left', padx=(12, 0))
        ttk.Button(actions, text="Delete", style='Ghost.TButton', command=self.delete_book).pack(side='left', padx=(12, 0))
        sf = ttk.Frame(actions); sf.pack(side='right')
        self.search_var = tk.StringVar(); self.search_var.trace('w', lambda *a: self.refresh_book_list())
        self.create_entry(sf, self.search_var, width=30).pack(side='left')
        
        lf = ttk.Frame(tab); lf.pack(fill='both', expand=True)
        cols = ('title', 'author', 'status', 'quality')
        self.book_tree = ttk.Treeview(lf, columns=cols, show='headings', height=20)
        for c, w in [('title', 450), ('author', 200), ('status', 120), ('quality', 100)]:
            self.book_tree.heading(c, text=c.title()); self.book_tree.column(c, width=w)
        self.book_tree.pack(side='left', fill='both', expand=True)
        self.book_tree.bind('<<TreeviewSelect>>', self.on_book_select)
        self.book_tree.bind('<Double-1>', lambda e: self.notebook.select(1))
        self.refresh_book_list()
    
    # ═══════════════════════════════════════════════════════════════
    # METADATA TAB
    # ═══════════════════════════════════════════════════════════════
    
    def create_metadata_tab(self):
        tab = ttk.Frame(self.notebook, padding=20); self.notebook.add(tab, text='  Metadata  ')
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 20))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        
        ttk.Label(left, text="Book Details", style='Heading.TLabel').pack(anchor='w', pady=(0, 20))
        self.meta_vars = {}
        for label in ['Title', 'Subtitle', 'Author', 'Series', 'ASIN']:
            ttk.Label(left, text=label, style='Muted.TLabel').pack(anchor='w', pady=(0, 4))
            var = tk.StringVar(); self.meta_vars[label.lower()] = var
            self.create_entry(left, var).pack(fill='x', pady=(0, 12))
        
        ttk.Label(right, text="Description", style='Heading.TLabel').pack(anchor='w', pady=(0, 20))
        self.description_text = self.create_text_area(right, height=12)
        self.description_text.pack(fill='both', expand=True)
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(20, 0), side='bottom')
        ttk.Button(bf, text="Save metadata", style='Accent.TButton', command=self.save_metadata).pack(side='right')
    
    # ═══════════════════════════════════════════════════════════════
    # KEYWORDS TAB
    # ═══════════════════════════════════════════════════════════════
    
    def create_keywords_tab(self):
        tab = ttk.Frame(self.notebook, padding=20); self.notebook.add(tab, text='  Keywords  ')
        ttk.Label(tab, text="7 keyword phrases, 50 chars each", style='Subtitle.TLabel').pack(anchor='w', pady=(0, 20))
        self.keyword_vars = []
        for i in range(7):
            row = ttk.Frame(tab); row.pack(fill='x', pady=(0, 10))
            ttk.Label(row, text=f"{i+1}", style='Muted.TLabel', width=3).pack(side='left')
            var = tk.StringVar(); self.keyword_vars.append(var)
            self.create_entry(row, var).pack(side='left', fill='x', expand=True, padx=(8, 0))
            cl = ttk.Label(row, text="0/50", style='Muted.TLabel', width=6); cl.pack(side='right', padx=(8, 0))
            var.trace('w', lambda *a, v=var, l=cl: l.configure(text=f"{len(v.get())}/50",
                     style='Error.TLabel' if len(v.get()) > 50 else 'Muted.TLabel'))
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(20, 0))
        ttk.Button(bf, text="Save", style='Accent.TButton', command=self.save_keywords).pack(side='right')
    
    # ═══════════════════════════════════════════════════════════════
    # QUALITY TAB
    # ═══════════════════════════════════════════════════════════════
    
    def create_quality_tab(self):
        tab = ttk.Frame(self.notebook, padding=20); self.notebook.add(tab, text='  Quality  ')
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 20))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Check Content Quality", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.quality_input = self.create_text_area(left, height=15); self.quality_input.pack(fill='both', expand=True)
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(12, 0))
        ttk.Button(bf, text="Check quality", style='Accent.TButton', command=self.check_quality).pack(side='left')
        ttk.Button(bf, text="Load file", style='Ghost.TButton', command=self.load_manuscript).pack(side='left', padx=(12, 0))
        ttk.Label(right, text="Report", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        sf = ttk.Frame(right); sf.pack(fill='x', pady=(0, 16))
        self.ai_score_label = ttk.Label(sf, text="AI: --"); self.ai_score_label.pack(side='left')
        self.quality_score_label = ttk.Label(sf, text="Quality: --"); self.quality_score_label.pack(side='left', padx=(40, 0))
        self.quality_output = self.create_text_area(right, height=12); self.quality_output.pack(fill='both', expand=True)
    
    # ═══════════════════════════════════════════════════════════════
    # MARKETING TAB (PHASE 3)
    # ═══════════════════════════════════════════════════════════════
    
    def create_marketing_tab(self):
        tab = ttk.Frame(self.notebook, padding=10); self.notebook.add(tab, text='  Marketing  ')
        self.mkt_nb = ttk.Notebook(tab, style='Sub.TNotebook')
        self.mkt_nb.pack(fill='both', expand=True, pady=(10, 0))
        for name, builder in [('BookTok', self._mkt_booktok), ('Instagram', self._mkt_instagram),
                              ('Scheduler', self._mkt_scheduler), ('Email', self._mkt_email),
                              ('Promo Sites', self._mkt_promo), ('Amazon Ads', self._mkt_ads), ('Reviews', self._mkt_reviews)]:
            t = ttk.Frame(self.mkt_nb, padding=16); self.mkt_nb.add(t, text=f'  {name}  '); builder(t)

    def _mkt_booktok(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="BookTok Script Generator", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.booktok_type = tk.StringVar(value='hook')
        self.create_radio_row(left, "Format", self.booktok_type, [('Hook', 'hook'), ('Review', 'review'), ('Vlog', 'vlog'), ('Rec', 'rec'), ('BTS', 'bts')]).pack(fill='x', pady=(0, 12))
        self.booktok_dur = tk.StringVar(value='30')
        self.create_radio_row(left, "Duration", self.booktok_dur, [('15s', '15'), ('30s', '30'), ('60s', '60')]).pack(fill='x', pady=(0, 12))
        self.booktok_ctx = self.create_text_area(left, height=4); self.booktok_ctx.pack(fill='x')
        ttk.Button(left, text="Generate", style='Accent.TButton', command=self.gen_booktok).pack(anchor='w', pady=(12, 0))
        self.booktok_out = self.create_text_area(right, height=18); self.booktok_out.pack(fill='both', expand=True)
        ttk.Button(right, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.booktok_out)).pack(anchor='w', pady=(8, 0))

    def _mkt_instagram(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Instagram Post Generator", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.insta_type = tk.StringVar(value='single')
        self.create_radio_row(left, "Type", self.insta_type, [('Post', 'single'), ('Carousel', 'carousel'), ('Reel', 'reel'), ('Story', 'story')]).pack(fill='x', pady=(0, 12))
        self.insta_theme = tk.StringVar(value='promo')
        self.create_radio_row(left, "Theme", self.insta_theme, [('Promo', 'promo'), ('Life', 'life'), ('Tips', 'tips'), ('Quote', 'quote')]).pack(fill='x', pady=(0, 12))
        self.insta_notes = self.create_text_area(left, height=3); self.insta_notes.pack(fill='x')
        self.hashtag_count = tk.StringVar(value='15')
        self.create_radio_row(left, "Hashtags", self.hashtag_count, [('5','5'),('10','10'),('15','15'),('30','30')]).pack(fill='x', pady=(12, 0))
        ttk.Button(left, text="Generate", style='Accent.TButton', command=self.gen_instagram).pack(anchor='w', pady=(16, 0))
        self.insta_out = self.create_text_area(right, height=18); self.insta_out.pack(fill='both', expand=True)
        ttk.Button(right, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.insta_out)).pack(anchor='w', pady=(8, 0))

    def _mkt_scheduler(self, tab):
        ttk.Label(tab, text="Social Media Scheduler", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        form = self.create_card(tab); form.pack(fill='x', pady=(0, 16))
        r1 = tk.Frame(form, bg=self.colors['surface']); r1.pack(fill='x', pady=(0, 8))
        self.sched_platform = tk.StringVar(value='Instagram')
        for p in ['Instagram', 'TikTok', 'X/Twitter', 'LinkedIn', 'Facebook']:
            tk.Radiobutton(r1, text=p, variable=self.sched_platform, value=p, bg=self.colors['surface'],
                          fg=self.colors['text_secondary'], selectcolor=self.colors['surface_raised'],
                          activebackground=self.colors['surface'], font=('SF Pro Display', 10), borderwidth=0, highlightthickness=0).pack(side='left', padx=(8, 0))
        r2 = tk.Frame(form, bg=self.colors['surface']); r2.pack(fill='x', pady=(0, 8))
        self.sched_date = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.sched_time = tk.StringVar(value='10:00')
        for lbl, var, w in [("Date", self.sched_date, 14), ("Time", self.sched_time, 8)]:
            tk.Label(r2, text=lbl, bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left', padx=(8, 0))
            tk.Entry(r2, textvariable=var, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 11), borderwidth=0, width=w).pack(side='left', padx=(4, 0))
        self.sched_content = tk.Text(form, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Mono', 10), height=3, wrap='word', borderwidth=0, padx=8, pady=6)
        self.sched_content.pack(fill='x', pady=(4, 8))
        ttk.Button(form, text="Add", style='Accent.TButton', command=self.add_sched_post).pack(anchor='w')
        cols = ('date', 'time', 'platform', 'content', 'status')
        self.sched_tree = ttk.Treeview(tab, columns=cols, show='headings', height=8)
        for c, w in [('date', 100), ('time', 60), ('platform', 100), ('content', 480), ('status', 80)]:
            self.sched_tree.heading(c, text=c.title()); self.sched_tree.column(c, width=w)
        self.sched_tree.pack(fill='both', expand=True)
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(8, 0))
        ttk.Button(bf, text="Delete", style='Ghost.TButton', command=self.del_sched).pack(side='left')
        ttk.Button(bf, text="Mark posted", style='Ghost.TButton', command=self.mark_posted).pack(side='left', padx=(8, 0))
        self.refresh_schedule()

    def _mkt_email(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Listmonk Integration", style='Heading.TLabel').pack(anchor='w', pady=(0, 12))
        cc = self.create_card(left); cc.pack(fill='x', pady=(0, 12))
        self.listmonk_url = tk.StringVar(value=self.listmonk_config['url'])
        self.listmonk_user = tk.StringVar(value=self.listmonk_config['username'])
        self.listmonk_pass = tk.StringVar(value=self.listmonk_config['password'])
        for lbl, var, sh in [("URL", self.listmonk_url, None), ("User", self.listmonk_user, None), ("Pass", self.listmonk_pass, '•')]:
            r = tk.Frame(cc, bg=self.colors['surface']); r.pack(fill='x', pady=2)
            tk.Label(r, text=lbl, bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10), width=6).pack(side='left')
            e = tk.Entry(r, textvariable=var, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 10), borderwidth=0, width=28)
            if sh: e.configure(show=sh)
            e.pack(side='left', padx=(4, 0))
        br = tk.Frame(cc, bg=self.colors['surface']); br.pack(fill='x', pady=(8, 0))
        ttk.Button(br, text="Test", style='Small.TButton', command=self.test_listmonk).pack(side='left')
        ttk.Button(br, text="Save", style='Small.TButton', command=self.save_lm_config).pack(side='left', padx=(8, 0))
        self.lm_status = ttk.Label(left, text="Not connected", style='Muted.TLabel'); self.lm_status.pack(anchor='w', pady=(0, 12))
        self.email_type = tk.StringVar(value='launch')
        for t, v in [('Book Launch', 'launch'), ('Newsletter', 'newsletter'), ('ARC', 'arc'), ('Sale', 'sale'), ('Magnet', 'magnet'), ('Series', 'series')]:
            tk.Radiobutton(left, text=t, variable=self.email_type, value=v, bg=self.colors['bg'], fg=self.colors['text_secondary'], selectcolor=self.colors['surface'], activebackground=self.colors['bg'], font=('SF Pro Display', 10), borderwidth=0, highlightthickness=0).pack(anchor='w', pady=2)
        ttk.Button(left, text="Generate", style='Accent.TButton', command=self.gen_email).pack(anchor='w', pady=(12, 0))
        self.email_subj = self.create_text_area(right, height=2); self.email_subj.pack(fill='x', pady=(0, 12))
        self.email_body = self.create_text_area(right, height=14); self.email_body.pack(fill='both', expand=True)
        ttk.Button(right, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.email_body)).pack(anchor='w', pady=(8, 0))

    def _mkt_promo(self, tab):
        ttk.Label(tab, text="Book Promotion Sites", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        cols = ('name', 'genres', 'cost', 'lead_days')
        self.promo_tree = ttk.Treeview(tab, columns=cols, show='headings', height=10)
        for c, w in [('name', 200), ('genres', 120), ('cost', 120), ('lead_days', 100)]:
            self.promo_tree.heading(c, text=c.replace('_', ' ').title()); self.promo_tree.column(c, width=w)
        self.promo_tree.pack(fill='both', expand=True)
        for i, s in enumerate(self.promo_sites):
            self.promo_tree.insert('', 'end', iid=str(i), values=(s['name'], s['genres'], s['cost'], f"{s['lead_days']}d"))
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(12, 0))
        ttk.Button(bf, text="Open site", style='Accent.TButton', command=self.open_promo).pack(side='left')
        ttk.Button(bf, text="Promo calendar", style='Ghost.TButton', command=self.promo_calendar).pack(side='left', padx=(12, 0))
        self.promo_out = self.create_text_area(tab, height=4); self.promo_out.pack(fill='x', pady=(12, 0))

    def _mkt_ads(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Amazon Ad Copy", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.ad_type = tk.StringVar(value='sponsored')
        self.create_radio_row(left, "Type", self.ad_type, [('Sponsored', 'sponsored'), ('Lockscreen', 'lockscreen'), ('Display', 'display')]).pack(fill='x', pady=(0, 12))
        self.ad_target = self.create_text_area(left, height=3); self.ad_target.pack(fill='x')
        self.ad_comps = self.create_text_area(left, height=3); self.ad_comps.pack(fill='x', pady=(8, 0))
        self.ad_vars = tk.StringVar(value='3')
        self.create_radio_row(left, "Variations", self.ad_vars, [('1','1'),('3','3'),('5','5'),('10','10')]).pack(fill='x', pady=(12, 0))
        ttk.Button(left, text="Generate", style='Accent.TButton', command=self.gen_ads).pack(anchor='w', pady=(12, 0))
        self.ads_out = self.create_text_area(right, height=20); self.ads_out.pack(fill='both', expand=True)
        ttk.Button(right, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.ads_out)).pack(anchor='w', pady=(8, 0))

    def _mkt_reviews(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Review Request Templates", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.review_type = tk.StringVar(value='arc_invite')
        for t, v in [('ARC Invite', 'arc_invite'), ('Post-Purchase', 'post_purchase'), ('Newsletter', 'newsletter'), ('Social', 'social'), ('Back of Book', 'back_of_book'), ('Follow-Up', 'followup')]:
            tk.Radiobutton(left, text=t, variable=self.review_type, value=v, bg=self.colors['bg'], fg=self.colors['text_secondary'], selectcolor=self.colors['surface'], activebackground=self.colors['bg'], font=('SF Pro Display', 10), borderwidth=0, highlightthickness=0).pack(anchor='w', pady=2)
        self.review_tone = tk.StringVar(value='warm')
        self.create_radio_row(left, "Tone", self.review_tone, [('Warm', 'warm'), ('Pro', 'pro'), ('Casual', 'casual')]).pack(fill='x', pady=(16, 0))
        ttk.Button(left, text="Generate", style='Accent.TButton', command=self.gen_review).pack(anchor='w', pady=(16, 0))
        self.review_out = self.create_text_area(right, height=20); self.review_out.pack(fill='both', expand=True)
        ttk.Button(right, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.review_out)).pack(anchor='w', pady=(8, 0))
    
    # ═══════════════════════════════════════════════════════════════
    # ANALYTICS TAB (PHASE 4)
    # ═══════════════════════════════════════════════════════════════
    
    def create_analytics_tab(self):
        tab = ttk.Frame(self.notebook, padding=10); self.notebook.add(tab, text='  Analytics  ')
        self.ana_nb = ttk.Notebook(tab, style='Sub.TNotebook')
        self.ana_nb.pack(fill='both', expand=True, pady=(10, 0))
        for name, builder in [('Sentiment', self._ana_sentiment), ('Keyword Rank', self._ana_keywords),
                              ('Competitors', self._ana_competitors), ('Reader Avatar', self._ana_avatar),
                              ('What Changed?', self._ana_whatchanged), ('LinkedIn', self._ana_linkedin)]:
            t = ttk.Frame(self.ana_nb, padding=16); self.ana_nb.add(t, text=f'  {name}  '); builder(t)

    def _ana_sentiment(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Review Sentiment Analyser", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.sentiment_input = self.create_text_area(left, height=14); self.sentiment_input.pack(fill='both', expand=True)
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(12, 0))
        ttk.Button(bf, text="Analyse", style='Accent.TButton', command=self.analyse_sentiment).pack(side='left')
        ttk.Button(bf, text="AI prompt", style='Ghost.TButton', command=self.gen_sent_prompt).pack(side='left', padx=(12, 0))
        sf = ttk.Frame(right); sf.pack(fill='x', pady=(0, 12))
        self.sent_pos = ttk.Label(sf, text="Pos: --", style='Success.TLabel'); self.sent_pos.pack(side='left')
        self.sent_neu = ttk.Label(sf, text="Neu: --", style='Muted.TLabel'); self.sent_neu.pack(side='left', padx=(24, 0))
        self.sent_neg = ttk.Label(sf, text="Neg: --", style='Error.TLabel'); self.sent_neg.pack(side='left', padx=(24, 0))
        self.sentiment_out = self.create_text_area(right, height=16); self.sentiment_out.pack(fill='both', expand=True)

    def _ana_keywords(self, tab):
        ttk.Label(tab, text="Keyword Rank Tracker", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        af = self.create_card(tab); af.pack(fill='x', pady=(0, 16))
        r = tk.Frame(af, bg=self.colors['surface']); r.pack(fill='x')
        self.track_kw = tk.StringVar(); self.track_pos = tk.StringVar()
        for lbl, var, w in [("Keyword", self.track_kw, 30), ("Position", self.track_pos, 6)]:
            tk.Label(r, text=lbl, bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left', padx=(8, 0))
            tk.Entry(r, textvariable=var, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 11), borderwidth=0, width=w).pack(side='left', padx=(4, 0))
        ttk.Button(af, text="Log", style='Accent.TButton', command=self.log_kw_pos).pack(anchor='w', pady=(8, 0))
        cols = ('date', 'keyword', 'position', 'change')
        self.kw_tree = ttk.Treeview(tab, columns=cols, show='headings', height=12)
        for c, w in [('date', 120), ('keyword', 300), ('position', 100), ('change', 100)]:
            self.kw_tree.heading(c, text=c.title()); self.kw_tree.column(c, width=w)
        self.kw_tree.pack(fill='both', expand=True); self.refresh_kw_history()

    def _ana_competitors(self, tab):
        ttk.Label(tab, text="Competitor Tracker", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        af = self.create_card(tab); af.pack(fill='x', pady=(0, 16))
        r = tk.Frame(af, bg=self.colors['surface']); r.pack(fill='x')
        self.comp_title = tk.StringVar(); self.comp_asin = tk.StringVar(); self.comp_price = tk.StringVar(); self.comp_rank = tk.StringVar()
        for lbl, var, w in [("Title", self.comp_title, 25), ("ASIN", self.comp_asin, 12), ("Price", self.comp_price, 8), ("Rank", self.comp_rank, 10)]:
            tk.Label(r, text=lbl, bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left', padx=(8, 0))
            tk.Entry(r, textvariable=var, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 10), borderwidth=0, width=w).pack(side='left', padx=(4, 0))
        ttk.Button(af, text="Add", style='Accent.TButton', command=self.add_competitor).pack(anchor='w', pady=(8, 0))
        cols = ('title', 'asin', 'price', 'rank', 'last_updated')
        self.comp_tree = ttk.Treeview(tab, columns=cols, show='headings', height=10)
        for c, w in [('title', 250), ('asin', 120), ('price', 80), ('rank', 100), ('last_updated', 140)]:
            self.comp_tree.heading(c, text=c.replace('_', ' ').title()); self.comp_tree.column(c, width=w)
        self.comp_tree.pack(fill='both', expand=True)
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(8, 0))
        ttk.Button(bf, text="Delete", style='Ghost.TButton', command=self.del_competitor).pack(side='left')
        self.comp_out = self.create_text_area(tab, height=3); self.comp_out.pack(fill='x', pady=(8, 0))
        self.refresh_competitors()

    def _ana_avatar(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Reader Avatar Builder™", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.avatar_fields = {}
        for label, key, hint in [("Name", "name", "e.g. Sarah, 34"), ("Demographics", "demographics", "Age, location"),
                                  ("Reading habits", "reading", "Genres, frequency"), ("Pain points", "pain", "Problems solved"),
                                  ("Desires", "desires", "Feel/achieve"), ("Online", "online", "Platforms"), ("Triggers", "triggers", "Buy signals")]:
            ttk.Label(left, text=f"{label} ({hint})", style='Muted.TLabel').pack(anchor='w', pady=(0, 2))
            var = tk.StringVar(); self.avatar_fields[key] = var
            self.create_entry(left, var).pack(fill='x', pady=(0, 6))
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(8, 0))
        ttk.Button(bf, text="Build", style='Accent.TButton', command=self.build_avatar).pack(side='left')
        ttk.Button(bf, text="AI prompt", style='Ghost.TButton', command=self.gen_avatar_prompt).pack(side='left', padx=(12, 0))
        self.avatar_out = self.create_text_area(right, height=20); self.avatar_out.pack(fill='both', expand=True)

    def _ana_whatchanged(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text='"What Changed?"', style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.wc_fields = {}
        for label, key in [("BSR", "bsr"), ("Reviews", "reviews"), ("Rating", "rating"), ("Price", "price"), ("KENP", "kenp"), ("Sales", "sales")]:
            r = ttk.Frame(left); r.pack(fill='x', pady=(0, 6))
            ttk.Label(r, text=label, style='Muted.TLabel', width=12).pack(side='left')
            var = tk.StringVar(); self.wc_fields[key] = var
            self.create_entry(r, var, width=15).pack(side='left', padx=(8, 0))
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(16, 0))
        ttk.Button(bf, text="Snapshot", style='Accent.TButton', command=self.take_snapshot).pack(side='left')
        ttk.Button(bf, text="Compare", style='Ghost.TButton', command=self.compare_snapshots).pack(side='left', padx=(12, 0))
        self.wc_out = self.create_text_area(right, height=10); self.wc_out.pack(fill='both', expand=True)
        self.snap_tree = ttk.Treeview(right, columns=('date', 'bsr', 'reviews', 'rating', 'price'), show='headings', height=5)
        for c, w in [('date', 140), ('bsr', 100), ('reviews', 80), ('rating', 80), ('price', 80)]:
            self.snap_tree.heading(c, text=c.upper()); self.snap_tree.column(c, width=w)
        self.snap_tree.pack(fill='x', pady=(8, 0)); self.refresh_snapshots()

    def _ana_linkedin(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="LinkedIn Ad Manager", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.li_type = tk.StringVar(value='thought_leader')
        self.create_radio_row(left, "Type", self.li_type, [('Thought Leader', 'thought_leader'), ('Book', 'book_promo'), ('Service', 'service'), ('Event', 'event')]).pack(fill='x', pady=(0, 10))
        self.li_format = tk.StringVar(value='post')
        self.create_radio_row(left, "Format", self.li_format, [('Post', 'post'), ('Article', 'article'), ('Carousel', 'carousel'), ('Video', 'video')]).pack(fill='x', pady=(0, 10))
        ttk.Label(left, text="Audience", style='Muted.TLabel').pack(anchor='w', pady=(0, 2))
        self.li_audience = self.create_text_area(left, height=2); self.li_audience.pack(fill='x', pady=(0, 6))
        ttk.Label(left, text="Objective", style='Muted.TLabel').pack(anchor='w', pady=(0, 2))
        self.li_objective = self.create_text_area(left, height=2); self.li_objective.pack(fill='x', pady=(0, 6))
        self.li_cta = tk.StringVar(value='learn_more')
        self.create_radio_row(left, "CTA", self.li_cta, [('Learn More', 'learn_more'), ('Sign Up', 'sign_up'), ('Download', 'download'), ('Contact', 'contact')]).pack(fill='x', pady=(0, 10))
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(8, 0))
        ttk.Button(bf, text="Generate", style='Accent.TButton', command=self.gen_linkedin).pack(side='left')
        ttk.Button(bf, text="Script", style='Ghost.TButton', command=self.gen_li_script).pack(side='left', padx=(12, 0))
        ttk.Button(bf, text="Hashtags", style='Ghost.TButton', command=self.gen_li_hashtags).pack(side='left', padx=(12, 0))
        self.li_out = self.create_text_area(right, height=20); self.li_out.pack(fill='both', expand=True)
        bf2 = ttk.Frame(right); bf2.pack(fill='x', pady=(8, 0))
        ttk.Button(bf2, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.li_out)).pack(side='left')
        ttk.Button(bf2, text="Save", style='Ghost.TButton', command=self.save_li_campaign).pack(side='left', padx=(8, 0))
    
    # ═══════════════════════════════════════════════════════════════
    # MUSE TAB (Creative Intelligence Engine)
    # ═══════════════════════════════════════════════════════════════
    
    def create_muse_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text='  ✦ Muse  ')
        self.muse_nb = ttk.Notebook(tab, style='Sub.TNotebook')
        self.muse_nb.pack(fill='both', expand=True, pady=(10, 0))
        
        for name, builder in [('Dashboard', self._muse_dashboard), ('Inbox Monitor', self._muse_inbox),
                              ('File Watcher', self._muse_files), ('Idea Generator', self._muse_ideas_tab),
                              ('Pattern Lab', self._muse_patterns_tab), ('Content Calendar', self._muse_calendar)]:
            t = ttk.Frame(self.muse_nb, padding=16); self.muse_nb.add(t, text=f'  {name}  '); builder(t)
    
    # ── Muse Dashboard ──
    
    def _muse_dashboard(self, tab):
        ttk.Label(tab, text="✦ Muse — Creative Intelligence Engine", style='Heading.TLabel').pack(anchor='w', pady=(0, 8))
        ttk.Label(tab, text="Monitors your inbox, files, and writing. Surfaces ideas while you work.",
                 style='Subtitle.TLabel').pack(anchor='w', pady=(0, 20))
        
        # Status panel
        status_card = self.create_card(tab); status_card.pack(fill='x', pady=(0, 16))
        sr = tk.Frame(status_card, bg=self.colors['surface']); sr.pack(fill='x')
        self.muse_file_status = tk.Label(sr, text="⬤ File Watcher: Off", bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 11))
        self.muse_file_status.pack(side='left')
        self.muse_inbox_status = tk.Label(sr, text="⬤ Inbox Monitor: Off", bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 11))
        self.muse_inbox_status.pack(side='left', padx=(30, 0))
        self.muse_ideas_count = tk.Label(sr, text="Ideas: 0", bg=self.colors['surface'], fg=self.colors['accent'], font=('SF Pro Display', 11, 'bold'))
        self.muse_ideas_count.pack(side='left', padx=(30, 0))
        self.muse_last_scan = tk.Label(sr, text="Last scan: never", bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10))
        self.muse_last_scan.pack(side='right')
        
        # Master controls
        ctrl = ttk.Frame(tab); ctrl.pack(fill='x', pady=(0, 20))
        ttk.Button(ctrl, text="▶ Start all monitoring", style='Accent.TButton', command=self.muse_start_all).pack(side='left')
        ttk.Button(ctrl, text="■ Stop all", style='Ghost.TButton', command=self.muse_stop_all).pack(side='left', padx=(12, 0))
        ttk.Button(ctrl, text="⟳ Scan now", style='Ghost.TButton', command=self.muse_scan_now).pack(side='left', padx=(12, 0))
        ttk.Button(ctrl, text="Generate ideas from library", style='Ghost.TButton', command=self.muse_library_ideas).pack(side='left', padx=(12, 0))
        
        # Recent ideas feed
        ttk.Label(tab, text="Recent Ideas", style='Heading.TLabel').pack(anchor='w', pady=(0, 8))
        
        cols = ('time', 'source', 'type', 'idea')
        self.muse_feed = ttk.Treeview(tab, columns=cols, show='headings', height=14)
        for c, w in [('time', 130), ('source', 100), ('type', 110), ('idea', 600)]:
            self.muse_feed.heading(c, text=c.title()); self.muse_feed.column(c, width=w)
        self.muse_feed.pack(fill='both', expand=True)
        
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(8, 0))
        ttk.Button(bf, text="Expand selected", style='Ghost.TButton', command=self.muse_expand_idea).pack(side='left')
        ttk.Button(bf, text="Send to Idea Generator", style='Ghost.TButton', command=self.muse_idea_to_gen).pack(side='left', padx=(12, 0))
        ttk.Button(bf, text="Export ideas", style='Ghost.TButton', command=self.muse_export_ideas).pack(side='right')
        ttk.Button(bf, text="Clear feed", style='Ghost.TButton', command=self.muse_clear_feed).pack(side='right', padx=(0, 12))
        
        self.refresh_muse_feed()
    
    # ── Inbox Monitor ──
    
    def _muse_inbox(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        
        ttk.Label(left, text="Email Inbox Monitor", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        ttk.Label(left, text="Scans your inbox for writing triggers, industry news, reader feedback",
                 style='Subtitle.TLabel').pack(anchor='w', pady=(0, 12))
        
        # IMAP Config
        cc = self.create_card(left); cc.pack(fill='x', pady=(0, 12))
        self.imap_server = tk.StringVar(value=self.imap_config.get('server', ''))
        self.imap_port = tk.StringVar(value=str(self.imap_config.get('port', 993)))
        self.imap_email = tk.StringVar(value=self.imap_config.get('email', ''))
        self.imap_pass = tk.StringVar(value=self.imap_config.get('password', ''))
        self.imap_folder = tk.StringVar(value=self.imap_config.get('folder', 'INBOX'))
        
        for lbl, var, sh, w in [("Server", self.imap_server, None, 25), ("Port", self.imap_port, None, 6),
                                 ("Email", self.imap_email, None, 25), ("Password", self.imap_pass, '•', 25),
                                 ("Folder", self.imap_folder, None, 15)]:
            r = tk.Frame(cc, bg=self.colors['surface']); r.pack(fill='x', pady=2)
            tk.Label(r, text=lbl, bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10), width=8).pack(side='left')
            e = tk.Entry(r, textvariable=var, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 10), borderwidth=0, width=w)
            if sh: e.configure(show=sh)
            e.pack(side='left', padx=(4, 0))
        
        # Keywords to watch
        kw_frame = tk.Frame(cc, bg=self.colors['surface']); kw_frame.pack(fill='x', pady=(8, 0))
        tk.Label(kw_frame, text="Watch keywords (comma-separated)", bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(anchor='w')
        self.imap_keywords = tk.StringVar(value=', '.join(self.imap_config.get('keywords', [])))
        tk.Entry(kw_frame, textvariable=self.imap_keywords, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 10), borderwidth=0).pack(fill='x', pady=(4, 0))
        
        bc = tk.Frame(cc, bg=self.colors['surface']); bc.pack(fill='x', pady=(8, 0))
        ttk.Button(bc, text="Test connection", style='Small.TButton', command=self.test_imap).pack(side='left')
        ttk.Button(bc, text="Save config", style='Small.TButton', command=self.save_imap_config).pack(side='left', padx=(8, 0))
        ttk.Button(bc, text="Start monitoring", style='Small.TButton', command=self.start_inbox_monitor).pack(side='left', padx=(8, 0))
        ttk.Button(bc, text="Stop", style='Small.TButton', command=self.stop_inbox_monitor).pack(side='left', padx=(8, 0))
        
        self.imap_status = ttk.Label(left, text="Not connected", style='Muted.TLabel')
        self.imap_status.pack(anchor='w', pady=(0, 12))
        
        # Scan interval
        iv = ttk.Frame(left); iv.pack(fill='x', pady=(0, 8))
        ttk.Label(iv, text="Scan every", style='Muted.TLabel').pack(side='left')
        self.scan_interval_var = tk.StringVar(value='5')
        self.create_radio_row(iv, "", self.scan_interval_var, [('1 min', '1'), ('5 min', '5'), ('15 min', '15'), ('30 min', '30')]).pack(side='left')
        
        ttk.Button(left, text="Scan inbox now", style='Accent.TButton', command=self.scan_inbox_now).pack(anchor='w', pady=(8, 0))
        
        # Right - found items
        ttk.Label(right, text="Inbox Findings", style='Heading.TLabel').pack(anchor='w', pady=(0, 12))
        
        cols = ('date', 'from', 'subject', 'trigger')
        self.inbox_tree = ttk.Treeview(right, columns=cols, show='headings', height=12)
        for c, w in [('date', 100), ('from', 150), ('subject', 300), ('trigger', 120)]:
            self.inbox_tree.heading(c, text=c.title()); self.inbox_tree.column(c, width=w)
        self.inbox_tree.pack(fill='both', expand=True)
        
        ttk.Label(right, text="Idea from selected email", style='Muted.TLabel').pack(anchor='w', pady=(8, 4))
        self.inbox_idea_out = self.create_text_area(right, height=4)
        self.inbox_idea_out.pack(fill='x')
        ttk.Button(right, text="Generate idea from email", style='Ghost.TButton', command=self.gen_idea_from_email).pack(anchor='w', pady=(8, 0))
    
    # ── File Watcher ──
    
    def _muse_files(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        
        ttk.Label(left, text="File Watcher", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        ttk.Label(left, text="Watches folders for new/changed writing files and surfaces ideas",
                 style='Subtitle.TLabel').pack(anchor='w', pady=(0, 12))
        
        # Watch folders
        ttk.Label(left, text="Watched folders", style='Muted.TLabel').pack(anchor='w', pady=(0, 4))
        self.folder_listbox = tk.Listbox(left, bg=self.colors['surface'], fg=self.colors['text'],
                                        font=('SF Mono', 10), height=6, borderwidth=0,
                                        selectbackground=self.colors['accent'], highlightthickness=0)
        self.folder_listbox.pack(fill='x', pady=(0, 8))
        for f in self.watch_folders:
            self.folder_listbox.insert('end', f)
        
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(0, 12))
        ttk.Button(bf, text="Add folder", style='Accent.TButton', command=self.add_watch_folder).pack(side='left')
        ttk.Button(bf, text="Remove", style='Ghost.TButton', command=self.remove_watch_folder).pack(side='left', padx=(12, 0))
        
        # File types
        ttk.Label(left, text="File types to watch", style='Muted.TLabel').pack(anchor='w', pady=(0, 4))
        self.watch_extensions = tk.StringVar(value='.txt, .md, .docx, .doc, .rtf, .odt')
        self.create_entry(left, self.watch_extensions).pack(fill='x', pady=(0, 12))
        
        bf2 = ttk.Frame(left); bf2.pack(fill='x', pady=(0, 8))
        ttk.Button(bf2, text="▶ Start watching", style='Accent.TButton', command=self.start_file_watcher).pack(side='left')
        ttk.Button(bf2, text="■ Stop", style='Ghost.TButton', command=self.stop_file_watcher).pack(side='left', padx=(12, 0))
        ttk.Button(bf2, text="Scan now", style='Ghost.TButton', command=self.scan_files_now).pack(side='left', padx=(12, 0))
        
        self.file_watch_status = ttk.Label(left, text="Not watching", style='Muted.TLabel')
        self.file_watch_status.pack(anchor='w')
        
        # Right - detected changes
        ttk.Label(right, text="Detected Changes", style='Heading.TLabel').pack(anchor='w', pady=(0, 12))
        
        cols = ('time', 'event', 'file', 'words')
        self.file_tree = ttk.Treeview(right, columns=cols, show='headings', height=12)
        for c, w in [('time', 130), ('event', 80), ('file', 350), ('words', 80)]:
            self.file_tree.heading(c, text=c.title()); self.file_tree.column(c, width=w)
        self.file_tree.pack(fill='both', expand=True)
        
        ttk.Label(right, text="Writing insights", style='Muted.TLabel').pack(anchor='w', pady=(8, 4))
        self.file_insights = self.create_text_area(right, height=4)
        self.file_insights.pack(fill='x')
    
    # ── Idea Generator ──
    
    def _muse_ideas_tab(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        
        ttk.Label(left, text="Idea Generator", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        
        # Idea type
        self.idea_type = tk.StringVar(value='book')
        self.create_radio_row(left, "Type", self.idea_type, [
            ('Book', 'book'), ('Article', 'article'), ('Blog', 'blog'),
            ('LinkedIn', 'linkedin'), ('Newsletter', 'newsletter')
        ]).pack(fill='x', pady=(0, 12))
        
        # Seed / context
        ttk.Label(left, text="Seed idea, topic, or context", style='Muted.TLabel').pack(anchor='w', pady=(0, 4))
        self.idea_seed = self.create_text_area(left, height=3)
        self.idea_seed.pack(fill='x', pady=(0, 8))
        
        # Based on
        self.idea_source = tk.StringVar(value='scratch')
        self.create_radio_row(left, "Based on", self.idea_source, [
            ('Scratch', 'scratch'), ('My books', 'books'), ('Inbox findings', 'inbox'),
            ('File changes', 'files'), ('Competitor gaps', 'competitors')
        ]).pack(fill='x', pady=(0, 12))
        
        # Quantity
        self.idea_count = tk.StringVar(value='5')
        self.create_radio_row(left, "Generate", self.idea_count, [('3', '3'), ('5', '5'), ('10', '10'), ('20', '20')]).pack(fill='x', pady=(0, 12))
        
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(8, 0))
        ttk.Button(bf, text="Generate ideas", style='Accent.TButton', command=self.gen_ideas).pack(side='left')
        ttk.Button(bf, text="Surprise me", style='Ghost.TButton', command=self.surprise_ideas).pack(side='left', padx=(12, 0))
        
        # Saved ideas list
        ttk.Label(left, text="Saved Ideas", style='Muted.TLabel').pack(anchor='w', pady=(16, 4))
        self.saved_ideas_list = tk.Listbox(left, bg=self.colors['surface'], fg=self.colors['text'],
                                          font=('SF Pro Display', 10), height=6, borderwidth=0,
                                          selectbackground=self.colors['accent'], highlightthickness=0)
        self.saved_ideas_list.pack(fill='x')
        self.refresh_saved_ideas()
        
        # Right - output
        ttk.Label(right, text="Generated Ideas", style='Muted.TLabel').pack(anchor='w', pady=(0, 4))
        self.ideas_out = self.create_text_area(right, height=20)
        self.ideas_out.pack(fill='both', expand=True)
        
        bf2 = ttk.Frame(right); bf2.pack(fill='x', pady=(8, 0))
        ttk.Button(bf2, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.ideas_out)).pack(side='left')
        ttk.Button(bf2, text="Save to feed", style='Ghost.TButton', command=self.save_ideas_to_feed).pack(side='left', padx=(12, 0))
    
    # ── Pattern Lab ──
    
    def _muse_patterns_tab(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        
        ttk.Label(left, text="Pattern Lab", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        ttk.Label(left, text="Analyses your writing patterns, topics, and gaps to find opportunities",
                 style='Subtitle.TLabel').pack(anchor='w', pady=(0, 12))
        
        ttk.Button(left, text="Analyse my library", style='Accent.TButton', command=self.analyse_library_patterns).pack(anchor='w', pady=(0, 12))
        ttk.Button(left, text="Find topic gaps", style='Ghost.TButton', command=self.find_topic_gaps).pack(anchor='w', pady=(0, 12))
        ttk.Button(left, text="Series opportunities", style='Ghost.TButton', command=self.find_series_opps).pack(anchor='w', pady=(0, 12))
        ttk.Button(left, text="Cross-pollination ideas", style='Ghost.TButton', command=self.cross_pollinate).pack(anchor='w', pady=(0, 12))
        ttk.Button(left, text="Seasonal content map", style='Ghost.TButton', command=self.seasonal_map).pack(anchor='w', pady=(0, 12))
        
        ttk.Label(left, text="Pattern History", style='Muted.TLabel').pack(anchor='w', pady=(16, 4))
        self.pattern_list = tk.Listbox(left, bg=self.colors['surface'], fg=self.colors['text'],
                                      font=('SF Pro Display', 10), height=6, borderwidth=0,
                                      selectbackground=self.colors['accent'], highlightthickness=0)
        self.pattern_list.pack(fill='x')
        
        self.pattern_out = self.create_text_area(right, height=20)
        self.pattern_out.pack(fill='both', expand=True)
        ttk.Button(right, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.pattern_out)).pack(anchor='w', pady=(8, 0))
    
    # ── Content Calendar ──
    
    def _muse_calendar(self, tab):
        ttk.Label(tab, text="Content Calendar Generator", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        ttk.Label(tab, text="Auto-generate a content plan from your ideas, books, and goals", style='Subtitle.TLabel').pack(anchor='w', pady=(0, 12))
        
        # Settings
        settings = self.create_card(tab); settings.pack(fill='x', pady=(0, 16))
        sr = tk.Frame(settings, bg=self.colors['surface']); sr.pack(fill='x', pady=(0, 8))
        self.cal_weeks = tk.StringVar(value='4')
        tk.Label(sr, text="Weeks ahead", bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left')
        for n in ['2', '4', '8', '12']:
            tk.Radiobutton(sr, text=n, variable=self.cal_weeks, value=n, bg=self.colors['surface'],
                          fg=self.colors['text_secondary'], selectcolor=self.colors['surface_raised'],
                          activebackground=self.colors['surface'], font=('SF Pro Display', 10), borderwidth=0, highlightthickness=0).pack(side='left', padx=(10, 0))
        
        sr2 = tk.Frame(settings, bg=self.colors['surface']); sr2.pack(fill='x')
        self.cal_freq = tk.StringVar(value='3')
        tk.Label(sr2, text="Posts/week", bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left')
        for n in ['1', '3', '5', '7']:
            tk.Radiobutton(sr2, text=n, variable=self.cal_freq, value=n, bg=self.colors['surface'],
                          fg=self.colors['text_secondary'], selectcolor=self.colors['surface_raised'],
                          activebackground=self.colors['surface'], font=('SF Pro Display', 10), borderwidth=0, highlightthickness=0).pack(side='left', padx=(10, 0))
        
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(0, 12))
        ttk.Button(bf, text="Generate calendar", style='Accent.TButton', command=self.gen_content_calendar).pack(side='left')
        ttk.Button(bf, text="Push to scheduler", style='Ghost.TButton', command=self.push_to_scheduler).pack(side='left', padx=(12, 0))
        
        self.cal_out = self.create_text_area(tab, height=16)
        self.cal_out.pack(fill='both', expand=True)
        ttk.Button(tab, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.cal_out)).pack(anchor='w', pady=(8, 0))
    
    # ═══════════════════════════════════════════════════════════════
    # BUSINESS TAB (PHASE 5)
    # ═══════════════════════════════════════════════════════════════
    
    def create_business_tab(self):
        tab = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(tab, text='  Business  ')
        self.biz_nb = ttk.Notebook(tab, style='Sub.TNotebook')
        self.biz_nb.pack(fill='both', expand=True, pady=(10, 0))
        for n, b in [('Backlist', self._biz_backlist), ('Series', self._biz_series), ('Characters', self._biz_characters),
                     ('KDP Export', self._biz_kdp), ('Rights', self._biz_rights), ('ARIA', self._biz_aria)]:
            t = ttk.Frame(self.biz_nb, padding=16); self.biz_nb.add(t, text=f'  {n}  '); b(t)

    def _biz_backlist(self, tab):
        ttk.Label(tab, text="Backlist Manager", style='Heading.TLabel').pack(anchor='w', pady=(0, 8))
        ttk.Label(tab, text="Track royalties, editions, ISBNs across all books", style='Subtitle.TLabel').pack(anchor='w', pady=(0, 16))
        af = self.create_card(tab); af.pack(fill='x', pady=(0, 16))
        r = tk.Frame(af, bg=self.colors['surface']); r.pack(fill='x')
        self.roy_book = tk.StringVar(); self.roy_period = tk.StringVar(value=datetime.now().strftime('%Y-%m'))
        self.roy_platform = tk.StringVar(value='Amazon'); self.roy_amount = tk.StringVar()
        for lbl, var, w in [("Book", self.roy_book, 20), ("Period", self.roy_period, 8), ("Platform", self.roy_platform, 10), ("Amount $", self.roy_amount, 8)]:
            tk.Label(r, text=lbl, bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left', padx=(8, 0))
            tk.Entry(r, textvariable=var, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 10), borderwidth=0, width=w).pack(side='left', padx=(4, 0))
        ttk.Button(af, text="Add royalty", style='Accent.TButton', command=self.add_royalty).pack(anchor='w', pady=(12, 0))
        cols = ('period', 'book', 'platform', 'amount')
        self.royalty_tree = ttk.Treeview(tab, columns=cols, show='headings', height=10)
        for c, w in [('period', 100), ('book', 280), ('platform', 120), ('amount', 100)]:
            self.royalty_tree.heading(c, text=c.title()); self.royalty_tree.column(c, width=w)
        self.royalty_tree.pack(fill='both', expand=True)
        self.royalty_summary = ttk.Label(tab, text="Total: $0.00", style='Accent.TLabel')
        self.royalty_summary.pack(anchor='w', pady=(12, 0))
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(8, 0))
        ttk.Button(bf, text="Delete", style='Ghost.TButton', command=self.del_royalty).pack(side='left')
        ttk.Button(bf, text="Export CSV", style='Ghost.TButton', command=self.export_royalties).pack(side='right')
        self.refresh_royalties()

    def _biz_series(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Series Bible", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        ttk.Label(left, text="Series", style='Muted.TLabel').pack(anchor='w')
        self.series_listbox = tk.Listbox(left, bg=self.colors['surface'], fg=self.colors['text'], font=('SF Pro Display', 11), height=6, borderwidth=0, selectbackground=self.colors['accent'], highlightthickness=0)
        self.series_listbox.pack(fill='x', pady=(4, 8))
        self.series_listbox.bind('<<ListboxSelect>>', self.on_series_select)
        for s in self.series_data: self.series_listbox.insert('end', s.get('name', 'Untitled'))
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(0, 12))
        ttk.Button(bf, text="Add series", style='Accent.TButton', command=self.add_series).pack(side='left')
        ttk.Button(bf, text="Delete", style='Ghost.TButton', command=self.del_series).pack(side='left', padx=(12, 0))
        ttk.Label(left, text="Series name", style='Muted.TLabel').pack(anchor='w')
        self.series_name = tk.StringVar(); self.create_entry(left, self.series_name).pack(fill='x', pady=(4, 8))
        ttk.Label(left, text="Genre", style='Muted.TLabel').pack(anchor='w')
        self.series_genre = tk.StringVar(); self.create_entry(left, self.series_genre).pack(fill='x', pady=(4, 8))
        self.series_status = tk.StringVar(value='In Progress')
        self.create_radio_row(left, "Status", self.series_status, [('Planning', 'Planning'), ('In Progress', 'In Progress'), ('Complete', 'Complete')]).pack(fill='x', pady=(0, 8))
        ttk.Button(left, text="Save series", style='Accent.TButton', command=self.save_series).pack(anchor='w', pady=(8, 0))
        ttk.Label(right, text="Series Bible", style='Muted.TLabel').pack(anchor='w')
        self.series_bible = self.create_text_area(right, height=6); self.series_bible.pack(fill='x', pady=(4, 12))
        ttk.Label(right, text="Timeline", style='Muted.TLabel').pack(anchor='w')
        self.series_timeline = self.create_text_area(right, height=4); self.series_timeline.pack(fill='x', pady=(4, 12))
        ttk.Label(right, text="World-building", style='Muted.TLabel').pack(anchor='w')
        self.series_world = self.create_text_area(right, height=4); self.series_world.pack(fill='x', pady=(4, 0))

    def _biz_characters(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="Character Database", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        cols = ('name', 'role', 'book')
        self.char_tree = ttk.Treeview(left, columns=cols, show='headings', height=12)
        for c, w in [('name', 150), ('role', 100), ('book', 150)]:
            self.char_tree.heading(c, text=c.title()); self.char_tree.column(c, width=w)
        self.char_tree.pack(fill='both', expand=True)
        self.char_tree.bind('<<TreeviewSelect>>', self.on_char_select)
        bf = ttk.Frame(left); bf.pack(fill='x', pady=(12, 0))
        ttk.Button(bf, text="Add character", style='Accent.TButton', command=self.add_character).pack(side='left')
        ttk.Button(bf, text="Delete", style='Ghost.TButton', command=self.del_character).pack(side='left', padx=(12, 0))
        ttk.Label(right, text="Character Details", style='Heading.TLabel').pack(anchor='w', pady=(0, 16))
        self.char_fields = {}
        for lbl, key in [("Name", "name"), ("Role", "role"), ("Book/Series", "book"), ("Age", "age"), ("Appearance", "appearance")]:
            ttk.Label(right, text=lbl, style='Muted.TLabel').pack(anchor='w')
            v = tk.StringVar(); self.char_fields[key] = v
            self.create_entry(right, v).pack(fill='x', pady=(4, 8))
        ttk.Label(right, text="Background & Arc", style='Muted.TLabel').pack(anchor='w')
        self.char_arc = self.create_text_area(right, height=3); self.char_arc.pack(fill='x', pady=(4, 8))
        ttk.Label(right, text="Relationships", style='Muted.TLabel').pack(anchor='w')
        self.char_rels = self.create_text_area(right, height=2); self.char_rels.pack(fill='x', pady=(4, 8))
        ttk.Button(right, text="Save character", style='Accent.TButton', command=self.save_character).pack(anchor='w', pady=(8, 0))
        self.refresh_characters()

    def _biz_kdp(self, tab):
        ttk.Label(tab, text="KDP Export", style='Heading.TLabel').pack(anchor='w', pady=(0, 8))
        ttk.Label(tab, text="Export to Amazon KDP-ready format", style='Subtitle.TLabel').pack(anchor='w', pady=(0, 16))
        ttk.Label(tab, text="Select book", style='Muted.TLabel').pack(anchor='w')
        self.kdp_book_list = tk.Listbox(tab, bg=self.colors['surface'], fg=self.colors['text'], font=('SF Pro Display', 11), height=8, borderwidth=0, selectbackground=self.colors['accent'], highlightthickness=0)
        self.kdp_book_list.pack(fill='x', pady=(4, 16))
        for b in self.books: self.kdp_book_list.insert('end', b.get('title', 'Untitled'))
        oc = self.create_card(tab); oc.pack(fill='x', pady=(0, 16))
        tk.Label(oc, text="Export includes:", bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(anchor='w')
        self.kdp_metadata = tk.BooleanVar(value=True); self.kdp_keywords = tk.BooleanVar(value=True)
        self.kdp_description = tk.BooleanVar(value=True); self.kdp_categories = tk.BooleanVar(value=True)
        for txt, var in [("Metadata (title, author, ASIN, ISBN)", self.kdp_metadata), ("Keywords (7 phrases)", self.kdp_keywords),
                        ("Description (formatted)", self.kdp_description), ("Categories suggestion", self.kdp_categories)]:
            tk.Checkbutton(oc, text=txt, variable=var, bg=self.colors['surface'], fg=self.colors['text_secondary'],
                          selectcolor=self.colors['surface_raised'], activebackground=self.colors['surface'],
                          font=('SF Pro Display', 10), borderwidth=0, highlightthickness=0).pack(anchor='w', pady=2)
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(0, 16))
        ttk.Button(bf, text="Export selected", style='Accent.TButton', command=self.export_kdp).pack(side='left')
        ttk.Button(bf, text="Export all books", style='Ghost.TButton', command=self.export_all_kdp).pack(side='left', padx=(12, 0))
        ttk.Label(tab, text="Preview", style='Muted.TLabel').pack(anchor='w')
        self.kdp_preview = self.create_text_area(tab, height=8); self.kdp_preview.pack(fill='both', expand=True)

    def _biz_rights(self, tab):
        ttk.Label(tab, text="Rights & Licensing", style='Heading.TLabel').pack(anchor='w', pady=(0, 8))
        ttk.Label(tab, text="Track foreign rights, audio, film options", style='Subtitle.TLabel').pack(anchor='w', pady=(0, 16))
        af = self.create_card(tab); af.pack(fill='x', pady=(0, 16))
        r = tk.Frame(af, bg=self.colors['surface']); r.pack(fill='x')
        self.right_book = tk.StringVar(); self.right_type = tk.StringVar(value='Foreign')
        self.right_territory = tk.StringVar(); self.right_status = tk.StringVar(value='Available')
        self.right_licensee = tk.StringVar(); self.right_expiry = tk.StringVar()
        for lbl, var, w in [("Book", self.right_book, 18), ("Type", self.right_type, 10), ("Territory", self.right_territory, 12)]:
            tk.Label(r, text=lbl, bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left', padx=(6, 0))
            tk.Entry(r, textvariable=var, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 10), borderwidth=0, width=w).pack(side='left', padx=(4, 0))
        r2 = tk.Frame(af, bg=self.colors['surface']); r2.pack(fill='x', pady=(8, 0))
        for lbl, var, w in [("Licensee", self.right_licensee, 18), ("Expiry", self.right_expiry, 10)]:
            tk.Label(r2, text=lbl, bg=self.colors['surface'], fg=self.colors['text_muted'], font=('SF Pro Display', 10)).pack(side='left', padx=(6, 0))
            tk.Entry(r2, textvariable=var, bg=self.colors['surface_raised'], fg=self.colors['text'], font=('SF Pro Display', 10), borderwidth=0, width=w).pack(side='left', padx=(4, 0))
        self.create_radio_row(af, "Status", self.right_status, [('Available', 'Available'), ('Licensed', 'Licensed'), ('Negotiating', 'Negotiating')], bg=self.colors['surface']).pack(fill='x', pady=(8, 0))
        ttk.Button(af, text="Add right", style='Accent.TButton', command=self.add_right).pack(anchor='w', pady=(12, 0))
        cols = ('book', 'type', 'territory', 'status', 'licensee', 'expiry')
        self.rights_tree = ttk.Treeview(tab, columns=cols, show='headings', height=10)
        for c, w in [('book', 180), ('type', 80), ('territory', 100), ('status', 90), ('licensee', 140), ('expiry', 90)]:
            self.rights_tree.heading(c, text=c.title()); self.rights_tree.column(c, width=w)
        self.rights_tree.pack(fill='both', expand=True)
        bf = ttk.Frame(tab); bf.pack(fill='x', pady=(12, 0))
        ttk.Button(bf, text="Delete", style='Ghost.TButton', command=self.del_right).pack(side='left')
        ttk.Button(bf, text="Export", style='Ghost.TButton', command=self.export_rights).pack(side='right')
        self.refresh_rights()

    def _biz_aria(self, tab):
        left = ttk.Frame(tab); left.pack(side='left', fill='both', expand=True, padx=(0, 16))
        right = ttk.Frame(tab); right.pack(side='right', fill='both', expand=True)
        ttk.Label(left, text="ARIA — AI Analytics", style='Heading.TLabel').pack(anchor='w', pady=(0, 8))
        ttk.Label(left, text="AI-powered insights and recommendations", style='Subtitle.TLabel').pack(anchor='w', pady=(0, 16))
        ttk.Button(left, text="📊 Portfolio Analysis", style='Accent.TButton', command=self.aria_portfolio).pack(anchor='w', pady=(0, 10))
        ttk.Button(left, text="💰 Revenue Forecast", style='Ghost.TButton', command=self.aria_forecast).pack(anchor='w', pady=(0, 10))
        ttk.Button(left, text="📈 Growth Opportunities", style='Ghost.TButton', command=self.aria_opportunities).pack(anchor='w', pady=(0, 10))
        ttk.Button(left, text="🎯 Market Positioning", style='Ghost.TButton', command=self.aria_positioning).pack(anchor='w', pady=(0, 10))
        ttk.Button(left, text="⚡ Quick Wins", style='Ghost.TButton', command=self.aria_quickwins).pack(anchor='w', pady=(0, 10))
        ttk.Button(left, text="🔮 Trend Analysis", style='Ghost.TButton', command=self.aria_trends).pack(anchor='w', pady=(0, 10))
        ttk.Label(left, text="Saved Reports", style='Muted.TLabel').pack(anchor='w', pady=(20, 4))
        self.aria_reports_list = tk.Listbox(left, bg=self.colors['surface'], fg=self.colors['text'], font=('SF Pro Display', 10), height=5, borderwidth=0, selectbackground=self.colors['accent'], highlightthickness=0)
        self.aria_reports_list.pack(fill='x')
        for r in self.aria_reports: self.aria_reports_list.insert('end', f"{r.get('type', '')} - {r.get('date', '')}")
        self.aria_out = self.create_text_area(right, height=20); self.aria_out.pack(fill='both', expand=True)
        bf = ttk.Frame(right); bf.pack(fill='x', pady=(12, 0))
        ttk.Button(bf, text="Copy", style='Ghost.TButton', command=lambda: self.cp(self.aria_out)).pack(side='left')
        ttk.Button(bf, text="Save report", style='Ghost.TButton', command=self.save_aria_report).pack(side='left', padx=(12, 0))
    
    # ═══════════════════════════════════════════════════════════════
    # EXPORT TAB
    # ═══════════════════════════════════════════════════════════════
    
    def create_export_tab(self):
        tab = ttk.Frame(self.notebook, padding=20); self.notebook.add(tab, text='  Export  ')
        ttk.Label(tab, text="Export Options", style='Heading.TLabel').pack(anchor='w', pady=(0, 20))
        for title, desc, cmd in [("Export CSV", "All book metadata", self.export_csv),
                                  ("Export Analytics", "All tracking data", self.export_analytics),
                                  ("Export Muse Ideas", "All ideas and patterns", self.muse_export_ideas),
                                  ("Backup Everything", "Full JSON backup", self.backup_all)]:
            c = self.create_card(tab); c.pack(fill='x', pady=(0, 8))
            ttk.Label(c, text=title).pack(anchor='w')
            ttk.Label(c, text=desc, style='Muted.TLabel').pack(anchor='w', pady=(2, 6))
            ttk.Button(c, text="Export", style='Ghost.TButton', command=cmd).pack(anchor='w')
    
    # ═══════════════════════════════════════════════════════════════
    # DATA PERSISTENCE
    # ═══════════════════════════════════════════════════════════════
    
    def load_data(self):
        for attr, path in [('books', self.data_file), ('scheduled_posts', self.schedule_file)]:
            if path.exists():
                try:
                    with open(path) as f: setattr(self, attr, json.load(f))
                except: pass
        if self.config_file.exists():
            try:
                with open(self.config_file) as f:
                    cfg = json.load(f)
                    self.listmonk_config.update(cfg.get('listmonk', cfg))
                    if 'imap' in cfg: self.imap_config.update(cfg['imap'])
                    if 'watch_folders' in cfg: self.watch_folders = cfg['watch_folders']
            except: pass
        if self.analytics_file.exists():
            try:
                with open(self.analytics_file) as f:
                    d = json.load(f)
                    self.keyword_history = d.get('keywords', {}); self.competitors = d.get('competitors', [])
                    self.reader_avatars = d.get('avatars', []); self.snapshots = d.get('snapshots', {})
            except: pass
        if self.linkedin_file.exists():
            try:
                with open(self.linkedin_file) as f: self.linkedin_campaigns = json.load(f)
            except: pass
        if self.muse_file.exists():
            try:
                with open(self.muse_file) as f:
                    d = json.load(f)
                    self.muse_ideas = d.get('ideas', []); self.muse_inbox_items = d.get('inbox', [])
                    self.muse_file_changes = d.get('files', []); self.muse_patterns = d.get('patterns', [])
                    self.file_hashes = d.get('hashes', {})
            except: pass
        if self.business_file.exists():
            try:
                with open(self.business_file) as f:
                    d = json.load(f)
                    self.royalties = d.get('royalties', []); self.series_data = d.get('series', [])
                    self.characters = d.get('characters', []); self.rights = d.get('rights', [])
                    self.aria_reports = d.get('aria_reports', [])
            except: pass
    
    def save_books(self):
        with open(self.data_file, 'w') as f: json.dump(self.books, f, indent=2)
    def save_schedule(self):
        with open(self.schedule_file, 'w') as f: json.dump(self.scheduled_posts, f, indent=2)
    def save_analytics(self):
        with open(self.analytics_file, 'w') as f:
            json.dump({'keywords': self.keyword_history, 'competitors': self.competitors,
                       'avatars': self.reader_avatars, 'snapshots': self.snapshots}, f, indent=2)
    def save_li_data(self):
        with open(self.linkedin_file, 'w') as f: json.dump(self.linkedin_campaigns, f, indent=2)
    def save_config(self):
        with open(self.config_file, 'w') as f:
            json.dump({'listmonk': {'url': self.listmonk_url.get(), 'username': self.listmonk_user.get(), 'password': self.listmonk_pass.get()},
                       'imap': {'server': self.imap_server.get(), 'port': int(self.imap_port.get() or 993),
                               'email': self.imap_email.get(), 'password': self.imap_pass.get(),
                               'folder': self.imap_folder.get(), 'keywords': [k.strip() for k in self.imap_keywords.get().split(',')]},
                       'watch_folders': self.watch_folders}, f, indent=2)
    def save_muse_data(self):
        with open(self.muse_file, 'w') as f:
            json.dump({'ideas': self.muse_ideas[-500:], 'inbox': self.muse_inbox_items[-200:],
                       'files': self.muse_file_changes[-200:], 'patterns': self.muse_patterns[-50:],
                       'hashes': self.file_hashes}, f, indent=2)
    
    # ═══════════════════════════════════════════════════════════════
    # LOGIC - LIBRARY
    # ═══════════════════════════════════════════════════════════════
    
    def refresh_book_list(self):
        for i in self.book_tree.get_children(): self.book_tree.delete(i)
        s = self.search_var.get().lower() if hasattr(self, 'search_var') else ''
        for i, b in enumerate(self.books):
            t, a = b.get('title', 'Untitled'), b.get('author', '')
            if s and s not in t.lower() and s not in a.lower(): continue
            self.book_tree.insert('', 'end', iid=str(i), values=(t, a, b.get('status', 'Draft'), f"{b.get('quality_score', '--')}%"))
    
    def on_book_select(self, e):
        sel = self.book_tree.selection()
        if sel:
            self.current_book = int(sel[0]); b = self.books[self.current_book]
            for k in ['title', 'subtitle', 'author', 'series', 'asin']:
                if k in self.meta_vars: self.meta_vars[k].set(b.get(k, ''))
            self.st(self.description_text, b.get('description', ''))
            kws = b.get('keywords', [])
            for i, v in enumerate(self.keyword_vars): v.set(kws[i] if i < len(kws) else '')
    
    def add_book(self):
        self.books.append({'title': 'New Book', 'author': 'Mani Padisetti', 'status': 'Draft', 'created': datetime.now().isoformat(), 'keywords': [], 'description': ''})
        self.save_books(); self.refresh_book_list()
        self.book_tree.selection_set(str(len(self.books)-1)); self.current_book = len(self.books)-1; self.on_book_select(None); self.notebook.select(1)
    
    def delete_book(self):
        if self.current_book is not None and messagebox.askyesno("Delete", f"Delete '{self.gbt()}'?"):
            self.books.pop(self.current_book); self.current_book = None; self.save_books(); self.refresh_book_list()
    
    def import_folder(self):
        d = filedialog.askdirectory()
        if d:
            c = 0
            for ext in ['*.txt', '*.md', '*.docx']:
                for f in Path(d).glob(ext):
                    self.books.append({'title': f.stem, 'author': 'Mani Padisetti', 'status': 'Imported', 'file_path': str(f), 'created': datetime.now().isoformat()})
                    c += 1
            self.save_books(); self.refresh_book_list(); messagebox.showinfo("Import", f"Imported {c} books")
    
    def import_csv(self):
        f = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])
        if f:
            with open(f, encoding='utf-8') as fh:
                c = 0
                for row in csv.DictReader(fh):
                    self.books.append({'title': row.get('title', row.get('Title', '')), 'author': row.get('author', row.get('Author', '')), 'status': 'Imported', 'created': datetime.now().isoformat()})
                    c += 1
            self.save_books(); self.refresh_book_list()
    
    def save_metadata(self):
        if self.current_book is None: return
        b = self.books[self.current_book]
        for k, v in self.meta_vars.items(): b[k] = v.get()
        b['description'] = self.gt(self.description_text); b['updated'] = datetime.now().isoformat()
        self.save_books(); self.refresh_book_list()
    
    def save_keywords(self):
        if self.current_book is None: return
        self.books[self.current_book]['keywords'] = [v.get() for v in self.keyword_vars if v.get()]; self.save_books()
    
    # ═══════════════════════════════════════════════════════════════
    # LOGIC - QUALITY
    # ═══════════════════════════════════════════════════════════════
    
    def check_quality(self):
        text = self.gt(self.quality_input)
        if not text: return
        ai_phrases = ['delve', 'dive into', "it's important to note", 'in conclusion', 'leverage', 'utilize', 'facilitate', 'comprehensive', 'robust', 'seamless', 'innovative', 'cutting-edge', 'paradigm', 'synergy', 'ecosystem', 'landscape', 'navigate', 'journey', 'empower', 'unlock', 'unleash', 'game-changing', 'groundbreaking']
        found = [p for p in ai_phrases if p.lower() in text.lower()]
        score = min(len(found) * 8 + (15 if self._low_variance(text) else 0), 100)
        qual = 100 - score
        st = 'Error.TLabel' if score > 50 else ('Warning.TLabel' if score > 30 else 'Success.TLabel')
        self.ai_score_label.configure(text=f"AI: {score}%", style=st)
        self.quality_score_label.configure(text=f"Quality: {qual}%")
        r = [f"Words: {len(text.split())} | AI patterns: {len(found)}", ""]
        if found: r.append("Found: " + ", ".join(found))
        else: r.append("✓ No AI patterns")
        self.st(self.quality_output, '\n'.join(r))
        if self.current_book is not None:
            self.books[self.current_book]['quality_score'] = qual; self.save_books(); self.refresh_book_list()
    
    def _low_variance(self, text):
        sents = [s for s in re.split(r'[.!?]+', text) if s.strip()]
        if len(sents) < 3: return False
        lens = [len(s.split()) for s in sents]
        avg = sum(lens) / len(lens)
        return sum((l - avg) ** 2 for l in lens) / len(lens) < 10
    
    def load_manuscript(self):
        f = filedialog.askopenfilename(filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if f:
            with open(f, encoding='utf-8') as fh: self.st(self.quality_input, fh.read())
    
    # ═══════════════════════════════════════════════════════════════
    # LOGIC - MARKETING (abbreviated, same prompts as Phase 3/4)
    # ═══════════════════════════════════════════════════════════════
    
    def gen_booktok(self):
        b = self.gb()
        self.st(self.booktok_out, f"Create a {self.booktok_dur.get()}s BookTok {self.booktok_type.get()} script for '{b.get('title','')}'. Hook in 3s, visuals, hashtags. Australian English.\n\nCopy to Claude or ChatGPT.")
    def gen_instagram(self):
        b = self.gb()
        self.st(self.insta_out, f"Create Instagram {self.insta_type.get()} ({self.insta_theme.get()}) for '{b.get('title','')}'. {self.hashtag_count.get()} hashtags, CTA. Australian English.\n\nCopy to Claude or ChatGPT.")
    def add_sched_post(self):
        c = self.sched_content.get('1.0', 'end-1c').strip()
        if not c: return
        self.scheduled_posts.append({'date': self.sched_date.get(), 'time': self.sched_time.get(), 'platform': self.sched_platform.get(), 'content': c, 'status': 'Scheduled'}); self.save_schedule(); self.refresh_schedule(); self.sched_content.delete('1.0', 'end')
    def refresh_schedule(self):
        for i in self.sched_tree.get_children(): self.sched_tree.delete(i)
        for i, p in enumerate(sorted(self.scheduled_posts, key=lambda x: x.get('date', ''))):
            self.sched_tree.insert('', 'end', iid=str(i), values=(p['date'], p['time'], p['platform'], p['content'][:80], p['status']))
    def del_sched(self):
        sel = self.sched_tree.selection()
        if sel:
            sp = sorted(self.scheduled_posts, key=lambda x: x.get('date', '')); self.scheduled_posts.remove(sp[int(sel[0])]); self.save_schedule(); self.refresh_schedule()
    def mark_posted(self):
        sel = self.sched_tree.selection()
        if sel:
            sp = sorted(self.scheduled_posts, key=lambda x: x.get('date', '')); oi = self.scheduled_posts.index(sp[int(sel[0])]); self.scheduled_posts[oi]['status'] = 'Posted'; self.save_schedule(); self.refresh_schedule()
    def test_listmonk(self):
        try:
            import urllib.request, base64
            req = urllib.request.Request(f"{self.listmonk_url.get()}/api/health")
            req.add_header('Authorization', f'Basic {base64.b64encode(f"{self.listmonk_user.get()}:{self.listmonk_pass.get()}".encode()).decode()}')
            urllib.request.urlopen(req, timeout=5); self.lm_status.configure(text="✓ Connected", style='Success.TLabel')
        except Exception as e: self.lm_status.configure(text=f"Failed: {str(e)[:40]}", style='Error.TLabel')
    def save_lm_config(self): self.save_config()
    def gen_email(self):
        b = self.gb(); self.st(self.email_subj, f"{self.email_type.get().title()}: {b.get('title','')}")
        self.st(self.email_body, f"Generate a {self.email_type.get()} email for '{b.get('title','')}'. Warm, Australian English.\n\nCopy to Claude or ChatGPT.")
    def open_promo(self):
        sel = self.promo_tree.selection()
        if sel: webbrowser.open(self.promo_sites[int(sel[0])]['url'])
    def promo_calendar(self):
        b = self.gb(); today = datetime.now()
        cal = f"PROMO CALENDAR: {b.get('title','')}\n{'='*50}\n\n"
        for i, s in enumerate(self.promo_sites):
            sub = today + timedelta(days=i*3); cal += f"{sub.strftime('%b %d')} → {s['name']} ({s['cost']})\n"
        self.st(self.promo_out, cal)
    def gen_ads(self):
        b = self.gb()
        self.st(self.ads_out, f"Generate {self.ad_vars.get()} Amazon {self.ad_type.get()} ads for '{b.get('title','')}'. 150 chars each.\n\nCopy to Claude or ChatGPT.")
    def gen_review(self):
        self.st(self.review_out, f"Generate {self.review_type.get().replace('_',' ')} review request ({self.review_tone.get()}) for '{self.gbt()}'.\n\nCopy to Claude or ChatGPT.")
    
    # Analytics logic
    def analyse_sentiment(self):
        text = self.gt(self.sentiment_input)
        if not text: return
        reviews = [r.strip() for r in re.split(r'\n\n+|\n', text) if r.strip()]
        pw = {'love', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'brilliant', 'beautiful', 'perfect', 'recommend', 'best', 'captivating', 'gripping', 'masterpiece'}
        nw = {'bad', 'terrible', 'awful', 'boring', 'waste', 'disappointed', 'poor', 'worst', 'confusing', 'slow', 'dull', 'errors', 'typos', 'repetitive', 'predictable'}
        pos = neg = neu = 0
        for r in reviews:
            w = set(r.lower().split()); p = len(w & pw); n = len(w & nw)
            if p > n: pos += 1
            elif n > p: neg += 1
            else: neu += 1
        t = len(reviews)
        self.sent_pos.configure(text=f"Pos: {pos}"); self.sent_neu.configure(text=f"Neu: {neu}"); self.sent_neg.configure(text=f"Neg: {neg}")
        self.st(self.sentiment_out, f"{t} reviews: {pos} positive, {neu} neutral, {neg} negative")
    def gen_sent_prompt(self): self.st(self.sentiment_out, f"Analyse these reviews for sentiment and actionable insights:\n\n{self.gt(self.sentiment_input)[:2000]}\n\nCopy to Claude or ChatGPT.")
    def log_kw_pos(self):
        kw, pos = self.track_kw.get().strip(), self.track_pos.get().strip()
        if not kw or not pos: return
        bk = self.gbt()
        if bk not in self.keyword_history: self.keyword_history[bk] = []
        prev = None
        for e in reversed(self.keyword_history[bk]):
            if e['keyword'] == kw: prev = e['position']; break
        self.keyword_history[bk].append({'date': datetime.now().strftime('%Y-%m-%d %H:%M'), 'keyword': kw, 'position': int(pos), 'previous': prev})
        self.save_analytics(); self.refresh_kw_history(); self.track_kw.set(''); self.track_pos.set('')
    def refresh_kw_history(self):
        for i in self.kw_tree.get_children(): self.kw_tree.delete(i)
        for i, e in enumerate(reversed(self.keyword_history.get(self.gbt(), [])[-50:])):
            ch = '--' if e.get('previous') is None else (f"{'↑' if e['previous']-e['position'] > 0 else '↓'} {abs(e['previous']-e['position'])}" if e['previous'] != e['position'] else '=')
            self.kw_tree.insert('', 'end', iid=str(i), values=(e['date'], e['keyword'], e['position'], ch))
    def add_competitor(self):
        t = self.comp_title.get().strip()
        if not t: return
        self.competitors.append({'title': t, 'asin': self.comp_asin.get(), 'price': self.comp_price.get(), 'rank': self.comp_rank.get(), 'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M')})
        self.save_analytics(); self.refresh_competitors(); [v.set('') for v in [self.comp_title, self.comp_asin, self.comp_price, self.comp_rank]]
    def refresh_competitors(self):
        for i in self.comp_tree.get_children(): self.comp_tree.delete(i)
        for i, c in enumerate(self.competitors):
            self.comp_tree.insert('', 'end', iid=str(i), values=(c['title'], c.get('asin',''), c.get('price',''), c.get('rank',''), c.get('last_updated','')))
    def del_competitor(self):
        sel = self.comp_tree.selection()
        if sel: self.competitors.pop(int(sel[0])); self.save_analytics(); self.refresh_competitors()
    def build_avatar(self):
        d = {k: v.get() for k, v in self.avatar_fields.items()}
        self.st(self.avatar_out, f"READER AVATAR: {d.get('name','')}\n\nDemographics: {d.get('demographics','')}\nReading: {d.get('reading','')}\nPain: {d.get('pain','')}\nDesires: {d.get('desires','')}\nOnline: {d.get('online','')}\nTriggers: {d.get('triggers','')}")
    def gen_avatar_prompt(self): self.st(self.avatar_out, f"Build a reader avatar for '{self.gbt()}' targeting Australian market.\n\nCopy to Claude or ChatGPT.")
    def take_snapshot(self):
        bk = self.gbt(); snap = {k: v.get() for k, v in self.wc_fields.items()}; snap['date'] = datetime.now().strftime('%Y-%m-%d %H:%M')
        if bk not in self.snapshots: self.snapshots[bk] = []
        self.snapshots[bk].append(snap); self.save_analytics(); self.refresh_snapshots()
    def compare_snapshots(self):
        snaps = self.snapshots.get(self.gbt(), [])
        if len(snaps) < 2: self.st(self.wc_out, "Need 2+ snapshots"); return
        p, c = snaps[-2], snaps[-1]; r = [f"CHANGES: {p['date']} → {c['date']}", ""]
        for k, l in [('bsr','BSR'), ('reviews','Reviews'), ('rating','Rating'), ('price','Price'), ('kenp','KENP'), ('sales','Sales')]:
            try:
                o, n = float(p.get(k,0) or 0), float(c.get(k,0) or 0)
                if o == 0 and n == 0: continue
                d = n - o; r.append(f"{'✓' if (d<0 if k=='bsr' else d>0) else '⚠'} {l}: {o} → {n} ({'↑' if d>0 else '↓'} {abs(d):.0f})")
            except: pass
        self.st(self.wc_out, '\n'.join(r))
    def refresh_snapshots(self):
        for i in self.snap_tree.get_children(): self.snap_tree.delete(i)
        for i, s in enumerate(reversed(self.snapshots.get(self.gbt(), [])[-10:])):
            self.snap_tree.insert('', 'end', iid=str(i), values=(s.get('date',''), s.get('bsr',''), s.get('reviews',''), s.get('rating',''), s.get('price','')))
    def gen_linkedin(self):
        b = self.gb()
        self.st(self.li_out, f"""Generate 3 LinkedIn {self.li_format.get()} variations ({self.li_type.get().replace('_',' ')}):

BOOK: {b.get('title','')}
AUDIENCE: {self.gt(self.li_audience) or 'Business professionals'}
OBJECTIVE: {self.gt(self.li_objective) or b.get('title','')}
CTA: {self.li_cta.get().replace('_',' ').title()}

Angles: 1) Story-led 2) Data/insight-led 3) Contrarian
Voice: Authoritative, philosophical, Australian humour. 5-8 hashtags.

Copy to Claude or ChatGPT.""")
    def gen_li_script(self):
        self.st(self.li_out, f"Generate LinkedIn video script (60-90s) for '{self.gt(self.li_objective) or self.gbt()}'. Hook 3s, value 45s, CTA. B-roll notes. Australian English.\n\nCopy to Claude or ChatGPT.")
    def gen_li_hashtags(self):
        self.st(self.li_out, f"Research LinkedIn hashtags for '{self.gt(self.li_objective) or self.gbt()}'. 3 high-volume, 3 medium, 3 niche. Best times AEST.\n\nCopy to Claude or ChatGPT.")
    def save_li_campaign(self):
        t = self.gt(self.li_out)
        if t: self.linkedin_campaigns.append({'content': t, 'type': self.li_type.get(), 'date': datetime.now().isoformat()}); self.save_li_data()
    
    # ═══════════════════════════════════════════════════════════════
    # LOGIC - MUSE (Creative Intelligence Engine)
    # ═══════════════════════════════════════════════════════════════
    
    def add_muse_idea(self, source, idea_type, idea_text):
        entry = {'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'source': source, 'type': idea_type, 'idea': idea_text}
        self.muse_ideas.append(entry)
        self.save_muse_data()
        try: self.refresh_muse_feed()
        except: pass
    
    def refresh_muse_feed(self):
        for i in self.muse_feed.get_children(): self.muse_feed.delete(i)
        for i, idea in enumerate(reversed(self.muse_ideas[-100:])):
            self.muse_feed.insert('', 'end', iid=str(i), values=(idea['time'], idea['source'], idea['type'], idea['idea'][:100]))
        try:
            self.muse_ideas_count.configure(text=f"Ideas: {len(self.muse_ideas)}")
        except: pass
    
    def update_muse_status(self):
        try:
            self.muse_file_status.configure(text=f"⬤ Files: {'On' if self.muse_watching else 'Off'}",
                                           fg=self.colors['success'] if self.muse_watching else self.colors['text_muted'])
            self.muse_inbox_status.configure(text=f"⬤ Inbox: {'On' if self.muse_inbox_monitoring else 'Off'}",
                                            fg=self.colors['success'] if self.muse_inbox_monitoring else self.colors['text_muted'])
            self.muse_indicator.configure(text=f"⬤ Muse: {'Active' if (self.muse_watching or self.muse_inbox_monitoring) else 'Off'}",
                                         style='Success.TLabel' if (self.muse_watching or self.muse_inbox_monitoring) else 'Muted.TLabel')
        except: pass
    
    # ── Master Controls ──
    
    def muse_start_all(self):
        self.start_file_watcher()
        self.start_inbox_monitor()
    
    def muse_stop_all(self):
        self.stop_file_watcher()
        self.stop_inbox_monitor()
    
    def muse_scan_now(self):
        self.scan_files_now()
        self.scan_inbox_now()
        self.muse_library_ideas()
    
    # ── File Watcher ──
    
    def add_watch_folder(self):
        d = filedialog.askdirectory()
        if d and d not in self.watch_folders:
            self.watch_folders.append(d)
            self.folder_listbox.insert('end', d)
            self.save_config()
    
    def remove_watch_folder(self):
        sel = self.folder_listbox.curselection()
        if sel:
            idx = sel[0]; self.watch_folders.pop(idx)
            self.folder_listbox.delete(idx); self.save_config()
    
    def start_file_watcher(self):
        if self.muse_watching: return
        if not self.watch_folders:
            self.file_watch_status.configure(text="No folders to watch", style='Warning.TLabel'); return
        self.muse_watching = True
        self.file_watch_status.configure(text="✓ Watching...", style='Success.TLabel')
        self.update_muse_status()
        threading.Thread(target=self._file_watch_loop, daemon=True).start()
    
    def stop_file_watcher(self):
        self.muse_watching = False
        self.file_watch_status.configure(text="Stopped", style='Muted.TLabel')
        self.update_muse_status()
    
    def _file_watch_loop(self):
        while self.muse_watching:
            try: self._scan_watch_folders()
            except: pass
            interval = int(self.scan_interval_var.get()) * 60 if hasattr(self, 'scan_interval_var') else 300
            for _ in range(interval):
                if not self.muse_watching: break
                time.sleep(1)
    
    def scan_files_now(self):
        threading.Thread(target=self._scan_watch_folders, daemon=True).start()
    
    def _scan_watch_folders(self):
        exts = [e.strip() for e in self.watch_extensions.get().split(',')]
        for folder in self.watch_folders:
            p = Path(folder)
            if not p.exists(): continue
            for ext in exts:
                for file in p.rglob(f'*{ext}'):
                    try:
                        stat = file.stat()
                        file_key = str(file)
                        current_hash = f"{stat.st_size}_{stat.st_mtime}"
                        
                        if file_key not in self.file_hashes:
                            # New file
                            self.file_hashes[file_key] = current_hash
                            wc = 0
                            try:
                                with open(file, encoding='utf-8', errors='ignore') as f:
                                    wc = len(f.read().split())
                            except: pass
                            
                            change = {'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'event': 'New',
                                     'file': file.name, 'path': file_key, 'words': wc}
                            self.muse_file_changes.append(change)
                            
                            self.add_muse_idea('File Watcher', 'New File',
                                f"New file detected: '{file.stem}' ({wc} words). Consider: article from this, sequel ideas, related content.")
                            
                            self.root.after(0, self._update_file_tree, change)
                            
                        elif self.file_hashes[file_key] != current_hash:
                            # Modified file
                            self.file_hashes[file_key] = current_hash
                            wc = 0
                            try:
                                with open(file, encoding='utf-8', errors='ignore') as f:
                                    wc = len(f.read().split())
                            except: pass
                            
                            change = {'time': datetime.now().strftime('%Y-%m-%d %H:%M'), 'event': 'Modified',
                                     'file': file.name, 'path': file_key, 'words': wc}
                            self.muse_file_changes.append(change)
                            
                            self.add_muse_idea('File Watcher', 'File Changed',
                                f"'{file.stem}' updated ({wc} words). Your writing is evolving—any spin-off ideas?")
                            
                            self.root.after(0, self._update_file_tree, change)
                    except: pass
        
        self.save_muse_data()
        try:
            self.root.after(0, lambda: self.muse_last_scan.configure(text=f"Last scan: {datetime.now().strftime('%H:%M')}"))
        except: pass
    
    def _update_file_tree(self, change):
        try:
            self.file_tree.insert('', 0, values=(change['time'], change['event'], change['file'], change.get('words', '')))
        except: pass
    
    # ── Inbox Monitor ──
    
    def save_imap_config(self): self.save_config()
    
    def test_imap(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server.get(), int(self.imap_port.get() or 993))
            mail.login(self.imap_email.get(), self.imap_pass.get())
            mail.logout()
            self.imap_status.configure(text="✓ Connected", style='Success.TLabel')
        except Exception as e:
            self.imap_status.configure(text=f"Failed: {str(e)[:50]}", style='Error.TLabel')
    
    def start_inbox_monitor(self):
        if self.muse_inbox_monitoring: return
        if not self.imap_server.get():
            try: self.imap_status.configure(text="Configure email first", style='Warning.TLabel')
            except: pass
            return
        self.muse_inbox_monitoring = True
        self.update_muse_status()
        threading.Thread(target=self._inbox_monitor_loop, daemon=True).start()
    
    def stop_inbox_monitor(self):
        self.muse_inbox_monitoring = False
        self.update_muse_status()
    
    def _inbox_monitor_loop(self):
        while self.muse_inbox_monitoring:
            try: self._scan_inbox()
            except: pass
            interval = int(self.scan_interval_var.get()) * 60 if hasattr(self, 'scan_interval_var') else 300
            for _ in range(interval):
                if not self.muse_inbox_monitoring: break
                time.sleep(1)
    
    def scan_inbox_now(self):
        threading.Thread(target=self._scan_inbox, daemon=True).start()
    
    def _scan_inbox(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server.get(), int(self.imap_port.get() or 993))
            mail.login(self.imap_email.get(), self.imap_pass.get())
            mail.select(self.imap_folder.get())
            
            # Search last 3 days
            since = (datetime.now() - timedelta(days=3)).strftime('%d-%b-%Y')
            _, msg_ids = mail.search(None, f'(SINCE {since})')
            
            keywords = [k.strip().lower() for k in self.imap_keywords.get().split(',')]
            seen_ids = {item.get('msg_id') for item in self.muse_inbox_items}
            
            for num in msg_ids[0].split()[-50:]:  # Last 50 emails
                msg_id = num.decode()
                if msg_id in seen_ids: continue
                
                _, data = mail.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(data[0][1])
                
                subject = ''
                raw_subject = msg.get('Subject', '')
                if raw_subject:
                    decoded = decode_header(raw_subject)
                    subject = str(decoded[0][0], decoded[0][1] or 'utf-8') if isinstance(decoded[0][0], bytes) else str(decoded[0][0])
                
                from_addr = msg.get('From', '')
                date_str = msg.get('Date', '')[:16]
                
                # Check for keyword matches
                check_text = (subject + ' ' + from_addr).lower()
                triggers = [k for k in keywords if k in check_text]
                
                if triggers:
                    item = {'msg_id': msg_id, 'date': date_str, 'from': from_addr[:30],
                           'subject': subject[:60], 'triggers': ', '.join(triggers)}
                    self.muse_inbox_items.append(item)
                    
                    self.root.after(0, self._update_inbox_tree, item)
                    
                    self.add_muse_idea('Inbox', 'Email Trigger',
                        f"Email about '{subject[:50]}' — triggered by: {', '.join(triggers)}. "
                        f"Could inspire: article, response post, or content piece.")
            
            mail.logout()
            self.save_muse_data()
            self.root.after(0, lambda: self.muse_last_scan.configure(text=f"Last scan: {datetime.now().strftime('%H:%M')}"))
        except Exception as e:
            self.root.after(0, lambda: self.imap_status.configure(text=f"Scan error: {str(e)[:40]}", style='Warning.TLabel'))
    
    def _update_inbox_tree(self, item):
        try:
            self.inbox_tree.insert('', 0, values=(item['date'], item['from'], item['subject'], item['triggers']))
        except: pass
    
    def gen_idea_from_email(self):
        sel = self.inbox_tree.selection()
        if sel:
            vals = self.inbox_tree.item(sel[0])['values']
            self.st(self.inbox_idea_out, f"Generate content ideas from email '{vals[2]}' (triggered by: {vals[3]}). Consider: article, LinkedIn post, newsletter, book chapter.\n\nCopy to Claude or ChatGPT.")
    
    # ── Idea Generator ──
    
    def gen_ideas(self):
        b = self.gb(); seed = self.gt(self.idea_seed)
        source_context = ''
        if self.idea_source.get() == 'books':
            titles = ', '.join(b.get('title', '') for b in self.books[:10])
            source_context = f"\n\nBased on existing library: {titles}"
        elif self.idea_source.get() == 'inbox':
            subjects = ', '.join(i.get('subject', '') for i in self.muse_inbox_items[-10:])
            source_context = f"\n\nInspired by recent emails: {subjects}"
        elif self.idea_source.get() == 'files':
            files = ', '.join(c.get('file', '') for c in self.muse_file_changes[-10:])
            source_context = f"\n\nBased on recent file activity: {files}"
        elif self.idea_source.get() == 'competitors':
            comps = ', '.join(c.get('title', '') for c in self.competitors[:5])
            source_context = f"\n\nFilling gaps vs competitors: {comps}"
        
        self.st(self.ideas_out, f"""Generate {self.idea_count.get()} {self.idea_type.get()} ideas:

AUTHOR: {b.get('author', 'Mani Padisetti')}
EXPERTISE: AI governance, cybersecurity, consulting, writing, philosophy
SEED: {seed or 'Open to anything'}
{source_context}

For each idea provide:
1. Title/headline
2. One-line pitch
3. Target audience
4. Why now (timeliness)
5. Unique angle

Australian perspective. Artfully genuine voice.

Copy to Claude or ChatGPT.""")
    
    def surprise_ideas(self):
        import random
        angles = ['What if you combined two unrelated topics?', 'What would the contrarian take be?',
                  "What personal story haven't you told?", "What question do clients always ask?",
                  'What did you learn the hard way?', 'What trend is everyone wrong about?',
                  'What would you tell your younger self?', 'What hidden pattern do you see?']
        self.st(self.ideas_out, f"SURPRISE PROMPT: {random.choice(angles)}\n\nNow generate 5 content ideas from this angle for '{self.gbt()}'.\n\nCopy to Claude or ChatGPT.")
    
    def save_ideas_to_feed(self):
        text = self.gt(self.ideas_out)
        if text:
            for line in text.split('\n'):
                if line.strip() and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    self.add_muse_idea('Generator', self.idea_type.get().title(), line.strip()[:200])
            self.refresh_muse_feed()
    
    def refresh_saved_ideas(self):
        self.saved_ideas_list.delete(0, 'end')
        for idea in self.muse_ideas[-20:]:
            self.saved_ideas_list.insert('end', f"[{idea['type']}] {idea['idea'][:80]}")
    
    # ── Library Ideas ──
    
    def muse_library_ideas(self):
        if not self.books: return
        
        # Analyse library for patterns
        titles = [b.get('title', '') for b in self.books]
        descriptions = [b.get('description', '') for b in self.books]
        all_text = ' '.join(titles + descriptions).lower()
        
        # Find common themes
        words = re.findall(r'\b[a-z]{4,}\b', all_text)
        freq = {}
        stop = {'this', 'that', 'with', 'from', 'your', 'have', 'will', 'they', 'been', 'their', 'about', 'would', 'could', 'which', 'there'}
        for w in words:
            if w not in stop: freq[w] = freq.get(w, 0) + 1
        
        top = sorted(freq.items(), key=lambda x: -x[1])[:10]
        themes = [w for w, c in top]
        
        ideas = [
            f"You write a lot about {themes[0]} and {themes[1]} — have you written their intersection?",
            f"Your library has {len(self.books)} books. Time for a 'Complete Guide' compilation?",
            f"Recurring theme: {themes[2] if len(themes) > 2 else 'technology'}. What's the controversial take you haven't published?",
            f"Cross-format opportunity: Turn your most popular book into a LinkedIn article series.",
            f"Gap analysis: Your themes ({', '.join(themes[:5])}) could yield a new book on their convergence.",
        ]
        
        for idea in ideas:
            self.add_muse_idea('Library Analysis', 'Pattern', idea)
        
        self.refresh_muse_feed()
    
    # ── Pattern Lab ──
    
    def analyse_library_patterns(self):
        if not self.books: self.st(self.pattern_out, "Add books to your library first."); return
        titles = [b.get('title', '') for b in self.books]
        all_text = ' '.join(b.get('description', '') for b in self.books).lower()
        words = re.findall(r'\b[a-z]{4,}\b', all_text)
        freq = {}
        for w in words:
            if w not in {'this', 'that', 'with', 'from', 'your', 'have', 'will'}: freq[w] = freq.get(w, 0) + 1
        top = sorted(freq.items(), key=lambda x: -x[1])[:20]
        
        r = [f"LIBRARY ANALYSIS: {len(self.books)} books", ""]
        r.append("TOP THEMES:")
        for w, c in top: r.append(f"  {w}: {c}")
        r.append(f"\nBOOK TITLES:\n" + '\n'.join(f"  • {t}" for t in titles))
        r.append("\nOPPORTUNITIES:")
        r.append("  • Combine top themes into a new book")
        r.append("  • Turn underexplored themes into articles")
        r.append("  • Create a reader magnet from popular topics")
        self.st(self.pattern_out, '\n'.join(r))
    
    def find_topic_gaps(self):
        b = self.gb()
        self.st(self.pattern_out, f"""Analyse these books for topic GAPS:

LIBRARY: {', '.join(b.get('title','') for b in self.books[:15])}
EXPERTISE: AI governance, cybersecurity, consulting, Vipassana, writing

What topics has this author NOT written about but should? What's missing?
What adjacent topics would attract new readers?

Copy to Claude or ChatGPT.""")
    
    def find_series_opps(self):
        self.st(self.pattern_out, f"""Given this library:

{chr(10).join('• ' + b.get('title','') for b in self.books[:15])}

Which books could become series? What sequels, prequels, or spin-offs make sense?
What linked non-fiction series would build authority?

Copy to Claude or ChatGPT.""")
    
    def cross_pollinate(self):
        import random
        if len(self.books) < 2: self.st(self.pattern_out, "Need 2+ books"); return
        b1, b2 = random.sample(self.books[:10], min(2, len(self.books)))
        self.st(self.pattern_out, f"""CROSS-POLLINATION CHALLENGE:

Book A: {b1.get('title','')}
Book B: {b2.get('title','')}

What new book/article/content would combine these two perspectives?
Think: unexpected connections, shared themes, contrasting lessons.

Copy to Claude or ChatGPT.""")
    
    def seasonal_map(self):
        now = datetime.now()
        months = []
        for i in range(12):
            m = (now.month + i - 1) % 12 + 1
            months.append(datetime(now.year if m >= now.month else now.year + 1, m, 1).strftime('%B %Y'))
        
        self.st(self.pattern_out, f"""SEASONAL CONTENT MAP for {self.gb().get('author', 'Mani Padisetti')}

{chr(10).join(f'{m}: [plan content here]' for m in months)}

Consider: seasonal reading trends, industry events, awards seasons, holiday promotions, back-to-school, new year goals.

Generate specific content ideas for each month based on my library of {len(self.books)} books.

Copy to Claude or ChatGPT.""")
    
    # ── Content Calendar ──
    
    def gen_content_calendar(self):
        weeks = int(self.cal_weeks.get()); freq = int(self.cal_freq.get())
        b = self.gb()
        
        cal = f"CONTENT CALENDAR: {weeks} weeks, {freq}x/week\n"
        cal += f"Book focus: {b.get('title', 'General')}\n"
        cal += "=" * 60 + "\n\n"
        
        platforms = ['LinkedIn', 'Instagram', 'Newsletter', 'BookTok', 'X/Twitter']
        content_types = ['Thought leadership', 'Book excerpt', 'Behind the scenes', 'Reader Q&A',
                        'Industry insight', 'Personal story', 'How-to/tips', 'Book recommendation',
                        'Controversial take', 'Community question']
        
        import random
        today = datetime.now()
        for week in range(weeks):
            cal += f"WEEK {week+1} ({(today + timedelta(weeks=week)).strftime('%b %d')})\n"
            for day in range(freq):
                post_date = today + timedelta(weeks=week, days=day * (7 // freq))
                platform = platforms[day % len(platforms)]
                content = random.choice(content_types)
                cal += f"  {post_date.strftime('%a %b %d')} | {platform:12s} | {content}\n"
            cal += "\n"
        
        cal += "\nCustomise this calendar, then copy to Claude for detailed content briefs."
        self.st(self.cal_out, cal)
    
    def push_to_scheduler(self):
        text = self.gt(self.cal_out)
        if not text: return
        count = 0
        for line in text.split('\n'):
            if '|' in line and any(p in line for p in ['LinkedIn', 'Instagram', 'BookTok', 'X/Twitter', 'Newsletter']):
                parts = [p.strip() for p in line.strip().split('|')]
                if len(parts) >= 3:
                    self.scheduled_posts.append({
                        'date': parts[0], 'time': '10:00', 'platform': parts[1],
                        'content': parts[2], 'status': 'Planned'
                    })
                    count += 1
        self.save_schedule()
        messagebox.showinfo("Scheduler", f"Pushed {count} items to scheduler")
    
    # ── Muse Feed Actions ──
    
    def muse_expand_idea(self):
        sel = self.muse_feed.selection()
        if sel:
            vals = self.muse_feed.item(sel[0])['values']
            idea = self.muse_ideas[len(self.muse_ideas) - 1 - int(sel[0])]['idea']
            messagebox.showinfo("Idea", idea)
    
    def muse_idea_to_gen(self):
        sel = self.muse_feed.selection()
        if sel:
            idea = self.muse_ideas[len(self.muse_ideas) - 1 - int(sel[0])]['idea']
            self.st(self.idea_seed, idea)
            self.muse_nb.select(3)  # Idea Generator tab
    
    def muse_export_ideas(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json"), ("CSV", "*.csv")])
        if f:
            if f.endswith('.csv'):
                with open(f, 'w', newline='', encoding='utf-8') as fh:
                    w = csv.writer(fh); w.writerow(['Time', 'Source', 'Type', 'Idea'])
                    for i in self.muse_ideas: w.writerow([i['time'], i['source'], i['type'], i['idea']])
            else:
                with open(f, 'w', encoding='utf-8') as fh: json.dump(self.muse_ideas, fh, indent=2)
            messagebox.showinfo("Export", f"Exported {len(self.muse_ideas)} ideas")
    
    def muse_clear_feed(self):
        if messagebox.askyesno("Clear", "Clear all ideas from feed?"):
            self.muse_ideas = []; self.save_muse_data(); self.refresh_muse_feed()
    
    # ═══════════════════════════════════════════════════════════════
    # LOGIC - EXPORT
    # ═══════════════════════════════════════════════════════════════
    
    def export_csv(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if f:
            with open(f, 'w', newline='', encoding='utf-8') as fh:
                w = csv.writer(fh); w.writerow(['Title', 'Author', 'ASIN', 'Description', 'Keywords', 'Status'])
                for b in self.books: w.writerow([b.get('title',''), b.get('author',''), b.get('asin',''), b.get('description',''), '; '.join(b.get('keywords',[])), b.get('status','')])
    
    def export_analytics(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if f:
            with open(f, 'w', encoding='utf-8') as fh:
                json.dump({'keywords': self.keyword_history, 'competitors': self.competitors, 'snapshots': self.snapshots, 'linkedin': self.linkedin_campaigns}, fh, indent=2)
    
    def backup_all(self):
        f = filedialog.asksaveasfilename(defaultextension=".json", initialfile=f"author_studio_{datetime.now().strftime('%Y%m%d')}.json", filetypes=[("JSON", "*.json")])
        if f:
            with open(f, 'w', encoding='utf-8') as fh:
                json.dump({'books': self.books, 'schedule': self.scheduled_posts,
                          'analytics': {'keywords': self.keyword_history, 'competitors': self.competitors, 'snapshots': self.snapshots},
                          'linkedin': self.linkedin_campaigns, 'muse': {'ideas': self.muse_ideas, 'inbox': self.muse_inbox_items,
                          'files': self.muse_file_changes, 'patterns': self.muse_patterns},
                          'business': {'royalties': self.royalties, 'series': self.series_data, 'characters': self.characters,
                          'rights': self.rights, 'aria_reports': self.aria_reports}}, fh, indent=2)
    
    # ═══════════════════════════════════════════════════════════════
    # PHASE 5 - BUSINESS LOGIC
    # ═══════════════════════════════════════════════════════════════
    
    def save_business_data(self):
        with open(self.business_file, 'w') as f:
            json.dump({'royalties': self.royalties, 'series': self.series_data, 'characters': self.characters,
                       'rights': self.rights, 'aria_reports': self.aria_reports}, f, indent=2)
    
    def load_business_data(self):
        if self.business_file.exists():
            try:
                with open(self.business_file) as f:
                    d = json.load(f)
                    self.royalties = d.get('royalties', [])
                    self.series_data = d.get('series', [])
                    self.characters = d.get('characters', [])
                    self.rights = d.get('rights', [])
                    self.aria_reports = d.get('aria_reports', [])
            except: pass
    
    # ── Backlist / Royalties ──
    
    def add_royalty(self):
        if not self.roy_book.get() or not self.roy_amount.get(): return
        self.royalties.append({
            'period': self.roy_period.get(), 'book': self.roy_book.get(),
            'platform': self.roy_platform.get(), 'amount': float(self.roy_amount.get() or 0)
        })
        self.save_business_data(); self.refresh_royalties()
        self.roy_book.set(''); self.roy_amount.set('')
    
    def del_royalty(self):
        sel = self.royalty_tree.selection()
        if sel:
            self.royalties.pop(int(sel[0]))
            self.save_business_data(); self.refresh_royalties()
    
    def refresh_royalties(self):
        for i in self.royalty_tree.get_children(): self.royalty_tree.delete(i)
        total = 0
        for i, r in enumerate(sorted(self.royalties, key=lambda x: x.get('period', ''), reverse=True)):
            self.royalty_tree.insert('', 'end', iid=str(i), values=(r['period'], r['book'], r['platform'], f"${r['amount']:.2f}"))
            total += r.get('amount', 0)
        self.royalty_summary.configure(text=f"Total: ${total:,.2f}")
    
    def export_royalties(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if f:
            with open(f, 'w', newline='', encoding='utf-8') as fh:
                w = csv.writer(fh); w.writerow(['Period', 'Book', 'Platform', 'Amount'])
                for r in self.royalties: w.writerow([r['period'], r['book'], r['platform'], r['amount']])
    
    # ── Series Bible ──
    
    def add_series(self):
        self.series_data.append({'name': 'New Series', 'genre': '', 'status': 'Planning', 'bible': '', 'timeline': '', 'world': ''})
        self.series_listbox.insert('end', 'New Series')
        self.save_business_data()
    
    def del_series(self):
        sel = self.series_listbox.curselection()
        if sel:
            self.series_data.pop(sel[0])
            self.series_listbox.delete(sel[0])
            self.save_business_data()
    
    def on_series_select(self, e):
        sel = self.series_listbox.curselection()
        if sel:
            s = self.series_data[sel[0]]
            self.series_name.set(s.get('name', ''))
            self.series_genre.set(s.get('genre', ''))
            self.series_status.set(s.get('status', 'In Progress'))
            self.st(self.series_bible, s.get('bible', ''))
            self.st(self.series_timeline, s.get('timeline', ''))
            self.st(self.series_world, s.get('world', ''))
    
    def save_series(self):
        sel = self.series_listbox.curselection()
        if sel:
            self.series_data[sel[0]] = {
                'name': self.series_name.get(), 'genre': self.series_genre.get(),
                'status': self.series_status.get(), 'bible': self.gt(self.series_bible),
                'timeline': self.gt(self.series_timeline), 'world': self.gt(self.series_world)
            }
            self.series_listbox.delete(sel[0])
            self.series_listbox.insert(sel[0], self.series_name.get())
            self.save_business_data()
    
    # ── Characters ──
    
    def add_character(self):
        self.characters.append({'name': 'New Character', 'role': '', 'book': '', 'age': '', 'appearance': '', 'arc': '', 'relationships': ''})
        self.save_business_data(); self.refresh_characters()
    
    def del_character(self):
        sel = self.char_tree.selection()
        if sel:
            self.characters.pop(int(sel[0]))
            self.save_business_data(); self.refresh_characters()
    
    def on_char_select(self, e):
        sel = self.char_tree.selection()
        if sel:
            c = self.characters[int(sel[0])]
            for key, var in self.char_fields.items(): var.set(c.get(key, ''))
            self.st(self.char_arc, c.get('arc', ''))
            self.st(self.char_rels, c.get('relationships', ''))
    
    def save_character(self):
        sel = self.char_tree.selection()
        if sel:
            idx = int(sel[0])
            self.characters[idx] = {key: var.get() for key, var in self.char_fields.items()}
            self.characters[idx]['arc'] = self.gt(self.char_arc)
            self.characters[idx]['relationships'] = self.gt(self.char_rels)
            self.save_business_data(); self.refresh_characters()
    
    def refresh_characters(self):
        for i in self.char_tree.get_children(): self.char_tree.delete(i)
        for i, c in enumerate(self.characters):
            self.char_tree.insert('', 'end', iid=str(i), values=(c.get('name',''), c.get('role',''), c.get('book','')))
    
    # ── KDP Export ──
    
    def export_kdp(self):
        sel = self.kdp_book_list.curselection()
        if not sel: return
        b = self.books[sel[0]]
        out = ["=" * 60, f"KDP EXPORT: {b.get('title', '')}", "=" * 60, ""]
        if self.kdp_metadata.get():
            out.append("METADATA:")
            out.append(f"  Title: {b.get('title', '')}")
            out.append(f"  Subtitle: {b.get('subtitle', '')}")
            out.append(f"  Author: {b.get('author', '')}")
            out.append(f"  Series: {b.get('series', '')}")
            out.append(f"  ASIN: {b.get('asin', '')}")
            out.append(f"  ISBN: {b.get('isbn', '')}")
            out.append("")
        if self.kdp_keywords.get():
            out.append("KEYWORDS (7 phrases, 50 chars each):")
            for i, kw in enumerate(b.get('keywords', [])[:7], 1):
                out.append(f"  {i}. {kw}")
            out.append("")
        if self.kdp_description.get():
            out.append("DESCRIPTION:")
            out.append(b.get('description', ''))
            out.append("")
        if self.kdp_categories.get():
            out.append("SUGGESTED CATEGORIES:")
            out.append("  (Use Publisher Rocket or KDP category search)")
            out.append("  1. [Primary category]")
            out.append("  2. [Secondary category]")
        self.st(self.kdp_preview, '\n'.join(out))
    
    def export_all_kdp(self):
        f = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt")])
        if f:
            with open(f, 'w', encoding='utf-8') as fh:
                for b in self.books:
                    fh.write(f"{'='*60}\n{b.get('title','')}\n{'='*60}\n")
                    fh.write(f"Author: {b.get('author','')}\nASIN: {b.get('asin','')}\n")
                    fh.write(f"Keywords: {', '.join(b.get('keywords',[]))}\n")
                    fh.write(f"Description:\n{b.get('description','')}\n\n")
            messagebox.showinfo("Export", f"Exported {len(self.books)} books")
    
    # ── Rights ──
    
    def add_right(self):
        if not self.right_book.get(): return
        self.rights.append({
            'book': self.right_book.get(), 'type': self.right_type.get(),
            'territory': self.right_territory.get(), 'status': self.right_status.get(),
            'licensee': self.right_licensee.get(), 'expiry': self.right_expiry.get()
        })
        self.save_business_data(); self.refresh_rights()
        for v in [self.right_book, self.right_territory, self.right_licensee, self.right_expiry]: v.set('')
    
    def del_right(self):
        sel = self.rights_tree.selection()
        if sel:
            self.rights.pop(int(sel[0]))
            self.save_business_data(); self.refresh_rights()
    
    def refresh_rights(self):
        for i in self.rights_tree.get_children(): self.rights_tree.delete(i)
        for i, r in enumerate(self.rights):
            self.rights_tree.insert('', 'end', iid=str(i), values=(r['book'], r['type'], r['territory'], r['status'], r['licensee'], r['expiry']))
    
    def export_rights(self):
        f = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
        if f:
            with open(f, 'w', newline='', encoding='utf-8') as fh:
                w = csv.writer(fh); w.writerow(['Book', 'Type', 'Territory', 'Status', 'Licensee', 'Expiry'])
                for r in self.rights: w.writerow([r['book'], r['type'], r['territory'], r['status'], r['licensee'], r['expiry']])
    
    # ── ARIA Analytics ──
    
    def aria_portfolio(self):
        if not self.books: self.st(self.aria_out, "Add books first."); return
        r = ["📊 PORTFOLIO ANALYSIS", "=" * 50, ""]
        r.append(f"Total books: {len(self.books)}")
        authors = set(b.get('author', '') for b in self.books)
        r.append(f"Authors: {', '.join(authors)}")
        series = set(b.get('series', '') for b in self.books if b.get('series'))
        r.append(f"Series: {len(series)}")
        if self.royalties:
            total = sum(r.get('amount', 0) for r in self.royalties)
            r.append(f"\n💰 Total royalties tracked: ${total:,.2f}")
        r.append("\n🎯 RECOMMENDATIONS:")
        r.append("• Review underperforming titles for keyword optimization")
        r.append("• Consider bundling related books")
        r.append("• Explore foreign rights for top performers")
        r.append("\nCopy to Claude for deeper analysis.")
        self.st(self.aria_out, '\n'.join(r))
    
    def aria_forecast(self):
        self.st(self.aria_out, f"""💰 REVENUE FORECAST PROMPT

Analyse my author business for revenue forecasting:

PORTFOLIO: {len(self.books)} books
RECENT ROYALTIES: ${sum(r.get('amount',0) for r in self.royalties[-12:]):,.2f} (last 12 entries)

Generate:
1. 12-month revenue projection
2. Best/worst case scenarios
3. Revenue optimization strategies
4. Passive income opportunities

Copy to Claude or ChatGPT for analysis.""")
    
    def aria_opportunities(self):
        self.st(self.aria_out, f"""📈 GROWTH OPPORTUNITIES PROMPT

Analyse for growth:

BOOKS: {', '.join(b.get('title','') for b in self.books[:10])}
SERIES: {len([b for b in self.books if b.get('series')])} books in series

Identify:
1. Underexploited niches
2. Series expansion opportunities  
3. Format opportunities (audio, large print, etc.)
4. International market potential
5. Adjacent product opportunities (courses, consulting)

Copy to Claude or ChatGPT for analysis.""")
    
    def aria_positioning(self):
        self.st(self.aria_out, f"""🎯 MARKET POSITIONING PROMPT

Position my author brand:

BOOKS: {len(self.books)}
GENRES: {', '.join(set(b.get('genre','') for b in self.books if b.get('genre')))}
COMPETITORS: {len(self.competitors)} tracked

Analyse:
1. Current market position
2. Differentiation opportunities
3. Brand positioning statement
4. Target reader profile refinement
5. Competitive advantages

Copy to Claude or ChatGPT for analysis.""")
    
    def aria_quickwins(self):
        r = ["⚡ QUICK WINS", "=" * 50, ""]
        r.append("Immediate actions for results:\n")
        if any(not b.get('keywords') for b in self.books):
            r.append("🔑 KEYWORDS: Some books missing keywords - add all 7 phrases")
        if any(len(b.get('description', '')) < 200 for b in self.books):
            r.append("📝 DESCRIPTIONS: Some descriptions under 200 chars - expand them")
        if not self.scheduled_posts:
            r.append("📅 SCHEDULE: No posts scheduled - plan your content")
        if len(self.books) > 3 and not self.series_data:
            r.append("📚 SERIES: Consider grouping books into a series")
        available_rights = [r for r in self.rights if r.get('status') == 'Available']
        if available_rights:
            r.append(f"🌍 RIGHTS: {len(available_rights)} rights available to license")
        r.append("\n✅ Review each item and take action this week.")
        self.st(self.aria_out, '\n'.join(r))
    
    def aria_trends(self):
        self.st(self.aria_out, f"""🔮 TREND ANALYSIS PROMPT

Analyse publishing trends for my portfolio:

MY GENRES: {', '.join(set(b.get('genre','') for b in self.books if b.get('genre'))) or 'Various'}
MY KEYWORDS: {', '.join(kw for b in self.books for kw in b.get('keywords',[])[:2])}

Research and report:
1. Current genre trends (hot/cooling)
2. Emerging subgenres to watch
3. Reader preference shifts
4. Platform algorithm changes
5. Pricing trend recommendations
6. Marketing channel effectiveness

Copy to Claude or ChatGPT (with web search) for current data.""")
    
    def save_aria_report(self):
        text = self.gt(self.aria_out)
        if text:
            self.aria_reports.append({'type': 'Analysis', 'date': datetime.now().strftime('%Y-%m-%d'), 'content': text})
            self.aria_reports_list.insert('end', f"Analysis - {datetime.now().strftime('%Y-%m-%d')}")
            self.save_business_data()

def main():
    root = tk.Tk()
    try: root.tk.call('tk', 'scaling', 1.5)
    except: pass
    AuthorStudio(root)
    root.mainloop()

if __name__ == "__main__":
    main()
