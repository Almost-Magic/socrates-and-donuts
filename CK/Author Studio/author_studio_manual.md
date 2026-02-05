# Author Studio Complete Edition
## User Manual v1.0

---

# Table of Contents

1. [Introduction](#introduction)
2. [Installation & Setup](#installation--setup)
3. [Quick Start Guide](#quick-start-guide)
4. [Main Tabs Overview](#main-tabs-overview)
5. [Library Tab](#library-tab)
6. [Metadata Tab](#metadata-tab)
7. [Keywords Tab](#keywords-tab)
8. [Quality Tab](#quality-tab)
9. [Marketing Tab](#marketing-tab)
10. [Analytics Tab](#analytics-tab)
11. [Muse Tab](#muse-tab)
12. [Business Tab](#business-tab)
13. [Export Tab](#export-tab)
14. [Data Storage & Backup](#data-storage--backup)
15. [Keyboard Shortcuts](#keyboard-shortcuts)
16. [Troubleshooting](#troubleshooting)
17. [Appendix: AI Prompt Templates](#appendix-ai-prompt-templates)

---

# Introduction

**Author Studio** is a comprehensive desktop application designed for indie authors, self-publishers, and content creators. Built with a modern Linear/Vercel-inspired dark interface, it consolidates all aspects of book management, marketing, analytics, creative intelligence, and business operations into a single powerful tool.

## Who Is This For?

- **Indie authors** managing multiple books
- **Self-publishers** on Amazon KDP, IngramSpark, and other platforms
- **Content creators** who write books, articles, and social media content
- **Author-entrepreneurs** running consulting or coaching businesses alongside their writing

## Key Features

- **9 main tabs** covering the complete author workflow
- **30+ sub-tools** for marketing, analytics, and business
- **Muse Creative Intelligence Engine** that monitors your inbox and files
- **AI-ready prompts** designed for Claude, ChatGPT, or other LLMs
- **Persistent data storage** — your work is saved automatically
- **Dark mode interface** optimised for long writing sessions

---

# Installation & Setup

## System Requirements

- **Operating System:** Windows 10/11, macOS 10.14+, or Linux
- **Python:** Version 3.8 or higher
- **RAM:** 4GB minimum (8GB recommended)
- **Display:** 1400x900 minimum resolution (1600x1000 recommended)

## Installation Steps

### 1. Install Python

If you don't have Python installed:

**Windows:**
```powershell
# Download from python.org or use winget
winget install Python.Python.3.11
```

**macOS:**
```bash
brew install python@3.11
```

**Linux:**
```bash
sudo apt install python3 python3-tk
```

### 2. Run Author Studio

```bash
python author_studio_complete.py
```

The application will create its data directory automatically at:
- **Windows:** `C:\Users\YourName\.author_studio\`
- **macOS/Linux:** `~/.author_studio/`

## First Launch

On first launch, Author Studio will:
1. Create the `.author_studio` data directory
2. Initialise empty data files
3. Display the main interface with the Library tab selected

---

# Quick Start Guide

## 5-Minute Setup

### Step 1: Add Your First Book
1. Click **Library** tab
2. Click **Add book** button
3. Double-click the new book to open Metadata tab
4. Fill in title, author, description
5. Click **Save**

### Step 2: Add Keywords
1. Click **Keywords** tab
2. Enter up to 7 keyword phrases (50 characters each)
3. Click **Save**

### Step 3: Generate Marketing Content
1. Click **Marketing** tab
2. Select **BookTok** sub-tab
3. Choose format and duration
4. Click **Generate**
5. Copy the prompt to Claude or ChatGPT

### Step 4: Set Up Muse Monitoring (Optional)
1. Click **Muse** tab
2. Go to **Files** sub-tab
3. Click **Add folder** to watch your writing directory
4. Click **▶ Start** to begin monitoring

---

# Main Tabs Overview

| Tab | Purpose | Sub-tabs |
|-----|---------|----------|
| **Library** | Manage your book catalogue | — |
| **Metadata** | Edit book details | — |
| **Keywords** | Amazon keyword optimisation | — |
| **Quality** | AI content detection | — |
| **Marketing** | Social media & advertising | BookTok, Instagram, Scheduler, Email, Promo, Ads, Reviews |
| **Analytics** | Track performance | Sentiment, Keywords, Competitors, Avatar, Changes, LinkedIn |
| **✦ Muse** | Creative intelligence | Dashboard, Inbox, Files, Ideas, Patterns, Calendar |
| **Business** | Royalties & rights | Backlist, Series, Characters, KDP Export, Rights, ARIA |
| **Export** | Backup & export | — |

---

# Library Tab

The Library tab is your central book catalogue.

## Features

### Book List
- Displays all books with title, author, series, status, and quality score
- Click a book to select it
- Double-click to open Metadata tab for editing

### Actions

| Button | Function |
|--------|----------|
| **Add book** | Create a new book entry |
| **Import folder** | Scan a folder for .txt, .md, .docx files and import as books |
| **Import CSV** | Import books from a CSV file with columns: title, author |
| **Delete** | Remove the selected book (with confirmation) |

### Search
- Type in the search box to filter books by title or author
- Search is instant — no need to press Enter

## Workflow Tips

1. **Organise by series** — Use the Series field in Metadata to group related books
2. **Track status** — Use Draft, Published, Out of Print to track lifecycle
3. **Quality scores** — Run content through the Quality tab to get AI detection scores

---

# Metadata Tab

Edit comprehensive details for the selected book.

## Fields

### Left Panel — Book Details

| Field | Description | Example |
|-------|-------------|---------|
| **Title** | Main book title | "The AI Governance Handbook" |
| **Subtitle** | Secondary title | "A Practical Guide for Business Leaders" |
| **Author** | Author name(s) | "Mani Padisetti" |
| **Series** | Series name if applicable | "Almost Magic Guides" |
| **ASIN** | Amazon Standard Identification Number | "B0XXXXXXXX" |
| **ISBN** | International Standard Book Number | "978-0-XXXX-XXXX-X" |
| **Publisher** | Publishing imprint | "Almost Magic Press" |
| **Pub Date** | Publication date | "2025-02-15" |

### Right Panel — Description

- Write your book description/blurb here
- Supports multiple paragraphs
- Tip: Keep to 150-200 words for Amazon optimisation

## Saving

Click **Save** to store all metadata. Changes are written to `~/.author_studio/books.json`.

---

# Keywords Tab

Optimise your book's discoverability with Amazon's 7 keyword phrases.

## Amazon Keyword Rules

1. **7 phrases maximum** per book
2. **50 characters maximum** per phrase
3. **No commas** within a phrase (Amazon treats commas as separators)
4. **No repetition** of words from your title
5. **No competitor names** or trademarked terms

## Interface

- 7 numbered input fields
- Character counter shows current/maximum (e.g., "32/50")
- Counter turns **red** if you exceed 50 characters

## Keyword Research Tips

1. **Use Amazon's search bar** — Start typing and note autocomplete suggestions
2. **Check competitor books** — Look at their categories and "Customers also bought"
3. **Use tools** — Publisher Rocket, KDP Rocket, or free alternatives
4. **Think like a reader** — What would they search for?

## Example Keywords for a Cybersecurity Book

```
1. cybersecurity for small business owners
2. protect company from hackers guide
3. IT security basics beginners
4. data breach prevention strategies
5. network security fundamentals
6. cyber attack protection business
7. information security management
```

---

# Quality Tab

Detect AI-generated content and assess writing quality.

## How It Works

The Quality checker scans your text for:
- **AI-typical phrases** (e.g., "delve," "it's important to note," "leverage")
- **Low sentence variance** (AI tends to write uniform sentence lengths)
- **Overused patterns** common in AI-generated text

## Using the Quality Checker

1. Paste your text into the left panel (or click **Load file** to import)
2. Click **Check quality**
3. Review the scores:
   - **AI Score** — Higher = more AI-like (aim for under 30%)
   - **Quality Score** — 100 minus AI score (aim for 70%+)

## Score Interpretation

| AI Score | Meaning | Action |
|----------|---------|--------|
| 0-20% | Highly human | Excellent — publish as-is |
| 21-40% | Mostly human | Good — minor edits may help |
| 41-60% | Mixed signals | Review flagged phrases |
| 61-80% | AI-like | Significant rewriting needed |
| 81-100% | Likely AI | Complete rewrite recommended |

## Flagged Phrases

The checker identifies specific AI-typical phrases in your text:
- delve, dive into
- it's important to note
- in conclusion
- leverage, utilize, facilitate
- comprehensive, robust, seamless
- innovative, cutting-edge, paradigm
- synergy, ecosystem, landscape
- navigate, journey, empower
- unlock, unleash, game-changing

## Tips for Reducing AI Score

1. **Vary sentence length** — Mix short punchy sentences with longer ones
2. **Use specific examples** — AI tends to be vague; specifics sound human
3. **Add personal voice** — Anecdotes, opinions, Australian idioms
4. **Replace flagged words** — Use simpler alternatives

---

# Marketing Tab

Seven sub-tabs for comprehensive marketing support.

## BookTok Sub-tab

Generate TikTok/BookTok video scripts.

### Options

| Setting | Choices |
|---------|---------|
| **Format** | Hook, Review, Rec (recommendation), BTS (behind the scenes) |
| **Duration** | 15s, 30s, 60s |
| **Context** | Optional notes for customisation |

### Output
A prompt ready to paste into Claude or ChatGPT that generates:
- Opening hook (first 3 seconds)
- Main content structure
- Visual/action suggestions
- Trending hashtags
- Call-to-action

---

## Instagram Sub-tab

Generate Instagram content.

### Options

| Setting | Choices |
|---------|---------|
| **Type** | Post, Carousel, Reel |
| **Theme** | Promo, Life (author life), Tips |
| **Hashtags** | 5, 15, or 30 hashtags |

### Output
A prompt that generates:
- Caption with hook
- Carousel slide content (if applicable)
- Hashtag set organised by reach
- Best posting times

---

## Scheduler Sub-tab

Plan and track social media posts.

### Adding a Post

1. Select **platform** (Instagram, TikTok, X, LinkedIn, Facebook)
2. Enter **date** (YYYY-MM-DD format)
3. Enter **time** (HH:MM format)
4. Type your **content**
5. Click **Add**

### Managing Posts

| Button | Function |
|--------|----------|
| **Delete** | Remove selected post |
| **Mark posted** | Change status from "Scheduled" to "Posted" |

### Status Values

- **Scheduled** — Planned but not yet posted
- **Posted** — Successfully published
- **Planned** — From content calendar (needs content)

---

## Email Sub-tab

Listmonk email marketing integration.

### Listmonk Configuration

1. Enter your Listmonk **URL** (e.g., `http://localhost:9000`)
2. Enter **username** and **password**
3. Click **Test** to verify connection
4. Click **Open** to launch Listmonk in browser

### Email Templates

| Type | Use Case |
|------|----------|
| **Launch** | New book announcement |
| **Newsletter** | Regular subscriber update |
| **ARC** | Advance Reader Copy invitation |
| **Sale** | Price promotion announcement |

Click **Generate** to create an AI prompt for your selected email type.

---

## Promo Sub-tab

Directory of book promotion sites.

### Included Sites

| Site | Cost | Lead Time |
|------|------|-----------|
| BookBub | Paid (varies) | 30 days |
| Freebooksy | $80-160 | 14 days |
| Bargain Booksy | $40-80 | 14 days |
| Robin Reads | $30-60 | 7 days |
| Book Gorilla | $50-75 | 7 days |
| Fussy Librarian | $12-52 | 3 days |
| BookSends | $10-50 | 3 days |

### Actions

| Button | Function |
|--------|----------|
| **Open** | Launch selected site in browser |
| **Calendar** | Generate a submission schedule |

---

## Ads Sub-tab

Generate Amazon advertising copy.

### Options

| Setting | Choices |
|---------|---------|
| **Type** | Sponsored Products, Lockscreen |
| **Target** | Describe your target audience |
| **Variations** | 1, 3, or 5 ad variations |

### Output
AI prompt that generates:
- Multiple ad headlines (150 characters max)
- Targeting suggestions
- Keyword recommendations

---

## Reviews Sub-tab

Generate review request templates.

### Template Types

| Type | When to Use |
|------|-------------|
| **ARC Invite** | Before launch, recruiting advance readers |
| **Post-Purchase** | In back matter or follow-up email |
| **Newsletter** | Requesting reviews from subscribers |
| **Back of Book** | Text for the end of your book |

### Tone Options
- **Warm** — Friendly, personal
- **Pro** — Professional, business-like
- **Casual** — Relaxed, conversational

---

# Analytics Tab

Six sub-tabs for tracking and analysis.

## Sentiment Sub-tab

Analyse reader reviews for sentiment.

### How to Use

1. Paste reviews into the left panel (one per line or separated by blank lines)
2. Click **Analyse**
3. View breakdown: Positive / Neutral / Negative

### AI Prompt
Click **AI prompt** to generate a detailed analysis request for Claude/ChatGPT that extracts:
- Key themes
- Common complaints
- Suggested improvements
- Quotable praise

---

## Keywords Sub-tab

Track your Amazon keyword rankings over time.

### Logging a Position

1. Enter the **keyword** phrase
2. Enter current **position** (1-100)
3. Click **Log**

### Tracking
- View historical positions in the table
- **Change** column shows movement (↑3, ↓2, =)
- Track trends to see which keywords are improving

---

## Competitors Sub-tab

Monitor competing books.

### Adding a Competitor

1. Enter book **title**
2. Enter **ASIN** (Amazon product ID)
3. Enter current **price**
4. Enter **rank** (BSR)
5. Click **Add**

### Updates
Manually update prices and ranks periodically to track trends.

---

## Avatar Sub-tab

Build detailed reader personas.

### Fields

| Field | Description |
|-------|-------------|
| **Name** | Persona name (e.g., "Sarah, 34") |
| **Demographics** | Age, location, occupation |
| **Reading** | Genres, frequency, format preferences |
| **Pain** | Problems your book solves |
| **Desires** | What they want to feel/achieve |
| **Online** | Social platforms they use |
| **Triggers** | What makes them buy |

### Output
Click **Build** to compile the avatar, or **AI prompt** to generate a deeper analysis.

---

## Changes Sub-tab

"What Changed?" snapshot comparison.

### Taking a Snapshot

1. Enter current values for:
   - BSR (Best Seller Rank)
   - Reviews (count)
   - Rating (average)
   - Price
   - KENP (Kindle Edition Normalised Pages read)
   - Sales (if known)
2. Click **Snapshot**

### Comparing
Click **Compare** to see changes between your two most recent snapshots:
- ✓ indicates improvement
- ⚠ indicates decline
- Shows absolute change values

---

## LinkedIn Sub-tab

Generate LinkedIn advertising content.

### Options

| Setting | Choices |
|---------|---------|
| **Type** | Thought Leader, Book Promo, Service |
| **Format** | Post, Article, Carousel, Video |
| **Audience** | Describe your target audience |
| **Objective** | What you want to achieve |

### Actions

| Button | Function |
|--------|----------|
| **Generate** | Create content prompt |
| **Script** | Generate video script prompt |

---

# Muse Tab

The Creative Intelligence Engine — your AI-powered writing assistant.

## Dashboard Sub-tab

Central command for Muse.

### Status Panel
- **Files** — File watcher status (On/Off)
- **Inbox** — Email monitor status (On/Off)
- **Ideas** — Total ideas generated
- **Last** — Time of last scan

### Master Controls

| Button | Function |
|--------|----------|
| **▶ Start all** | Begin file and inbox monitoring |
| **■ Stop** | Halt all monitoring |
| **⟳ Scan now** | Run immediate scan |
| **Library ideas** | Generate ideas from your book catalogue |

### Ideas Feed
- Displays all generated ideas with timestamp, source, type, and summary
- Click an idea to expand
- **To generator** — Send idea to Idea Generator for expansion
- **Export** — Save all ideas to JSON or CSV
- **Clear** — Remove all ideas from feed

---

## Inbox Sub-tab

Monitor your email for writing triggers.

### IMAP Configuration

| Field | Example |
|-------|---------|
| **Server** | imap.gmail.com |
| **Port** | 993 |
| **Email** | your.email@gmail.com |
| **Password** | Your app password |
| **Folder** | INBOX |

### Gmail Setup
For Gmail, you need an **App Password**:
1. Go to Google Account → Security → 2-Step Verification
2. At the bottom, click "App passwords"
3. Generate a password for "Mail"
4. Use this password in Author Studio

### Watch Keywords
Comma-separated list of keywords to watch for:
```
book, writing, publish, author, review, manuscript, reader, amazon, kindle, AI, cybersecurity, consulting, client
```

### Scan Interval
Choose how often to check: 1 minute, 5 minutes, or 15 minutes.

---

## Files Sub-tab

Monitor your writing folders for changes.

### Setting Up

1. Click **Add folder** to add a directory to watch
2. Set **file types** (default: `.txt, .md, .docx`)
3. Click **▶ Start** to begin watching

### What Gets Detected

| Event | Trigger |
|-------|---------|
| **New** | New file created in watched folder |
| **Modified** | Existing file changed |

### Output
Each detection creates an idea in the feed with:
- Filename
- Word count
- Suggestion for related content

---

## Ideas Sub-tab

Generate content ideas on demand.

### Options

| Setting | Choices |
|---------|---------|
| **Type** | Book, Article, Post, Newsletter |
| **Seed** | Starting topic or context |
| **Based on** | Scratch, Books, Inbox, Files |
| **Generate** | 3, 5, or 10 ideas |

### Surprise Me
Click **Surprise me** for random creative prompts:
- "What if you combined two unrelated topics?"
- "What would the contrarian take be?"
- "What personal story haven't you told?"
- "What question do clients always ask?"

---

## Patterns Sub-tab

Analyse your writing patterns and find opportunities.

### Analysis Tools

| Button | Function |
|--------|----------|
| **Analyse library** | Find common themes across your books |
| **Find topic gaps** | Identify what you haven't written about |
| **Series opportunities** | Suggest book series or sequels |
| **Cross-pollinate** | Combine two random books for new ideas |
| **Seasonal map** | Generate 12-month content themes |

---

## Calendar Sub-tab

Auto-generate content calendars.

### Settings

| Setting | Options |
|---------|---------|
| **Weeks** | 2, 4, 8, or 12 weeks |
| **Posts/week** | 1, 3, 5, or 7 posts |

### Output
A structured calendar with:
- Date
- Platform (rotates through LinkedIn, Instagram, Newsletter, BookTok, X)
- Content type (Thought leadership, Book excerpt, Behind the scenes, etc.)

### Push to Scheduler
Click **Push to scheduler** to automatically create scheduled posts from the calendar.

---

# Business Tab

Six sub-tabs for author business management.

## Backlist Sub-tab

Track royalties across all books and platforms.

### Adding a Royalty Entry

| Field | Description |
|-------|-------------|
| **Book** | Book title |
| **Period** | Month (YYYY-MM format) |
| **Platform** | Amazon, Apple, Kobo, etc. |
| **Amount** | Royalty amount in dollars |

### Features
- Running **total** displayed at bottom
- **Export CSV** for accounting/tax purposes
- Sort by period (most recent first)

---

## Series Sub-tab

Maintain series bibles for continuity.

### Series Information

| Field | Description |
|-------|-------------|
| **Name** | Series title |
| **Genre** | Primary genre |
| **Status** | Planning, In Progress, Complete |

### Bible Content

| Section | Purpose |
|---------|---------|
| **Series Bible** | Overall series notes, themes, rules |
| **Timeline** | Chronological events |
| **World-building** | Settings, systems, lore |

---

## Characters Sub-tab

Database of all characters across your books.

### Character Fields

| Field | Description |
|-------|-------------|
| **Name** | Character name |
| **Role** | Protagonist, Antagonist, Supporting, etc. |
| **Book/Series** | Where they appear |
| **Age** | Character's age |
| **Appearance** | Physical description |
| **Background & Arc** | History and character development |
| **Relationships** | Connections to other characters |

---

## KDP Export Sub-tab

Export books in Amazon KDP-ready format.

### How to Use

1. Select a book from the list
2. Check which elements to include:
   - ☑ Metadata
   - ☑ Keywords
   - ☑ Description
   - ☑ Categories suggestion
3. Click **Export selected** to preview
4. Click **Export all books** to save all books to a file

### Output Format
```
============================================================
Book Title
============================================================
METADATA:
  Title: ...
  Author: ...
  ASIN: ...

KEYWORDS (7 phrases, 50 chars each):
  1. keyword phrase one
  2. keyword phrase two
  ...

DESCRIPTION:
Your book description...

SUGGESTED CATEGORIES:
  1. [Primary category]
  2. [Secondary category]
```

---

## Rights Sub-tab

Track intellectual property rights and licensing.

### Adding a Right

| Field | Description |
|-------|-------------|
| **Book** | Book title |
| **Type** | Foreign, Audio, Film, Merchandise, etc. |
| **Territory** | Geographic region (e.g., "Germany", "World") |
| **Status** | Available, Licensed, Negotiating |
| **Licensee** | Company/person holding the license |
| **Expiry** | When the license expires |

### Status Types

| Status | Meaning |
|--------|---------|
| **Available** | Right is available for licensing |
| **Licensed** | Currently licensed to someone |
| **Negotiating** | In active negotiation |

---

## ARIA Sub-tab

AI-powered analytics and recommendations.

### Analysis Tools

| Button | What It Generates |
|--------|-------------------|
| **📊 Portfolio Analysis** | Overview of your book catalogue |
| **💰 Revenue Forecast** | Prompt for 12-month projection |
| **📈 Growth Opportunities** | Identify expansion possibilities |
| **🎯 Market Positioning** | Brand positioning analysis |
| **⚡ Quick Wins** | Immediate actionable items |
| **🔮 Trend Analysis** | Publishing trend research prompt |

### Quick Wins
ARIA scans your data and suggests immediate actions:
- Books missing keywords
- Descriptions under 200 characters
- No scheduled posts
- Available rights to license

### Saving Reports
Click **Save report** to store analysis results for future reference.

---

# Export Tab

Backup and export your data.

## Export Options

| Option | Description | Format |
|--------|-------------|--------|
| **Export CSV** | All book metadata | .csv |
| **Export Analytics** | Keywords, competitors, snapshots | .json |
| **Export Muse Ideas** | All creative ideas | .json or .csv |
| **Backup Everything** | Complete data backup | .json |

## Recommended Backup Schedule

| Frequency | What to Backup |
|-----------|----------------|
| **Daily** | If actively adding data |
| **Weekly** | Minimum recommendation |
| **Before updates** | Always backup before updating the app |

---

# Data Storage & Backup

## Data Location

All Author Studio data is stored in:
```
~/.author_studio/
```

### Files

| File | Contents |
|------|----------|
| `books.json` | All book metadata and keywords |
| `schedule.json` | Scheduled social media posts |
| `config.json` | Listmonk and IMAP settings |
| `analytics.json` | Keywords, competitors, snapshots |
| `linkedin.json` | LinkedIn campaigns |
| `muse.json` | Ideas, inbox items, file changes |
| `business.json` | Royalties, series, characters, rights |

## Manual Backup

Copy the entire `.author_studio` folder to:
- External drive
- Cloud storage (Dropbox, OneDrive, Google Drive)
- Version control (git)

## Restore from Backup

1. Close Author Studio
2. Replace files in `~/.author_studio/` with backup files
3. Restart Author Studio

---

# Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+C` / `Cmd+C` | Copy selected text |
| `Ctrl+V` / `Cmd+V` | Paste text |
| `Tab` | Move to next field |
| `Shift+Tab` | Move to previous field |
| `Enter` | Activate focused button |
| `Double-click` | Open book in Metadata tab |

---

# Troubleshooting

## Application Won't Start

**Symptom:** Error message or nothing happens

**Solutions:**
1. Verify Python is installed: `python --version`
2. Check for tkinter: `python -c "import tkinter"`
3. On Linux, install tkinter: `sudo apt install python3-tk`

## Data Not Saving

**Symptom:** Changes disappear after restart

**Solutions:**
1. Check write permissions on `~/.author_studio/`
2. Ensure disk has free space
3. Try running as administrator (Windows)

## IMAP Connection Failed

**Symptom:** Email monitoring won't connect

**Solutions:**
1. Verify server and port (Gmail: imap.gmail.com, 993)
2. For Gmail, use an App Password, not your regular password
3. Check firewall isn't blocking port 993
4. Ensure "Less secure apps" or IMAP is enabled in email settings

## High Memory Usage

**Symptom:** Application becomes slow

**Solutions:**
1. Clear Muse feed periodically
2. Limit watched folders
3. Increase scan interval (5 or 15 minutes)

## Display Issues

**Symptom:** Text too small or UI elements overlap

**Solutions:**
1. Increase display scaling in OS settings
2. Use a higher resolution monitor
3. Edit the scaling in code: `root.tk.call('tk', 'scaling', 2.0)`

---

# Appendix: AI Prompt Templates

Author Studio generates prompts designed for Claude, ChatGPT, and other AI assistants. Here's how to use them effectively.

## Best Practices

1. **Copy the entire prompt** — Don't edit before pasting
2. **Add context** — After pasting, add specific details
3. **Iterate** — Ask follow-up questions to refine output
4. **Combine outputs** — Use multiple prompts for comprehensive content

## Example Workflow: Book Launch

1. **Marketing → Email** — Generate launch email prompt
2. **Marketing → BookTok** — Generate video script prompt
3. **Marketing → Instagram** — Generate social posts prompt
4. **Analytics → Avatar** — Refine target reader prompt
5. **Muse → Calendar** — Generate content calendar

## Customising Prompts

All prompts include:
- Book title and author
- Selected options
- Australian English preference
- "Copy to Claude or ChatGPT" instruction

You can customise by:
- Adding tone preferences
- Specifying word counts
- Including competitor examples
- Adding brand voice guidelines

---

# Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Feb 2025 | Initial release with all 5 phases |

---

# Support

For issues, feature requests, or feedback:

1. **Check this manual** for troubleshooting steps
2. **Backup your data** before making changes
3. **Document the issue** with screenshots if possible

---

*Author Studio Complete Edition*
*Built for indie authors, by an indie author*
*Almost Magic Tech Lab*
