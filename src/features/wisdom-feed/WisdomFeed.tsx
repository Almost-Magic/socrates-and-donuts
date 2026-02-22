import { useState } from 'react';
import { Bookmark } from 'lucide-react';

const wisdomPassages = [
  { id: '1', text: 'You are not what happened to you. You are what you choose to become.', source: 'Unknown' },
  { id: '2', text: 'Between stimulus and response there is a space. In that space is our power to choose our response.', source: 'Viktor Frankl' },
  { id: '3', text: 'What you resist, persists. What you look at, dissolves.', source: 'Carl Jung' },
  { id: '4', text: 'The mind is everything. What you think you become.', source: 'Buddha' },
  { id: '5', text: 'It is not the things that disturb us, but our judgments about things.', source: 'Epictetus' },
];

export default function WisdomFeed() {
  const [bookmarks, setBookmarks] = useState<string[]>([]);

  const toggleBookmark = (id: string) => {
    setBookmarks(bookmarks.includes(id) ? bookmarks.filter((b) => b !== id) : [...bookmarks, id]);
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-light text-gray-200">Wisdom Feed</h1>
        <p className="text-gray-400 mt-1">The anti-doomscroll. Curated wisdom, not outrage.</p>
      </div>

      <div className="space-y-6">
        {wisdomPassages.map((passage) => (
          <div key={passage.id} className="p-6 bg-midnight-800 border border-midnight-700 rounded-lg">
            <p className="text-xl text-gray-200 italic mb-4">"{passage.text}"</p>
            <div className="flex items-center justify-between">
              <span className="text-gold text-sm">{passage.source}</span>
              <button
                onClick={() => toggleBookmark(passage.id)}
                className={bookmarks.includes(passage.id) ? 'text-gold' : 'text-gray-400'}
              >
                <Bookmark size={20} fill={bookmarks.includes(passage.id) ? 'currentColor' : 'none'} />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
