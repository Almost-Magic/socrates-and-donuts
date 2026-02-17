import { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

export default function QuickCapture() {
  const [capture, setCapture] = useState('');
  // const [tags, setTags] = useState<string[]>([]);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [search, setSearch] = useState('');

  const tagOptions = ['#insight', '#reactive', '#observation', '#gratitude', '#question'];

  const handleSave = () => {
    if (!capture.trim()) return;
    // Save to IndexedDB
    setCapture('');
    setSelectedTags([]);
    alert('Saved!');
  };

  const toggleTag = (tag: string) => {
    setSelectedTags(selectedTags.includes(tag) ? selectedTags.filter((t) => t !== tag) : [...selectedTags, tag]);
  };

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        handleSave();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [capture, selectedTags]);

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-light text-gray-200">Quick Capture</h1>
        <p className="text-gray-400 mt-1">Catch the thought before it's gone.</p>
      </div>

      <div className="mb-6">
        <textarea
          value={capture}
          onChange={(e) => setCapture(e.target.value)}
          placeholder="What's on your mind? (Cmd+Enter to save)"
          className="w-full p-4 bg-midnight-800 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none resize-none mb-4"
          rows={4}
          autoFocus
        />

        <div className="flex flex-wrap gap-2 mb-4">
          {tagOptions.map((tag) => (
            <button
              key={tag}
              onClick={() => toggleTag(tag)}
              className={`px-3 py-1 rounded-full text-sm transition-all ${
                selectedTags.includes(tag)
                  ? 'bg-gold text-midnight-900'
                  : 'bg-midnight-700 text-gray-300 hover:bg-midnight-600'
              }`}
            >
              {tag}
            </button>
          ))}
        </div>

        <button
          onClick={handleSave}
          disabled={!capture.trim()}
          className="w-full bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors disabled:opacity-50"
        >
          Save (Cmd+Enter)
        </button>
      </div>

      <div className="flex items-center gap-2 mb-4">
        <Search size={18} className="text-gray-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search captures..."
          className="flex-1 p-2 bg-transparent border-b border-midnight-700 text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none"
        />
      </div>

      <div className="text-center py-12 text-gray-500">
        <p>No captures yet.</p>
        <p className="mt-2 text-sm">Start capturing your thoughts.</p>
      </div>
    </div>
  );
}
