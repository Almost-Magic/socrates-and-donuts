import { useState } from 'react';
import { Flame, Save } from 'lucide-react';

export default function Letter() {
  const [letter, setLetter] = useState('');
  const [isBurning, setIsBurning] = useState(false);
  const [showBurnOption, setShowBurnOption] = useState(false);

  const handleBurn = () => {
    if (!letter.trim()) return;
    setIsBurning(true);
    // After animation, save to journal
    setTimeout(() => {
      setLetter('');
      setIsBurning(false);
      setShowBurnOption(false);
    }, 3000);
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-light text-gray-200">Letter You'll Never Send</h1>
        <p className="text-gray-400 mt-1">Write it. Burn it. Watch it dissolve.</p>
      </div>

      {!showBurnOption && !isBurning ? (
        <>
          <div className="mb-4">
            <input
              type="text"
              placeholder="Dear..."
              className="w-full p-3 bg-transparent border-b border-midnight-700 text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none transition-colors"
            />
          </div>
          <textarea
            value={letter}
            onChange={(e) => setLetter(e.target.value)}
            placeholder="Write what you need to say..."
            className="w-full p-4 bg-midnight-800/50 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none transition-colors resize-none min-h-[400px]"
          />
          {letter.trim() && (
            <button
              onClick={() => setShowBurnOption(true)}
              className="mt-6 flex items-center gap-2 bg-red-900/30 text-red-400 px-4 py-2 rounded-lg hover:bg-red-900/50 transition-colors"
            >
              <Flame size={18} />
              I'm done writing
            </button>
          )}
        </>
      ) : isBurning ? (
        <div className="min-h-[400px] flex flex-col items-center justify-center">
          <div className="text-6xl animate-pulse">🔥</div>
          <p className="text-gray-400 mt-4">Burning...</p>
          <p className="text-gray-500 text-sm mt-2">Let it go</p>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-300 mb-6">What would you like to do with this letter?</p>
          <div className="space-y-4">
            <button
              onClick={handleBurn}
              className="w-full flex items-center justify-center gap-2 bg-gradient-to-r from-orange-600 to-red-600 text-white px-6 py-4 rounded-lg hover:from-orange-500 hover:to-red-500 transition-all"
            >
              <Flame size={20} />
              Burn it
            </button>
            <button className="w-full flex items-center justify-center gap-2 bg-midnight-700 text-gray-300 px-6 py-4 rounded-lg hover:bg-midnight-600 transition-colors">
              <Save size={20} />
              Keep in journal
            </button>
            <button
              onClick={() => setShowBurnOption(false)}
              className="w-full text-gray-400 hover:text-gray-200 py-2"
            >
              Keep writing
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
