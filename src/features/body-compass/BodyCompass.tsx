import { useState } from 'react';

const sensationTypes = [
  'warmth', 'tightness', 'tingling', 'heaviness', 'numbness', 'lightness', 'pain', 'pressure'
];

export default function BodyCompass() {
  const [sensations, setSensations] = useState<Array<{ x: number; y: number; type: string; rating: string }>>([]);
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [selectedRating, setSelectedRating] = useState<string | null>(null);

  const handleBodyClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;

    if (selectedType && selectedRating) {
      setSensations([...sensations, { x, y, type: selectedType, rating: selectedRating }]);
      setSelectedType(null);
      setSelectedRating(null);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-light text-gray-200">Body Compass</h1>
        <p className="text-gray-400 mt-1">Tap where you feel it. Your body knows first.</p>
      </div>

      <div className="mb-6">
        <h2 className="text-gold text-sm font-medium mb-3">1. What sensation?</h2>
        <div className="flex flex-wrap gap-2">
          {sensationTypes.map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-3 py-1 rounded-full text-sm transition-all ${
                selectedType === type
                  ? 'bg-gold text-midnight-900'
                  : 'bg-midnight-800 text-gray-300 hover:bg-midnight-700'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-gold text-sm font-medium mb-3">2. How does it feel?</h2>
        <div className="flex gap-3">
          {['pleasant', 'unpleasant', 'neutral'].map((rating) => (
            <button
              key={rating}
              onClick={() => setSelectedRating(rating)}
              className={`flex-1 py-2 rounded-lg text-sm transition-all ${
                selectedRating === rating
                  ? rating === 'pleasant'
                    ? 'bg-green-900/50 text-green-300 border border-green-500'
                    : rating === 'unpleasant'
                    ? 'bg-red-900/50 text-red-300 border border-red-500'
                    : 'bg-midnight-700 text-gray-300 border border-gold'
                  : 'bg-midnight-800 text-gray-400 hover:bg-midnight-700'
              }`}
            >
              {rating}
            </button>
          ))}
        </div>
      </div>

      <div className="mb-6">
        <h2 className="text-gold text-sm font-medium mb-3">3. Tap where you feel it</h2>
        <div
          onClick={handleBodyClick}
          className="relative w-full aspect-[1/2] bg-midnight-800 rounded-lg border border-midnight-700 cursor-crosshair overflow-hidden"
        >
          {/* Simple body silhouette */}
          <svg viewBox="0 0 100 200" className="w-full h-full opacity-30">
            <ellipse cx="50" cy="25" rx="20" ry="25" fill="currentColor" />
            <rect x="35" y="50" width="30" height="80" rx="10" fill="currentColor" />
            <rect x="15" y="55" width="20" height="60" rx="8" fill="currentColor" />
            <rect x="65" y="55" width="20" height="60" rx="8" fill="currentColor" />
            <rect x="30" y="130" width="15" height="50" rx="6" fill="currentColor" />
            <rect x="55" y="130" width="15" height="50" rx="6" fill="currentColor" />
          </svg>

          {/* Sensation dots */}
          {sensations.map((s, i) => (
            <div
              key={i}
              className="absolute w-4 h-4 rounded-full transform -translate-x-1/2 -translate-y-1/2"
              style={{
                left: `${s.x}%`,
                top: `${s.y}%`,
                backgroundColor: s.rating === 'pleasant' ? '#4ADE80' : s.rating === 'unpleasant' ? '#E85454' : '#C9944A'
              }}
            />
          ))}
        </div>
      </div>

      {sensations.length > 0 && (
        <div className="text-center">
          <p className="text-gray-400 text-sm mb-4">{sensations.length} sensations recorded</p>
          <button
            onClick={() => setSensations([])}
            className="text-red-400 hover:text-red-300 text-sm"
          >
            Clear all
          </button>
        </div>
      )}
    </div>
  );
}
