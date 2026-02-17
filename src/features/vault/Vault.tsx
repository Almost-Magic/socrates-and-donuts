import { useState, useEffect } from 'react';
import { Lock, Unlock, Send, Trash2 } from 'lucide-react';

interface VaultEntry {
  id: string;
  content: string;
  createdAt: number;
  unlocksAt: number;
  status: 'locked' | 'unlocked' | 'sent';
}

export default function Vault() {
  const [entries, setEntries] = useState<VaultEntry[]>([]);
  const [newContent, setNewContent] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    loadEntries();
  }, []);

  const loadEntries = async () => {
    setEntries([]);
  };

  const handleCreate = () => {
    if (!newContent.trim()) return;

    const now = Date.now();
    const entry: VaultEntry = {
      id: crypto.randomUUID(),
      content: newContent,
      createdAt: now,
      unlocksAt: now + 24 * 60 * 60 * 1000,
      status: 'locked',
    };

    setEntries([entry, ...entries]);
    setNewContent('');
    setIsCreating(false);
  };

  const handleUnlock = (id: string) => {
    setEntries(entries.map(e => 
      e.id === id ? { ...e, status: 'unlocked' } : e
    ));
  };

  const handleSend = async (entry: VaultEntry) => {
    await navigator.clipboard.writeText(entry.content);
    const updatedEntry: VaultEntry = { ...entry, status: 'sent' };
    setEntries(entries.map(e => e.id === entry.id ? updatedEntry : e));
    alert('Copied to clipboard!');
  };

  const handleDiscard = (id: string) => {
    if (confirm('Are you sure you want to discard this message?')) {
      setEntries(entries.filter(e => e.id !== id));
    }
  };

  const formatTimeRemaining = (unlocksAt: number) => {
    const diff = unlocksAt - Date.now();
    if (diff <= 0) return 'Ready';
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    
    if (hours > 24) {
      const days = Math.floor(hours / 24);
      return `${days}d ${hours % 24}h`;
    }
    return `${hours}h ${minutes}m`;
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-light text-gray-200">The Vault</h1>
          <p className="text-gray-400 mt-1">
            Write the angry message. Lock it. Decide tomorrow.
          </p>
        </div>
        {!isCreating && (
          <button
            onClick={() => setIsCreating(true)}
            className="bg-gold text-midnight-900 px-4 py-2 rounded-lg font-medium hover:bg-gold-hover transition-colors"
          >
            + New Vault Entry
          </button>
        )}
      </div>

      {isCreating && (
        <div className="mb-8 p-6 bg-midnight-800 border border-midnight-700 rounded-lg">
          <textarea
            value={newContent}
            onChange={(e) => setNewContent(e.target.value)}
            placeholder="Write what you want to say... (it will be locked for 24 hours)"
            className="w-full p-4 bg-midnight-900 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none transition-colors resize-none"
            rows={6}
          />
          <div className="flex gap-3 mt-4">
            <button
              onClick={handleCreate}
              disabled={!newContent.trim()}
              className="flex items-center gap-2 bg-gold text-midnight-900 px-4 py-2 rounded-lg font-medium hover:bg-gold-hover transition-colors disabled:opacity-50"
            >
              <Lock size={18} />
              Lock for 24 Hours
            </button>
            <button
              onClick={() => {
                setIsCreating(false);
                setNewContent('');
              }}
              className="px-4 py-2 text-gray-400 hover:text-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {entries.length === 0 ? (
        <div className="text-center py-16 text-gray-500">
          <div className="text-4xl mb-4">🔐</div>
          <p>Your vault is empty.</p>
          <p className="mt-2">When you need to pause before acting, write it here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {entries.map((entry) => (
            <div
              key={entry.id}
              className={`p-6 border rounded-lg ${
                entry.status === 'locked'
                  ? 'bg-midnight-800/50 border-midnight-700'
                  : 'bg-midnight-800 border-gold/30'
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2 text-sm">
                  {entry.status === 'locked' ? (
                    <>
                      <Lock size={14} className="text-gold" />
                      <span className="text-gold">
                        Unlocks in {formatTimeRemaining(entry.unlocksAt)}
                      </span>
                    </>
                  ) : (
                    <>
                      <Unlock size={14} className="text-green-400" />
                      <span className="text-green-400">Ready to review</span>
                    </>
                  )}
                </div>
                <div className="flex items-center gap-2 text-gray-400 text-sm">
                  {new Date(entry.createdAt).toLocaleDateString()}
                </div>
              </div>

              <div className="text-gray-300 mb-4 whitespace-pre-wrap">
                {entry.content}
              </div>

              {entry.status === 'locked' ? (
                <button
                  onClick={() => handleUnlock(entry.id)}
                  className="text-gold hover:text-gold-hover transition-colors text-sm"
                >
                  Unlock early
                </button>
              ) : (
                <div className="flex gap-3">
                  <button
                    onClick={() => handleSend(entry)}
                    className="flex items-center gap-2 text-green-400 hover:text-green-300 transition-colors"
                  >
                    <Send size={16} />
                    Send (copy)
                  </button>
                  <button
                    onClick={() => handleDiscard(entry.id)}
                    className="flex items-center gap-2 text-red-400 hover:text-red-300 transition-colors"
                  >
                    <Trash2 size={16} />
                    Discard
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
