import { useState, useEffect } from 'react';
import { Mail, Archive, PenLine } from 'lucide-react';
import { getInsights, getLetters, saveInsight, saveLetter, getLetter } from '../../lib/api';

type Tab = 'insights' | 'letters' | 'unsent';

interface Insight {
  id: string;
  title: string;
  content: string;
  tags: string[];
  created_at: string;
}

interface Letter {
  id: string;
  title: string;
  content?: string;
  opens_at?: string;
  created_at: string;
}

export default function Vault() {
  const [activeTab, setActiveTab] = useState<Tab>('insights');
  const [insights, setInsights] = useState<Insight[]>([]);
  const [letters, setLetters] = useState<Letter[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  
  // New entry state
  const [isCreating, setIsCreating] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newContent, setNewContent] = useState('');
  const [letterType, setLetterType] = useState<'unsent' | 'oneyear'>('unsent');

  useEffect(() => {
    loadData();
  }, [activeTab]);

  const loadData = async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'insights') {
        const data = await getInsights();
        setInsights(data);
      } else {
        const data = await getLetters();
        setLetters(data);
      }
    } catch (err) {
      console.error('Failed to load vault data:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveInsight = async () => {
    if (!newTitle.trim() || !newContent.trim()) return;
    
    try {
      await saveInsight(newTitle, newContent, []);
      setNewTitle('');
      setNewContent('');
      setIsCreating(false);
      loadData();
    } catch (err) {
      console.error('Failed to save insight:', err);
    }
  };

  const handleSaveLetter = async () => {
    if (!newTitle.trim() || !newContent.trim()) return;
    
    try {
      const result = await saveLetter(letterType, newTitle, newContent, []);
      console.log('Letter saved:', result);
      setNewTitle('');
      setNewContent('');
      setIsCreating(false);
      loadData();
    } catch (err) {
      console.error('Failed to save letter:', err);
    }
  };

  const handleViewLetter = async (letter: Letter) => {
    try {
      const result = await getLetter(letter.id);
      if (result.locked) {
        alert(`This letter is locked until ${new Date(letter.opens_at!).toLocaleDateString()}`);
      } else {
        // Show the content in a modal or expand it
        alert(result.content || letter.content);
      }
    } catch (err) {
      console.error('Failed to view letter:', err);
    }
  };

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString('en-AU', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  const isLetterLocked = (letter: Letter) => {
    if (!letter.opens_at) return false;
    return new Date(letter.opens_at) > new Date();
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-light text-gray-200">The Vault</h1>
          <p className="text-gray-400 mt-1">
            Insights and letters you've saved along the way.
          </p>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 mb-8">
        <button
          onClick={() => { setActiveTab('insights'); setIsCreating(false); }}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeTab === 'insights'
              ? 'bg-gold text-midnight-900'
              : 'bg-midnight-800 text-gray-400 hover:text-gray-200'
          }`}
        >
          <Archive size={16} className="inline mr-2" />
          Insights
        </button>
        <button
          onClick={() => { setActiveTab('letters'); setIsCreating(false); }}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeTab === 'letters'
              ? 'bg-gold text-midnight-900'
              : 'bg-midnight-800 text-gray-400 hover:text-gray-200'
          }`}
        >
          <Mail size={16} className="inline mr-2" />
          Letters
        </button>
        <button
          onClick={() => { setActiveTab('unsent'); setIsCreating(false); }}
          className={`px-4 py-2 rounded-lg transition-colors ${
            activeTab === 'unsent'
              ? 'bg-gold text-midnight-900'
              : 'bg-midnight-800 text-gray-400 hover:text-gray-200'
          }`}
        >
          <PenLine size={16} className="inline mr-2" />
          Unsent
        </button>
      </div>

      {/* Create new entry */}
      {activeTab !== 'insights' && !isCreating && (
        <button
          onClick={() => setIsCreating(true)}
          className="mb-6 bg-midnight-800 border border-midnight-700 text-gray-300 px-4 py-2 rounded-lg hover:border-gold/50 transition-colors"
        >
          + New {activeTab === 'letters' ? 'Letter' : 'Unsent Message'}
        </button>
      )}

      {activeTab === 'insights' && !isCreating && (
        <button
          onClick={() => setIsCreating(true)}
          className="mb-6 bg-midnight-800 border border-midnight-700 text-gray-300 px-4 py-2 rounded-lg hover:border-gold/50 transition-colors"
        >
          + Save an Insight
        </button>
      )}

      {/* Create form */}
      {isCreating && (
        <div className="mb-8 p-6 bg-midnight-800 border border-midnight-700 rounded-lg">
          <input
            type="text"
            value={newTitle}
            onChange={(e) => setNewTitle(e.target.value)}
            placeholder="Title..."
            className="w-full p-3 mb-4 bg-midnight-900 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-600 focus:border-gold/50 focus:outline-none"
          />
          <textarea
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder={activeTab === 'insights' ? 'What did you learn?' : 'Write what you need to say...'}
            className="w-full p-4 bg-midnight-900 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-600 focus:border-gold/50 focus:outline-none resize-none"
            rows={6}
          />
          <div className="flex items-center gap-4 mt-4">
            {activeTab === 'letters' && (
              <select
                value={letterType}
                onChange={(e) => setLetterType(e.target.value as 'unsent' | 'oneyear')}
                className="p-2 bg-midnight-900 border border-midnight-700 rounded-lg text-gray-200"
              >
                <option value="unsent">Unsent (24 hours)</option>
                <option value="oneyear">One year from now</option>
              </select>
            )}
            <button
              onClick={activeTab === 'insights' ? handleSaveInsight : handleSaveLetter}
              disabled={!newTitle.trim() || !newContent.trim()}
              className="bg-gold text-midnight-900 px-4 py-2 rounded-lg font-medium hover:bg-gold-hover transition-colors disabled:opacity-50"
            >
              Save
            </button>
            <button
              onClick={() => { setIsCreating(false); setNewTitle(''); setNewContent(''); }}
              className="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Loading state */}
      {isLoading ? (
        <div className="text-center py-16 text-gray-500">Loading...</div>
      ) : (
        <>
          {/* Insights tab */}
          {activeTab === 'insights' && (
            insights.length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <div className="text-4xl mb-4">💡</div>
                <p>No insights yet.</p>
                <p className="mt-2 text-sm">Save reflections from your sessions.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {insights.map((insight) => (
                  <div
                    key={insight.id}
                    className="p-6 bg-midnight-800 border border-midnight-700 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-gold font-medium">{insight.title}</h3>
                      <span className="text-gray-500 text-sm">{formatDate(insight.created_at)}</span>
                    </div>
                    <div className="text-gray-300 whitespace-pre-wrap">{insight.content}</div>
                    {insight.tags.length > 0 && (
                      <div className="flex gap-2 mt-4">
                        {insight.tags.map((tag) => (
                          <span key={tag} className="px-2 py-1 bg-midnight-900 text-gray-500 text-xs rounded">
                            {tag}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )
          )}

          {/* Letters tab (oneyear) */}
          {activeTab === 'letters' && (
            letters.filter(l => l.opens_at).length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <div className="text-4xl mb-4">✉️</div>
                <p>No time-locked letters.</p>
                <p className="mt-2 text-sm">Write a letter to your future self.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {letters.filter(l => l.opens_at).map((letter) => (
                  <div
                    key={letter.id}
                    className={`p-6 border rounded-lg ${
                      isLetterLocked(letter)
                        ? 'bg-midnight-800/50 border-midnight-700'
                        : 'bg-midnight-800 border-gold/30'
                    }`}
                  >
                    <div className="flex items-center gap-3 mb-4">
                      {/* Sealed envelope visual */}
                      <div className="w-10 h-8 bg-gold/20 rounded flex items-center justify-center">
                        <Mail size={18} className={isLetterLocked(letter) ? 'text-gold' : 'text-green-400'} />
                      </div>
                      <div>
                        <h3 className="text-gray-200 font-medium">{letter.title}</h3>
                        <p className="text-gray-500 text-sm">
                          {isLetterLocked(letter)
                            ? `Opens ${formatDate(letter.opens_at!)}`
                            : 'Ready to open'}
                        </p>
                      </div>
                    </div>
                    {!isLetterLocked(letter) && (
                      <button
                        onClick={() => handleViewLetter(letter)}
                        className="text-gold hover:text-gold-hover text-sm"
                      >
                        Read letter →
                      </button>
                    )}
                  </div>
                ))}
              </div>
            )
          )}

          {/* Unsent tab */}
          {activeTab === 'unsent' && (
            letters.filter(l => !l.opens_at).length === 0 ? (
              <div className="text-center py-16 text-gray-500">
                <div className="text-4xl mb-4">📝</div>
                <p>No unsent messages.</p>
                <p className="mt-2 text-sm">Write it here, lock it, decide later.</p>
              </div>
            ) : (
              <div className="space-y-4">
                {letters.filter(l => !l.opens_at).map((letter) => (
                  <div
                    key={letter.id}
                    className="p-6 bg-midnight-800 border border-midnight-700 rounded-lg"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <h3 className="text-gray-200 font-medium">{letter.title}</h3>
                      <span className="text-gray-500 text-sm">{formatDate(letter.created_at)}</span>
                    </div>
                    <div className="text-gray-300 whitespace-pre-wrap">{letter.content}</div>
                  </div>
                ))}
              </div>
            )
          )}
        </>
      )}
    </div>
  );
}
