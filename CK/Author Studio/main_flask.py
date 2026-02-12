"""
Author Studio v2.1 - Flask Web Version
By Almost Magic Tech Lab
Runs in your browser - no Windows security issues!
"""

from flask import Flask, jsonify, request, render_template_string
import webbrowser
from threading import Timer
from pathlib import Path
from datetime import datetime

from src.parsers import parse_file, get_word_count
from src.analyzer import BookAnalyzer
from src.aria import ARIA
from src.database import Database
from src.amazon import fetch_amazon_listing, analyze_listing, generate_description
from src.keywords import KeywordResearcher, CategoryFinder, PricingOptimizer
from src.batch import FolderScanner, BatchProcessor, BulkExporter, DeploymentQueue
from src.manuscript import MarkdownToWord, ManuscriptFormatter, convert_md_to_docx
from src.quality import PlagiarismChecker, AIDetector, QualityChecker

app = Flask(__name__)

# Global state
db = Database()
aria = ARIA()
aria.set_books(db.get_all_books())
batch_processor = BatchProcessor(db)
scanned_files = []

HTML = """<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Author Studio v2.1</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
:root{--bg:#0a0a0f;--bg2:#12121a;--card:#1a1a25;--hover:#252535;--accent:#8b5cf6;--green:#22c55e;--red:#ef4444;--orange:#f59e0b;--text:#f8fafc;--muted:#94a3b8;--border:rgba(255,255,255,0.1)}
body{font-family:-apple-system,sans-serif;background:var(--bg);color:var(--text)}
.app{display:flex;height:100vh}
.sidebar{width:240px;background:var(--bg2);border-right:1px solid var(--border);padding:20px;overflow-y:auto}
.logo{font-size:18px;font-weight:700;color:var(--accent);margin-bottom:4px}
.version{font-size:11px;color:var(--muted);margin-bottom:20px}
.nav-item{padding:10px 12px;border-radius:8px;cursor:pointer;color:var(--muted);margin-bottom:2px;font-size:13px}
.nav-item:hover{background:var(--hover);color:var(--text)}
.nav-item.active{background:var(--accent);color:white}
.nav-title{font-size:10px;color:var(--muted);text-transform:uppercase;margin:16px 0 8px 12px}
.main{flex:1;display:flex;flex-direction:column;overflow:hidden}
.header{padding:16px 24px;border-bottom:1px solid var(--border)}
.header h1{font-size:20px}
.content{flex:1;overflow-y:auto;padding:24px}
.card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:20px;margin-bottom:16px}
.card h2{font-size:12px;color:var(--muted);text-transform:uppercase;margin-bottom:12px}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:20px}
.stat{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px}
.stat .label{color:var(--muted);font-size:12px}
.stat .value{font-size:24px;font-weight:700;margin-top:4px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px}
.book{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;cursor:pointer}
.book:hover{border-color:var(--accent)}
.book .title{font-weight:600;margin-bottom:4px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.book .meta{color:var(--muted);font-size:12px}
.book .badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:600;margin-top:8px}
.badge.a{background:var(--green)}.badge.b{background:#3b82f6}.badge.c{background:var(--orange);color:#000}.badge.d{background:var(--red)}.badge.none{background:var(--hover);color:var(--muted)}
.add{border:2px dashed var(--border);background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100px;color:var(--muted)}
.add:hover{border-color:var(--accent);color:var(--accent)}
.btn{padding:10px 20px;border:none;border-radius:8px;font-weight:600;cursor:pointer;font-size:13px}
.btn-p{background:var(--accent);color:white}
.btn-s{background:var(--hover);color:var(--text)}
.btn-g{background:var(--green);color:white}
.btn-w{background:var(--orange);color:#000}
.btn-lg{padding:14px 28px}
input,select,textarea{width:100%;padding:10px;background:var(--bg);border:1px solid var(--border);border-radius:8px;color:var(--text);font-size:13px}
input:focus,select:focus{outline:none;border-color:var(--accent)}
input[type=file]{padding:8px}
label{display:block;margin-bottom:6px;color:var(--muted);font-size:12px}
.fg{margin-bottom:12px}
.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.hidden{display:none!important}
.alert{padding:10px 14px;border-radius:8px;margin-bottom:12px;font-size:13px}
.alert-s{background:rgba(34,197,94,0.2);border:1px solid var(--green)}
.alert-e{background:rgba(239,68,68,0.2);border:1px solid var(--red)}
.score{display:inline-block;padding:6px 14px;border-radius:20px;font-weight:700}
.score-h{background:var(--green)}.score-m{background:var(--orange);color:#000}.score-l{background:var(--red)}
.issue{padding:10px;background:var(--bg);border-radius:8px;margin-bottom:8px;font-size:13px}
.chat{display:flex;flex-direction:column;height:calc(100vh - 120px)}
.msgs{flex:1;overflow-y:auto;padding:16px}
.msg{max-width:80%;margin-bottom:12px;padding:12px 16px;border-radius:14px;font-size:14px;white-space:pre-wrap}
.msg.u{background:var(--accent);margin-left:auto}
.msg.a{background:var(--hover)}
.cinput{padding:16px;border-top:1px solid var(--border);display:flex;gap:10px}
.cinput input{flex:1;border-radius:20px}
.modal{position:fixed;inset:0;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;z-index:1000;opacity:0;pointer-events:none;transition:opacity 0.2s}
.modal.open{opacity:1;pointer-events:auto}
.mbox{background:var(--card);border-radius:16px;width:500px;max-width:90vw;max-height:80vh;overflow:hidden}
.mhead{padding:16px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}
.mbody{padding:20px;overflow-y:auto}
.mfoot{padding:12px 16px;border-top:1px solid var(--border);display:flex;justify-content:flex-end;gap:10px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:10px;text-align:left;border-bottom:1px solid var(--border)}
th{color:var(--muted);font-size:11px;text-transform:uppercase}
</style></head><body>
<div class="app">
<aside class="sidebar">
<div class="logo">📚 Author Studio</div><div class="version">v2.1 Flask Edition</div>
<div class="nav-title">General</div>
<div class="nav-item active" onclick="go('dash')">📊 Dashboard</div>
<div class="nav-item" onclick="go('books')">📖 Books</div>
<div class="nav-item" onclick="go('aria')">🤖 ARIA</div>
<div class="nav-title">Quality</div>
<div class="nav-item" onclick="go('quality')">✅ Quality Check</div>
<div class="nav-title">Batch</div>
<div class="nav-item" onclick="go('bulk')">⚡ Bulk Actions</div>
<div class="nav-title">Amazon</div>
<div class="nav-item" onclick="go('keywords')">🏷️ Keywords</div>
<div class="nav-item" onclick="go('pricing')">💰 Pricing</div>
</aside>
<main class="main"><div class="header"><h1 id="title">Dashboard</h1></div>
<div class="content">

<div id="p-dash" class="page">
<div class="stats">
<div class="stat"><div class="label">Books</div><div class="value" id="s-books">0</div></div>
<div class="stat"><div class="label">Words</div><div class="value" id="s-words">0</div></div>
<div class="stat"><div class="label">Analyzed</div><div class="value" id="s-analyzed">0</div></div>
<div class="stat"><div class="label">Streak</div><div class="value" id="s-streak">0</div></div>
</div>
<div class="card"><h2>💡 Tip</h2><p id="tip">Loading...</p></div>
<div class="card"><h2>📚 Recent Books</h2><div id="recent" class="grid"></div></div>
</div>

<div id="p-books" class="page hidden">
<div class="card">
<h2>📤 Add Book</h2>
<input type="file" id="bookfile" accept=".pdf,.epub,.docx,.txt,.md">
<button class="btn btn-p" style="margin-top:10px" onclick="uploadBook()">Upload</button>
<div id="uploadres" style="margin-top:10px"></div>
</div>
<div class="card"><h2>📚 All Books</h2><div id="allbooks" class="grid"></div></div>
</div>

<div id="p-aria" class="page hidden">
<div class="chat">
<div class="msgs" id="msgs"><div class="msg a">👋 Hi! I'm ARIA!</div></div>
<div class="cinput"><input id="cin" placeholder="Ask..." onkeypress="if(event.key==='Enter')chat()"><button class="btn btn-p" onclick="chat()">Send</button></div>
</div>
</div>

<div id="p-quality" class="page hidden">
<div class="card"><h2>✅ Quality Checker</h2>
<p style="color:var(--muted);margin-bottom:12px">Check plagiarism & AI patterns</p>
<div class="fg"><label>Book</label><select id="qbook"></select></div>
<button class="btn btn-p" onclick="qcheck()">🔍 Full Check</button>
</div>
<div id="qresults" class="hidden">
<div class="card"><h2>Score</h2><div id="qscore"></div></div>
<div class="card"><h2>Plagiarism</h2><div id="qplag"></div></div>
<div class="card"><h2>AI Detection</h2><div id="qai"></div></div>
<div class="card"><h2>Suggestions</h2><div id="qhum"></div></div>
</div>
</div>

<div id="p-bulk" class="page hidden">
<div class="card"><h2>⚡ Bulk Actions</h2>
<button class="btn btn-p btn-lg" onclick="analyzeall()">🔬 Analyze All</button>
</div>
<div id="bulkres" class="hidden"><div class="card"><div id="bulksum"></div></div></div>
<div class="card"><h2>Status</h2><table><thead><tr><th>Title</th><th>Words</th><th>Genre</th><th>Health</th></tr></thead><tbody id="bulktable"></tbody></table></div>
</div>

<div id="p-keywords" class="page hidden">
<div class="card"><h2>🏷️ Keywords</h2>
<div class="fg"><label>Genre</label>
<select id="kwgenre">
<optgroup label="Non-Fiction"><option value="business">Business</option><option value="self-help">Self-Help</option><option value="spirituality">Spirituality</option><option value="poetry">Poetry</option><option value="memoir">Memoir</option><option value="technology">Technology</option></optgroup>
<optgroup label="Fiction"><option value="thriller">Thriller</option><option value="romance">Romance</option><option value="fantasy">Fantasy</option></optgroup>
</select></div>
<button class="btn btn-p" onclick="getkw()">Get Keywords</button>
</div>
<div id="kwres" class="hidden">
<div class="card"><h2>Keywords</h2><div id="kwlist"></div></div>
<div class="card"><h2>Backend 7</h2><div id="kwback"></div><button class="btn btn-g" style="margin-top:12px" onclick="copykw()">📋 Copy</button></div>
</div>
</div>

<div id="p-pricing" class="page hidden">
<div class="card"><h2>💰 Pricing</h2>
<div class="row">
<div class="fg"><label>Genre</label><select id="prgenre"><option value="business">Business</option><option value="self-help">Self-Help</option><option value="poetry">Poetry</option><option value="thriller">Thriller</option><option value="romance">Romance</option></select></div>
<div class="fg"><label>Pages</label><input type="number" id="prpages" placeholder="200"></div>
</div>
<button class="btn btn-p" onclick="getpr()">Get Price</button>
</div>
<div id="prres" class="hidden"><div class="card"><h2>Suggested</h2><div id="prsugg"></div></div></div>
</div>

</div></main></div>

<div class="modal" id="m-book"><div class="mbox">
<div class="mhead"><h2 id="mtitle">Book</h2><button class="btn btn-s" onclick="cm('m-book')">✕</button></div>
<div class="mbody" id="mbody"></div>
<div class="mfoot">
<button class="btn" style="background:var(--red);color:white" onclick="delbook()">Delete</button>
<button class="btn btn-p" onclick="anbook()">Analyze</button>
</div>
</div></div>

<script>
let cur = null;

async function api(endpoint, data={}) {
    const r = await fetch('/api/' + endpoint, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(data)
    });
    return r.json();
}

async function load() {
    const d = await api('dashboard');
    document.getElementById('s-books').textContent = d.total_books;
    document.getElementById('s-words').textContent = d.total_words.toLocaleString();
    document.getElementById('s-analyzed').textContent = d.analyzed;
    document.getElementById('s-streak').textContent = d.streak + '🔥';
    document.getElementById('tip').textContent = d.tip || 'Welcome!';
    render(d.books, 'recent');
    const books = await api('books');
    render(books, 'allbooks');
    loadq();
}

async function loadq() {
    const b = await api('books');
    document.getElementById('qbook').innerHTML = b.map(x => '<option value="'+x.id+'">'+x.title+'</option>').join('');
}

function render(b, id) {
    let h = '';
    for (const x of b) {
        const d = x.dna_profile || {};
        const g = d.health_grade || 'none';
        h += '<div class="book" onclick="ob('+x.id+')"><div class="title">'+x.title+'</div><div class="meta">'+(x.word_count||0).toLocaleString()+' • '+(d.primary_genre||'—')+'</div><span class="badge '+g.toLowerCase()+'">'+(g!=='none'?g+' '+d.health_score:'Analyze')+'</span></div>';
    }
    document.getElementById(id).innerHTML = h || '<p style="color:var(--muted)">No books yet</p>';
}

function go(p) {
    document.querySelectorAll('.page').forEach(x => x.classList.add('hidden'));
    document.getElementById('p-'+p).classList.remove('hidden');
    document.querySelectorAll('.nav-item').forEach(x => x.classList.remove('active'));
    event.target.classList.add('active');
    const t = {dash:'Dashboard',books:'Books',aria:'ARIA',quality:'Quality',bulk:'Bulk',keywords:'Keywords',pricing:'Pricing'};
    document.getElementById('title').textContent = t[p] || p;
    if (p==='dash' || p==='books') load();
    if (p==='bulk') loadbulk();
    if (p==='quality') loadq();
}

function om(id) { document.getElementById(id).classList.add('open'); }
function cm(id) { document.getElementById(id).classList.remove('open'); }

async function uploadBook() {
    const f = document.getElementById('bookfile').files[0];
    if (!f) { alert('Select a file'); return; }
    const formData = new FormData();
    formData.append('file', f);
    const r = await fetch('/api/upload', {method:'POST', body:formData});
    const j = await r.json();
    document.getElementById('uploadres').innerHTML = j.success 
        ? '<div class="alert alert-s">✅ Added: '+j.title+'</div>'
        : '<div class="alert alert-e">'+j.error+'</div>';
    if (j.success) load();
}

async function ob(id) {
    const b = await api('book', {id});
    if (!b) return;
    cur = b;
    document.getElementById('mtitle').textContent = b.title;
    const d = b.dna_profile;
    document.getElementById('mbody').innerHTML = d 
        ? '<p><b>Genre:</b> '+d.primary_genre+'</p><p><b>Tone:</b> '+d.tone+'</p><p><b>Health:</b> '+d.health_score+'/100</p>'
        : '<p style="color:var(--muted)">Not analyzed yet</p>';
    om('m-book');
}

async function anbook() {
    if (!cur) return;
    document.getElementById('mbody').innerHTML = '<p>Analyzing...</p>';
    const r = await api('analyze', {id: cur.id});
    if (r.success) { ob(cur.id); load(); }
    else alert(r.error);
}

async function delbook() {
    if (!cur || !confirm('Delete?')) return;
    await api('delete', {id: cur.id});
    cm('m-book');
    load();
}

async function qcheck() {
    const id = document.getElementById('qbook').value;
    if (!id) return;
    document.getElementById('qresults').classList.add('hidden');
    const r = await api('quality', {id: parseInt(id)});
    if (!r.success) { alert(r.error); return; }
    
    const sc = r.quality_score >= 75 ? 'score-h' : r.quality_score >= 50 ? 'score-m' : 'score-l';
    document.getElementById('qscore').innerHTML = '<span class="score '+sc+'">'+r.quality_grade+' '+r.quality_score+'/100</span>';
    
    let ph = '<p><b>Risk:</b> '+(r.plagiarism?.risk_level||'low').toUpperCase()+'</p>';
    if (r.plagiarism?.cliches_found?.length) {
        for (const c of r.plagiarism.cliches_found.slice(0,5)) {
            ph += '<div class="issue">"'+c.phrase+'" ('+c.count+'x)</div>';
        }
    }
    document.getElementById('qplag').innerHTML = ph;
    
    let ah = '<p><b>AI:</b> '+(r.ai_detection?.ai_probability||0)+'%</p><p>'+(r.ai_detection?.assessment||'')+'</p>';
    document.getElementById('qai').innerHTML = ah;
    
    let hh = '<p style="color:var(--muted)">No changes needed</p>';
    if (r.humanize_suggestions?.suggestions?.length) {
        hh = '';
        for (const s of r.humanize_suggestions.suggestions.slice(0,5)) {
            hh += '<div class="issue">Replace "'+s.find+'" → "'+s.replace_with+'"</div>';
        }
    }
    document.getElementById('qhum').innerHTML = hh;
    document.getElementById('qresults').classList.remove('hidden');
}

async function loadbulk() {
    const b = await api('books');
    let h = '';
    for (const x of b) {
        const d = x.dna_profile || {};
        h += '<tr><td>'+x.title+'</td><td>'+(x.word_count||0).toLocaleString()+'</td><td>'+(d.primary_genre||'—')+'</td><td>'+(d.health_score!==undefined?d.health_score+'/100':'—')+'</td></tr>';
    }
    document.getElementById('bulktable').innerHTML = h || '<tr><td colspan="4">No books</td></tr>';
}

async function analyzeall() {
    const r = await api('analyzeall');
    document.getElementById('bulksum').innerHTML = '<div class="alert alert-s"><b>'+(r.count||0)+'</b> analyzed!</div>';
    document.getElementById('bulkres').classList.remove('hidden');
    loadbulk();
    load();
}

async function getkw() {
    const r = await api('keywords', {genre: document.getElementById('kwgenre').value});
    if (r.success) {
        let h = '';
        const all = [...(r.keywords.primary_keywords||[]), ...(r.keywords.secondary_keywords||[])];
        for (const k of all) {
            h += '<span style="display:inline-block;padding:4px 10px;background:var(--hover);border-radius:16px;font-size:12px;margin:4px">'+k+'</span>';
        }
        document.getElementById('kwlist').innerHTML = h;
        document.getElementById('kwback').innerHTML = '<ol>'+(r.backend_keywords||[]).map(k => '<li style="margin-bottom:6px">'+k+'</li>').join('')+'</ol>';
        document.getElementById('kwres').classList.remove('hidden');
    }
}

function copykw() {
    const k = Array.from(document.querySelectorAll('#kwback li')).map(x => x.textContent);
    navigator.clipboard.writeText(k.join('\\n'));
    alert('Copied!');
}

async function getpr() {
    const r = await api('pricing', {genre: document.getElementById('prgenre').value, pages: parseInt(document.getElementById('prpages').value)||null});
    if (r.success) {
        document.getElementById('prsugg').innerHTML = '<p style="font-size:36px;font-weight:700;color:var(--green)">$'+r.suggested_price.toFixed(2)+'</p><p>'+r.royalty_at_suggested.royalty_rate+' = $'+r.royalty_at_suggested.royalty_per_sale+'/sale</p>';
        document.getElementById('prres').classList.remove('hidden');
    }
}

async function chat() {
    const i = document.getElementById('cin');
    const m = i.value.trim();
    if (!m) return;
    document.getElementById('msgs').innerHTML += '<div class="msg u">'+m+'</div>';
    i.value = '';
    const r = await api('chat', {message: m});
    document.getElementById('msgs').innerHTML += '<div class="msg a">'+r.response+'</div>';
    document.getElementById('msgs').scrollTop = document.getElementById('msgs').scrollHeight;
}

load();
</script>
</body></html>"""

@app.route('/api/health', methods=['GET'])
def api_health():
    """Health check for Foreperson and Supervisor."""
    return jsonify({
        'status': 'healthy',
        'service': 'author-studio',
        'version': '2.1',
        'books_loaded': len(db.get_all_books()),
        'timestamp': datetime.now().isoformat(),
    })

@app.route('/api/book-dna', methods=['GET'])
def api_book_dna():
    """Return DNA profiles for all analyzed books."""
    books = db.get_all_books()
    profiles = [{'id': b['id'], 'title': b.get('title',''), 'dna': b.get('dna_profile')}
                for b in books if b.get('dna_profile')]
    return jsonify({'profiles': profiles, 'total': len(profiles)})

@app.route('/api/amazon', methods=['GET'])
def api_amazon():
    """Amazon keyword research and pricing info."""
    return jsonify({'service': 'amazon-tools', 'tools': ['keywords', 'pricing', 'listing_analysis'],
                    'status': 'available'})

@app.route('/api/aria', methods=['GET'])
def api_aria():
    """ARIA chat assistant status."""
    return jsonify({'assistant': 'ARIA', 'status': 'ready',
                    'books_context': len(aria.books) if hasattr(aria, 'books') else 0})

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/api/dashboard', methods=['POST'])
def dashboard():
    books = db.get_all_books()
    return jsonify({
        'total_books': len(books),
        'total_words': sum(b.get('word_count', 0) for b in books),
        'analyzed': sum(1 for b in books if b.get('dna_profile')),
        'streak': db.get_streak(),
        'books': books[:5],
        'tip': aria.get_tip()
    })

@app.route('/api/books', methods=['POST'])
def get_books():
    return jsonify(db.get_all_books())

@app.route('/api/book', methods=['POST'])
def get_book():
    data = request.json
    return jsonify(db.get_book(data['id']))

@app.route('/api/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return jsonify({'error': 'No file'})
    f = request.files['file']
    if f.filename == '':
        return jsonify({'error': 'No file selected'})
    
    # Save temporarily
    import tempfile
    import os
    temp_dir = tempfile.gettempdir()
    temp_path = os.path.join(temp_dir, f.filename)
    f.save(temp_path)
    
    # Parse
    text, error = parse_file(temp_path)
    if error:
        return jsonify({'error': error})
    
    title = Path(f.filename).stem.replace('_', ' ').replace('-', ' ').title()
    word_count = get_word_count(text)
    book_id = db.add_book(title=title, file_path=temp_path, word_count=word_count, raw_text=text, file_name=f.filename)
    aria.set_books(db.get_all_books())
    
    return jsonify({'success': True, 'book_id': book_id, 'title': title, 'word_count': word_count})

@app.route('/api/analyze', methods=['POST'])
def analyze():
    data = request.json
    book = db.get_book(data['id'])
    if not book:
        return jsonify({'error': 'Book not found'})
    text = book.get('raw_text', '')
    if not text:
        return jsonify({'error': 'No text'})
    dna = BookAnalyzer.generate_dna_profile(text, book.get('title', 'Untitled'))
    db.update_book(data['id'], dna_profile=dna, chapter_count=dna.get('chapter_count', 0), analyzed_at=datetime.now().isoformat())
    aria.set_books(db.get_all_books())
    return jsonify({'success': True, 'dna_profile': dna})

@app.route('/api/delete', methods=['POST'])
def delete():
    data = request.json
    db.delete_book(data['id'])
    aria.set_books(db.get_all_books())
    return jsonify({'success': True})

@app.route('/api/quality', methods=['POST'])
def quality():
    data = request.json
    book = db.get_book(data['id'])
    if not book:
        return jsonify({'error': 'Book not found'})
    text = book.get('raw_text', '')
    if not text:
        return jsonify({'error': 'No text'})
    result = QualityChecker.full_check(text)
    return jsonify({'success': True, **result})

@app.route('/api/analyzeall', methods=['POST'])
def analyzeall():
    books = db.get_all_books()
    count = 0
    for book in books:
        if not book.get('dna_profile'):
            text = book.get('raw_text', '')
            if text:
                dna = BookAnalyzer.generate_dna_profile(text, book.get('title', 'Untitled'))
                db.update_book(book['id'], dna_profile=dna, chapter_count=dna.get('chapter_count', 0), analyzed_at=datetime.now().isoformat())
                count += 1
    aria.set_books(db.get_all_books())
    return jsonify({'success': True, 'count': count})

@app.route('/api/keywords', methods=['POST'])
def keywords():
    data = request.json
    genre = data.get('genre', 'literary')
    kw = KeywordResearcher.get_genre_keywords(genre)
    backend = KeywordResearcher.generate_backend_keywords(genre, '')
    return jsonify({'success': True, 'keywords': kw, 'backend_keywords': backend})

@app.route('/api/pricing', methods=['POST'])
def pricing():
    data = request.json
    result = PricingOptimizer.suggest_price(data.get('genre', 'literary'), data.get('pages'))
    return jsonify({'success': True, **result})

@app.route('/api/chat', methods=['POST'])
def chat_api():
    data = request.json
    response = aria.chat(data['message'])
    db.add_message('user', data['message'])
    db.add_message('assistant', response)
    return jsonify({'response': response})

def open_browser():
    webbrowser.open('http://127.0.0.1:5007')

if __name__ == '__main__':
    print("=" * 50)
    print("Author Studio v2.1 - Flask Edition")
    print("Port 5007 | http://localhost:5007")
    print("=" * 50)
    app.run(debug=False, port=5007)
