import { useState } from 'react';

const weatherOptions = [
  { id: 'clear', emoji: '☀️', label: 'Clear' },
  { id: 'partly-cloudy', emoji: '🌤️', label: 'Partly Cloudy' },
  { id: 'overcast', emoji: '☁️', label: 'Overcast' },
  { id: 'rain', emoji: '🌧️', label: 'Rain' },
  { id: 'storm', emoji: '⛈️', label: 'Storm' },
  { id: 'fog', emoji: '🌫️', label: 'Fog' },
  { id: 'rainbow', emoji: '🌈', label: 'Rainbow' },
];

export default function WeatherMap() {
  const [selectedWeather, setSelectedWeather] = useState<string | null>(null);
  const [notes, setNotes] = useState('');
  const [history, setHistory] = useState<Array<{ weather: string; date: string }>>([]);

  const handleSave = () => {
    if (selectedWeather) {
      setHistory([{ weather: selectedWeather, date: new Date().toLocaleDateString() }, ...history]);
      setSelectedWeather(null);
      setNotes('');
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-light text-gray-200">Emotional Weather Map</h1>
        <p className="text-gray-400 mt-1">Your emotions as beautiful weather patterns</p>
      </div>

      <div className="mb-8">
        <h2 className="text-gold text-sm font-medium mb-4">How's your emotional weather today?</h2>
        <div className="grid grid-cols-4 gap-3 mb-6">
          {weatherOptions.map((w) => (
            <button
              key={w.id}
              onClick={() => setSelectedWeather(w.id)}
              className={`p-4 rounded-lg text-center transition-all ${
                selectedWeather === w.id
                  ? 'bg-midnight-700 border-2 border-gold'
                  : 'bg-midnight-800/50 border border-midnight-700 hover:border-midnight-600'
              }`}
            >
              <div className="text-3xl mb-1">{w.emoji}</div>
              <div className="text-xs text-gray-400">{w.label}</div>
            </button>
          ))}
        </div>

        {selectedWeather && (
          <>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any notes about your weather? (optional)"
              className="w-full p-4 bg-midnight-800/50 border border-midnight-700 rounded-lg text-gray-200 placeholder-gray-500 focus:border-gold/50 focus:outline-none transition-colors resize-none mb-4"
              rows={3}
            />
            <button
              onClick={handleSave}
              className="bg-gold text-midnight-900 px-6 py-3 rounded-lg font-medium hover:bg-gold-hover transition-colors"
            >
              Save Today's Weather
            </button>
          </>
        )}
      </div>

      {history.length > 0 && (
        <div>
          <h2 className="text-gray-400 text-sm font-medium mb-4">Your Weather History</h2>
          <div className="space-y-2">
            {history.slice(0, 7).map((entry, i) => {
              const weather = weatherOptions.find((w) => w.id === entry.weather);
              return (
                <div key={i} className="flex items-center gap-3 p-3 bg-midnight-800/30 rounded-lg">
                  <span className="text-2xl">{weather?.emoji}</span>
                  <span className="text-gray-300">{entry.date}</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
