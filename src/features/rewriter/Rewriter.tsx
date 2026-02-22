import { useState } from 'react';
import { Copy, Wand2 } from 'lucide-react';

export default function Rewriter() {
  const [input, setInput] = useState('');
  const [rewrites, setRewrites] = useState<{ calm: string; empathetic: string; assertive: string } | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleRewrite = async () => {
    if (!input.trim()) return;
    setIsLoading(true);
    // Simulated — would use AI
    setTimeout(() => {
      setRewrites({
        calm: input.replace(/!/g, '.').replace(/I need/i, 'I would appreciate').replace(/you/i, 'you'),
        empathetic: input.replace(/!/g, '...').replace(/always/i, 'sometimes').replace(/never/i, 'rarely'),
        assertive: input.replace(/maybe/i, '').replace(/sorry/i, '').trim(),
      });
      setIsLoading(false);
    }, 1500);
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    alert('Copied!');
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-light text-gray-200">Message Rewriter</h1>
        <p className="text-gray-400 mt-1">Your angry email in Calm, Empathetic, and Assertive</p>
      </div>

      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Paste the message you want to rewrite..."
        className="w-full p-4 bg-midnight-800 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none resize-none mb-4"
        rows={6}
      />

      <button
        onClick={handleRewrite}
        disabled={!input.trim() || isLoading}
        className="w-full flex items-center justify-center gap-2 bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors disabled:opacity-50"
      >
        <Wand2 size={18} />
        {isLoading ? 'Rewriting...' : 'Rewrite with AI'}
      </button>

      {rewrites && (
        <div className="mt-8 space-y-4">
          {(['calm', 'empathetic', 'assertive'] as const).map((style) => (
            <div key={style} className="p-4 bg-midnight-800 border border-midnight-700 rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <span className="text-gold capitalize">{style}</span>
                <button
                  onClick={() => copyToClipboard(rewrites[style])}
                  className="text-gray-400 hover:text-gray-200"
                >
                  <Copy size={16} />
                </button>
              </div>
              <p className="text-gray-300">{rewrites[style]}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
